from __future__ import annotations

import re
from typing import Any, Dict, Optional, Tuple

from sqlalchemy import MetaData, Table, select
from sqlalchemy.exc import NoSuchTableError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.gramasewaka import Gramasewaka
from app.models.user import UserAccount
from app.repositories.gramasewaka_repo import gramasewaka_repo
from app.schemas.gramasewaka import GramasewakaCreate, GramasewakaUpdate


class GramasewakaService:
    """Business logic and validations for Gramasewaka (cmm_gndata) records."""

    FK_TABLE_MAP: Dict[str, Tuple[Optional[str], str, str]] = {
        "gn_dvcode": ("public", "cmm_dvsec", "dv_dvcode"),
    }

    MOBILE_PATTERN = re.compile(r"^0\d{9}$")

    def __init__(self) -> None:
        self._table_cache: Dict[Tuple[Optional[str], str], Table] = {}

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def create_gramasewaka(
        self, db: Session, *, payload: GramasewakaCreate, actor_id: Optional[str]
    ) -> Gramasewaka:
        payload_dict = payload.model_dump()
        payload_dict["gn_created_by"] = actor_id
        payload_dict["gn_updated_by"] = actor_id

        payload_dict = self._strip_strings(payload_dict)
        payload_dict = self._normalize_contact_fields(payload_dict)
        self._validate_required_fields(payload_dict, require_all=True)
        self._validate_contact_formats(payload_dict)
        self._validate_foreign_keys(db, payload_dict)
        self._ensure_unique_fields(
            db,
            gn_gnc=payload_dict["gn_gnc"],
            gn_mbile=payload_dict.get("gn_mbile"),
            gn_email=payload_dict.get("gn_email"),
            current_id=None,
        )

        create_payload = GramasewakaCreate(**payload_dict)
        return gramasewaka_repo.create(db, data=create_payload)

    def list_gramasewaka(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        divisional_code: Optional[str] = None,
    ) -> list[Gramasewaka]:
        limit = max(1, min(limit, 200))
        skip = max(0, skip)
        return gramasewaka_repo.list(
            db,
            skip=skip,
            limit=limit,
            search=search,
            divisional_code=divisional_code,
        )

    def count_gramasewaka(
        self,
        db: Session,
        *,
        search: Optional[str] = None,
        divisional_code: Optional[str] = None,
    ) -> int:
        return gramasewaka_repo.count(
            db, search=search, divisional_code=divisional_code
        )

    def get_gramasewaka(self, db: Session, *, gn_id: int) -> Optional[Gramasewaka]:
        return gramasewaka_repo.get(db, gn_id)

    def get_gramasewaka_by_code(
        self, db: Session, *, gn_gnc: str
    ) -> Optional[Gramasewaka]:
        return gramasewaka_repo.get_by_code(db, gn_gnc)

    def update_gramasewaka(
        self,
        db: Session,
        *,
        gn_id: int,
        payload: GramasewakaUpdate,
        actor_id: Optional[str],
    ) -> Gramasewaka:
        entity = gramasewaka_repo.get(db, gn_id)
        if not entity:
            raise ValueError("Gramasewaka record not found.")

        update_data = payload.model_dump(exclude_unset=True)
        update_data = self._strip_strings(update_data)
        update_data = self._normalize_contact_fields(update_data)

        if not update_data:
            raise ValueError("No data provided for update.")

        if "gn_gnc" in update_data:
            if not self._has_value(update_data["gn_gnc"]):
                raise ValueError("gn_gnc cannot be empty.")
            if update_data["gn_gnc"] != entity.gn_gnc:
                self._ensure_unique_fields(
                    db,
                    gn_gnc=update_data["gn_gnc"],
                    gn_mbile=None,
                    gn_email=None,
                    current_id=entity.gn_id,
                )

        self._validate_required_fields(update_data, require_all=False)
        self._validate_contact_formats(update_data)

        if "gn_mbile" in update_data and update_data["gn_mbile"] != entity.gn_mbile:
            self._ensure_unique_fields(
                db,
                gn_gnc=None,
                gn_mbile=update_data.get("gn_mbile"),
                gn_email=None,
                current_id=entity.gn_id,
            )

        if "gn_email" in update_data and update_data["gn_email"] != entity.gn_email:
            self._ensure_unique_fields(
                db,
                gn_gnc=None,
                gn_mbile=None,
                gn_email=update_data.get("gn_email"),
                current_id=entity.gn_id,
            )

        update_data["gn_updated_by"] = actor_id
        self._validate_foreign_keys(db, update_data)

        update_payload = GramasewakaUpdate(**update_data)
        return gramasewaka_repo.update(db, entity=entity, data=update_payload)

    def delete_gramasewaka(
        self, db: Session, *, gn_id: int, actor_id: Optional[str]
    ) -> Gramasewaka:
        entity = gramasewaka_repo.get(db, gn_id)
        if not entity:
            raise ValueError("Gramasewaka record not found.")

        return gramasewaka_repo.soft_delete(db, entity=entity, actor_id=actor_id)

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _ensure_unique_fields(
        self,
        db: Session,
        *,
        gn_gnc: Optional[str],
        gn_mbile: Optional[str],
        gn_email: Optional[str],
        current_id: Optional[int],
    ) -> None:
        if self._has_value(gn_gnc):
            existing = gramasewaka_repo.get_by_code(db, gn_gnc)
            if existing and existing.gn_id != current_id:
                raise ValueError(f"gn_gnc '{gn_gnc}' already exists.")

        if self._has_value(gn_mbile):
            existing = gramasewaka_repo.get_by_mobile(db, gn_mbile)
            if existing and existing.gn_id != current_id:
                raise ValueError(f"gn_mbile '{gn_mbile}' already exists.")

        if self._has_value(gn_email):
            existing = gramasewaka_repo.get_by_email(db, gn_email)
            if existing and existing.gn_id != current_id:
                raise ValueError(f"gn_email '{gn_email}' already exists.")

    def _validate_required_fields(
        self, payload: Dict[str, Any], *, require_all: bool
    ) -> None:
        gn_gnc = payload.get("gn_gnc")
        gn_dvcode = payload.get("gn_dvcode")

        if require_all or "gn_gnc" in payload:
            if not self._has_value(gn_gnc):
                raise ValueError("gn_gnc is required.")

        if require_all or "gn_dvcode" in payload:
            if not self._has_value(gn_dvcode):
                raise ValueError("gn_dvcode is required.")

    def _validate_contact_formats(self, payload: Dict[str, Any]) -> None:
        mobile = payload.get("gn_mbile")
        if self._has_value(mobile):
            if not isinstance(mobile, str) or not self.MOBILE_PATTERN.match(mobile):
                raise ValueError(
                    "gn_mbile must be a 10-digit mobile number starting with 0."
                )

    def _validate_foreign_keys(
        self,
        db: Session,
        payload: Dict[str, Any],
    ) -> None:
        self._validate_user_reference(db, payload.get("gn_created_by"), "gn_created_by")
        self._validate_user_reference(db, payload.get("gn_updated_by"), "gn_updated_by")

        for field, target in self.FK_TABLE_MAP.items():
            value = payload.get(field)
            if not self._has_value(value):
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
        if not self._has_value(value):
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
    def _normalize_contact_fields(data: Dict[str, Any]) -> Dict[str, Any]:
        normalized = dict(data)
        email = normalized.get("gn_email")
        if isinstance(email, str):
            normalized["gn_email"] = email.lower()
        return normalized

    @staticmethod
    def _has_value(value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, str) and value.strip() == "":
            return False
        return True


gramasewaka_service = GramasewakaService()
