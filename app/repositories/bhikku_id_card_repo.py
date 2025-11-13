# app/repositories/bhikku_id_card_repo.py
from __future__ import annotations

from typing import Optional

from sqlalchemy import String, cast, func, or_
from sqlalchemy.orm import Session

from app.models.bhikku_id_card import BhikkuIDCard
from app.schemas.bhikku_id_card import BhikkuIDCardCreate, BhikkuIDCardUpdate


class BhikkuIDCardRepository:
    """Data access helpers for the bhikku_id_card table."""

    def get(self, db: Session, bic_id: int) -> Optional[BhikkuIDCard]:
        return (
            db.query(BhikkuIDCard)
            .filter(
                BhikkuIDCard.bic_id == bic_id,
                BhikkuIDCard.bic_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_form_no(
        self, db: Session, bic_form_no: str
    ) -> Optional[BhikkuIDCard]:
        return (
            db.query(BhikkuIDCard)
            .filter(
                func.lower(BhikkuIDCard.bic_form_no) == bic_form_no.lower(),
                BhikkuIDCard.bic_is_deleted.is_(False),
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
    ) -> list[BhikkuIDCard]:
        query = db.query(BhikkuIDCard).filter(
            BhikkuIDCard.bic_is_deleted.is_(False)
        )

        search_term = search.strip() if search else None
        if search_term:
            term = f"%{search_term}%"
            query = query.filter(
                or_(
                    BhikkuIDCard.bic_form_no.ilike(term),
                    BhikkuIDCard.bic_national_id.ilike(term),
                    cast(BhikkuIDCard.bic_regn, String).ilike(term),
                    cast(BhikkuIDCard.bic_br_id, String).ilike(term),
                )
            )

        return (
            query.order_by(BhikkuIDCard.bic_created_at.desc())
            .offset(max(skip, 0))
            .limit(limit)
            .all()
        )

    def count(self, db: Session, *, search: Optional[str] = None) -> int:
        query = db.query(func.count(BhikkuIDCard.bic_id)).filter(
            BhikkuIDCard.bic_is_deleted.is_(False)
        )

        search_term = search.strip() if search else None
        if search_term:
            term = f"%{search_term}%"
            query = query.filter(
                or_(
                    BhikkuIDCard.bic_form_no.ilike(term),
                    BhikkuIDCard.bic_national_id.ilike(term),
                    cast(BhikkuIDCard.bic_regn, String).ilike(term),
                    cast(BhikkuIDCard.bic_br_id, String).ilike(term),
                )
            )

        return query.scalar() or 0

    def create(
        self,
        db: Session,
        *,
        data: BhikkuIDCardCreate,
        actor_id: Optional[str],
    ) -> BhikkuIDCard:
        payload = data.model_dump(exclude_unset=True)
        payload.setdefault("bic_is_deleted", False)
        payload.setdefault("bic_version_number", 1)
        payload["bic_created_by"] = actor_id
        payload["bic_updated_by"] = actor_id

        entity = BhikkuIDCard(**payload)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def update(
        self,
        db: Session,
        *,
        entity: BhikkuIDCard,
        data: BhikkuIDCardUpdate,
        actor_id: Optional[str],
    ) -> BhikkuIDCard:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        entity.bic_updated_by = actor_id
        entity.bic_version_number = (entity.bic_version_number or 1) + 1
        db.commit()
        db.refresh(entity)
        return entity

    def soft_delete(
        self, db: Session, *, entity: BhikkuIDCard, actor_id: Optional[str]
    ) -> BhikkuIDCard:
        entity.bic_is_deleted = True
        entity.bic_updated_by = actor_id
        entity.bic_version_number = (entity.bic_version_number or 1) + 1
        db.commit()
        db.refresh(entity)
        return entity


bhikku_id_card_repo = BhikkuIDCardRepository()
