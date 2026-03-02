# app/services/bank_service.py
from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.bank import Bank
from app.repositories.bank_repo import bank_repo
from app.schemas.bank import BankCreate, BankUpdate


class BankService:
    """Business logic for bank management."""

    def create_bank(
        self,
        db: Session,
        *,
        payload: BankCreate,
        actor_id: Optional[str],
    ) -> Bank:
        create_data = self._strip_strings(payload.model_dump())
        create_payload = BankCreate(**create_data)
        return bank_repo.create(db, data=create_payload, actor_id=actor_id)

    def get_bank(self, db: Session, bk_id: int) -> Bank | None:
        return bank_repo.get(db, bk_id)

    def get_bank_by_code(self, db: Session, bk_bcode: str) -> Bank | None:
        code = bk_bcode.strip()
        if not code:
            return None
        return bank_repo.get_by_code(db, code)

    def list_banks(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> list[Bank]:
        limit = max(1, min(limit, 200))
        skip = max(0, skip)
        search_term = search.strip() if search else None
        if search_term == "":
            search_term = None
        return bank_repo.list(db, skip=skip, limit=limit, search=search_term)

    def count_banks(self, db: Session, *, search: Optional[str] = None) -> int:
        search_term = search.strip() if search else None
        if search_term == "":
            search_term = None
        return bank_repo.count(db, search=search_term)

    def update_bank(
        self,
        db: Session,
        *,
        bk_id: int,
        payload: BankUpdate,
        actor_id: Optional[str],
    ) -> Bank:
        entity = bank_repo.get(db, bk_id)
        if not entity:
            raise ValueError("Bank record not found.")

        update_data = self._strip_strings(payload.model_dump(exclude_unset=True))
        if not update_data:
            raise ValueError("No updates supplied.")

        update_payload = BankUpdate(**update_data)
        return bank_repo.update(
            db, entity=entity, data=update_payload, actor_id=actor_id
        )

    def delete_bank(
        self,
        db: Session,
        *,
        bk_id: int,
        actor_id: Optional[str],
    ) -> Bank:
        entity = bank_repo.get(db, bk_id)
        if not entity:
            raise ValueError("Bank record not found.")
        return bank_repo.soft_delete(db, entity=entity, actor_id=actor_id)

    @staticmethod
    def _strip_strings(data: Dict[str, Any]) -> Dict[str, Any]:
        cleaned: Dict[str, Any] = {}
        for key, value in data.items():
            if isinstance(value, str):
                cleaned[key] = value.strip()
            else:
                cleaned[key] = value
        return cleaned


bank_service = BankService()
