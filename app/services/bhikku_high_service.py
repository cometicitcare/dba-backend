from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from sqlalchemy import MetaData, Table, select
from sqlalchemy.exc import NoSuchTableError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.bhikku_high import BhikkuHighRegist
from app.models.user import UserAccount
from app.models.vihara import ViharaData
from app.repositories import bhikku_repo
from app.repositories.bhikku_high_repo import bhikku_high_repo
from app.schemas.bhikku_high import BhikkuHighCreate, BhikkuHighUpdate


class BhikkuHighService:
    """Business logic layer for higher bhikku registrations."""

    FK_TABLE_MAP: Dict[str, Tuple[Optional[str], str, str]] = {
        "bhr_gndiv": ("public", "cmm_gndata", "gn_gnc"),
    }

    def __init__(self) -> None:
        self._table_cache: Dict[Tuple[Optional[str], str], Table] = {}

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def create_bhikku_high(
        self, db: Session, *, payload: BhikkuHighCreate, actor_id: Optional[str]
    ) -> BhikkuHighRegist:
        payload_dict = self._strip_strings(payload.model_dump())

        explicit_regn = payload_dict.get("bhr_regn")
        if explicit_regn:
            existing = bhikku_high_repo.get_raw_by_regn(db, explicit_regn)
            if existing and not existing.bhr_is_deleted:
                raise ValueError(f"bhr_regn '{explicit_regn}' already exists.")
            if existing and existing.bhr_is_deleted:
                raise ValueError(
                    f"bhr_regn '{explicit_regn}' belongs to a deleted record and cannot be reused."
                )

        self._validate_foreign_keys(db, payload_dict)
        self._validate_user_reference(db, actor_id, "bhr_created_by")
        self._validate_user_reference(db, actor_id, "bhr_updated_by")
        self._validate_unique_contact_fields(
            db,
            bhr_mobile=payload_dict.get("bhr_mobile"),
            bhr_email=payload_dict.get("bhr_email"),
            current_regn=None,
        )

        enriched_payload = BhikkuHighCreate(**payload_dict)
        return bhikku_high_repo.create(db, data=enriched_payload, actor_id=actor_id)

    def list_bhikku_highs(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> list[BhikkuHighRegist]:
        limit = max(1, min(limit, 200))
        skip = max(0, skip)
        return bhikku_high_repo.list(db, skip=skip, limit=limit, search=search)

    def count_bhikku_highs(self, db: Session, *, search: Optional[str] = None) -> int:
        total = bhikku_high_repo.count(db, search=search)
        return int(total or 0)

    def get_bhikku_high(self, db: Session, *, bhr_id: int) -> Optional[BhikkuHighRegist]:
        return bhikku_high_repo.get(db, bhr_id)

    def get_bhikku_high_by_regn(
        self, db: Session, *, bhr_regn: str
    ) -> Optional[BhikkuHighRegist]:
        return bhikku_high_repo.get_by_regn(db, bhr_regn)

    def update_bhikku_high(
        self,
        db: Session,
        *,
        bhr_id: int,
        payload: BhikkuHighUpdate,
        actor_id: Optional[str],
    ) -> BhikkuHighRegist:
        entity = bhikku_high_repo.get(db, bhr_id)
        if not entity:
            raise ValueError("Higher bhikku registration not found.")

        update_data = payload.model_dump(exclude_unset=True)
        update_data = self._strip_strings(update_data)

        if "bhr_regn" in update_data and update_data["bhr_regn"]:
            new_regn = update_data["bhr_regn"]
            if new_regn != entity.bhr_regn:
                raise ValueError("bhr_regn cannot be modified once created.")

        self._validate_foreign_keys(db, update_data)
        self._validate_user_reference(db, actor_id, "bhr_updated_by")
        self._validate_unique_contact_fields(
            db,
            bhr_mobile=update_data.get("bhr_mobile"),
            bhr_email=update_data.get("bhr_email"),
            current_regn=entity.bhr_regn,
        )

        patched_payload = BhikkuHighUpdate(**update_data)
        return bhikku_high_repo.update(
            db, entity=entity, data=patched_payload, actor_id=actor_id
        )

    def delete_bhikku_high(
        self,
        db: Session,
        *,
        bhr_id: int,
        actor_id: Optional[str],
    ) -> BhikkuHighRegist:
        entity = bhikku_high_repo.get(db, bhr_id)
        if not entity:
            raise ValueError("Higher bhikku registration not found.")

        return bhikku_high_repo.soft_delete(db, entity=entity, actor_id=actor_id)

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _validate_unique_contact_fields(
        self,
        db: Session,
        *,
        bhr_mobile: Optional[str],
        bhr_email: Optional[str],
        current_regn: Optional[str],
    ) -> None:
        if self._has_meaningful_value(bhr_mobile):
            existing = bhikku_high_repo.get_by_mobile(db, bhr_mobile)
            if existing and existing.bhr_regn != current_regn:
                raise ValueError(
                    f"bhr_mobile '{bhr_mobile}' is already associated with another higher bhikku."
                )

        if self._has_meaningful_value(bhr_email):
            existing = bhikku_high_repo.get_by_email(db, bhr_email)
            if existing and existing.bhr_regn != current_regn:
                raise ValueError(
                    f"bhr_email '{bhr_email}' is already associated with another higher bhikku."
                )

    def _validate_foreign_keys(
        self,
        db: Session,
        payload: Dict[str, Any],
    ) -> None:
        self._validate_bhikku_reference(
            db, payload.get("bhr_samanera_serial_no"), "bhr_samanera_serial_no"
        )
        self._validate_bhikku_reference(
            db, payload.get("bhr_mahanaacharyacd"), "bhr_mahanaacharyacd"
        )
        self._validate_bhikku_reference(
            db, payload.get("bhr_karmacharya"), "bhr_karmacharya"
        )
        self._validate_vihara_reference(
            db, payload.get("bhr_ordination_temple"), "bhr_ordination_temple"
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
        self, db: Session, value: Optional[str], field_name: str
    ) -> None:
        if not self._has_meaningful_value(value):
            return

        exists = bhikku_repo.get_by_regn(db, value)
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


bhikku_high_service = BhikkuHighService()
