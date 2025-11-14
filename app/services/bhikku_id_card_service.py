from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.repositories.bhikku_id_card_repo import bhikku_id_card_repo
from app.repositories.bhikku_repo import bhikku_repo
from app.schemas.bhikku_id_card import BhikkuIDCardCreate, BhikkuIDCardUpdate
from app.storage import LocalStorage, local_storage
from app.services.bhikku_id_card_workflow_service import bhikku_id_card_workflow_service


class BhikkuIDCardService:
    """Business logic helpers for bhikku ID cards, including file handling."""

    def __init__(self, storage: Optional[LocalStorage] = None) -> None:
        self._storage = storage or local_storage

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def create_card(
        self,
        db: Session,
        *,
        payload: BhikkuIDCardCreate,
        actor_id: Optional[str],
        left_thumbprint: Optional[UploadFile] = None,
        applicant_image: Optional[UploadFile] = None,
    ):
        create_data = self._strip_strings(payload.model_dump(exclude_unset=True))
        bhikku = self._resolve_bhikku_reference(
            db,
            br_id=create_data.get("bic_br_id"),
            regn=create_data.get("bic_regn"),
        )
        create_data["bic_br_id"] = bhikku.br_id
        create_data["bic_regn"] = bhikku.br_regn
        self._ensure_unique_registration(
            db, bhikku_id=bhikku.br_id, registration=bhikku.br_regn
        )
        self._ensure_unique_form_no(
            db, create_data.get("bic_form_no"), current_id=None
        )

        context_key = self._resolve_file_context(
            national_id=create_data.get("bic_national_id"),
            fallback_id=create_data.get("bic_regn") or create_data.get("bic_br_id"),
        )
        if left_thumbprint:
            create_data["bic_left_thumbprint_url"] = self._store_upload(
                left_thumbprint, context_key, prefix="left-thumbprint"
            )
        if applicant_image:
            create_data["bic_applicant_image_url"] = self._store_upload(
                applicant_image, context_key, prefix="applicant-photo"
            )

        create_payload = BhikkuIDCardCreate(**create_data)
        created_card = bhikku_id_card_repo.create(
            db, data=create_payload, actor_id=actor_id
        )
        
        # Create workflow record with PENDING status
        bhikku_id_card_workflow_service.get_or_create_workflow(db, created_card)
        
        return created_card

    def update_card(
        self,
        db: Session,
        *,
        bic_id: int,
        payload: BhikkuIDCardUpdate,
        actor_id: Optional[str],
        left_thumbprint: Optional[UploadFile] = None,
        applicant_image: Optional[UploadFile] = None,
    ):
        entity = bhikku_id_card_repo.get(db, bic_id)
        if not entity:
            raise ValueError("Bhikku ID card not found.")

        update_data = self._strip_strings(payload.model_dump(exclude_unset=True))

        if "bic_form_no" in update_data and update_data["bic_form_no"]:
            self._ensure_unique_form_no(
                db, update_data["bic_form_no"], current_id=entity.bic_id
            )

        if "bic_regn" in update_data or "bic_br_id" in update_data:
            bhikku = self._resolve_bhikku_reference(
                db,
                br_id=update_data.get("bic_br_id"),
                regn=update_data.get("bic_regn"),
            )
            update_data["bic_br_id"] = bhikku.br_id
            update_data["bic_regn"] = bhikku.br_regn
            self._ensure_unique_registration(
                db,
                bhikku_id=bhikku.br_id,
                registration=bhikku.br_regn,
                current_card_id=entity.bic_id,
            )

        context_key = self._resolve_file_context(
            national_id=update_data.get("bic_national_id")
            or entity.bic_national_id,
            fallback_id=update_data.get("bic_regn")
            or update_data.get("bic_br_id")
            or entity.bic_regn
            or entity.bic_br_id,
        )
        if left_thumbprint:
            update_data["bic_left_thumbprint_url"] = self._store_upload(
                left_thumbprint, context_key, prefix="left-thumbprint"
            )
        if applicant_image:
            update_data["bic_applicant_image_url"] = self._store_upload(
                applicant_image, context_key, prefix="applicant-photo"
            )

        if not update_data:
            raise ValueError("No updates supplied.")

        update_payload = BhikkuIDCardUpdate(**update_data)
        updated = bhikku_id_card_repo.update(
            db, entity=entity, data=update_payload, actor_id=actor_id
        )
        return updated

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
        return bhikku_id_card_repo.list(
            db, skip=skip, limit=limit, search=search_term
        )

    def count_cards(self, db: Session, *, search: Optional[str] = None) -> int:
        search_term = search.strip() if search else None
        if search_term == "":
            search_term = None
        return bhikku_id_card_repo.count(db, search=search_term)

    def get_card(self, db: Session, bic_id: int):
        return bhikku_id_card_repo.get(db, bic_id)

    def delete_card(self, db: Session, *, bic_id: int, actor_id: Optional[str]):
        entity = bhikku_id_card_repo.get(db, bic_id)
        if not entity:
            raise ValueError("Bhikku ID card not found.")
        return bhikku_id_card_repo.soft_delete(
            db, entity=entity, actor_id=actor_id
        )

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _resolve_bhikku_reference(
        self,
        db: Session,
        *,
        br_id: Optional[int],
        regn: Optional[str],
    ):
        normalized_regn = None
        if regn is not None:
            normalized_regn = regn.strip()
            if normalized_regn:
                normalized_regn = normalized_regn.upper()
            else:
                normalized_regn = None

        if br_id is not None:
            if br_id < 1:
                raise ValueError("bic_br_id must be a positive integer.")
            bhikku = bhikku_repo.get_by_id(db, br_id)
            if not bhikku:
                raise ValueError(f"bic_br_id '{br_id}' does not reference a bhikku.")
            if normalized_regn and bhikku.br_regn != normalized_regn:
                raise ValueError(
                    "Provided bic_regn does not match the selected bhikku."
                )
            return bhikku

        if normalized_regn:
            bhikku = bhikku_repo.get_by_regn(db, normalized_regn)
            if not bhikku:
                raise ValueError(
                    f"bic_regn '{normalized_regn}' does not reference a bhikku."
                )
            return bhikku

        raise ValueError("Either bic_br_id or bic_regn must be provided.")

    def _ensure_unique_registration(
        self,
        db: Session,
        *,
        bhikku_id: int,
        registration: str,
        current_card_id: Optional[int] = None,
    ) -> None:
        existing_by_id = bhikku_id_card_repo.get_by_bhikku_id(
            db, bhikku_id=bhikku_id
        )
        if existing_by_id and existing_by_id.bic_id != current_card_id:
            raise ValueError(
                f"An ID card already exists for bhikku registration {registration}."
            )

        existing_by_reg = bhikku_id_card_repo.get_by_registration(
            db, registration=registration
        )
        if existing_by_reg and existing_by_reg.bic_id != current_card_id:
            raise ValueError(
                f"An ID card already exists for bhikku registration {registration}."
            )

    def _ensure_unique_form_no(
        self, db: Session, form_no: Optional[str], *, current_id: Optional[int]
    ) -> None:
        if not form_no:
            return
        existing = bhikku_id_card_repo.get_by_form_no(db, form_no)
        if existing and existing.bic_id != current_id:
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


bhikku_id_card_service = BhikkuIDCardService()
