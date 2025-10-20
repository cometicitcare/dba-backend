# app/repositories/nilame_repo.py
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.nilame import NilameRegist
from app.schemas.nilame import NilameCreate, NilameUpdate


class NilameRepository:
    """Data access helpers for nilame registrations."""

    def get(self, db: Session, kr_id: int) -> Optional[NilameRegist]:
        return (
            db.query(NilameRegist)
            .filter(
                NilameRegist.kr_id == kr_id,
                NilameRegist.kr_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_krn(self, db: Session, kr_krn: str) -> Optional[NilameRegist]:
        return (
            db.query(NilameRegist)
            .filter(
                NilameRegist.kr_krn == kr_krn,
                NilameRegist.kr_is_deleted.is_(False),
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
    ) -> list[NilameRegist]:
        query = db.query(NilameRegist).filter(
            NilameRegist.kr_is_deleted.is_(False)
        )

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    NilameRegist.kr_krn.ilike(term),
                    NilameRegist.kr_kname.ilike(term),
                    NilameRegist.kr_nic.ilike(term),
                    NilameRegist.kr_addrs.ilike(term),
                    NilameRegist.kr_grndiv.ilike(term),
                    NilameRegist.kr_trn.ilike(term),
                )
            )

        return (
            query.order_by(NilameRegist.kr_id)
            .offset(max(skip, 0))
            .limit(limit)
            .all()
        )

    def count(self, db: Session, *, search: Optional[str] = None) -> int:
        query = db.query(func.count(NilameRegist.kr_id)).filter(
            NilameRegist.kr_is_deleted.is_(False)
        )

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    NilameRegist.kr_krn.ilike(term),
                    NilameRegist.kr_kname.ilike(term),
                    NilameRegist.kr_nic.ilike(term),
                    NilameRegist.kr_addrs.ilike(term),
                    NilameRegist.kr_grndiv.ilike(term),
                    NilameRegist.kr_trn.ilike(term),
                )
            )

        return query.scalar() or 0

    def create(
        self,
        db: Session,
        *,
        data: NilameCreate,
        actor_id: Optional[str],
    ) -> NilameRegist:
        payload = data.model_dump()
        payload.setdefault("kr_is_deleted", False)
        payload.setdefault("kr_version_number", 1)
        payload["kr_created_by"] = actor_id
        payload["kr_updated_by"] = actor_id

        entity = NilameRegist(**payload)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def update(
        self,
        db: Session,
        *,
        entity: NilameRegist,
        data: NilameUpdate,
        actor_id: Optional[str],
    ) -> NilameRegist:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(entity, key, value)

        entity.kr_updated_by = actor_id
        entity.kr_version_number = (entity.kr_version_number or 1) + 1
        db.commit()
        db.refresh(entity)
        return entity

    def soft_delete(
        self, db: Session, *, entity: NilameRegist, actor_id: Optional[str]
    ) -> NilameRegist:
        entity.kr_is_deleted = True
        entity.kr_updated_by = actor_id
        entity.kr_version_number = (entity.kr_version_number or 1) + 1
        db.commit()
        db.refresh(entity)
        return entity


nilame_repo = NilameRepository()

