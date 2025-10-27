from datetime import datetime
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.district import District
from app.schemas.district import DistrictCreate, DistrictUpdate


class DistrictRepository:
    """Data access helpers for the cmm_districtdata table."""

    def get(self, db: Session, dd_id: int) -> Optional[District]:
        return (
            db.query(District)
            .filter(
                District.dd_id == dd_id,
                District.dd_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_code(self, db: Session, dd_dcode: str) -> Optional[District]:
        return (
            db.query(District)
            .filter(
                District.dd_dcode == dd_dcode,
                District.dd_is_deleted.is_(False),
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
    ) -> list[District]:
        query = db.query(District).filter(District.dd_is_deleted.is_(False))

        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    District.dd_dcode.ilike(pattern),
                    District.dd_dname.ilike(pattern),
                )
            )

        return (
            query.order_by(District.dd_id)
            .offset(max(skip, 0))
            .limit(limit)
            .all()
        )

    def count(self, db: Session, *, search: Optional[str] = None) -> int:
        query = db.query(func.count(District.dd_id)).filter(
            District.dd_is_deleted.is_(False)
        )

        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    District.dd_dcode.ilike(pattern),
                    District.dd_dname.ilike(pattern),
                )
            )

        return int(query.scalar() or 0)

    def create(self, db: Session, *, data: DistrictCreate) -> District:
        payload = data.model_dump(exclude_unset=True)
        now = datetime.utcnow()

        payload.setdefault("dd_is_deleted", False)
        payload.setdefault("dd_version_number", 1)
        payload.setdefault("dd_created_at", now)
        payload.setdefault("dd_updated_at", now)
        payload.setdefault("dd_version", now)

        entity = District(**payload)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def update(
        self,
        db: Session,
        *,
        entity: District,
        data: DistrictUpdate,
    ) -> District:
        update_data = data.model_dump(exclude_unset=True)
        update_data.pop("dd_id", None)
        update_data.pop("dd_version_number", None)

        for key, value in update_data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        now = datetime.utcnow()
        entity.dd_version_number = (entity.dd_version_number or 1) + 1
        entity.dd_updated_at = now
        entity.dd_version = now

        db.commit()
        db.refresh(entity)
        return entity

    def soft_delete(
        self, db: Session, *, entity: District, actor_id: Optional[str]
    ) -> District:
        now = datetime.utcnow()
        entity.dd_is_deleted = True
        entity.dd_updated_by = actor_id
        entity.dd_version_number = (entity.dd_version_number or 1) + 1
        entity.dd_updated_at = now
        entity.dd_version = now

        db.commit()
        db.refresh(entity)
        return entity


district_repo = DistrictRepository()
