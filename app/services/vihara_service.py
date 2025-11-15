from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import MetaData, Table, inspect, select
from sqlalchemy.exc import OperationalError
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
        contact_fields = (
            ("vh_mobile", payload.vh_mobile, vihara_repo.get_by_mobile),
            ("vh_whtapp", payload.vh_whtapp, vihara_repo.get_by_whtapp),
            ("vh_email", payload.vh_email, vihara_repo.get_by_email),
        )
        for field_name, value, getter in contact_fields:
            if value and getter(db, value):
                raise ValueError(f"{field_name} '{value}' is already registered.")

        now = datetime.utcnow()
        payload_dict = payload.model_dump(exclude_unset=True)
        payload_dict.pop("vh_trn", None)
        payload_dict.pop("vh_id", None)
        payload_dict.pop("vh_version_number", None)
        payload_dict["vh_created_by"] = actor_id
        payload_dict["vh_updated_by"] = actor_id
        payload_dict.setdefault("vh_created_at", now)
        payload_dict.setdefault("vh_updated_at", now)
        payload_dict.setdefault("vh_is_deleted", False)
        payload_dict["vh_version_number"] = 1

        self._validate_foreign_keys(db, payload_dict)
        enriched_payload = ViharaCreate(**payload_dict)
        return vihara_repo.create(db, data=enriched_payload)

    def list_viharas(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        vh_trn: Optional[str] = None,
        province: Optional[str] = None,
        district: Optional[str] = None,
        divisional_secretariat: Optional[str] = None,
        gn_division: Optional[str] = None,
        temple: Optional[str] = None,
        child_temple: Optional[str] = None,
        nikaya: Optional[str] = None,
        parshawaya: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        vh_typ: Optional[str] = None,
        date_from: Optional[Any] = None,
        date_to: Optional[Any] = None,
    ) -> list[ViharaData]:
        limit = max(1, min(limit, 200))
        skip = max(0, skip)
        return vihara_repo.list(
            db,
            skip=skip,
            limit=limit,
            search=search,
            vh_trn=vh_trn,
            province=province,
            district=district,
            divisional_secretariat=divisional_secretariat,
            gn_division=gn_division,
            temple=temple,
            child_temple=child_temple,
            nikaya=nikaya,
            parshawaya=parshawaya,
            category=category,
            status=status,
            vh_typ=vh_typ,
            date_from=date_from,
            date_to=date_to,
        )

    def count_viharas(
        self, 
        db: Session, 
        *, 
        search: Optional[str] = None,
        vh_trn: Optional[str] = None,
        province: Optional[str] = None,
        district: Optional[str] = None,
        divisional_secretariat: Optional[str] = None,
        gn_division: Optional[str] = None,
        temple: Optional[str] = None,
        child_temple: Optional[str] = None,
        nikaya: Optional[str] = None,
        parshawaya: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        vh_typ: Optional[str] = None,
        date_from: Optional[Any] = None,
        date_to: Optional[Any] = None,
    ) -> int:
        return vihara_repo.count(
            db,
            search=search,
            vh_trn=vh_trn,
            province=province,
            district=district,
            divisional_secretariat=divisional_secretariat,
            gn_division=gn_division,
            temple=temple,
            child_temple=child_temple,
            nikaya=nikaya,
            parshawaya=parshawaya,
            category=category,
            status=status,
            vh_typ=vh_typ,
            date_from=date_from,
            date_to=date_to,
        )

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
            raise ValueError("vh_trn cannot be modified once generated.")

        if payload.vh_mobile and payload.vh_mobile != entity.vh_mobile:
            conflict = vihara_repo.get_by_mobile(db, payload.vh_mobile)
            if conflict and conflict.vh_id != entity.vh_id:
                raise ValueError(
                    f"vh_mobile '{payload.vh_mobile}' is already registered."
                )

        if payload.vh_whtapp and payload.vh_whtapp != entity.vh_whtapp:
            conflict = vihara_repo.get_by_whtapp(db, payload.vh_whtapp)
            if conflict and conflict.vh_id != entity.vh_id:
                raise ValueError(
                    f"vh_whtapp '{payload.vh_whtapp}' is already registered."
                )

        if payload.vh_email and payload.vh_email != entity.vh_email:
            conflict = vihara_repo.get_by_email(db, payload.vh_email)
            if conflict and conflict.vh_id != entity.vh_id:
                raise ValueError(
                    f"vh_email '{payload.vh_email}' is already registered."
                )

        update_data = payload.model_dump(exclude_unset=True)
        update_data.pop("vh_version_number", None)
        update_data["vh_updated_by"] = actor_id
        update_data["vh_updated_at"] = datetime.utcnow()

        fk_values = self._build_fk_validation_payload(entity, update_data)
        self._validate_foreign_keys(db, fk_values)

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

    def _validate_foreign_keys(self, db: Session, values: Dict[str, Any]) -> None:
        try:
            fk_targets = self._get_foreign_key_targets(db)
        except OperationalError as exc:
            raise ValueError(
                "Unable to verify references due to temporary database connectivity issues."
            ) from exc
        fields_to_validate = {
            "vh_gndiv": values.get("vh_gndiv"),
            "vh_ownercd": values.get("vh_ownercd"),
            "vh_parshawa": values.get("vh_parshawa"),
            "vh_ssbmcode": values.get("vh_ssbmcode"),
            "vh_created_by": values.get("vh_created_by"),
            "vh_updated_by": values.get("vh_updated_by"),
        }

        for field, raw_value in fields_to_validate.items():
            value = raw_value
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
            try:
                exists = self._reference_exists(
                    db,
                    schema=schema,
                    table_name=table_name,
                    column_name=column_name,
                    value=value,
                )
            except OperationalError as exc:
                raise ValueError(
                    "Unable to verify references due to temporary database connectivity issues."
                ) from exc

            if not exists:
                raise ValueError(f"Invalid reference: {field} not found")

    def _build_fk_validation_payload(
        self, entity: ViharaData, update_values: Dict[str, Any]
    ) -> Dict[str, Any]:
        fk_fields = [
            "vh_gndiv",
            "vh_ownercd",
            "vh_parshawa",
            "vh_ssbmcode",
            "vh_created_by",
            "vh_updated_by",
        ]
        payload: Dict[str, Any] = {}
        for field in fk_fields:
            if field in update_values:
                payload[field] = update_values[field]
            else:
                payload[field] = getattr(entity, field, None)
        return payload

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
