# app/repositories/silmatha_id_card_repo.py
from __future__ import annotations

from typing import Optional

from sqlalchemy import String, cast, func, or_
from sqlalchemy.orm import Session

from app.models.silmatha_id_card import SilmathaIDCard
from app.schemas.silmatha_id_card import (
    SilmathaIDCardCreate,
    SilmathaIDCardUpdate,
)


class SilmathaIDCardRepository:
    """Data access helpers for the silmatha_id_card table."""

    def get(self, db: Session, sic_id: int) -> Optional[SilmathaIDCard]:
        return (
            db.query(SilmathaIDCard)
            .filter(
                SilmathaIDCard.sic_id == sic_id,
                SilmathaIDCard.sic_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_form_no(
        self, db: Session, sic_form_no: str
    ) -> Optional[SilmathaIDCard]:
        return (
            db.query(SilmathaIDCard)
            .filter(
                func.lower(SilmathaIDCard.sic_form_no) == sic_form_no.lower(),
                SilmathaIDCard.sic_is_deleted.is_(False),
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
    ) -> list[SilmathaIDCard]:
        query = db.query(SilmathaIDCard).filter(
            SilmathaIDCard.sic_is_deleted.is_(False)
        )

        search_term = search.strip() if search else None
        if search_term:
            term = f"%{search_term}%"
            query = query.filter(
                or_(
                    SilmathaIDCard.sic_form_no.ilike(term),
                    SilmathaIDCard.sic_national_id.ilike(term),
                    cast(SilmathaIDCard.sic_regn, String).ilike(term),
                    cast(SilmathaIDCard.sic_br_id, String).ilike(term),
                )
            )

        return (
            query.order_by(SilmathaIDCard.sic_created_at.desc())
            .offset(max(skip, 0))
            .limit(limit)
            .all()
        )

    def count(self, db: Session, *, search: Optional[str] = None) -> int:
        query = db.query(func.count(SilmathaIDCard.sic_id)).filter(
            SilmathaIDCard.sic_is_deleted.is_(False)
        )

        search_term = search.strip() if search else None
        if search_term:
            term = f"%{search_term}%"
            query = query.filter(
                or_(
                    SilmathaIDCard.sic_form_no.ilike(term),
                    SilmathaIDCard.sic_national_id.ilike(term),
                    cast(SilmathaIDCard.sic_regn, String).ilike(term),
                    cast(SilmathaIDCard.sic_br_id, String).ilike(term),
                )
            )

        return query.scalar() or 0

    def create(
        self,
        db: Session,
        *,
        data: SilmathaIDCardCreate,
        actor_id: Optional[str],
    ) -> SilmathaIDCard:
        payload = data.model_dump(exclude_unset=True)
        payload.setdefault("sic_is_deleted", False)
        payload.setdefault("sic_version_number", 1)
        payload["sic_created_by"] = actor_id
        payload["sic_updated_by"] = actor_id

        entity = SilmathaIDCard(**payload)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def update(
        self,
        db: Session,
        *,
        entity: SilmathaIDCard,
        data: SilmathaIDCardUpdate,
        actor_id: Optional[str],
    ) -> SilmathaIDCard:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        entity.sic_updated_by = actor_id
        entity.sic_version_number = (entity.sic_version_number or 1) + 1
        db.commit()
        db.refresh(entity)
        return entity

    def soft_delete(
        self, db: Session, *, entity: SilmathaIDCard, actor_id: Optional[str]
    ) -> SilmathaIDCard:
        entity.sic_is_deleted = True
        entity.sic_updated_by = actor_id
        entity.sic_version_number = (entity.sic_version_number or 1) + 1
        db.commit()
        db.refresh(entity)
        return entity


silmatha_id_card_repo = SilmathaIDCardRepository()
