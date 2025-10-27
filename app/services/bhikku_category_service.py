from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.bhikku_category import BhikkuCategory
from app.models.user import UserAccount
from app.repositories.bhikku_category_repo import bhikku_category_repo
from app.schemas.bhikku_category import BhikkuCategoryCreate, BhikkuCategoryUpdate


class BhikkuCategoryService:
    """Business logic helpers for bhikku category management."""

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def create_category(
        self, db: Session, *, payload: BhikkuCategoryCreate, actor_id: Optional[str]
    ) -> BhikkuCategory:
        payload_dict = self._strip_strings(payload.model_dump())
        payload_dict["cc_created_by"] = actor_id
        payload_dict["cc_updated_by"] = actor_id

        self._validate_required_fields(payload_dict, require_all=True)
        self._validate_user_reference(db, payload_dict.get("cc_created_by"), "cc_created_by")
        self._validate_user_reference(db, payload_dict.get("cc_updated_by"), "cc_updated_by")
        self._ensure_unique_code(db, payload_dict["cc_code"])

        create_payload = BhikkuCategoryCreate(**payload_dict)
        return bhikku_category_repo.create(db, data=create_payload)

    def list_categories(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> list[BhikkuCategory]:
        limit = max(1, min(limit, 200))
        skip = max(0, skip)
        return bhikku_category_repo.list(db, skip=skip, limit=limit, search=search)

    def count_categories(self, db: Session, *, search: Optional[str] = None) -> int:
        return bhikku_category_repo.count(db, search=search)

    def get_category(self, db: Session, *, cc_id: int) -> Optional[BhikkuCategory]:
        return bhikku_category_repo.get(db, cc_id)

    def get_category_by_code(
        self, db: Session, *, cc_code: str
    ) -> Optional[BhikkuCategory]:
        return bhikku_category_repo.get_by_code(db, cc_code)

    def update_category(
        self,
        db: Session,
        *,
        cc_id: int,
        payload: BhikkuCategoryUpdate,
        actor_id: Optional[str],
    ) -> BhikkuCategory:
        entity = bhikku_category_repo.get(db, cc_id)
        if not entity:
            raise ValueError("Bhikku category not found.")

        update_data = self._strip_strings(payload.model_dump(exclude_unset=True))
        if not update_data:
            raise ValueError("No data provided for update.")

        if "cc_code" in update_data:
            if not self._has_value(update_data["cc_code"]):
                raise ValueError("cc_code cannot be empty.")
            if update_data["cc_code"] != entity.cc_code:
                self._ensure_unique_code(db, update_data["cc_code"])

        update_data["cc_updated_by"] = actor_id
        self._validate_user_reference(db, update_data.get("cc_updated_by"), "cc_updated_by")

        update_payload = BhikkuCategoryUpdate(**update_data)
        return bhikku_category_repo.update(db, entity=entity, data=update_payload)

    def delete_category(
        self, db: Session, *, cc_id: int, actor_id: Optional[str]
    ) -> BhikkuCategory:
        entity = bhikku_category_repo.get(db, cc_id)
        if not entity:
            raise ValueError("Bhikku category not found.")

        return bhikku_category_repo.soft_delete(db, entity=entity, actor_id=actor_id)

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _ensure_unique_code(self, db: Session, cc_code: str) -> None:
        existing = bhikku_category_repo.get_by_code(db, cc_code)
        if existing:
            raise ValueError(f"cc_code '{cc_code}' already exists.")

    def _validate_required_fields(
        self, payload: Dict[str, Any], *, require_all: bool
    ) -> None:
        code = payload.get("cc_code")
        if require_all or "cc_code" in payload:
            if not self._has_value(code):
                raise ValueError("cc_code is required.")

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


bhikku_category_service = BhikkuCategoryService()
