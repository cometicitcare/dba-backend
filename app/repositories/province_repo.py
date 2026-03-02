from datetime import datetime
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.province import Province
from app.schemas.province import ProvinceCreate, ProvinceUpdate


class ProvinceRepository:
    """Data access helpers for the cmm_province table."""

    def get(self, db: Session, cp_id: int) -> Optional[Province]:
        return (
            db.query(Province)
            .filter(
                Province.cp_id == cp_id,
                Province.cp_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_code(self, db: Session, cp_code: str) -> Optional[Province]:
        return (
            db.query(Province)
            .filter(
                Province.cp_code == cp_code,
                Province.cp_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_name(self, db: Session, cp_name: str) -> Optional[Province]:
        return (
            db.query(Province)
            .filter(
                Province.cp_name == cp_name,
                Province.cp_is_deleted.is_(False),
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
    ) -> list[Province]:
        query = db.query(Province).filter(Province.cp_is_deleted.is_(False))

        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Province.cp_code.ilike(pattern),
                    Province.cp_name.ilike(pattern),
                )
            )

        return (
            query.order_by(Province.cp_id)
            .offset(max(skip, 0))
            .limit(limit)
            .all()
        )

    def count(self, db: Session, *, search: Optional[str] = None) -> int:
        query = db.query(func.count(Province.cp_id)).filter(
            Province.cp_is_deleted.is_(False)
        )

        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Province.cp_code.ilike(pattern),
                    Province.cp_name.ilike(pattern),
                )
            )

        return int(query.scalar() or 0)

    def create(self, db: Session, *, data: ProvinceCreate) -> Province:
        payload = data.model_dump(exclude_unset=True)
        now = datetime.utcnow()

        payload.setdefault("cp_is_deleted", False)
        payload.setdefault("cp_version_number", 1)
        payload.setdefault("cp_created_at", now)
        payload.setdefault("cp_updated_at", now)
        payload.setdefault("cp_version", now)

        entity = Province(**payload)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def update(
        self,
        db: Session,
        *,
        entity: Province,
        data: ProvinceUpdate,
    ) -> Province:
        update_data = data.model_dump(exclude_unset=True)
        update_data.pop("cp_id", None)
        update_data.pop("cp_version_number", None)

        for key, value in update_data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        now = datetime.utcnow()
        entity.cp_version_number = (entity.cp_version_number or 1) + 1
        entity.cp_updated_at = now
        entity.cp_version = now

        db.commit()
        db.refresh(entity)
        return entity

    def soft_delete(
        self, db: Session, *, entity: Province, actor_id: Optional[str]
    ) -> Province:
        now = datetime.utcnow()
        entity.cp_is_deleted = True
        entity.cp_updated_by = actor_id
        entity.cp_version_number = (entity.cp_version_number or 1) + 1
        entity.cp_updated_at = now
        entity.cp_version = now

        db.commit()
        db.refresh(entity)
        return entity


province_repo = ProvinceRepository()
