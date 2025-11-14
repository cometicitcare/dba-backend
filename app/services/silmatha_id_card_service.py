from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.repositories.bhikku_repo import bhikku_repo
from app.repositories.silmatha_id_card_repo import silmatha_id_card_repo
from app.schemas.silmatha_id_card import (
    SilmathaIDCardCreate,
    SilmathaIDCardUpdate,
)
from app.storage import LocalStorage, local_storage


class SilmathaIDCardService:
    """Business logic helpers for silmatha ID cards, including file handling."""

    def __init__(self, storage: Optional[LocalStorage] = None) -> None:
        self._storage = storage or local_storage

    def create_card(
        self,
        db: Session,
        *,
        payload: SilmathaIDCardCreate,
        actor_id: Optional[str],
        left_thumbprint: Optional[UploadFile] = None,
        applicant_image: Optional[UploadFile] = None,
    ):
        create_data = self._strip_strings(payload.model_dump(exclude_unset=True))
        self._validate_required_references(db, create_data)
        self._ensure_unique_form_no(
            db, create_data.get("sic_form_no"), current_id=None
        )

        context_key = self._resolve_file_context(
            national_id=create_data.get("sic_national_id"),
            fallback_id=create_data.get("sic_regn") or create_data.get("sic_br_id"),
        )
        if left_thumbprint:
            create_data["sic_left_thumbprint_url"] = self._store_upload(
                left_thumbprint, context_key, prefix="left-thumbprint"
            )
        if applicant_image:
            create_data["sic_applicant_image_url"] = self._store_upload(
                applicant_image, context_key, prefix="applicant-photo"
            )

        create_payload = SilmathaIDCardCreate(**create_data)
        return silmatha_id_card_repo.create(
            db, data=create_payload, actor_id=actor_id
        )

    def update_card(
        self,
        db: Session,
        *,
        sic_id: int,
        payload: SilmathaIDCardUpdate,
        actor_id: Optional[str],
        left_thumbprint: Optional[UploadFile] = None,
        applicant_image: Optional[UploadFile] = None,
    ):
        entity = silmatha_id_card_repo.get(db, sic_id)
        if not entity:
            raise ValueError("Silmatha ID card not found.")

        update_data = self._strip_strings(payload.model_dump(exclude_unset=True))

        if "sic_form_no" in update_data and update_data["sic_form_no"]:
            self._ensure_unique_form_no(
                db, update_data["sic_form_no"], current_id=entity.sic_id
            )

        for field in ("sic_regn", "sic_br_id"):
            if field in update_data:
                self._validate_bhikku_reference(
                    db, update_data.get(field), field_name=field
                )

        context_key = self._resolve_file_context(
            national_id=update_data.get("sic_national_id")
            or entity.sic_national_id,
            fallback_id=update_data.get("sic_regn")
            or update_data.get("sic_br_id")
            or entity.sic_regn
            or entity.sic_br_id,
        )
        if left_thumbprint:
            update_data["sic_left_thumbprint_url"] = self._store_upload(
                left_thumbprint, context_key, prefix="left-thumbprint"
            )
        if applicant_image:
            update_data["sic_applicant_image_url"] = self._store_upload(
                applicant_image, context_key, prefix="applicant-photo"
            )

        if not update_data:
            raise ValueError("No updates supplied.")

        update_payload = SilmathaIDCardUpdate(**update_data)
        return silmatha_id_card_repo.update(
            db, entity=entity, data=update_payload, actor_id=actor_id
        )

    def list_cards(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ):
        limit = max(1, min(limit, 200))
        skip = max(0, skip)
        search_term = search.strip() if search else None
        if search_term == "":
            search_term = None
        return silmatha_id_card_repo.list(
            db, skip=skip, limit=limit, search=search_term
        )

    def count_cards(self, db: Session, *, search: Optional[str] = None) -> int:
        search_term = search.strip() if search else None
        if search_term == "":
            search_term = None
        return silmatha_id_card_repo.count(db, search=search_term)

    def get_card(self, db: Session, sic_id: int):
        return silmatha_id_card_repo.get(db, sic_id)

    def delete_card(self, db: Session, *, sic_id: int, actor_id: Optional[str]):
        entity = silmatha_id_card_repo.get(db, sic_id)
        if not entity:
            raise ValueError("Silmatha ID card not found.")
        return silmatha_id_card_repo.soft_delete(
            db, entity=entity, actor_id=actor_id
        )

    def _validate_required_references(
        self, db: Session, payload: Dict[str, Any]
    ) -> None:
        for field in ("sic_regn", "sic_br_id"):
            self._validate_bhikku_reference(
                db, payload.get(field), field_name=field
            )

    def _validate_bhikku_reference(
        self, db: Session, value: Optional[int], *, field_name: str
    ) -> None:
        if value is None:
            raise ValueError(f"{field_name} is required.")
        if value < 1:
            raise ValueError(f"{field_name} must be a positive integer.")
        exists = bhikku_repo.get_by_id(db, value)
        if not exists:
            raise ValueError(f"{field_name} '{value}' does not reference a bhikku.")

    def _ensure_unique_form_no(
        self, db: Session, form_no: Optional[str], *, current_id: Optional[int]
    ) -> None:
        if not form_no:
            return
        existing = silmatha_id_card_repo.get_by_form_no(db, form_no)
        if existing and existing.sic_id != current_id:
            raise ValueError(f"Form number '{form_no}' already exists.")

    def _store_upload(
        self, upload: UploadFile, context_key: str, *, prefix: str
    ) -> str:
        extension = Path(upload.filename or "").suffix.lower()
        if len(extension) > 10:
            extension = ""
        filename = f"{prefix}-{uuid4().hex}{extension}"
        now = datetime.utcnow()
        timestamp_segment = now.strftime("%H%M%S%f")
        relative_path = Path(
            str(now.year),
            f"{now.month:02d}",
            f"{now.day:02d}",
            context_key,
            timestamp_segment,
            filename,
        )
        return self._storage.save_fileobj(upload.file, relative_path)

    def _resolve_file_context(
        self, *, national_id: Optional[str], fallback_id: Any
    ) -> str:
        candidate = national_id or fallback_id or uuid4().hex
        candidate_str = str(candidate)
        sanitized = re.sub(r"[^A-Za-z0-9_-]", "", candidate_str)
        return sanitized or uuid4().hex

    @staticmethod
    def _strip_strings(data: Dict[str, Any]) -> Dict[str, Any]:
        cleaned: Dict[str, Any] = {}
        for key, value in data.items():
            if isinstance(value, str):
                cleaned[key] = value.strip()
            else:
                cleaned[key] = value
        return cleaned


silmatha_id_card_service = SilmathaIDCardService()
