from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models.nikaya import NikayaData
from app.repositories.nikaya_repo import nikaya_repo
from app.schemas.nikaya import NikayaCreate, NikayaUpdate


class NikayaService:
    """Business logic layer for Bhikku Nikaya data management."""

    def create_entry(
        self, db: Session, *, payload: NikayaCreate, actor_id: Optional[str]
    ) -> NikayaData:
        existing = nikaya_repo.get_by_nkn(db, payload.nk_nkn)
        if existing:
            raise ValueError(f"nk_nkn '{payload.nk_nkn}' already exists.")
        return nikaya_repo.create(db, data=payload, actor_id=actor_id)

    def list_entries(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> list[NikayaData]:
        return nikaya_repo.list(db, skip=skip, limit=limit, search=search)

    def count_entries(self, db: Session, *, search: Optional[str] = None) -> int:
        return nikaya_repo.count(db, search=search)

    def get_by_id(self, db: Session, nk_id: int) -> Optional[NikayaData]:
        return nikaya_repo.get(db, nk_id)

    def get_by_nkn(self, db: Session, nk_nkn: str) -> Optional[NikayaData]:
        return nikaya_repo.get_by_nkn(db, nk_nkn)

    def update_entry(
        self,
        db: Session,
        *,
        entity_id: int,
        payload: NikayaUpdate,
        actor_id: Optional[str],
    ) -> NikayaData:
        entity = nikaya_repo.get(db, entity_id)
        if not entity:
            raise ValueError("Nikaya data record not found.")

        return nikaya_repo.update(db, entity=entity, data=payload, actor_id=actor_id)

    def delete_entry(
        self,
        db: Session,
        *,
        entity_id: int,
        actor_id: Optional[str],
    ) -> NikayaData:
        entity = nikaya_repo.get(db, entity_id)
        if not entity:
            raise ValueError("Nikaya data record not found.")
        return nikaya_repo.soft_delete(db, entity=entity, actor_id=actor_id)


nikaya_service = NikayaService()
