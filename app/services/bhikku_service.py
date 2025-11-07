from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from sqlalchemy import MetaData, Table, select
from sqlalchemy.exc import NoSuchTableError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.bhikku import Bhikku
from app.models.bhikku_high import BhikkuHighRegist
from app.models.user import UserAccount
from app.models.vihara import ViharaData
from app.repositories.bhikku_repo import bhikku_repo
from app.schemas.bhikku import BhikkuCreate, BhikkuUpdate


class BhikkuService:
    """Business logic and validation helpers for bhikku registrations."""

    FK_TABLE_MAP: Dict[str, Tuple[Optional[str], str, str]] = {
        "br_gndiv": ("public", "cmm_gndata", "gn_gnc"),
        "br_currstat": ("public", "statusdata", "st_statcd"),
        "br_parshawaya": ("public", "cmm_parshawadata", "pr_prn"),
        "br_cat": ("public", "cmm_cat", "cc_code"),
    }

    MOBILE_PATTERN = re.compile(r"^0\d{9}$")

    def __init__(self) -> None:
        self._table_cache: Dict[Tuple[Optional[str], str], Table] = {}

    # --------------------------------------------------------------------- #
    # Public API
    # --------------------------------------------------------------------- #
    def create_bhikku(
        self, db: Session, *, payload: BhikkuCreate, actor_id: Optional[str]
    ) -> Bhikku:
        payload_dict = payload.model_dump()
        payload_dict["br_created_by"] = actor_id
        payload_dict["br_updated_by"] = actor_id
        payload_dict = self._strip_strings(payload_dict)
        payload_dict = self._normalize_contact_fields(payload_dict)
        self._validate_contact_formats(payload_dict)

        explicit_regn = payload_dict.get("br_regn")
        if explicit_regn:
            existing = bhikku_repo.get_raw_by_regn(db, explicit_regn)
            if existing and not existing.br_is_deleted:
                raise ValueError(f"br_regn '{explicit_regn}' already exists.")
            if existing and existing.br_is_deleted:
                raise ValueError(
                    f"br_regn '{explicit_regn}' belongs to a deleted record and cannot be reused."
                )

        self._validate_foreign_keys(db, payload_dict, current_regn=None)
        self._validate_unique_contact_fields(
            db,
            br_mobile=payload_dict.get("br_mobile"),
            br_email=payload_dict.get("br_email"),
            br_fathrsmobile=payload_dict.get("br_fathrsmobile"),
            current_regn=None,
        )

        enriched_payload = BhikkuCreate(**payload_dict)
        created = bhikku_repo.create(db, enriched_payload)
        return created

    def list_bhikkus(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> list[Bhikku]:
        limit = max(1, min(limit, 200))
        skip = max(0, skip)
        return bhikku_repo.get_all(db, skip=skip, limit=limit, search_key=search)

    def count_bhikkus(self, db: Session, *, search: Optional[str] = None) -> int:
        total = bhikku_repo.get_total_count(db, search_key=search)
        return int(total or 0)

    def get_bhikku(self, db: Session, *, br_regn: str) -> Optional[Bhikku]:
        return bhikku_repo.get_by_regn(db, br_regn)

    def get_bhikku_by_id(self, db: Session, *, br_id: int) -> Optional[Bhikku]:
        return bhikku_repo.get_by_id(db, br_id)

    def update_bhikku(
        self,
        db: Session,
        *,
        br_regn: str,
        payload: BhikkuUpdate,
        actor_id: Optional[str],
    ) -> Bhikku:
        entity = bhikku_repo.get_by_regn(db, br_regn)
        if not entity:
            raise ValueError("Bhikku record not found.")

        update_data = payload.model_dump(exclude_unset=True)
        update_data = self._strip_strings(update_data)
        update_data = self._normalize_contact_fields(update_data)
        self._validate_contact_formats(update_data)

        if "br_regn" in update_data and update_data["br_regn"]:
            new_regn = update_data["br_regn"]
            if new_regn != br_regn:
                raise ValueError("br_regn cannot be modified once created.")

        update_data["br_updated_by"] = actor_id
        self._validate_foreign_keys(db, update_data, current_regn=br_regn)
        self._validate_unique_contact_fields(
            db,
            br_mobile=update_data.get("br_mobile"),
            br_email=update_data.get("br_email"),
            br_fathrsmobile=update_data.get("br_fathrsmobile"),
            current_regn=br_regn,
        )

        update_payload = BhikkuUpdate(**update_data)
        updated = bhikku_repo.update(db, br_regn=br_regn, bhikku_update=update_payload)
        if not updated:
            raise ValueError("Bhikku record not found.")
        return updated

    def delete_bhikku(
        self,
        db: Session,
        *,
        br_regn: str,
        actor_id: Optional[str],
    ) -> Bhikku:
        entity = bhikku_repo.get_by_regn(db, br_regn)
        if not entity:
            raise ValueError("Bhikku record not found.")

        entity.br_updated_by = actor_id
        entity.br_updated_at = datetime.utcnow()
        deleted = bhikku_repo.delete(db, br_regn=br_regn, updated_by=actor_id)
        if not deleted:
            raise ValueError("Bhikku record not found.")
        return deleted

    # --------------------------------------------------------------------- #
    # Helpers
    # --------------------------------------------------------------------- #
    def _validate_unique_contact_fields(
        self,
        db: Session,
        *,
        br_mobile: Optional[str],
        br_email: Optional[str],
        br_fathrsmobile: Optional[str],
        current_regn: Optional[str],
    ) -> None:
        if self._has_meaningful_value(br_mobile):
            existing_mobile = bhikku_repo.get_by_mobile(db, br_mobile)
            if existing_mobile and existing_mobile.br_regn != current_regn:
                raise ValueError(
                    f"br_mobile '{br_mobile}' is already associated with another bhikku."
                )

        if self._has_meaningful_value(br_email):
            existing_email = bhikku_repo.get_by_email(db, br_email)
            if existing_email and existing_email.br_regn != current_regn:
                raise ValueError(
                    f"br_email '{br_email}' is already associated with another bhikku."
                )

        if self._has_meaningful_value(br_fathrsmobile):
            existing_father_mobile = bhikku_repo.get_by_fathrsmobile(
                db, br_fathrsmobile
            )
            if existing_father_mobile and existing_father_mobile.br_regn != current_regn:
                raise ValueError(
                    f"br_fathrsmobile '{br_fathrsmobile}' is already associated with another bhikku."
                )

    def _validate_contact_formats(self, payload: Dict[str, Any]) -> None:
        for field in ("br_mobile", "br_fathrsmobile"):
            value = payload.get(field)
            if not self._has_meaningful_value(value):
                continue
            if not isinstance(value, str) or not self.MOBILE_PATTERN.match(value):
                raise ValueError(
                    f"{field} '{value}' is not a valid mobile number. Expected 10 digits starting with 0."
                )

    @staticmethod
    def _normalize_contact_fields(data: Dict[str, Any]) -> Dict[str, Any]:
        normalized = dict(data)
        if "br_email" in normalized and isinstance(normalized["br_email"], str):
            normalized["br_email"] = normalized["br_email"].lower()
        return normalized

    def _validate_foreign_keys(
        self,
        db: Session,
        payload: Dict[str, Any],
        *,
        current_regn: Optional[str],
    ) -> None:
        """Validate foreign key references for the provided payload."""
        # Direct table validations handled via ORM models for better readability.
        self._validate_user_reference(db, payload.get("br_created_by"), "br_created_by")
        self._validate_user_reference(db, payload.get("br_updated_by"), "br_updated_by")

        self._validate_vihara_reference(
            db, payload.get("br_livtemple"), "br_livtemple"
        )
        self._validate_vihara_reference(
            db, payload.get("br_mahanatemple"), "br_mahanatemple"
        )

        self._validate_bhikku_reference(
            db,
            payload.get("br_mahanaacharyacd"),
            "br_mahanaacharyacd",
            current_regn=current_regn,
        )

        self._validate_bhikku_high_reference(
            db, payload.get("br_upasampada_serial_no"), "br_upasampada_serial_no"
        )

        for field, target in self.FK_TABLE_MAP.items():
            value = payload.get(field)
            if not self._has_meaningful_value(value):
                continue
            if not self._reference_exists(db, target, value):
                schema, table_name, column_name = target
                raise ValueError(
                    f"Invalid reference: {field} '{value}' not found in "
                    f"{schema or 'public'}.{table_name}."
                )

    def _validate_user_reference(
        self, db: Session, value: Optional[str], field_name: str
    ) -> None:
        if not self._has_meaningful_value(value):
            return

        exists = (
            db.query(UserAccount.ua_user_id)
            .filter(
                UserAccount.ua_user_id == value,
                UserAccount.ua_is_deleted.is_(False),
            )
            .first()
        )
        if not exists:
            raise ValueError(f"Invalid reference: {field_name} '{value}' not found.")

    def _validate_vihara_reference(
        self, db: Session, value: Optional[str], field_name: str
    ) -> None:
        if not self._has_meaningful_value(value):
            return

        exists = (
            db.query(ViharaData.vh_trn)
            .filter(
                ViharaData.vh_trn == value,
                ViharaData.vh_is_deleted.is_(False),
            )
            .first()
        )
        if not exists:
            raise ValueError(f"Invalid reference: {field_name} '{value}' not found.")

    def _validate_bhikku_reference(
        self,
        db: Session,
        value: Optional[str],
        field_name: str,
        *,
        current_regn: Optional[str],
    ) -> None:
        if not self._has_meaningful_value(value):
            return

        # Allow referencing the current record when updating.
        if current_regn and value == current_regn:
            exists = bhikku_repo.get_raw_by_regn(db, value)
        else:
            exists = bhikku_repo.get_by_regn(db, value)

        if not exists:
            raise ValueError(f"Invalid reference: {field_name} '{value}' not found.")

    def _validate_bhikku_high_reference(
        self, db: Session, value: Optional[str], field_name: str
    ) -> None:
        if not self._has_meaningful_value(value):
            return

        exists = (
            db.query(BhikkuHighRegist.bhr_regn)
            .filter(
                BhikkuHighRegist.bhr_regn == value,
                BhikkuHighRegist.bhr_is_deleted.is_(False),
            )
            .first()
        )
        if not exists:
            raise ValueError(f"Invalid reference: {field_name} '{value}' not found.")

    def _reference_exists(
        self,
        db: Session,
        target: Tuple[Optional[str], str, str],
        value: Any,
    ) -> bool:
        schema, table_name, column_name = target
        try:
            table = self._get_table(db, schema, table_name)
        except (NoSuchTableError, SQLAlchemyError) as exc:
            raise RuntimeError(
                f"Foreign key metadata for '{table_name}.{column_name}' is not available."
            ) from exc

        column = table.c.get(column_name)
        if column is None:
            raise RuntimeError(
                f"Column '{column_name}' not found on table '{table_name}'."
            )

        stmt = select(column).where(column == value).limit(1)
        result = db.execute(stmt).first()
        return result is not None

    def _get_table(
        self, db: Session, schema: Optional[str], table_name: str
    ) -> Table:
        cache_key = (schema, table_name)
        if cache_key not in self._table_cache:
            metadata = MetaData()
            table = Table(
                table_name,
                metadata,
                schema=schema,
                autoload_with=db.get_bind(),
            )
            self._table_cache[cache_key] = table
        return self._table_cache[cache_key]

    @staticmethod
    def _strip_strings(data: Dict[str, Any]) -> Dict[str, Any]:
        cleaned: Dict[str, Any] = {}
        for key, value in data.items():
            if isinstance(value, str):
                cleaned[key] = value.strip()
            else:
                cleaned[key] = value
        return cleaned

    @staticmethod
    def _has_meaningful_value(value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, str) and value.strip() == "":
            return False
        return True


bhikku_service = BhikkuService()
