from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.bhikku import Bhikku
from app.models.main_bhikku import MainBhikku
from app.models.nikaya import NikayaData
from app.models.parshawadata import ParshawaData
from app.models.user import UserAccount
from app.schemas.main_bhikku import MainBhikkuCreate, MainBhikkuUpdate


class MainBhikkuRepository:
    """Data access helpers for the `main_bhikkus` table."""

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------

    def get(self, db: Session, mb_id: int) -> Optional[MainBhikku]:
        return (
            db.query(MainBhikku)
            .filter(MainBhikku.mb_id == mb_id, MainBhikku.mb_is_deleted.is_(False))
            .first()
        )

    def get_active_by_nikaya_and_type(
        self,
        db: Session,
        mb_nikaya_cd: str,
        mb_type: str,
        *,
        mb_parshawa_cd: Optional[str] = None,
    ) -> Optional[MainBhikku]:
        """Find the currently active record for a given nikaya (+parshawa) and type."""
        q = db.query(MainBhikku).filter(
            func.upper(MainBhikku.mb_nikaya_cd) == mb_nikaya_cd.strip().upper(),
            MainBhikku.mb_type == mb_type,
            MainBhikku.mb_is_active.is_(True),
            MainBhikku.mb_is_deleted.is_(False),
        )
        if mb_parshawa_cd:
            q = q.filter(func.upper(MainBhikku.mb_parshawa_cd) == mb_parshawa_cd.strip().upper())
        else:
            q = q.filter(MainBhikku.mb_parshawa_cd.is_(None))
        return q.first()

    def list(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        mb_type: Optional[str] = None,
        mb_nikaya_cd: Optional[str] = None,
        mb_parshawa_cd: Optional[str] = None,
    ) -> list[MainBhikku]:
        q = db.query(MainBhikku).filter(MainBhikku.mb_is_deleted.is_(False))

        if mb_type:
            q = q.filter(MainBhikku.mb_type == mb_type)
        if mb_nikaya_cd:
            q = q.filter(func.upper(MainBhikku.mb_nikaya_cd) == mb_nikaya_cd.strip().upper())
        if mb_parshawa_cd:
            q = q.filter(func.upper(MainBhikku.mb_parshawa_cd) == mb_parshawa_cd.strip().upper())

        if search:
            term = f"%{search.strip()}%"
            q = q.filter(
                or_(
                    MainBhikku.mb_nikaya_cd.ilike(term),
                    MainBhikku.mb_parshawa_cd.ilike(term),
                    MainBhikku.mb_bhikku_regn.ilike(term),
                    MainBhikku.mb_remarks.ilike(term),
                    MainBhikku.mb_type.ilike(term),
                )
            )

        return (
            q.order_by(MainBhikku.mb_id.desc())
            .offset(max(skip, 0))
            .limit(max(1, min(limit, 200)))
            .all()
        )

    def count(
        self,
        db: Session,
        *,
        search: Optional[str] = None,
        mb_type: Optional[str] = None,
        mb_nikaya_cd: Optional[str] = None,
        mb_parshawa_cd: Optional[str] = None,
    ) -> int:
        q = db.query(func.count(MainBhikku.mb_id)).filter(
            MainBhikku.mb_is_deleted.is_(False)
        )
        if mb_type:
            q = q.filter(MainBhikku.mb_type == mb_type)
        if mb_nikaya_cd:
            q = q.filter(func.upper(MainBhikku.mb_nikaya_cd) == mb_nikaya_cd.strip().upper())
        if mb_parshawa_cd:
            q = q.filter(func.upper(MainBhikku.mb_parshawa_cd) == mb_parshawa_cd.strip().upper())
        if search:
            term = f"%{search.strip()}%"
            q = q.filter(
                or_(
                    MainBhikku.mb_nikaya_cd.ilike(term),
                    MainBhikku.mb_parshawa_cd.ilike(term),
                    MainBhikku.mb_bhikku_regn.ilike(term),
                    MainBhikku.mb_remarks.ilike(term),
                    MainBhikku.mb_type.ilike(term),
                )
            )
        return q.scalar() or 0

    # ------------------------------------------------------------------
    # Writes
    # ------------------------------------------------------------------

    def create(
        self,
        db: Session,
        *,
        data: MainBhikkuCreate,
        actor_id: Optional[str],
    ) -> MainBhikku:
        payload = data.model_dump(exclude_unset=True)

        self._validate_fks(
            db,
            nikaya_cd=payload["mb_nikaya_cd"],
            parshawa_cd=payload.get("mb_parshawa_cd"),
            bhikku_regn=payload["mb_bhikku_regn"],
        )

        now = datetime.utcnow()
        payload["mb_created_by"] = actor_id
        payload["mb_updated_by"] = actor_id
        payload["mb_created_at"] = now
        payload["mb_updated_at"] = now
        payload["mb_is_deleted"] = False
        payload["mb_version_number"] = 1
        payload.setdefault("mb_is_active", True)

        entity = MainBhikku(**payload)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def update(
        self,
        db: Session,
        *,
        entity: MainBhikku,
        data: MainBhikkuUpdate,
        actor_id: Optional[str],
    ) -> MainBhikku:
        update_data = data.model_dump(exclude_unset=True)

        # Immutable / audit fields
        for key in ("mb_id", "mb_created_by", "mb_created_at", "mb_is_deleted", "mb_version_number"):
            update_data.pop(key, None)

        nk = update_data.get("mb_nikaya_cd", entity.mb_nikaya_cd)
        pr = update_data.get("mb_parshawa_cd", entity.mb_parshawa_cd)
        br = update_data.get("mb_bhikku_regn", entity.mb_bhikku_regn)
        self._validate_fks(db, nikaya_cd=nk, parshawa_cd=pr, bhikku_regn=br)

        for key, value in update_data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        entity.mb_updated_by = actor_id
        entity.mb_updated_at = datetime.utcnow()
        entity.mb_version_number = (entity.mb_version_number or 1) + 1

        db.commit()
        db.refresh(entity)
        return entity

    def soft_delete(
        self,
        db: Session,
        *,
        entity: MainBhikku,
        actor_id: Optional[str],
    ) -> MainBhikku:
        entity.mb_is_deleted = True
        entity.mb_is_active = False
        entity.mb_updated_by = actor_id
        entity.mb_updated_at = datetime.utcnow()
        entity.mb_version_number = (entity.mb_version_number or 1) + 1
        db.commit()
        db.refresh(entity)
        return entity

    def deactivate_existing(
        self,
        db: Session,
        *,
        mb_nikaya_cd: str,
        mb_type: str,
        mb_parshawa_cd: Optional[str] = None,
        actor_id: Optional[str],
    ) -> None:
        """Deactivate (but don't delete) any currently active record of the same type/nikaya/parshawa."""
        existing = self.get_active_by_nikaya_and_type(
            db, mb_nikaya_cd, mb_type, mb_parshawa_cd=mb_parshawa_cd
        )
        if existing:
            existing.mb_is_active = False
            existing.mb_updated_by = actor_id
            existing.mb_updated_at = datetime.utcnow()
            existing.mb_version_number = (existing.mb_version_number or 1) + 1

    # ------------------------------------------------------------------
    # FK Validation
    # ------------------------------------------------------------------

    def _validate_fks(
        self,
        db: Session,
        *,
        nikaya_cd: Optional[str],
        parshawa_cd: Optional[str],
        bhikku_regn: Optional[str],
    ) -> None:
        if nikaya_cd:
            exists = (
                db.query(NikayaData.nk_nkn)
                .filter(
                    func.upper(NikayaData.nk_nkn) == nikaya_cd.strip().upper(),
                    NikayaData.nk_is_deleted.is_(False),
                )
                .first()
            )
            if not exists:
                raise ValueError(f"Nikaya '{nikaya_cd}' does not exist.")

        if parshawa_cd:
            exists = (
                db.query(ParshawaData.pr_prn)
                .filter(
                    func.upper(ParshawaData.pr_prn) == parshawa_cd.strip().upper(),
                    ParshawaData.pr_is_deleted.is_(False),
                )
                .first()
            )
            if not exists:
                raise ValueError(f"Parshawaya '{parshawa_cd}' does not exist.")

        if bhikku_regn:
            exists = (
                db.query(Bhikku.br_regn)
                .filter(
                    Bhikku.br_regn == bhikku_regn,
                    Bhikku.br_is_deleted.is_(False),
                )
                .first()
            )
            if not exists:
                raise ValueError(f"Bhikku '{bhikku_regn}' does not exist.")


main_bhikku_repo = MainBhikkuRepository()
