from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from sqlalchemy import MetaData, Table, select
from sqlalchemy.exc import NoSuchTableError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.certificate import CertificateData
from app.repositories.certificate_repo import certificate_repo
from app.schemas.certificate import CertificateCreate, CertificateUpdate


class CertificateService:
    """Business logic for certificate management."""

    STATUS_REFERENCE: Tuple[Optional[str], str, str] = ("public", "statusdata", "st_statcd")

    def __init__(self) -> None:
        self._table_cache: Dict[Tuple[Optional[str], str], Table] = {}

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def create_certificate(
        self,
        db: Session,
        *,
        payload: CertificateCreate,
        actor_id: Optional[str],
    ) -> CertificateData:
        payload_dict = self._strip_strings(payload.model_dump())

        supplied_code = payload_dict.pop("cd_code", None)
        if supplied_code:
            raise ValueError("cd_code is auto-generated and must not be provided.")

        cd_stat = payload_dict.get("cd_stat")
        self._validate_status_reference(db, cd_stat)

        payload_dict["cd_code"] = None  # Repository will supply the next sequence.
        create_payload = CertificateCreate(**payload_dict)
        return certificate_repo.create(db, data=create_payload, actor_id=actor_id)

    def update_certificate(
        self,
        db: Session,
        *,
        cd_id: int,
        payload: CertificateUpdate,
        actor_id: Optional[str],
    ) -> CertificateData:
        entity = certificate_repo.get(db, cd_id)
        if not entity:
            raise ValueError("Certificate not found.")

        update_data = self._strip_strings(payload.model_dump(exclude_unset=True))

        if "cd_code" in update_data:
            proposed_code = update_data.pop("cd_code")
            if proposed_code and proposed_code != entity.cd_code:
                raise ValueError("cd_code is auto-generated and cannot be modified.")

        if "cd_stat" in update_data:
            self._validate_status_reference(db, update_data["cd_stat"])

        update_payload = CertificateUpdate(**update_data)
        return certificate_repo.update(
            db, entity=entity, data=update_payload, actor_id=actor_id
        )

    def delete_certificate(
        self,
        db: Session,
        *,
        cd_id: int,
        actor_id: Optional[str],
    ) -> CertificateData:
        entity = certificate_repo.get(db, cd_id)
        if not entity:
            raise ValueError("Certificate not found.")
        return certificate_repo.soft_delete(db, entity=entity, actor_id=actor_id)

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _validate_status_reference(self, db: Session, value: Optional[str]) -> None:
        if not self._has_meaningful_value(value):
            raise ValueError("cd_stat is required.")

        if not self._reference_exists(db, self.STATUS_REFERENCE, value):
            raise ValueError(f"Invalid reference: cd_stat '{value}' not found.")

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


certificate_service = CertificateService()
