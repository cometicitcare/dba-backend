from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.district import District
from app.models.user import UserAccount
from app.repositories.district_repo import district_repo
from app.schemas.district import DistrictCreate, DistrictUpdate


class DistrictService:
    """Business logic helpers for district management."""

    def create_district(
        self, db: Session, *, payload: DistrictCreate, actor_id: Optional[str]
    ) -> District:
        payload_dict = self._strip_strings(payload.model_dump())
        payload_dict["dd_created_by"] = actor_id
        payload_dict["dd_updated_by"] = actor_id

        self._validate_required_fields(payload_dict, require_all=True)
        self._validate_user_reference(db, payload_dict.get("dd_created_by"), "dd_created_by")
        self._validate_user_reference(db, payload_dict.get("dd_updated_by"), "dd_updated_by")
        self._ensure_unique_code(db, payload_dict["dd_dcode"])

        create_payload = DistrictCreate(**payload_dict)
        return district_repo.create(db, data=create_payload)

    def list_districts(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> list[District]:
        limit = max(1, min(limit, 200))
        skip = max(0, skip)
        return district_repo.list(db, skip=skip, limit=limit, search=search)

    def count_districts(self, db: Session, *, search: Optional[str] = None) -> int:
        return district_repo.count(db, search=search)

    def get_district(self, db: Session, *, dd_id: int) -> Optional[District]:
        return district_repo.get(db, dd_id)

    def get_district_by_code(
        self, db: Session, *, dd_dcode: str
    ) -> Optional[District]:
        return district_repo.get_by_code(db, dd_dcode)

    def update_district(
        self,
        db: Session,
        *,
        dd_id: int,
        payload: DistrictUpdate,
        actor_id: Optional[str],
    ) -> District:
        entity = district_repo.get(db, dd_id)
        if not entity:
            raise ValueError("District not found.")

        update_data = self._strip_strings(payload.model_dump(exclude_unset=True))
        if not update_data:
            raise ValueError("No data provided for update.")

        if "dd_dcode" in update_data:
            if not self._has_value(update_data["dd_dcode"]):
                raise ValueError("dd_dcode cannot be empty.")
            if update_data["dd_dcode"] != entity.dd_dcode:
                self._ensure_unique_code(db, update_data["dd_dcode"])

        update_data["dd_updated_by"] = actor_id
        self._validate_user_reference(db, update_data.get("dd_updated_by"), "dd_updated_by")

        update_payload = DistrictUpdate(**update_data)
        return district_repo.update(db, entity=entity, data=update_payload)

    def delete_district(
        self, db: Session, *, dd_id: int, actor_id: Optional[str]
    ) -> District:
        entity = district_repo.get(db, dd_id)
        if not entity:
            raise ValueError("District not found.")

        return district_repo.soft_delete(db, entity=entity, actor_id=actor_id)

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _ensure_unique_code(self, db: Session, dd_dcode: str) -> None:
        existing = district_repo.get_by_code(db, dd_dcode)
        if existing:
            raise ValueError(f"dd_dcode '{dd_dcode}' already exists.")

    def _validate_required_fields(
        self, payload: Dict[str, Any], *, require_all: bool
    ) -> None:
        code = payload.get("dd_dcode")
        if require_all or "dd_dcode" in payload:
            if not self._has_value(code):
                raise ValueError("dd_dcode is required.")

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


district_service = DistrictService()
