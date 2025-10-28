from datetime import datetime
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.bhikku import Bhikku
from app.models.nikaya import NikayaData
from app.models.parshawadata import ParshawaData
from app.models.user import UserAccount
from app.schemas.parshawadata import ParshawaCreate, ParshawaUpdate


class ParshawaRepository:
    """Data access helpers for Bhikku Parshawa data."""

    def get(self, db: Session, pr_id: int) -> Optional[ParshawaData]:
        return (
            db.query(ParshawaData)
            .filter(
                ParshawaData.pr_id == pr_id,
                ParshawaData.pr_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_prn(self, db: Session, pr_prn: str) -> Optional[ParshawaData]:
        return (
            db.query(ParshawaData)
            .filter(
                ParshawaData.pr_prn == pr_prn,
                ParshawaData.pr_is_deleted.is_(False),
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
    ) -> list[ParshawaData]:
        query = db.query(ParshawaData).filter(
            ParshawaData.pr_is_deleted.is_(False)
        )

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    ParshawaData.pr_prn.ilike(term),
                    ParshawaData.pr_pname.ilike(term),
                    ParshawaData.pr_nayakahimi.ilike(term),
                    ParshawaData.pr_nikayacd.ilike(term),
                    ParshawaData.pr_rmrks.ilike(term),
                )
            )

        return (
            query.order_by(ParshawaData.pr_id)
            .offset(max(skip, 0))
            .limit(limit)
            .all()
        )

    def count(self, db: Session, *, search: Optional[str] = None) -> int:
        query = db.query(func.count(ParshawaData.pr_id)).filter(
            ParshawaData.pr_is_deleted.is_(False)
        )

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    ParshawaData.pr_prn.ilike(term),
                    ParshawaData.pr_pname.ilike(term),
                    ParshawaData.pr_nayakahimi.ilike(term),
                    ParshawaData.pr_nikayacd.ilike(term),
                    ParshawaData.pr_rmrks.ilike(term),
                )
            )

        return query.scalar() or 0

    def create(
        self,
        db: Session,
        *,
        data: ParshawaCreate,
        actor_id: Optional[str],
    ) -> ParshawaData:
        payload = data.model_dump(exclude_unset=True)
        self._assert_unique_prn(db, payload["pr_prn"], exclude_id=None)
        self._assert_bhikku_exists(db, payload["pr_nayakahimi"])

        nikaya_code = payload.get("pr_nikayacd")
        if nikaya_code:
            self._assert_nikaya_exists(db, nikaya_code)

        if actor_id:
            self._assert_user_exists(db, actor_id)

        now = datetime.utcnow()
        payload["pr_created_by"] = actor_id
        payload["pr_updated_by"] = actor_id
        payload["pr_created_at"] = now
        payload["pr_updated_at"] = now
        payload["pr_is_deleted"] = False
        payload["pr_version_number"] = 1

        entity = ParshawaData(**payload)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def update(
        self,
        db: Session,
        *,
        entity: ParshawaData,
        data: ParshawaUpdate,
        actor_id: Optional[str],
    ) -> ParshawaData:
        update_data = data.model_dump(exclude_unset=True)

        prn = update_data.get("pr_prn")
        if prn:
            self._assert_unique_prn(db, prn, exclude_id=entity.pr_id)

        nayaka = update_data.get("pr_nayakahimi")
        if nayaka:
            self._assert_bhikku_exists(db, nayaka)

        nikaya_code = update_data.get("pr_nikayacd")
        if "pr_nikayacd" in update_data and nikaya_code:
            self._assert_nikaya_exists(db, nikaya_code)

        if actor_id:
            self._assert_user_exists(db, actor_id)

        update_data.pop("pr_is_deleted", None)
        update_data.pop("pr_updated_by", None)
        update_data.pop("pr_updated_at", None)

        for key, value in update_data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        entity.pr_updated_by = actor_id
        entity.pr_updated_at = datetime.utcnow()
        entity.pr_version_number = (entity.pr_version_number or 1) + 1

        db.commit()
        db.refresh(entity)
        return entity

    def soft_delete(
        self,
        db: Session,
        *,
        entity: ParshawaData,
        actor_id: Optional[str],
    ) -> ParshawaData:
        if entity.pr_is_deleted:
            raise ValueError("Parshawa data record is already deleted.")

        if actor_id:
            self._assert_user_exists(db, actor_id)

        entity.pr_is_deleted = True
        entity.pr_updated_by = actor_id
        entity.pr_updated_at = datetime.utcnow()
        entity.pr_version_number = (entity.pr_version_number or 1) + 1

        db.commit()
        db.refresh(entity)
        return entity

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _assert_unique_prn(
        self, db: Session, pr_prn: str, *, exclude_id: Optional[int]
    ) -> None:
        query = db.query(ParshawaData).filter(
            ParshawaData.pr_prn == pr_prn,
            ParshawaData.pr_is_deleted.is_(False),
        )
        if exclude_id is not None:
            query = query.filter(ParshawaData.pr_id != exclude_id)
        if query.first():
            raise ValueError(f"pr_prn '{pr_prn}' already exists.")

    def _assert_bhikku_exists(self, db: Session, br_regn: str) -> None:
        exists = (
            db.query(Bhikku.br_regn)
            .filter(
                Bhikku.br_regn == br_regn,
                Bhikku.br_is_deleted.is_(False),
            )
            .first()
        )
        if not exists:
            raise ValueError(f"Bhikku '{br_regn}' does not exist.")

    def _assert_nikaya_exists(self, db: Session, nk_code: str) -> None:
        exists = (
            db.query(NikayaData.nk_nkn)
            .filter(
                NikayaData.nk_nkn == nk_code,
                NikayaData.nk_is_deleted.is_(False),
            )
            .first()
        )
        if not exists:
            raise ValueError(f"Nikaya '{nk_code}' does not exist.")

    def _assert_user_exists(self, db: Session, user_id: str) -> None:
        exists = (
            db.query(UserAccount.ua_user_id)
            .filter(
                UserAccount.ua_user_id == user_id,
                UserAccount.ua_is_deleted.is_(False),
            )
            .first()
        )
        if not exists:
            raise ValueError(f"user '{user_id}' does not exist.")


parshawa_repo = ParshawaRepository()
