# app/repositories/bank_branch_repo.py
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.bank import Bank
from app.models.bank_branch import BankBranch
from app.models.user import UserAccount
from app.schemas.bank_branch import BankBranchCreate, BankBranchUpdate


class BankBranchRepository:
    """Data access helpers for bank branch records."""

    def get(self, db: Session, bb_id: int) -> Optional[BankBranch]:
        return (
            db.query(BankBranch)
            .filter(
                BankBranch.bb_id == bb_id,
                BankBranch.bb_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_branch_code(
        self, db: Session, bb_bbcode: str
    ) -> Optional[BankBranch]:
        return (
            db.query(BankBranch)
            .filter(
                BankBranch.bb_bbcode == bb_bbcode,
                BankBranch.bb_is_deleted.is_(False),
            )
            .first()
        )

    def list(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> list[BankBranch]:
        query = db.query(BankBranch).filter(BankBranch.bb_is_deleted.is_(False))

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    BankBranch.bb_bbcode.ilike(term),
                    BankBranch.bb_bcode.ilike(term),
                    BankBranch.bb_brname.ilike(term),
                )
            )

        return (
            query.order_by(BankBranch.bb_id)
            .offset(max(skip, 0))
            .limit(limit)
            .all()
        )

    def count(self, db: Session, *, search: Optional[str] = None) -> int:
        query = db.query(func.count(BankBranch.bb_id)).filter(
            BankBranch.bb_is_deleted.is_(False)
        )

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    BankBranch.bb_bbcode.ilike(term),
                    BankBranch.bb_bcode.ilike(term),
                    BankBranch.bb_brname.ilike(term),
                )
            )

        return query.scalar() or 0

    def create(
        self,
        db: Session,
        *,
        data: BankBranchCreate,
        actor_id: Optional[str],
    ) -> BankBranch:
        self._assert_user_exists(db, actor_id, "actor_id")
        payload = data.model_dump()
        payload["bb_bcode"] = payload["bb_bcode"].strip()
        payload["bb_bbcode"] = payload["bb_bbcode"].strip()
        if payload.get("bb_brname") is not None:
            payload["bb_brname"] = payload["bb_brname"].strip()
        payload.setdefault("bb_is_deleted", False)
        payload.setdefault("bb_version_number", 1)
        payload["bb_created_by"] = actor_id
        payload["bb_updated_by"] = actor_id

        self._assert_bank_exists(db, payload["bb_bcode"])
        self._assert_unique_branch_code(db, payload["bb_bbcode"])

        entity = BankBranch(**payload)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def update(
        self,
        db: Session,
        *,
        entity: BankBranch,
        data: BankBranchUpdate,
        actor_id: Optional[str],
    ) -> BankBranch:
        self._assert_user_exists(db, actor_id, "actor_id")

        update_data = data.model_dump(exclude_unset=True)
        if "bb_bcode" in update_data and update_data["bb_bcode"] is not None:
            update_data["bb_bcode"] = update_data["bb_bcode"].strip()
        if "bb_bbcode" in update_data and update_data["bb_bbcode"] is not None:
            update_data["bb_bbcode"] = update_data["bb_bbcode"].strip()
        if "bb_brname" in update_data and update_data["bb_brname"] is not None:
            update_data["bb_brname"] = update_data["bb_brname"].strip()

        next_bcode = update_data.get("bb_bcode", entity.bb_bcode)
        next_branch_code = update_data.get("bb_bbcode", entity.bb_bbcode)

        self._assert_bank_exists(db, next_bcode)
        if next_branch_code != entity.bb_bbcode:
            self._assert_unique_branch_code(
                db, next_branch_code, exclude_id=entity.bb_id
            )

        for key, value in update_data.items():
            setattr(entity, key, value)

        entity.bb_updated_by = actor_id
        entity.bb_version_number = (entity.bb_version_number or 1) + 1
        db.commit()
        db.refresh(entity)
        return entity

    def soft_delete(
        self, db: Session, *, entity: BankBranch, actor_id: Optional[str]
    ) -> BankBranch:
        self._assert_user_exists(db, actor_id, "actor_id")
        entity.bb_is_deleted = True
        entity.bb_updated_by = actor_id
        entity.bb_version_number = (entity.bb_version_number or 1) + 1
        db.commit()
        db.refresh(entity)
        return entity

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _assert_user_exists(
        self, db: Session, user_id: Optional[str], field_name: str
    ) -> None:
        if not user_id:
            raise ValueError(f"{field_name} is required.")
        exists = (
            db.query(UserAccount.ua_user_id)
            .filter(
                UserAccount.ua_user_id == user_id,
                UserAccount.ua_is_deleted.is_(False),
            )
            .first()
        )
        if not exists:
            raise ValueError(f"{field_name} '{user_id}' does not exist.")

    def _assert_bank_exists(self, db: Session, bank_code: Optional[str]) -> None:
        if not bank_code:
            raise ValueError("bb_bcode is required.")
        normalized = bank_code.strip()
        if normalized == "":
            raise ValueError("bb_bcode is required.")

        exists = (
            db.query(Bank.bk_bcode)
            .filter(
                Bank.bk_bcode == normalized,
                Bank.bk_is_deleted.is_(False),
            )
            .first()
        )
        if not exists:
            raise ValueError(f"bb_bcode '{normalized}' does not exist.")

    def _assert_unique_branch_code(
        self,
        db: Session,
        branch_code: Optional[str],
        *,
        exclude_id: Optional[int] = None,
    ) -> None:
        if not branch_code:
            raise ValueError("bb_bbcode is required.")
        normalized = branch_code.strip()
        if normalized == "":
            raise ValueError("bb_bbcode is required.")

        query = db.query(BankBranch).filter(
            BankBranch.bb_bbcode == normalized,
            BankBranch.bb_is_deleted.is_(False),
        )
        if exclude_id is not None:
            query = query.filter(BankBranch.bb_id != exclude_id)

        exists = query.first() is not None
        if exists:
            raise ValueError(f"bb_bbcode '{normalized}' already exists.")


bank_branch_repo = BankBranchRepository()
