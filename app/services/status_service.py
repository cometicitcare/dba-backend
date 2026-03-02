# app/services/status_service.py
from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.status import StatusData
from app.repositories.status_repo import status_repo
from app.schemas.status import StatusCreate, StatusUpdate


class StatusService:
    """Business logic for status management."""

    def create_status(
        self,
        db: Session,
        *,
        payload: StatusCreate,
        actor_id: Optional[str],
    ) -> StatusData:
        create_data = self._strip_strings(payload.model_dump())
        create_payload = StatusCreate(**create_data)
        return status_repo.create(
            db,
            data=create_payload,
            actor_id=actor_id,
        )

    def get_status(self, db: Session, st_id: int) -> StatusData | None:
        return status_repo.get(db, st_id)

    def get_status_by_code(
        self,
        db: Session,
        st_statcd: str,
    ) -> StatusData | None:
        code = st_statcd.strip() if isinstance(st_statcd, str) else ""
        if not code:
            return None
        return status_repo.get_by_code(db, code)

    def list_statuses(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> list[StatusData]:
        limit = max(1, min(limit, 200))
        skip = max(0, skip)
        search_term = search.strip() if isinstance(search, str) else None
        if search_term == "":
            search_term = None

        return status_repo.list(
            db,
            skip=skip,
            limit=limit,
            search=search_term,
        )

    def count_statuses(
        self,
        db: Session,
        *,
        search: Optional[str] = None,
    ) -> int:
        search_term = search.strip() if isinstance(search, str) else None
        if search_term == "":
            search_term = None
        return status_repo.count(db, search=search_term)

    def update_status(
        self,
        db: Session,
        *,
        st_id: int,
        payload: StatusUpdate,
        actor_id: Optional[str],
    ) -> StatusData:
        entity = status_repo.get(db, st_id)
        if not entity:
            raise ValueError("Status not found.")

        update_data = self._strip_strings(payload.model_dump(exclude_unset=True))
        if not update_data:
            raise ValueError("No updates supplied.")

        update_payload = StatusUpdate(**update_data)
        return status_repo.update(
            db,
            entity=entity,
            data=update_payload,
            actor_id=actor_id,
        )

    def delete_status(
        self,
        db: Session,
        *,
        st_id: int,
        actor_id: Optional[str],
    ) -> StatusData:
        entity = status_repo.get(db, st_id)
        if not entity:
            raise ValueError("Status not found.")
        return status_repo.soft_delete(
            db,
            entity=entity,
            actor_id=actor_id,
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


status_service = StatusService()
