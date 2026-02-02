from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.province import Province
from app.models.user import UserAccount
from app.repositories.province_repo import province_repo
from app.schemas.province import ProvinceCreate, ProvinceUpdate


class ProvinceService:
    """Business logic helpers for province management."""

    def create_province(
        self, db: Session, *, payload: ProvinceCreate, actor_id: Optional[str]
    ) -> Province:
        payload_dict = self._strip_strings(payload.model_dump())
        payload_dict["cp_created_by"] = actor_id
        payload_dict["cp_updated_by"] = actor_id

        self._validate_required_fields(payload_dict, require_all=True)
        self._validate_user_reference(db, payload_dict.get("cp_created_by"), "cp_created_by")
        self._validate_user_reference(db, payload_dict.get("cp_updated_by"), "cp_updated_by")
        self._ensure_unique_code(db, payload_dict["cp_code"])
        if self._has_value(payload_dict.get("cp_name")):
            self._ensure_unique_name(db, payload_dict["cp_name"])

        create_payload = ProvinceCreate(**payload_dict)
        return province_repo.create(db, data=create_payload)

    def list_provinces(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> list[Province]:
        limit = max(1, min(limit, 200))
        skip = max(0, skip)
        return province_repo.list(db, skip=skip, limit=limit, search=search)

    def count_provinces(self, db: Session, *, search: Optional[str] = None) -> int:
        return province_repo.count(db, search=search)

    def get_province(self, db: Session, *, cp_id: int) -> Optional[Province]:
        return province_repo.get(db, cp_id)

    def get_province_by_code(self, db: Session, *, cp_code: str) -> Optional[Province]:
        return province_repo.get_by_code(db, cp_code)

    def get_province_by_name(self, db: Session, *, cp_name: str) -> Optional[Province]:
        return province_repo.get_by_name(db, cp_name)

    def update_province(
        self,
        db: Session,
        *,
        cp_id: int,
        payload: ProvinceUpdate,
        actor_id: Optional[str],
    ) -> Province:
        entity = province_repo.get(db, cp_id)
        if not entity:
            raise ValueError("Province not found.")

        update_data = self._strip_strings(payload.model_dump(exclude_unset=True))
        if not update_data:
            raise ValueError("No data provided for update.")

        if "cp_code" in update_data:
            if not self._has_value(update_data["cp_code"]):
                raise ValueError("cp_code cannot be empty.")
            if update_data["cp_code"] != entity.cp_code:
                self._ensure_unique_code(db, update_data["cp_code"])

        if "cp_name" in update_data and self._has_value(update_data["cp_name"]):
            if update_data["cp_name"] != entity.cp_name:
                self._ensure_unique_name(db, update_data["cp_name"])

        update_data["cp_updated_by"] = actor_id
        self._validate_user_reference(db, update_data.get("cp_updated_by"), "cp_updated_by")

        update_payload = ProvinceUpdate(**update_data)
        return province_repo.update(db, entity=entity, data=update_payload)

    def delete_province(
        self, db: Session, *, cp_id: int, actor_id: Optional[str]
    ) -> Province:
        entity = province_repo.get(db, cp_id)
        if not entity:
            raise ValueError("Province not found.")

        return province_repo.soft_delete(db, entity=entity, actor_id=actor_id)

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _ensure_unique_code(self, db: Session, cp_code: str) -> None:
        existing = province_repo.get_by_code(db, cp_code)
        if existing:
            raise ValueError(f"cp_code '{cp_code}' already exists.")

    def _ensure_unique_name(self, db: Session, cp_name: str) -> None:
        existing = province_repo.get_by_name(db, cp_name)
        if existing:
            raise ValueError(f"cp_name '{cp_name}' already exists.")

    def _validate_required_fields(
        self, payload: Dict[str, Any], *, require_all: bool
    ) -> None:
        code = payload.get("cp_code")
        if require_all or "cp_code" in payload:
            if not self._has_value(code):
                raise ValueError("cp_code is required.")

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


province_service = ProvinceService()
