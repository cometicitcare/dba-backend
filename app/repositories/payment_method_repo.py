# app/repositories/payment_method_repo.py
import re
from datetime import datetime
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.payment_method import PaymentMethod
from app.models.user import UserAccount
from app.schemas.payment_method import (
    PaymentMethodCreate,
    PaymentMethodUpdate,
)


class PaymentMethodRepository:
    """Data access helpers for payment methods."""

    CODE_PREFIX = "PAY"
    CODE_PADDING = 3

    def get(self, db: Session, pm_id: int) -> Optional[PaymentMethod]:
        return (
            db.query(PaymentMethod)
            .filter(
                PaymentMethod.pm_id == pm_id,
                PaymentMethod.pm_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_code(self, db: Session, pm_code: str) -> Optional[PaymentMethod]:
        return (
            db.query(PaymentMethod)
            .filter(
                PaymentMethod.pm_code == pm_code,
                PaymentMethod.pm_is_deleted.is_(False),
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
    ) -> list[PaymentMethod]:
        query = db.query(PaymentMethod).filter(
            PaymentMethod.pm_is_deleted.is_(False)
        )

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    PaymentMethod.pm_code.ilike(term),
                    PaymentMethod.pm_method_name.ilike(term),
                )
            )

        return (
            query.order_by(PaymentMethod.pm_id)
            .offset(max(skip, 0))
            .limit(limit)
            .all()
        )

    def count(self, db: Session, *, search: Optional[str] = None) -> int:
        query = db.query(func.count(PaymentMethod.pm_id)).filter(
            PaymentMethod.pm_is_deleted.is_(False)
        )

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    PaymentMethod.pm_code.ilike(term),
                    PaymentMethod.pm_method_name.ilike(term),
                )
            )

        return query.scalar() or 0

    def create(
        self,
        db: Session,
        *,
        data: PaymentMethodCreate,
        actor_id: Optional[str],
    ) -> PaymentMethod:
        self._assert_user_exists(db, actor_id, "actor_id")

        payload = data.model_dump()
        payload["pm_method_name"] = payload["pm_method_name"].strip()
        if payload.get("pm_is_active") is None:
            payload["pm_is_active"] = True
        payload.setdefault("pm_is_deleted", False)
        payload.setdefault("pm_version_number", 1)
        payload["pm_created_by"] = actor_id
        payload["pm_updated_by"] = actor_id

        next_code = self.generate_next_code(db)
        self._assert_unique_code(db, next_code)
        payload["pm_code"] = next_code

        now = datetime.utcnow()
        payload["pm_created_at"] = now
        payload["pm_updated_at"] = now
        payload["pm_version"] = now

        entity = PaymentMethod(**payload)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def update(
        self,
        db: Session,
        *,
        entity: PaymentMethod,
        data: PaymentMethodUpdate,
        actor_id: Optional[str],
    ) -> PaymentMethod:
        self._assert_user_exists(db, actor_id, "actor_id")

        update_data = data.model_dump(exclude_unset=True)

        if "pm_method_name" in update_data and update_data["pm_method_name"] is not None:
            update_data["pm_method_name"] = update_data["pm_method_name"].strip()

        if "pm_is_active" in update_data and update_data["pm_is_active"] is None:
            update_data.pop("pm_is_active")

        for key, value in update_data.items():
            setattr(entity, key, value)

        entity.pm_updated_by = actor_id
        entity.pm_version_number = (entity.pm_version_number or 1) + 1
        now = datetime.utcnow()
        entity.pm_updated_at = now
        entity.pm_version = now

        db.commit()
        db.refresh(entity)
        return entity

    def soft_delete(
        self,
        db: Session,
        *,
        entity: PaymentMethod,
        actor_id: Optional[str],
    ) -> PaymentMethod:
        self._assert_user_exists(db, actor_id, "actor_id")

        entity.pm_is_deleted = True
        entity.pm_updated_by = actor_id
        entity.pm_version_number = (entity.pm_version_number or 1) + 1
        now = datetime.utcnow()
        entity.pm_updated_at = now
        entity.pm_version = now

        db.commit()
        db.refresh(entity)
        return entity

    def generate_next_code(self, db: Session) -> str:
        latest = (
            db.query(PaymentMethod.pm_code)
            .order_by(PaymentMethod.pm_id.desc())
            .first()
        )
        if not latest or not latest[0]:
            return f"{self.CODE_PREFIX}{1:0{self.CODE_PADDING}d}"

        latest_code = latest[0]
        match = re.search(r"(\d+)$", latest_code)
        if match:
            next_number = int(match.group(1)) + 1
        else:
            next_number = 1

        pad_width = max(self.CODE_PADDING, len(str(next_number)))
        return f"{self.CODE_PREFIX}{next_number:0{pad_width}d}"

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
    ) -> None:
        if not code:
            raise ValueError("pm_code is required.")

        normalized = code.strip()
        query = db.query(PaymentMethod).filter(
            PaymentMethod.pm_code == normalized,
            PaymentMethod.pm_is_deleted.is_(False),
        )

        exists = query.first() is not None
        if exists:
            raise ValueError(f"pm_code '{normalized}' already exists.")


payment_method_repo = PaymentMethodRepository()
