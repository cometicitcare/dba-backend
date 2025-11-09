from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.divisional_secretariat import DivisionalSecretariat
from app.models.user import UserAccount
from app.repositories.divisional_secretariat_repo import (
    divisional_secretariat_repo,
)
from app.repositories.district_repo import district_repo
from app.schemas.divisional_secretariat import (
    DivisionalSecretariatCreate,
    DivisionalSecretariatUpdate,
)


class DivisionalSecretariatService:
    """Business logic helpers for divisional secretariat management."""

    def create_divisional_secretariat(
        self,
        db: Session,
        *,
        payload: DivisionalSecretariatCreate,
        actor_id: Optional[str],
    ) -> DivisionalSecretariat:
        payload_dict = self._strip_strings(payload.model_dump())
        payload_dict["dv_created_by"] = actor_id
        payload_dict["dv_updated_by"] = actor_id

        self._validate_required_fields(payload_dict, require_all=True)
        self._validate_user_reference(db, payload_dict.get("dv_created_by"), "dv_created_by")
        self._validate_user_reference(db, payload_dict.get("dv_updated_by"), "dv_updated_by")
        self._validate_district_reference(db, payload_dict.get("dv_distrcd"))
        self._ensure_unique_code(db, payload_dict["dv_dvcode"])

        create_payload = DivisionalSecretariatCreate(**payload_dict)
        return divisional_secretariat_repo.create(db, data=create_payload)

    def list_divisional_secretariats(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        district_code: Optional[str] = None,
    ) -> list[DivisionalSecretariat]:
        limit = max(1, min(limit, 200))
        skip = max(0, skip)
        return divisional_secretariat_repo.list(
            db,
            skip=skip,
            limit=limit,
            search=search,
            district_code=district_code,
        )

    def count_divisional_secretariats(
        self,
        db: Session,
        *,
        search: Optional[str] = None,
        district_code: Optional[str] = None,
    ) -> int:
        return divisional_secretariat_repo.count(
            db, search=search, district_code=district_code
        )

    def get_divisional_secretariat(
        self, db: Session, *, dv_id: int
    ) -> Optional[DivisionalSecretariat]:
        return divisional_secretariat_repo.get(db, dv_id)

    def get_divisional_secretariat_by_code(
        self, db: Session, *, dv_dvcode: str
    ) -> Optional[DivisionalSecretariat]:
        return divisional_secretariat_repo.get_by_code(db, dv_dvcode)

    def update_divisional_secretariat(
        self,
        db: Session,
        *,
        dv_id: int,
        payload: DivisionalSecretariatUpdate,
        actor_id: Optional[str],
    ) -> DivisionalSecretariat:
        entity = divisional_secretariat_repo.get(db, dv_id)
        if not entity:
            raise ValueError("Divisional secretariat not found.")

        update_data = self._strip_strings(payload.model_dump(exclude_unset=True))
        if not update_data:
            raise ValueError("No data provided for update.")

        if "dv_dvcode" in update_data:
            if not self._has_value(update_data["dv_dvcode"]):
                raise ValueError("dv_dvcode cannot be empty.")
            if update_data["dv_dvcode"] != entity.dv_dvcode:
                self._ensure_unique_code(db, update_data["dv_dvcode"])

        if "dv_distrcd" in update_data:
            if not self._has_value(update_data["dv_distrcd"]):
                raise ValueError("dv_distrcd cannot be empty.")
            self._validate_district_reference(db, update_data["dv_distrcd"])

        update_data["dv_updated_by"] = actor_id
        self._validate_user_reference(db, update_data.get("dv_updated_by"), "dv_updated_by")

        update_payload = DivisionalSecretariatUpdate(**update_data)
        return divisional_secretariat_repo.update(db, entity=entity, data=update_payload)

    def delete_divisional_secretariat(
        self,
        db: Session,
        *,
        dv_id: int,
        actor_id: Optional[str],
    ) -> DivisionalSecretariat:
        entity = divisional_secretariat_repo.get(db, dv_id)
        if not entity:
            raise ValueError("Divisional secretariat not found.")

        return divisional_secretariat_repo.soft_delete(db, entity=entity, actor_id=actor_id)

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _ensure_unique_code(self, db: Session, dv_dvcode: str) -> None:
        existing = divisional_secretariat_repo.get_by_code(db, dv_dvcode)
        if existing:
            raise ValueError(f"dv_dvcode '{dv_dvcode}' already exists.")

    def _validate_required_fields(
        self,
        payload: Dict[str, Any],
        *,
        require_all: bool,
    ) -> None:
        code = payload.get("dv_dvcode")
        district_code = payload.get("dv_distrcd")

        if require_all or "dv_dvcode" in payload:
            if not self._has_value(code):
                raise ValueError("dv_dvcode is required.")

        if require_all or "dv_distrcd" in payload:
            if not self._has_value(district_code):
                raise ValueError("dv_distrcd is required.")

    def _validate_district_reference(self, db: Session, dv_distrcd: Optional[str]) -> None:
        if not self._has_value(dv_distrcd):
            return
        district = district_repo.get_by_code(db, dv_distrcd)
        if not district:
            raise ValueError(f"Invalid reference: dv_distrcd '{dv_distrcd}' not found.")

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


divisional_secretariat_service = DivisionalSecretariatService()
