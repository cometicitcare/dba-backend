from datetime import datetime
from typing import Any, Optional

from sqlalchemy import MetaData, Table, inspect, select
from sqlalchemy.orm import Session

from app.models.vihara import ViharaData
from app.repositories.vihara_repo import vihara_repo
from app.schemas.vihara import ViharaCreate, ViharaUpdate


class ViharaService:
    """Business logic layer for vihara data."""

    def __init__(self) -> None:
        self._fk_targets: Optional[dict[str, tuple[Optional[str], str, str]]] = None

    def create_vihara(
        self, db: Session, *, payload: ViharaCreate, actor_id: Optional[str]
    ) -> ViharaData:
        existing = vihara_repo.get_by_trn(db, payload.vh_trn)
        if existing:
            raise ValueError(f"vh_trn '{payload.vh_trn}' already exists.")

        email_conflict = vihara_repo.get_by_email(db, payload.vh_email)
        if email_conflict:
            raise ValueError(f"vh_email '{payload.vh_email}' is already registered.")

        self._validate_foreign_keys(db, payload)

        now = datetime.utcnow()
        payload_dict = payload.model_dump()
        payload_dict["vh_created_by"] = actor_id
        payload_dict["vh_updated_by"] = actor_id
        payload_dict.setdefault("vh_created_at", now)
        payload_dict.setdefault("vh_updated_at", now)

        enriched_payload = ViharaCreate(**payload_dict)
        return vihara_repo.create(db, data=enriched_payload)

    def list_viharas(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> list[ViharaData]:
        limit = max(1, min(limit, 200))
        skip = max(0, skip)
        return vihara_repo.list(db, skip=skip, limit=limit, search=search)

    def count_viharas(self, db: Session, *, search: Optional[str] = None) -> int:
        return vihara_repo.count(db, search=search)

    def get_vihara(self, db: Session, vh_id: int) -> Optional[ViharaData]:
        return vihara_repo.get(db, vh_id)

    def get_vihara_by_trn(self, db: Session, vh_trn: str) -> Optional[ViharaData]:
        return vihara_repo.get_by_trn(db, vh_trn)

    def update_vihara(
        self,
        db: Session,
        *,
        vh_id: int,
        payload: ViharaUpdate,
        actor_id: Optional[str],
    ) -> ViharaData:
        entity = vihara_repo.get(db, vh_id)
        if not entity:
            raise ValueError("Vihara record not found.")

        if payload.vh_trn and payload.vh_trn != entity.vh_trn:
            duplicate = vihara_repo.get_by_trn(db, payload.vh_trn)
            if duplicate:
                raise ValueError(f"vh_trn '{payload.vh_trn}' already exists.")

        if payload.vh_email and payload.vh_email != entity.vh_email:
            email_conflict = vihara_repo.get_by_email(db, payload.vh_email)
            if email_conflict:
                raise ValueError(
                    f"vh_email '{payload.vh_email}' is already registered."
                )

        update_data = payload.model_dump(exclude_unset=True)
        update_data["vh_updated_by"] = actor_id
        update_data["vh_updated_at"] = datetime.utcnow()

        patched_payload = ViharaUpdate(**update_data)
        return vihara_repo.update(db, entity=entity, data=patched_payload)

    def delete_vihara(
        self, db: Session, *, vh_id: int, actor_id: Optional[str]
    ) -> ViharaData:
        entity = vihara_repo.get(db, vh_id)
        if not entity:
            raise ValueError("Vihara record not found.")

        entity.vh_updated_by = actor_id
        entity.vh_updated_at = datetime.utcnow()
        return vihara_repo.soft_delete(db, entity=entity)

    def _validate_foreign_keys(self, db: Session, payload: ViharaCreate) -> None:
        fk_targets = self._get_foreign_key_targets(db)
        fields_to_validate = {
            "vh_gndiv": payload.vh_gndiv,
            "vh_ownercd": payload.vh_ownercd,
            "vh_parshawa": payload.vh_parshawa,
            "vh_ssbmcode": payload.vh_ssbmcode,
        }

        for field, value in fields_to_validate.items():
            if value is None:
                continue
            if isinstance(value, str):
                value = value.strip()
                if not value:
                    continue

            target = fk_targets.get(field)
            if not target:
                raise RuntimeError(
                    f"Foreign key metadata for '{field}' is missing; unable to validate reference."
                )

            schema, table_name, column_name = target
            if not self._reference_exists(
                db,
                schema=schema,
                table_name=table_name,
                column_name=column_name,
                value=value,
            ):
                raise ValueError(f"Invalid reference: {field} not found")

    def _get_foreign_key_targets(
        self, db: Session
    ) -> dict[str, tuple[Optional[str], str, str]]:
        if self._fk_targets is not None:
            return self._fk_targets

        inspector = inspect(db.get_bind())
        mapping: dict[str, tuple[Optional[str], str, str]] = {}
        for fk in inspector.get_foreign_keys(ViharaData.__tablename__):
            constrained_columns = fk.get("constrained_columns") or []
            referred_columns = fk.get("referred_columns") or []
            table_name = fk.get("referred_table")
            schema = fk.get("referred_schema")
            if not table_name:
                continue

            for column, referred_column in zip(constrained_columns, referred_columns):
                if not column or not referred_column:
                    continue
                mapping[column] = (schema, table_name, referred_column)

        self._fk_targets = mapping
        return mapping

    def _reference_exists(
        self,
        db: Session,
        *,
        schema: Optional[str],
        table_name: str,
        column_name: str,
        value: Any,
    ) -> bool:
        metadata = MetaData()
        table = Table(table_name, metadata, schema=schema, autoload_with=db.get_bind())
        column = table.c.get(column_name)
        if column is None:
            raise RuntimeError(
                f"Invalid foreign key configuration: column '{column_name}' "
                f"not found in table '{table_name}'."
            )

        stmt = select(column).where(column == value).limit(1)
        result = db.execute(stmt).first()
        return result is not None


vihara_service = ViharaService()
