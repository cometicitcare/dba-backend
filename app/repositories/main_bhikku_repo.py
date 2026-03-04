# app/repositories/main_bhikku_repo.py
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.main_bhikku import MainBhikku


class MainBhikkuRepository:
    """Data-access helpers for `main_bhikkus`."""

    def get(self, db: Session, mb_id: int) -> Optional[MainBhikku]:
        return (
            db.query(MainBhikku)
            .filter(MainBhikku.mb_id == mb_id, MainBhikku.mb_is_deleted.is_(False))
            .first()
        )

    def get_active_nikaya_mahanayaka(
        self, db: Session, *, nikaya_cd: str
    ) -> Optional[MainBhikku]:
        return (
            db.query(MainBhikku)
            .filter(
                MainBhikku.mb_nikaya_cd == nikaya_cd,
                MainBhikku.mb_type == "NIKAYA_MAHANAYAKA",
                MainBhikku.mb_is_active.is_(True),
                MainBhikku.mb_is_deleted.is_(False),
            )
            .first()
        )

    def get_active_parshawa_mahanayaka(
        self, db: Session, *, nikaya_cd: str, parshawa_cd: str
    ) -> Optional[MainBhikku]:
        return (
            db.query(MainBhikku)
            .filter(
                MainBhikku.mb_nikaya_cd == nikaya_cd,
                MainBhikku.mb_parshawa_cd == parshawa_cd,
                MainBhikku.mb_type == "PARSHAWA_MAHANAYAKA",
                MainBhikku.mb_is_active.is_(True),
                MainBhikku.mb_is_deleted.is_(False),
            )
            .first()
        )

    def deactivate_existing(
        self,
        db: Session,
        *,
        nikaya_cd: str,
        parshawa_cd: Optional[str],
        mb_type: str,
        actor_id: Optional[str],
    ) -> None:
        """Deactivate all currently-active records of the same type/scope."""
        query = db.query(MainBhikku).filter(
            MainBhikku.mb_nikaya_cd == nikaya_cd,
            MainBhikku.mb_type == mb_type,
            MainBhikku.mb_is_active.is_(True),
            MainBhikku.mb_is_deleted.is_(False),
        )
        if parshawa_cd:
            query = query.filter(MainBhikku.mb_parshawa_cd == parshawa_cd)

        now = datetime.utcnow()
        for record in query.all():
            record.mb_is_active = False
            record.mb_end_date = now.date()
            record.mb_updated_by = actor_id
            record.mb_updated_at = now

    def create(
        self,
        db: Session,
        *,
        mb_type: str,
        nikaya_cd: str,
        parshawa_cd: Optional[str],
        bhikku_regn: str,
        start_date,
        remarks: Optional[str],
        actor_id: Optional[str],
    ) -> MainBhikku:
        now = datetime.utcnow()
        record = MainBhikku(
            mb_type=mb_type,
            mb_nikaya_cd=nikaya_cd,
            mb_parshawa_cd=parshawa_cd,
            mb_bhikku_regn=bhikku_regn,
            mb_start_date=start_date,
            mb_remarks=remarks,
            mb_is_active=True,
            mb_is_deleted=False,
            mb_created_by=actor_id,
            mb_updated_by=actor_id,
            mb_created_at=now,
            mb_updated_at=now,
            mb_version_number=1,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record


main_bhikku_repo = MainBhikkuRepository()
