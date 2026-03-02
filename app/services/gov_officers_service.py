# app/services/gov_officers_service.py
from __future__ import annotations

from typing import List, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.gov_officers import GovOfficer
from app.repositories.gov_officers_repo import gov_officers_repo
from app.schemas.gov_officers import (
    GovOfficerCreate,
    GovOfficerResponse,
    GovOfficerUpdate,
)


class GovOfficerService:
    """Business logic for Government Officers."""

    # ── helpers ───────────────────────────────────────────────────────────────

    def _to_response(self, record: GovOfficer) -> GovOfficerResponse:
        return GovOfficerResponse.model_validate(record)

    # ── CRUD ──────────────────────────────────────────────────────────────────

    def create(
        self,
        db: Session,
        *,
        payload: GovOfficerCreate,
        actor_id: Optional[str] = None,
    ) -> GovOfficerResponse:
        """Create a new Government Officer record."""
        try:
            record = gov_officers_repo.create(db, obj_in=payload, created_by=actor_id)
        except IntegrityError as exc:
            db.rollback()
            raise ValueError(f"Database error while creating officer: {exc}") from exc
        return self._to_response(record)

    def get_by_id(
        self, db: Session, go_id: int
    ) -> Optional[GovOfficerResponse]:
        record = gov_officers_repo.get_by_id(db, go_id)
        return self._to_response(record) if record else None

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 10,
        search_key: Optional[str] = None,
    ) -> Tuple[List[GovOfficerResponse], int]:
        records, total = gov_officers_repo.get_all(
            db, skip=skip, limit=limit, search_key=search_key
        )
        return [self._to_response(r) for r in records], total

    def update(
        self,
        db: Session,
        *,
        go_id: int,
        payload: GovOfficerUpdate,
        actor_id: Optional[str] = None,
    ) -> Optional[GovOfficerResponse]:
        db_obj = gov_officers_repo.get_by_id(db, go_id)
        if not db_obj:
            raise ValueError(f"Government officer with ID {go_id} not found.")
        updated = gov_officers_repo.update(
            db, db_obj=db_obj, obj_in=payload, updated_by=actor_id
        )
        return self._to_response(updated)

    def delete(
        self,
        db: Session,
        *,
        go_id: int,
        actor_id: Optional[str] = None,
    ) -> bool:
        result = gov_officers_repo.soft_delete(db, go_id=go_id, deleted_by=actor_id)
        return result is not None


gov_officers_service = GovOfficerService()
