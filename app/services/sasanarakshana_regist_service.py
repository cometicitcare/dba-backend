# app/services/sasanarakshana_regist_service.py
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session

from app.models.sasanarakshana_regist import SasanarakshanaRegist
from app.repositories.sasanarakshana_regist_repo import sasanarakshana_regist_repo
from app.schemas.sasanarakshana_regist import (
    SasanarakshanaRegistCreate,
    SasanarakshanaRegistUpdate,
    SasanarakshanaRegistResponse,
)


class SasanarakshanaRegistService:
    """Business logic for Sasanaarakshana Registration Management operations."""

    def _to_response(self, record: SasanarakshanaRegist) -> SasanarakshanaRegistResponse:
        return SasanarakshanaRegistResponse.from_orm_map(record)

    def create(
        self,
        db: Session,
        *,
        payload: SasanarakshanaRegistCreate,
        actor_id: Optional[str] = None,
    ) -> SasanarakshanaRegistResponse:
        """Create a new Sasanaarakshana Registration record."""
        record = sasanarakshana_regist_repo.create(db, obj_in=payload, created_by=actor_id)
        return self._to_response(record)

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search_key: Optional[str] = None,
    ) -> Tuple[List[SasanarakshanaRegistResponse], int]:
        """Get paginated list of records."""
        records, total = sasanarakshana_regist_repo.get_all(
            db, skip=skip, limit=limit, search_key=search_key
        )
        return [self._to_response(r) for r in records], total

    def get_by_id(
        self, db: Session, sar_id: int
    ) -> Optional[SasanarakshanaRegistResponse]:
        """Get a single record by ID."""
        record = sasanarakshana_regist_repo.get_by_id(db, sar_id)
        if not record:
            return None
        return self._to_response(record)

    def update(
        self,
        db: Session,
        *,
        sar_id: int,
        payload: SasanarakshanaRegistUpdate,
        actor_id: Optional[str] = None,
    ) -> Optional[SasanarakshanaRegistResponse]:
        """Update an existing record."""
        db_obj = sasanarakshana_regist_repo.get_by_id(db, sar_id)
        if not db_obj:
            return None
        updated = sasanarakshana_regist_repo.update(
            db, db_obj=db_obj, obj_in=payload, updated_by=actor_id
        )
        return self._to_response(updated)

    def delete(
        self,
        db: Session,
        *,
        sar_id: int,
        actor_id: Optional[str] = None,
    ) -> bool:
        """Soft-delete a record. Returns True if deleted, False if not found."""
        result = sasanarakshana_regist_repo.soft_delete(db, sar_id=sar_id, deleted_by=actor_id)
        return result is not None


sasanarakshana_regist_service = SasanarakshanaRegistService()
