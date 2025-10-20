# app/repositories/bhikku_high_repo.py
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.bhikku_high import BhikkuHighRegist
from app.schemas.bhikku_high import BhikkuHighCreate, BhikkuHighUpdate


class BhikkuHighRepository:
    """Data access helpers for higher bhikku registrations."""

    def get(self, db: Session, bhr_id: int) -> Optional[BhikkuHighRegist]:
        return (
            db.query(BhikkuHighRegist)
            .filter(
                BhikkuHighRegist.bhr_id == bhr_id,
                BhikkuHighRegist.bhr_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_regn(self, db: Session, bhr_regn: str) -> Optional[BhikkuHighRegist]:
        return (
            db.query(BhikkuHighRegist)
            .filter(
                BhikkuHighRegist.bhr_regn == bhr_regn,
                BhikkuHighRegist.bhr_is_deleted.is_(False),
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
    ) -> list[BhikkuHighRegist]:
        query = db.query(BhikkuHighRegist).filter(
            BhikkuHighRegist.bhr_is_deleted.is_(False)
        )

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    BhikkuHighRegist.bhr_regn.ilike(term),
                    BhikkuHighRegist.bhr_samanera_serial_no.ilike(term),
                    BhikkuHighRegist.bhr_mahanaacharyacd.ilike(term),
                    BhikkuHighRegist.bhr_karmacharya.ilike(term),
                    BhikkuHighRegist.bhr_mahananame.ilike(term),
                    BhikkuHighRegist.bhr_ordination_temple.ilike(term),
                    BhikkuHighRegist.bhr_currstat.ilike(term),
                    BhikkuHighRegist.bhr_parshawaya.ilike(term),
                    BhikkuHighRegist.bhr_livtemple.ilike(term),
                    BhikkuHighRegist.bhr_mobile.ilike(term),
                    BhikkuHighRegist.bhr_email.ilike(term),
                )
            )

        return (
            query.order_by(BhikkuHighRegist.bhr_id)
            .offset(max(skip, 0))
            .limit(limit)
            .all()
        )

    def count(self, db: Session, *, search: Optional[str] = None) -> int:
        query = db.query(func.count(BhikkuHighRegist.bhr_id)).filter(
            BhikkuHighRegist.bhr_is_deleted.is_(False)
        )

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    BhikkuHighRegist.bhr_regn.ilike(term),
                    BhikkuHighRegist.bhr_samanera_serial_no.ilike(term),
                    BhikkuHighRegist.bhr_mahanaacharyacd.ilike(term),
                    BhikkuHighRegist.bhr_karmacharya.ilike(term),
                    BhikkuHighRegist.bhr_mahananame.ilike(term),
                    BhikkuHighRegist.bhr_ordination_temple.ilike(term),
                    BhikkuHighRegist.bhr_currstat.ilike(term),
                    BhikkuHighRegist.bhr_parshawaya.ilike(term),
                    BhikkuHighRegist.bhr_livtemple.ilike(term),
                    BhikkuHighRegist.bhr_mobile.ilike(term),
                    BhikkuHighRegist.bhr_email.ilike(term),
                )
            )

        return query.scalar() or 0

    def create(
        self, db: Session, *, data: BhikkuHighCreate, actor_id: Optional[str]
    ) -> BhikkuHighRegist:
        payload = data.model_dump()
        payload.setdefault("bhr_is_deleted", False)
        payload.setdefault("bhr_version_number", 1)
        payload["bhr_created_by"] = actor_id
        payload["bhr_updated_by"] = actor_id

        entity = BhikkuHighRegist(**payload)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def update(
        self,
        db: Session,
        *,
        entity: BhikkuHighRegist,
        data: BhikkuHighUpdate,
        actor_id: Optional[str],
    ) -> BhikkuHighRegist:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(entity, key, value)

        entity.bhr_updated_by = actor_id
        entity.bhr_version_number = (entity.bhr_version_number or 1) + 1
        db.commit()
        db.refresh(entity)
        return entity

    def soft_delete(
        self, db: Session, *, entity: BhikkuHighRegist, actor_id: Optional[str]
    ) -> BhikkuHighRegist:
        entity.bhr_is_deleted = True
        entity.bhr_updated_by = actor_id
        entity.bhr_version_number = (entity.bhr_version_number or 1) + 1
        db.commit()
        db.refresh(entity)
        return entity


bhikku_high_repo = BhikkuHighRepository()
