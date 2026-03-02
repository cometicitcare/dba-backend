from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from sqlalchemy import MetaData, Table, select
from sqlalchemy.exc import NoSuchTableError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.nilame import NilameRegist
from app.models.vihara import ViharaData
from app.repositories.nilame_repo import nilame_repo
from app.schemas.nilame import NilameCreate, NilameUpdate


class NilameService:
    """Business logic helpers for Nilame registrations."""

    FK_TABLE_MAP: Dict[str, Tuple[Optional[str], str, str]] = {
        "kr_grndiv": ("public", "cmm_gndata", "gn_gnc"),
    }

    def __init__(self) -> None:
        self._table_cache: Dict[Tuple[Optional[str], str], Table] = {}

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def create_nilame(
        self,
        db: Session,
        *,
        payload: NilameCreate,
        actor_id: Optional[str],
    ) -> NilameRegist:
        payload_dict = self._strip_strings(payload.model_dump(exclude_unset=True))
        self._validate_unique_nic(db, payload_dict.get("kr_nic"), current_id=None)
        self._validate_foreign_keys(db, payload_dict)
        enriched = NilameCreate(**payload_dict)
        return nilame_repo.create(db, data=enriched, actor_id=actor_id)

    def update_nilame(
        self,
        db: Session,
        *,
        kr_id: int,
        payload: NilameUpdate,
        actor_id: Optional[str],
    ) -> NilameRegist:
        entity = nilame_repo.get(db, kr_id)
        if not entity:
            raise ValueError("Nilame registration not found.")

        update_data = self._strip_strings(payload.model_dump(exclude_unset=True))
        if "kr_nic" in update_data:
            self._validate_unique_nic(
                db, update_data.get("kr_nic"), current_id=entity.kr_id
            )
        self._validate_foreign_keys(db, update_data)
        update_payload = NilameUpdate(**update_data)
        return nilame_repo.update(
            db, entity=entity, data=update_payload, actor_id=actor_id
        )

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _validate_foreign_keys(
        self,
        db: Session,
        payload: Dict[str, Any],
    ) -> None:
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

        self._validate_vihara_reference(db, payload.get("kr_trn"), "kr_trn")

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
        self,
        db: Session,
        schema: Optional[str],
        table_name: str,
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

    def _validate_unique_nic(
        self,
        db: Session,
        value: Optional[str],
        *,
        current_id: Optional[int],
    ) -> None:
        normalized = self._normalize_nic(value)
        if not normalized:
            return
        existing = nilame_repo.get_by_nic(db, normalized)
        if existing and existing.kr_id != current_id:
            raise ValueError(f"kr_nic '{normalized}' already exists.")

    @staticmethod
    def _normalize_nic(value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        trimmed = value.strip()
        if not trimmed:
            return None
        return trimmed.upper()


nilame_service = NilameService()
