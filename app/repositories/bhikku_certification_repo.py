# app/repositories/bhikku_certification_repo.py
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.bhikku_certification import BhikkuCertification
from app.schemas.bhikku_certification import (
    BhikkuCertificationCreate,
    BhikkuCertificationUpdate,
)


class BhikkuCertificationRepository:
    """Data access helpers for bhikku certification records."""

    def get(self, db: Session, bc_id: int) -> Optional[BhikkuCertification]:
        return (
            db.query(BhikkuCertification)
            .filter(
                BhikkuCertification.bc_id == bc_id,
                BhikkuCertification.bc_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_regno(self, db: Session, bc_regno: str) -> Optional[BhikkuCertification]:
        return (
            db.query(BhikkuCertification)
            .filter(
                BhikkuCertification.bc_regno == bc_regno,
                BhikkuCertification.bc_is_deleted.is_(False),
            )
            .order_by(BhikkuCertification.bc_issuedate.desc())
            .first()
        )

    def list(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> list[BhikkuCertification]:
        query = db.query(BhikkuCertification).filter(
            BhikkuCertification.bc_is_deleted.is_(False)
        )

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    BhikkuCertification.bc_regno.ilike(term),
                    BhikkuCertification.bc_adminautho.ilike(term),
                    BhikkuCertification.bc_prtoptn.ilike(term),
                    BhikkuCertification.bc_usr.ilike(term),
                    BhikkuCertification.bc_admnusr.ilike(term),
                )
            )

        return (
            query.order_by(BhikkuCertification.bc_id)
            .offset(max(skip, 0))
            .limit(limit)
            .all()
        )

    def count(self, db: Session, *, search: Optional[str] = None) -> int:
        query = db.query(func.count(BhikkuCertification.bc_id)).filter(
            BhikkuCertification.bc_is_deleted.is_(False)
        )

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    BhikkuCertification.bc_regno.ilike(term),
                    BhikkuCertification.bc_adminautho.ilike(term),
                    BhikkuCertification.bc_prtoptn.ilike(term),
                    BhikkuCertification.bc_usr.ilike(term),
                    BhikkuCertification.bc_admnusr.ilike(term),
                )
            )

        return query.scalar() or 0

    def create(
        self,
        db: Session,
        *,
        data: BhikkuCertificationCreate,
        actor_id: Optional[str],
    ) -> BhikkuCertification:
        payload = data.model_dump()
        payload.setdefault("bc_is_deleted", False)
        payload.setdefault("bc_version_number", 1)
        payload["bc_created_by"] = actor_id
        payload["bc_updated_by"] = actor_id

        entity = BhikkuCertification(**payload)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def update(
        self,
        db: Session,
        *,
        entity: BhikkuCertification,
        data: BhikkuCertificationUpdate,
        actor_id: Optional[str],
    ) -> BhikkuCertification:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(entity, key, value)

        entity.bc_updated_by = actor_id
        entity.bc_version_number = (entity.bc_version_number or 1) + 1
        db.commit()
        db.refresh(entity)
        return entity

    def soft_delete(
        self, db: Session, *, entity: BhikkuCertification, actor_id: Optional[str]
    ) -> BhikkuCertification:
        entity.bc_is_deleted = True
        entity.bc_updated_by = actor_id
        entity.bc_version_number = (entity.bc_version_number or 1) + 1
        db.commit()
        db.refresh(entity)
        return entity


bhikku_certification_repo = BhikkuCertificationRepository()

