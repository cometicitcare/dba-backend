from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from sqlalchemy import MetaData, Table, select
from sqlalchemy.exc import NoSuchTableError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.city import City
from app.models.user import UserAccount
from app.repositories.city_repo import city_repo
from app.schemas.city import CityCreate, CityUpdate


class CityService:
    """Business logic and validation helpers for city management."""

    FK_TABLE_MAP: Dict[str, Tuple[Optional[str], str, str]] = {
        "ct_gncode": ("public", "cmm_gndata", "gn_gnc"),
        "ct_dvcode": ("public", "cmm_dvsec", "dv_dvcode"),
    }

    def __init__(self) -> None:
        self._table_cache: Dict[Tuple[Optional[str], str], Table] = {}

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def create_city(
        self, db: Session, *, payload: CityCreate, actor_id: Optional[str]
    ) -> City:
        payload_dict = self._strip_strings(payload.model_dump())
        payload_dict["ct_created_by"] = actor_id
        payload_dict["ct_updated_by"] = actor_id

        self._validate_required_fields(payload_dict, require_all=True)
        self._validate_foreign_keys(db, payload_dict)
        self._ensure_unique_code(db, payload_dict["ct_code"])

        create_payload = CityCreate(**payload_dict)
        return city_repo.create(db, data=create_payload)

    def list_cities(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> list[City]:
        limit = max(1, min(limit, 200))
        skip = max(0, skip)
        return city_repo.list(db, skip=skip, limit=limit, search=search)

    def count_cities(self, db: Session, *, search: Optional[str] = None) -> int:
        return city_repo.count(db, search=search)

    def get_city(self, db: Session, *, ct_id: int) -> Optional[City]:
        return city_repo.get(db, ct_id)

    def get_city_by_code(self, db: Session, *, ct_code: str) -> Optional[City]:
        return city_repo.get_by_code(db, ct_code)

    def update_city(
        self,
        db: Session,
        *,
        ct_id: int,
        payload: CityUpdate,
        actor_id: Optional[str],
    ) -> City:
        entity = city_repo.get(db, ct_id)
        if not entity:
            raise ValueError("City record not found.")

        update_data = self._strip_strings(payload.model_dump(exclude_unset=True))
        if not update_data:
            raise ValueError("No data provided for update.")

        if "ct_code" in update_data:
            if not self._has_value(update_data["ct_code"]):
                raise ValueError("ct_code cannot be empty.")
            if update_data["ct_code"] != entity.ct_code:
                self._ensure_unique_code(db, update_data["ct_code"])

        if "ct_gncode" in update_data and not self._has_value(update_data["ct_gncode"]):
            raise ValueError("ct_gncode cannot be empty.")

        update_data["ct_updated_by"] = actor_id

        self._validate_foreign_keys(db, update_data)

        update_payload = CityUpdate(**update_data)
        return city_repo.update(db, entity=entity, data=update_payload)

    def delete_city(
        self, db: Session, *, ct_id: int, actor_id: Optional[str]
    ) -> City:
        entity = city_repo.get(db, ct_id)
        if not entity:
            raise ValueError("City record not found.")

        return city_repo.soft_delete(db, entity=entity, actor_id=actor_id)

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _ensure_unique_code(self, db: Session, ct_code: str) -> None:
        existing = city_repo.get_by_code(db, ct_code)
        if existing:
            raise ValueError(f"ct_code '{ct_code}' already exists.")

    def _validate_required_fields(
        self, payload: Dict[str, Any], *, require_all: bool
    ) -> None:
        code = payload.get("ct_code")
        gncode = payload.get("ct_gncode")

        if require_all or "ct_code" in payload:
            if not self._has_value(code):
                raise ValueError("ct_code is required.")

        if require_all or "ct_gncode" in payload:
            if not self._has_value(gncode):
                raise ValueError("ct_gncode is required.")

    def _validate_foreign_keys(
        self,
        db: Session,
        payload: Dict[str, Any],
    ) -> None:
        self._validate_user_reference(db, payload.get("ct_created_by"), "ct_created_by")
        self._validate_user_reference(db, payload.get("ct_updated_by"), "ct_updated_by")

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
    def _has_value(value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, str) and value.strip() == "":
            return False
        return True


city_service = CityService()
