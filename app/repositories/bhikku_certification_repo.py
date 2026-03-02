# app/repositories/bhikku_certification_repo.py
from datetime import datetime
from typing import Optional

from sqlalchemy import MetaData, Table, func, or_, select
from sqlalchemy.orm import Session

from app.models.bhikku import Bhikku
from app.models.bhikku_certification import BhikkuCertification
from app.models.user import UserAccount
from app.schemas.bhikku_certification import (
    BhikkuCertificationCreate,
    BhikkuCertificationUpdate,
)


class BhikkuCertificationRepository:
    """Data access helpers for bhikku certification records."""

    REGNO_PREFIX = "BH"
    REGNO_PADDING = 6
    INITIAL_SEQUENCE = 6
    BASE_YEAR = 2025

    def __init__(self) -> None:
        self._table_cache: dict[str, Table] = {}

    def get(self, db: Session, bc_id: int) -> Optional[BhikkuCertification]:
        return (
            db.query(BhikkuCertification)
            .filter(
                BhikkuCertification.bc_id == bc_id,
                BhikkuCertification.bc_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_regno(
        self, db: Session, bc_regno: str
    ) -> Optional[BhikkuCertification]:
        return (
            db.query(BhikkuCertification)
            .filter(
                BhikkuCertification.bc_regno == bc_regno,
                BhikkuCertification.bc_is_deleted.is_(False),
            )
            .order_by(BhikkuCertification.bc_issuedate.desc())
            .first()
        )

    def list(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> list[BhikkuCertification]:
        query = db.query(BhikkuCertification).filter(
            BhikkuCertification.bc_is_deleted.is_(False)
        )

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    BhikkuCertification.bc_regno.ilike(term),
                    BhikkuCertification.bc_adminautho.ilike(term),
                    BhikkuCertification.bc_prtoptn.ilike(term),
                    BhikkuCertification.bc_usr.ilike(term),
                    BhikkuCertification.bc_admnusr.ilike(term),
                )
            )

        return (
            query.order_by(BhikkuCertification.bc_id)
            .offset(max(skip, 0))
            .limit(limit)
            .all()
        )

    def count(self, db: Session, *, search: Optional[str] = None) -> int:
        query = db.query(func.count(BhikkuCertification.bc_id)).filter(
            BhikkuCertification.bc_is_deleted.is_(False)
        )

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    BhikkuCertification.bc_regno.ilike(term),
                    BhikkuCertification.bc_adminautho.ilike(term),
                    BhikkuCertification.bc_prtoptn.ilike(term),
                    BhikkuCertification.bc_usr.ilike(term),
                    BhikkuCertification.bc_admnusr.ilike(term),
                )
            )

        return query.scalar() or 0

    def create(
        self,
        db: Session,
        *,
        data: BhikkuCertificationCreate,
        actor_id: Optional[str],
    ) -> BhikkuCertification:
        payload = data.model_dump()
        payload.pop("bc_regno", None)
        payload.setdefault("bc_is_deleted", False)
        payload.setdefault("bc_version_number", 1)
        payload["bc_regno"] = self.generate_next_regno(db)
        payload["bc_created_by"] = actor_id
        payload["bc_updated_by"] = actor_id

        self._assert_user_exists(db, actor_id, "actor_id")
        self._assert_bhikku_exists(db, payload["bc_regno"])
        self._assert_legacy_user_exists(db, payload.get("bc_usr"), "bc_usr")
        self._assert_legacy_user_exists(db, payload.get("bc_admnusr"), "bc_admnusr")

        entity = BhikkuCertification(**payload)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def update(
        self,
        db: Session,
        *,
        entity: BhikkuCertification,
        data: BhikkuCertificationUpdate,
        actor_id: Optional[str],
    ) -> BhikkuCertification:
        update_data = data.model_dump(exclude_unset=True)
        update_data.pop("bc_regno", None)
        update_data.pop("bc_version_number", None)

        self._assert_user_exists(db, actor_id, "actor_id")
        next_usr = update_data.get("bc_usr", entity.bc_usr)
        next_admnusr = update_data.get("bc_admnusr", entity.bc_admnusr)
        self._assert_bhikku_exists(db, entity.bc_regno)
        self._assert_legacy_user_exists(db, next_usr, "bc_usr")
        self._assert_legacy_user_exists(db, next_admnusr, "bc_admnusr")

        for key, value in update_data.items():
            setattr(entity, key, value)

        entity.bc_updated_by = actor_id
        entity.bc_version_number = (entity.bc_version_number or 1) + 1
        db.commit()
        db.refresh(entity)
        return entity

    def soft_delete(
        self, db: Session, *, entity: BhikkuCertification, actor_id: Optional[str]
    ) -> BhikkuCertification:
        self._assert_user_exists(db, actor_id, "actor_id")
        entity.bc_is_deleted = True
        entity.bc_updated_by = actor_id
        entity.bc_version_number = (entity.bc_version_number or 1) + 1
        db.commit()
        db.refresh(entity)
        return entity

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def generate_next_regno(self, db: Session) -> str:
        current_year = datetime.utcnow().year
        if current_year < self.BASE_YEAR:
            current_year = self.BASE_YEAR
        prefix = f"{self.REGNO_PREFIX}{current_year}"

        latest_row = (
            db.query(BhikkuCertification.bc_regno)
            .filter(BhikkuCertification.bc_regno.like(f"{prefix}%"))
            .order_by(BhikkuCertification.bc_regno.desc())
            .first()
        )

        if latest_row and latest_row[0]:
            latest_code = latest_row[0]
            try:
                sequence_part = latest_code[len(prefix) :]
                last_sequence = int(sequence_part)
            except (ValueError, TypeError):
                last_sequence = self._initial_sequence_for_year(current_year) - 1
            next_sequence = max(
                last_sequence + 1, self._initial_sequence_for_year(current_year)
            )
        else:
            next_sequence = self._initial_sequence_for_year(current_year)

        return f"{prefix}{next_sequence:0{self.REGNO_PADDING}d}"

    def _initial_sequence_for_year(self, year: int) -> int:
        if year <= self.BASE_YEAR:
            return self.INITIAL_SEQUENCE
        return 1

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

    def _assert_bhikku_exists(self, db: Session, regno: str) -> None:
        exists = (
            db.query(Bhikku.br_regn)
            .filter(
                Bhikku.br_regn == regno,
                Bhikku.br_is_deleted.is_(False),
            )
            .first()
        )
        if not exists:
            raise ValueError(f"bhikku registration '{regno}' does not exist.")

    def _assert_legacy_user_exists(
        self, db: Session, legacy_id: Optional[str], field_name: str
    ) -> None:
        if not legacy_id:
            return
        table = self._get_reference_table(db, "legacy_user_mapping")
        column = table.c.get("lm_legacy_usn")
        if column is None:
            raise RuntimeError(
                "legacy_user_mapping.lm_legacy_usn column not found."
            )
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


bhikku_certification_repo = BhikkuCertificationRepository()
