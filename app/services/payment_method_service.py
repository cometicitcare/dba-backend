# app/services/payment_method_service.py
from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.payment_method import PaymentMethod
from app.repositories.payment_method_repo import payment_method_repo
from app.schemas.payment_method import (
    PaymentMethodCreate,
    PaymentMethodUpdate,
)


class PaymentMethodService:
    """Business logic for payment method management."""

    def create_payment_method(
        self,
        db: Session,
        *,
        payload: PaymentMethodCreate,
        actor_id: Optional[str],
    ) -> PaymentMethod:
        create_data = self._strip_strings(payload.model_dump())
        create_payload = PaymentMethodCreate(**create_data)
        return payment_method_repo.create(
            db,
            data=create_payload,
            actor_id=actor_id,
        )

    def get_payment_method(self, db: Session, pm_id: int) -> PaymentMethod | None:
        return payment_method_repo.get(db, pm_id)

    def get_payment_method_by_code(
        self,
        db: Session,
        pm_code: str,
    ) -> PaymentMethod | None:
        code = pm_code.strip()
        if not code:
            return None
        return payment_method_repo.get_by_code(db, code)

    def list_payment_methods(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> list[PaymentMethod]:
        limit = max(1, min(limit, 200))
        skip = max(0, skip)
        search_term = search.strip() if search else None
        if search_term == "":
            search_term = None

        return payment_method_repo.list(
            db,
            skip=skip,
            limit=limit,
            search=search_term,
        )

    def count_payment_methods(
        self,
        db: Session,
        *,
        search: Optional[str] = None,
    ) -> int:
        search_term = search.strip() if search else None
        if search_term == "":
            search_term = None
        return payment_method_repo.count(db, search=search_term)

    def update_payment_method(
        self,
        db: Session,
        *,
        pm_id: int,
        payload: PaymentMethodUpdate,
        actor_id: Optional[str],
    ) -> PaymentMethod:
        entity = payment_method_repo.get(db, pm_id)
        if not entity:
            raise ValueError("Payment method not found.")

        update_data = self._strip_strings(payload.model_dump(exclude_unset=True))
        if not update_data:
            raise ValueError("No updates supplied.")

        update_payload = PaymentMethodUpdate(**update_data)
        return payment_method_repo.update(
            db,
            entity=entity,
            data=update_payload,
            actor_id=actor_id,
        )

    def delete_payment_method(
        self,
        db: Session,
        *,
        pm_id: int,
        actor_id: Optional[str],
    ) -> PaymentMethod:
        entity = payment_method_repo.get(db, pm_id)
        if not entity:
            raise ValueError("Payment method not found.")
        return payment_method_repo.soft_delete(
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


payment_method_service = PaymentMethodService()
