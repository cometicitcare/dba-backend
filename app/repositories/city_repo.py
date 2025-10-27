from datetime import datetime
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.city import City
from app.schemas.city import CityCreate, CityUpdate


class CityRepository:
    """Data access helper for the cmm_city table."""

    def get(self, db: Session, ct_id: int) -> Optional[City]:
        return (
            db.query(City)
            .filter(
                City.ct_id == ct_id,
                City.ct_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_code(self, db: Session, ct_code: str) -> Optional[City]:
        return (
            db.query(City)
            .filter(
                City.ct_code == ct_code,
                City.ct_is_deleted.is_(False),
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
    ) -> list[City]:
        query = db.query(City).filter(City.ct_is_deleted.is_(False))

        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    City.ct_code.ilike(pattern),
                    City.ct_descr_name.ilike(pattern),
                    City.ct_gncode.ilike(pattern),
                    City.ct_dvcode.ilike(pattern),
                )
            )

        return (
            query.order_by(City.ct_id)
            .offset(max(skip, 0))
            .limit(limit)
            .all()
        )

    def count(self, db: Session, *, search: Optional[str] = None) -> int:
        query = db.query(func.count(City.ct_id)).filter(
            City.ct_is_deleted.is_(False)
        )

        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    City.ct_code.ilike(pattern),
                    City.ct_descr_name.ilike(pattern),
                    City.ct_gncode.ilike(pattern),
                    City.ct_dvcode.ilike(pattern),
                )
            )

        return int(query.scalar() or 0)

    def create(self, db: Session, *, data: CityCreate) -> City:
        payload = data.model_dump(exclude_unset=True)
        now = datetime.utcnow()

        payload.setdefault("ct_is_deleted", False)
        payload.setdefault("ct_version_number", 1)
        payload.setdefault("ct_created_at", now)
        payload.setdefault("ct_updated_at", now)
        payload.setdefault("ct_version", now)

        entity = City(**payload)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def update(self, db: Session, *, entity: City, data: CityUpdate) -> City:
        update_data = data.model_dump(exclude_unset=True)
        update_data.pop("ct_id", None)
        update_data.pop("ct_version_number", None)

        for key, value in update_data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        now = datetime.utcnow()
        entity.ct_version_number = (entity.ct_version_number or 1) + 1
        entity.ct_updated_at = now
        entity.ct_version = now

        db.commit()
        db.refresh(entity)
        return entity

    def soft_delete(
        self, db: Session, *, entity: City, actor_id: Optional[str]
    ) -> City:
        now = datetime.utcnow()
        entity.ct_is_deleted = True
        entity.ct_updated_by = actor_id
        entity.ct_version_number = (entity.ct_version_number or 1) + 1
        entity.ct_updated_at = now
        entity.ct_version = now

        db.commit()
        db.refresh(entity)
        return entity


city_repo = CityRepository()
