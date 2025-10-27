# app/repositories/bank_repo.py
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.bank import Bank
from app.models.user import UserAccount
from app.schemas.bank import BankCreate, BankUpdate


class BankRepository:
    """Data access helpers for bank records."""

    def get(self, db: Session, bk_id: int) -> Optional[Bank]:
        return (
            db.query(Bank)
            .filter(
                Bank.bk_id == bk_id,
                Bank.bk_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_code(self, db: Session, bk_bcode: str) -> Optional[Bank]:
        return (
            db.query(Bank)
            .filter(
                Bank.bk_bcode == bk_bcode,
                Bank.bk_is_deleted.is_(False),
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
    ) -> list[Bank]:
        query = db.query(Bank).filter(Bank.bk_is_deleted.is_(False))

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Bank.bk_bcode.ilike(term),
                    Bank.bk_bname.ilike(term),
                )
            )

        return (
            query.order_by(Bank.bk_id)
            .offset(max(skip, 0))
            .limit(limit)
            .all()
        )

    def count(self, db: Session, *, search: Optional[str] = None) -> int:
        query = db.query(func.count(Bank.bk_id)).filter(Bank.bk_is_deleted.is_(False))

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Bank.bk_bcode.ilike(term),
                    Bank.bk_bname.ilike(term),
                )
            )

        return query.scalar() or 0

    def create(
        self,
        db: Session,
        *,
        data: BankCreate,
        actor_id: Optional[str],
    ) -> Bank:
        self._assert_user_exists(db, actor_id, "actor_id")

        payload = data.model_dump()
        payload["bk_bcode"] = payload["bk_bcode"].strip()
        if payload.get("bk_bname") is not None:
            payload["bk_bname"] = payload["bk_bname"].strip()
        payload.setdefault("bk_is_deleted", False)
        payload.setdefault("bk_version_number", 1)
        payload["bk_created_by"] = actor_id
        payload["bk_updated_by"] = actor_id

        self._assert_unique_code(db, payload["bk_bcode"])

        entity = Bank(**payload)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def update(
        self,
        db: Session,
        *,
        entity: Bank,
        data: BankUpdate,
        actor_id: Optional[str],
    ) -> Bank:
        self._assert_user_exists(db, actor_id, "actor_id")

        update_data = data.model_dump(exclude_unset=True)
        if "bk_bcode" in update_data and update_data["bk_bcode"] is not None:
            update_data["bk_bcode"] = update_data["bk_bcode"].strip()
        if "bk_bname" in update_data and update_data["bk_bname"] is not None:
            update_data["bk_bname"] = update_data["bk_bname"].strip()

        next_code = update_data.get("bk_bcode", entity.bk_bcode)
        if next_code != entity.bk_bcode:
            self._assert_unique_code(db, next_code, exclude_id=entity.bk_id)

        for key, value in update_data.items():
            setattr(entity, key, value)

        entity.bk_updated_by = actor_id
        entity.bk_version_number = (entity.bk_version_number or 1) + 1
        db.commit()
        db.refresh(entity)
        return entity

    def soft_delete(
        self, db: Session, *, entity: Bank, actor_id: Optional[str]
    ) -> Bank:
        self._assert_user_exists(db, actor_id, "actor_id")
        entity.bk_is_deleted = True
        entity.bk_updated_by = actor_id
        entity.bk_version_number = (entity.bk_version_number or 1) + 1
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

    def _assert_unique_code(
        self,
        db: Session,
        code: Optional[str],
        *,
        exclude_id: Optional[int] = None,
    ) -> None:
        if not code:
            raise ValueError("bk_bcode is required.")

        normalized = code.strip()
        if normalized == "":
            raise ValueError("bk_bcode is required.")

        query = db.query(Bank).filter(
            Bank.bk_bcode == normalized,
            Bank.bk_is_deleted.is_(False),
        )
        if exclude_id is not None:
            query = query.filter(Bank.bk_id != exclude_id)

        exists = query.first() is not None
        if exists:
            raise ValueError(f"bk_bcode '{normalized}' already exists.")


bank_repo = BankRepository()
