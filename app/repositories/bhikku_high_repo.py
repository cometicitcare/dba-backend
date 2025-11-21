# app/repositories/bhikku_high_repo.py
from datetime import datetime
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.bhikku_high import BhikkuHighRegist
from app.schemas.bhikku_high import BhikkuHighCreate, BhikkuHighUpdate


class BhikkuHighRepository:
    """Data access helpers for higher bhikku registrations."""

    def generate_next_regn(self, db: Session) -> str:
        """
        Generate registration numbers in the format UPS{YEAR}{SEQUENCE}.
        Example: UPS2025001, UPS2025002, etc. Sequence resets each calendar year.
        """
        current_year = datetime.utcnow().year
        prefix = f"UPS{current_year}"

        latest = (
            db.query(BhikkuHighRegist)
            .filter(BhikkuHighRegist.bhr_regn.like(f"{prefix}%"))
            .order_by(BhikkuHighRegist.bhr_regn.desc())
            .first()
        )

        if latest:
            try:
                sequence_part = latest.bhr_regn[len(prefix) :]
                last_sequence = int(sequence_part)
                next_sequence = last_sequence + 1
            except (ValueError, IndexError):
                next_sequence = 1
        else:
            next_sequence = 1

        return f"{prefix}{next_sequence:03d}"

    def get(self, db: Session, bhr_id: int) -> Optional[BhikkuHighRegist]:
        return (
            db.query(BhikkuHighRegist)
            .filter(
                BhikkuHighRegist.bhr_id == bhr_id,
                BhikkuHighRegist.bhr_is_deleted.is_(False),
            )
            .first()
        )

    def get_raw_by_regn(self, db: Session, bhr_regn: str) -> Optional[BhikkuHighRegist]:
        return (
            db.query(BhikkuHighRegist)
            .filter(BhikkuHighRegist.bhr_regn == bhr_regn)
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

    def get_by_mobile(self, db: Session, bhr_mobile: str) -> Optional[BhikkuHighRegist]:
        return (
            db.query(BhikkuHighRegist)
            .filter(
                BhikkuHighRegist.bhr_mobile == bhr_mobile,
                BhikkuHighRegist.bhr_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_email(self, db: Session, bhr_email: str) -> Optional[BhikkuHighRegist]:
        return (
            db.query(BhikkuHighRegist)
            .filter(
                BhikkuHighRegist.bhr_email == bhr_email,
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
        payload = data.model_dump(exclude_none=True)
        payload.setdefault("bhr_is_deleted", False)
        payload.setdefault("bhr_version_number", 1)
        payload["bhr_created_by"] = actor_id
        payload["bhr_updated_by"] = actor_id

        if not payload.get("bhr_regn"):
            payload["bhr_regn"] = self.generate_next_regn(db)

        now = datetime.utcnow()
        payload.setdefault("bhr_created_at", now)
        payload.setdefault("bhr_updated_at", now)
        payload.setdefault("bhr_version", now)

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
        update_data.pop("bhr_regn", None)
        update_data.pop("bhr_version_number", None)

        for key, value in update_data.items():
            setattr(entity, key, value)

        entity.bhr_updated_by = actor_id
        entity.bhr_version_number = (entity.bhr_version_number or 1) + 1
        now = datetime.utcnow()
        entity.bhr_updated_at = now
        entity.bhr_version = now
        db.commit()
        db.refresh(entity)
        return entity

    def soft_delete(
        self, db: Session, *, entity: BhikkuHighRegist, actor_id: Optional[str]
    ) -> BhikkuHighRegist:
        entity.bhr_is_deleted = True
        entity.bhr_updated_by = actor_id
        entity.bhr_version_number = (entity.bhr_version_number or 1) + 1
        now = datetime.utcnow()
        entity.bhr_updated_at = now
        entity.bhr_version = now
        db.commit()
        db.refresh(entity)
        return entity


bhikku_high_repo = BhikkuHighRepository()


def generate_next_regn(db: Session) -> str:
    return bhikku_high_repo.generate_next_regn(db)


def get(db: Session, bhr_id: int):
    return bhikku_high_repo.get(db, bhr_id)


def get_by_regn(db: Session, bhr_regn: str):
    return bhikku_high_repo.get_by_regn(db, bhr_regn)


def get_by_mobile(db: Session, bhr_mobile: str):
    return bhikku_high_repo.get_by_mobile(db, bhr_mobile)


def get_by_email(db: Session, bhr_email: str):
    return bhikku_high_repo.get_by_email(db, bhr_email)


def list(
    db: Session, *, skip: int = 0, limit: int = 100, search: Optional[str] = None
):
    return bhikku_high_repo.list(db, skip=skip, limit=limit, search=search)


def count(db: Session, *, search: Optional[str] = None) -> int:
    return bhikku_high_repo.count(db, search=search)


def create(db: Session, *, data: BhikkuHighCreate, actor_id: Optional[str]):
    return bhikku_high_repo.create(db, data=data, actor_id=actor_id)


def update(
    db: Session,
    *,
    entity: BhikkuHighRegist,
    data: BhikkuHighUpdate,
    actor_id: Optional[str],
):
    return bhikku_high_repo.update(db, entity=entity, data=data, actor_id=actor_id)


def soft_delete(db: Session, *, entity: BhikkuHighRegist, actor_id: Optional[str]):
    return bhikku_high_repo.soft_delete(db, entity=entity, actor_id=actor_id)
