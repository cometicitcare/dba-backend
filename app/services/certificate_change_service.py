# app/services/certificate_change_service.py
from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.certificate_change import CertificateChange
from app.repositories.certificate_change_repo import certificate_change_repo
from app.schemas.certificate_change import (
    CertificateChangeCreate,
    CertificateChangeUpdate,
)


class CertificateChangeService:
    """Business logic for certificate change management."""

    def create_certificate_change(
        self,
        db: Session,
        *,
        payload: CertificateChangeCreate,
        actor_id: Optional[str],
    ) -> CertificateChange:
        create_data = self._strip_strings(payload.model_dump())
        create_payload = CertificateChangeCreate(**create_data)
        return certificate_change_repo.create(
            db, data=create_payload, actor_id=actor_id
        )

    def get_certificate_change(
        self, db: Session, ch_id: int
    ) -> CertificateChange | None:
        return certificate_change_repo.get(db, ch_id)

    def list_certificate_changes(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> list[CertificateChange]:
        limit = max(1, min(limit, 200))
        skip = max(0, skip)
        search_term = search.strip() if search else None
        if search_term == "":
            search_term = None
        return certificate_change_repo.list(
            db, skip=skip, limit=limit, search=search_term
        )

    def count_certificate_changes(
        self, db: Session, *, search: Optional[str] = None
    ) -> int:
        search_term = search.strip() if search else None
        if search_term == "":
            search_term = None
        return certificate_change_repo.count(db, search=search_term)

    def update_certificate_change(
        self,
        db: Session,
        *,
        ch_id: int,
        payload: CertificateChangeUpdate,
        actor_id: Optional[str],
    ) -> CertificateChange:
        entity = certificate_change_repo.get(db, ch_id)
        if not entity:
            raise ValueError("Certificate change record not found.")

        update_data = self._strip_strings(payload.model_dump(exclude_unset=True))
        update_data = {key: value for key, value in update_data.items() if value is not None}
        if not update_data:
            raise ValueError("No updates supplied.")

        update_payload = CertificateChangeUpdate(**update_data)
        return certificate_change_repo.update(
            db, entity=entity, data=update_payload, actor_id=actor_id
        )

    def delete_certificate_change(
        self,
        db: Session,
        *,
        ch_id: int,
        actor_id: Optional[str],
    ) -> CertificateChange:
        entity = certificate_change_repo.get(db, ch_id)
        if not entity:
            raise ValueError("Certificate change record not found.")
        return certificate_change_repo.soft_delete(
            db, entity=entity, actor_id=actor_id
        )

    @staticmethod
    def _strip_strings(data: Dict[str, Any]) -> Dict[str, Any]:
        cleaned: Dict[str, Any] = {}
        for key, value in data.items():
            if isinstance(value, str):
                cleaned[key] = value.strip()
            else:
                cleaned[key] = value
        return cleaned


certificate_change_service = CertificateChangeService()
