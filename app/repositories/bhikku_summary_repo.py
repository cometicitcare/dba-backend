# app/repositories/bhikku_summary_repo.py
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.bhikku_summary import BhikkuSummary
from app.schemas.bhikku_summary import BhikkuSummaryCreate, BhikkuSummaryUpdate


class BhikkuSummaryRepository:
    """Data access helpers for bhikku summary records."""

    def get(self, db: Session, bs_regn: str) -> Optional[BhikkuSummary]:
        return (
            db.query(BhikkuSummary)
            .filter(
                BhikkuSummary.bs_regn == bs_regn,
                BhikkuSummary.bs_is_deleted.is_(False),
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
    ) -> list[BhikkuSummary]:
        query = db.query(BhikkuSummary).filter(
            BhikkuSummary.bs_is_deleted.is_(False)
        )

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    BhikkuSummary.bs_regn.ilike(term),
                    BhikkuSummary.bs_mahananame.ilike(term),
                    BhikkuSummary.bs_gihiname.ilike(term),
                    BhikkuSummary.bs_teacher.ilike(term),
                    BhikkuSummary.bs_viharadipathi.ilike(term),
                    BhikkuSummary.bs_curstatus.ilike(term),
                    BhikkuSummary.bs_catogry.ilike(term),
                )
            )

        return (
            query.order_by(BhikkuSummary.bs_regn)
            .offset(max(skip, 0))
            .limit(limit)
            .all()
        )

    def count(self, db: Session, *, search: Optional[str] = None) -> int:
        query = db.query(func.count(BhikkuSummary.bs_regn)).filter(
            BhikkuSummary.bs_is_deleted.is_(False)
        )

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    BhikkuSummary.bs_regn.ilike(term),
                    BhikkuSummary.bs_mahananame.ilike(term),
                    BhikkuSummary.bs_gihiname.ilike(term),
                    BhikkuSummary.bs_teacher.ilike(term),
                    BhikkuSummary.bs_viharadipathi.ilike(term),
                    BhikkuSummary.bs_curstatus.ilike(term),
                    BhikkuSummary.bs_catogry.ilike(term),
                )
            )

        return query.scalar() or 0

    def create(
        self,
        db: Session,
        *,
        data: BhikkuSummaryCreate,
        actor_id: Optional[str],
    ) -> BhikkuSummary:
        payload = data.model_dump()
        payload.setdefault("bs_is_deleted", False)
        payload.setdefault("bs_version_number", 1)
        payload["bs_created_by"] = actor_id
        payload["bs_updated_by"] = actor_id

        entity = BhikkuSummary(**payload)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def update(
        self,
        db: Session,
        *,
        entity: BhikkuSummary,
        data: BhikkuSummaryUpdate,
        actor_id: Optional[str],
    ) -> BhikkuSummary:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(entity, key, value)

        entity.bs_updated_by = actor_id
        entity.bs_version_number = (entity.bs_version_number or 1) + 1
        db.commit()
        db.refresh(entity)
        return entity

    def soft_delete(
        self, db: Session, *, entity: BhikkuSummary, actor_id: Optional[str]
    ) -> BhikkuSummary:
        entity.bs_is_deleted = True
        entity.bs_updated_by = actor_id
        entity.bs_version_number = (entity.bs_version_number or 1) + 1
        db.commit()
        db.refresh(entity)
        return entity


bhikku_summary_repo = BhikkuSummaryRepository()

