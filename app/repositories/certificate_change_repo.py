# app/repositories/certificate_change_repo.py
from typing import Optional

from sqlalchemy import MetaData, Table, func, or_, select
from sqlalchemy.orm import Session

from app.models.bhikku import Bhikku
from app.models.certificate_change import CertificateChange
from app.models.user import UserAccount
from app.schemas.certificate_change import (
    CertificateChangeCreate,
    CertificateChangeUpdate,
)


class CertificateChangeRepository:
    """Data access helpers for certificate change records."""

    def __init__(self) -> None:
        self._table_cache: dict[str, Table] = {}

    def get(self, db: Session, ch_id: int) -> Optional[CertificateChange]:
        return (
            db.query(CertificateChange)
            .filter(
                CertificateChange.ch_id == ch_id,
                CertificateChange.ch_is_deleted.is_(False),
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
    ) -> list[CertificateChange]:
        query = db.query(CertificateChange).filter(
            CertificateChange.ch_is_deleted.is_(False)
        )

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    CertificateChange.ch_regno.ilike(term),
                    CertificateChange.ch_autho.ilike(term),
                    CertificateChange.ch_prt.ilike(term),
                    CertificateChange.ch_admnusr.ilike(term),
                    CertificateChange.ch_dptusr.ilike(term),
                )
            )

        return (
            query.order_by(CertificateChange.ch_id)
            .offset(max(skip, 0))
            .limit(limit)
            .all()
        )

    def count(self, db: Session, *, search: Optional[str] = None) -> int:
        query = db.query(func.count(CertificateChange.ch_id)).filter(
            CertificateChange.ch_is_deleted.is_(False)
        )

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    CertificateChange.ch_regno.ilike(term),
                    CertificateChange.ch_autho.ilike(term),
                    CertificateChange.ch_prt.ilike(term),
                    CertificateChange.ch_admnusr.ilike(term),
                    CertificateChange.ch_dptusr.ilike(term),
                )
            )

        return query.scalar() or 0

    def create(
        self,
        db: Session,
        *,
        data: CertificateChangeCreate,
        actor_id: Optional[str],
    ) -> CertificateChange:
        payload = data.model_dump()
        payload.setdefault("ch_is_deleted", False)
        payload.setdefault("ch_version_number", 1)
        payload["ch_created_by"] = actor_id
        payload["ch_updated_by"] = actor_id

        self._assert_user_exists(db, actor_id, "actor_id")
        self._assert_bhikku_exists(db, payload.get("ch_regno"))
        self._assert_legacy_user_exists(db, payload.get("ch_admnusr"), "ch_admnusr")
        self._assert_legacy_user_exists(db, payload.get("ch_dptusr"), "ch_dptusr")

        entity = CertificateChange(**payload)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def update(
        self,
        db: Session,
        *,
        entity: CertificateChange,
        data: CertificateChangeUpdate,
        actor_id: Optional[str],
    ) -> CertificateChange:
        update_data = data.model_dump(exclude_unset=True)

        next_regno = update_data.get("ch_regno", entity.ch_regno)
        next_admnusr = update_data.get("ch_admnusr", entity.ch_admnusr)
        next_dptusr = update_data.get("ch_dptusr", entity.ch_dptusr)

        self._assert_user_exists(db, actor_id, "actor_id")
        self._assert_bhikku_exists(db, next_regno)
        self._assert_legacy_user_exists(db, next_admnusr, "ch_admnusr")
        self._assert_legacy_user_exists(db, next_dptusr, "ch_dptusr")

        for key, value in update_data.items():
            setattr(entity, key, value)

        entity.ch_updated_by = actor_id
        entity.ch_version_number = (entity.ch_version_number or 1) + 1
        db.commit()
        db.refresh(entity)
        return entity

    def soft_delete(
        self, db: Session, *, entity: CertificateChange, actor_id: Optional[str]
    ) -> CertificateChange:
        self._assert_user_exists(db, actor_id, "actor_id")
        entity.ch_is_deleted = True
        entity.ch_updated_by = actor_id
        entity.ch_version_number = (entity.ch_version_number or 1) + 1
        db.commit()
        db.refresh(entity)
        return entity

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _assert_user_exists(
        self, db: Session, user_id: Optional[str], field_name: str
    ) -> None:
        if not user_id:
            raise ValueError(f"{field_name} is required.")
        exists = (
            db.query(UserAccount.ua_user_id)
            .filter(
                UserAccount.ua_user_id == user_id,
                UserAccount.ua_is_deleted.is_(False),
            )
            .first()
        )
        if not exists:
            raise ValueError(f"{field_name} '{user_id}' does not exist.")

    def _assert_bhikku_exists(self, db: Session, regno: Optional[str]) -> None:
        if not regno:
            raise ValueError("ch_regno is required.")
        exists = (
            db.query(Bhikku.br_regn)
            .filter(
                Bhikku.br_regn == regno,
                Bhikku.br_is_deleted.is_(False),
            )
            .first()
        )
        if not exists:
            raise ValueError(f"ch_regno '{regno}' does not exist.")

    def _assert_legacy_user_exists(
        self, db: Session, legacy_id: Optional[str], field_name: str
    ) -> None:
        if not legacy_id:
            raise ValueError(f"{field_name} is required.")
        table = self._get_reference_table(db, "legacy_user_mapping")
        column = table.c.get("lm_legacy_usn")
        if column is None:
            raise RuntimeError("legacy_user_mapping.lm_legacy_usn column not found.")
        stmt = select(column).where(column == legacy_id).limit(1)
        exists = db.execute(stmt).first()
        if not exists:
            raise ValueError(f"{field_name} '{legacy_id}' does not exist.")

    def _get_reference_table(self, db: Session, table_name: str) -> Table:
        if table_name in self._table_cache:
            return self._table_cache[table_name]

        bind = db.get_bind()
        if bind is None:
            raise RuntimeError(
                "Database engine is not available for metadata reflection."
            )

        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=bind)
        self._table_cache[table_name] = table
        return table


certificate_change_repo = CertificateChangeRepository()
