# app/services/religion_service.py
from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.religion import Religion
from app.repositories.religion_repo import religion_repo
from app.schemas.religion import ReligionCreate, ReligionUpdate


class ReligionService:
    """Business logic for religion management."""

    def create_religion(
        self,
        db: Session,
        *,
        payload: ReligionCreate,
        actor_id: Optional[str],
    ) -> Religion:
        create_data = self._strip_strings(payload.model_dump())
        create_payload = ReligionCreate(**create_data)
        return religion_repo.create(db, data=create_payload, actor_id=actor_id)

    def get_religion(self, db: Session, rl_id: int) -> Religion | None:
        return religion_repo.get(db, rl_id)

    def get_religion_by_code(self, db: Session, rl_code: str) -> Religion | None:
        code = rl_code.strip() if rl_code else ""
        if not code:
            return None
        return religion_repo.get_by_code(db, code)

    def list_religions(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> list[Religion]:
        limit = max(1, min(limit, 200))
        skip = max(0, skip)
        search_term = search.strip() if search else None
        if search_term == "":
            search_term = None
        return religion_repo.list(db, skip=skip, limit=limit, search=search_term)

    def count_religions(self, db: Session, *, search: Optional[str] = None) -> int:
        search_term = search.strip() if search else None
        if search_term == "":
            search_term = None
        return religion_repo.count(db, search=search_term)

    def update_religion(
        self,
        db: Session,
        *,
        rl_id: int,
        payload: ReligionUpdate,
        actor_id: Optional[str],
    ) -> Religion:
        entity = religion_repo.get(db, rl_id)
        if not entity:
            raise ValueError("Religion record not found.")

        update_data = self._strip_strings(payload.model_dump(exclude_unset=True))
        if not update_data:
            raise ValueError("No updates supplied.")

        update_payload = ReligionUpdate(**update_data)
        return religion_repo.update(
            db,
            entity=entity,
            data=update_payload,
            actor_id=actor_id,
        )

    def delete_religion(
        self,
        db: Session,
        *,
        rl_id: int,
        actor_id: Optional[str],
    ) -> Religion:
        entity = religion_repo.get(db, rl_id)
        if not entity:
            raise ValueError("Religion record not found.")
        return religion_repo.soft_delete(db, entity=entity, actor_id=actor_id)

    @staticmethod
    def _strip_strings(data: Dict[str, Any]) -> Dict[str, Any]:
        cleaned: Dict[str, Any] = {}
        for key, value in data.items():
            if isinstance(value, str):
                cleaned[key] = value.strip()
            else:
                cleaned[key] = value
        return cleaned


religion_service = ReligionService()
