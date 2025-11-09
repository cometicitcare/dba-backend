from datetime import datetime
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.gramasewaka import Gramasewaka
from app.schemas.gramasewaka import GramasewakaCreate, GramasewakaUpdate


class GramasewakaRepository:
    """Data access helper for cmm_gndata records."""

    def get(self, db: Session, gn_id: int) -> Optional[Gramasewaka]:
        return (
            db.query(Gramasewaka)
            .filter(
                Gramasewaka.gn_id == gn_id,
                Gramasewaka.gn_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_code(self, db: Session, gn_gnc: str) -> Optional[Gramasewaka]:
        return (
            db.query(Gramasewaka)
            .filter(
                Gramasewaka.gn_gnc == gn_gnc,
                Gramasewaka.gn_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_mobile(self, db: Session, gn_mbile: str) -> Optional[Gramasewaka]:
        return (
            db.query(Gramasewaka)
            .filter(
                Gramasewaka.gn_mbile == gn_mbile,
                Gramasewaka.gn_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_email(self, db: Session, gn_email: str) -> Optional[Gramasewaka]:
        return (
            db.query(Gramasewaka)
            .filter(
                Gramasewaka.gn_email == gn_email,
                Gramasewaka.gn_is_deleted.is_(False),
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
        divisional_code: Optional[str] = None,
    ) -> list[Gramasewaka]:
        query = db.query(Gramasewaka).filter(Gramasewaka.gn_is_deleted.is_(False))

        if divisional_code:
            query = query.filter(Gramasewaka.gn_dvcode == divisional_code)

        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Gramasewaka.gn_gnc.ilike(pattern),
                    Gramasewaka.gn_gnname.ilike(pattern),
                    Gramasewaka.gn_mbile.ilike(pattern),
                    Gramasewaka.gn_email.ilike(pattern),
                    Gramasewaka.gn_dvcode.ilike(pattern),
                )
            )

        return (
            query.order_by(Gramasewaka.gn_id)
            .offset(max(skip, 0))
            .limit(limit)
            .all()
        )

    def count(
        self,
        db: Session,
        *,
        search: Optional[str] = None,
        divisional_code: Optional[str] = None,
    ) -> int:
        query = db.query(func.count(Gramasewaka.gn_id)).filter(
            Gramasewaka.gn_is_deleted.is_(False)
        )

        if divisional_code:
            query = query.filter(Gramasewaka.gn_dvcode == divisional_code)

        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Gramasewaka.gn_gnc.ilike(pattern),
                    Gramasewaka.gn_gnname.ilike(pattern),
                    Gramasewaka.gn_mbile.ilike(pattern),
                    Gramasewaka.gn_email.ilike(pattern),
                    Gramasewaka.gn_dvcode.ilike(pattern),
                )
            )

        return int(query.scalar() or 0)

    def create(self, db: Session, *, data: GramasewakaCreate) -> Gramasewaka:
        payload = data.model_dump(exclude_unset=True)
        now = datetime.utcnow()

        payload.setdefault("gn_is_deleted", False)
        payload.setdefault("gn_version_number", 1)
        payload.setdefault("gn_created_at", now)
        payload.setdefault("gn_updated_at", now)
        payload.setdefault("gn_version", now)

        entity = Gramasewaka(**payload)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def update(
        self, db: Session, *, entity: Gramasewaka, data: GramasewakaUpdate
    ) -> Gramasewaka:
        update_data = data.model_dump(exclude_unset=True)
        update_data.pop("gn_id", None)
        update_data.pop("gn_version_number", None)

        for key, value in update_data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        now = datetime.utcnow()
        entity.gn_version_number = (entity.gn_version_number or 1) + 1
        entity.gn_updated_at = now
        entity.gn_version = now

        db.commit()
        db.refresh(entity)
        return entity

    def soft_delete(
        self, db: Session, *, entity: Gramasewaka, actor_id: Optional[str]
    ) -> Gramasewaka:
        now = datetime.utcnow()
        entity.gn_is_deleted = True
        entity.gn_updated_by = actor_id
        entity.gn_version_number = (entity.gn_version_number or 1) + 1
        entity.gn_updated_at = now
        entity.gn_version = now

        db.commit()
        db.refresh(entity)
        return entity


gramasewaka_repo = GramasewakaRepository()
