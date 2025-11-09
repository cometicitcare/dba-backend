from datetime import datetime
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.divisional_secretariat import DivisionalSecretariat
from app.schemas.divisional_secretariat import (
    DivisionalSecretariatCreate,
    DivisionalSecretariatUpdate,
)


class DivisionalSecretariatRepository:
    """Data access helpers for the cmm_dvsec table."""

    def get(self, db: Session, dv_id: int) -> Optional[DivisionalSecretariat]:
        return (
            db.query(DivisionalSecretariat)
                .filter(
                    DivisionalSecretariat.dv_id == dv_id,
                    DivisionalSecretariat.dv_is_deleted.is_(False),
                )
                .first()
        )

    def get_by_code(
        self, db: Session, dv_dvcode: str
    ) -> Optional[DivisionalSecretariat]:
        return (
            db.query(DivisionalSecretariat)
                .filter(
                    DivisionalSecretariat.dv_dvcode == dv_dvcode,
                    DivisionalSecretariat.dv_is_deleted.is_(False),
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
        district_code: Optional[str] = None,
    ) -> list[DivisionalSecretariat]:
        query = db.query(DivisionalSecretariat).filter(
            DivisionalSecretariat.dv_is_deleted.is_(False)
        )

        if district_code:
            query = query.filter(DivisionalSecretariat.dv_distrcd == district_code)

        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    DivisionalSecretariat.dv_dvcode.ilike(pattern),
                    DivisionalSecretariat.dv_distrcd.ilike(pattern),
                    DivisionalSecretariat.dv_dvname.ilike(pattern),
                )
            )

        return (
            query.order_by(DivisionalSecretariat.dv_id)
            .offset(max(skip, 0))
            .limit(limit)
            .all()
        )

    def count(
        self,
        db: Session,
        *,
        search: Optional[str] = None,
        district_code: Optional[str] = None,
    ) -> int:
        query = db.query(func.count(DivisionalSecretariat.dv_id)).filter(
            DivisionalSecretariat.dv_is_deleted.is_(False)
        )

        if district_code:
            query = query.filter(DivisionalSecretariat.dv_distrcd == district_code)

        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    DivisionalSecretariat.dv_dvcode.ilike(pattern),
                    DivisionalSecretariat.dv_distrcd.ilike(pattern),
                    DivisionalSecretariat.dv_dvname.ilike(pattern),
                )
            )

        return int(query.scalar() or 0)

    def create(
        self, db: Session, *, data: DivisionalSecretariatCreate
    ) -> DivisionalSecretariat:
        payload = data.model_dump(exclude_unset=True)
        now = datetime.utcnow()

        payload.setdefault("dv_is_deleted", False)
        payload.setdefault("dv_version_number", 1)
        payload.setdefault("dv_created_at", now)
        payload.setdefault("dv_updated_at", now)
        payload.setdefault("dv_version", now)

        entity = DivisionalSecretariat(**payload)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def update(
        self,
        db: Session,
        *,
        entity: DivisionalSecretariat,
        data: DivisionalSecretariatUpdate,
    ) -> DivisionalSecretariat:
        update_data = data.model_dump(exclude_unset=True)
        update_data.pop("dv_id", None)
        update_data.pop("dv_version_number", None)

        for key, value in update_data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        now = datetime.utcnow()
        entity.dv_version_number = (entity.dv_version_number or 1) + 1
        entity.dv_updated_at = now
        entity.dv_version = now

        db.commit()
        db.refresh(entity)
        return entity

    def soft_delete(
        self,
        db: Session,
        *,
        entity: DivisionalSecretariat,
        actor_id: Optional[str],
    ) -> DivisionalSecretariat:
        now = datetime.utcnow()
        entity.dv_is_deleted = True
        entity.dv_updated_by = actor_id
        entity.dv_version_number = (entity.dv_version_number or 1) + 1
        entity.dv_updated_at = now
        entity.dv_version = now

        db.commit()
        db.refresh(entity)
        return entity


divisional_secretariat_repo = DivisionalSecretariatRepository()
