# app/services/bank_branch_service.py
from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.bank_branch import BankBranch
from app.repositories.bank_branch_repo import bank_branch_repo
from app.schemas.bank_branch import BankBranchCreate, BankBranchUpdate


class BankBranchService:
    """Business logic for bank branch management."""

    def create_bank_branch(
        self,
        db: Session,
        *,
        payload: BankBranchCreate,
        actor_id: Optional[str],
    ) -> BankBranch:
        create_data = self._strip_strings(payload.model_dump())
        create_payload = BankBranchCreate(**create_data)
        return bank_branch_repo.create(db, data=create_payload, actor_id=actor_id)

    def get_bank_branch(self, db: Session, bb_id: int) -> BankBranch | None:
        return bank_branch_repo.get(db, bb_id)

    def get_bank_branch_by_code(
        self, db: Session, bb_bbcode: str
    ) -> BankBranch | None:
        code = bb_bbcode.strip()
        if not code:
            return None
        return bank_branch_repo.get_by_branch_code(db, code)

    def list_bank_branches(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> list[BankBranch]:
        limit = max(1, min(limit, 200))
        skip = max(0, skip)
        search_term = search.strip() if search else None
        if search_term == "":
            search_term = None
        return bank_branch_repo.list(db, skip=skip, limit=limit, search=search_term)

    def count_bank_branches(
        self, db: Session, *, search: Optional[str] = None
    ) -> int:
        search_term = search.strip() if search else None
        if search_term == "":
            search_term = None
        return bank_branch_repo.count(db, search=search_term)

    def update_bank_branch(
        self,
        db: Session,
        *,
        bb_id: int,
        payload: BankBranchUpdate,
        actor_id: Optional[str],
    ) -> BankBranch:
        entity = bank_branch_repo.get(db, bb_id)
        if not entity:
            raise ValueError("Bank branch record not found.")

        update_data = self._strip_strings(payload.model_dump(exclude_unset=True))
        if not update_data:
            raise ValueError("No updates supplied.")

        update_payload = BankBranchUpdate(**update_data)
        return bank_branch_repo.update(
            db, entity=entity, data=update_payload, actor_id=actor_id
        )

    def delete_bank_branch(
        self,
        db: Session,
        *,
        bb_id: int,
        actor_id: Optional[str],
    ) -> BankBranch:
        entity = bank_branch_repo.get(db, bb_id)
        if not entity:
            raise ValueError("Bank branch record not found.")
        return bank_branch_repo.soft_delete(db, entity=entity, actor_id=actor_id)

    @staticmethod
    def _strip_strings(data: Dict[str, Any]) -> Dict[str, Any]:
        cleaned: Dict[str, Any] = {}
        for key, value in data.items():
            if isinstance(value, str):
                cleaned[key] = value.strip()
            else:
                cleaned[key] = value
        return cleaned


bank_branch_service = BankBranchService()
