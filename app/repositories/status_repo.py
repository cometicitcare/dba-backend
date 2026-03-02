# app/repositories/status_repo.py
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.status import StatusData
from app.models.user import UserAccount
from app.schemas.status import StatusCreate, StatusUpdate


class StatusRepository:
    """Data access helpers for status records."""

    def get(self, db: Session, st_id: int) -> Optional[StatusData]:
        return (
            db.query(StatusData)
            .filter(
                StatusData.st_id == st_id,
                StatusData.st_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_code(self, db: Session, st_statcd: str) -> Optional[StatusData]:
        normalized = self._normalize_code(st_statcd)
        if not normalized:
            return None
        return (
            db.query(StatusData)
            .filter(
                StatusData.st_statcd == normalized,
                StatusData.st_is_deleted.is_(False),
            )
            .first()
        )

    def list(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> list[StatusData]:
        query = db.query(StatusData).filter(StatusData.st_is_deleted.is_(False))

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    StatusData.st_statcd.ilike(term),
                    StatusData.st_descr.ilike(term),
                )
            )

        return (
            query.order_by(StatusData.st_id)
            .offset(max(skip, 0))
            .limit(limit)
            .all()
        )

    def count(self, db: Session, *, search: Optional[str] = None) -> int:
        query = db.query(func.count(StatusData.st_id)).filter(
            StatusData.st_is_deleted.is_(False)
        )

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    StatusData.st_statcd.ilike(term),
                    StatusData.st_descr.ilike(term),
                )
            )

        return query.scalar() or 0

    def create(
        self,
        db: Session,
        *,
        data: StatusCreate,
        actor_id: Optional[str],
    ) -> StatusData:
        self._assert_user_exists(db, actor_id, "actor_id")

        payload = data.model_dump()
        payload["st_statcd"] = self._normalize_code(payload.get("st_statcd"))
        if not payload["st_statcd"]:
            raise ValueError("st_statcd is required.")
        self._assert_unique_code(db, payload["st_statcd"])

        descr = payload.get("st_descr")
        if descr is not None:
            payload["st_descr"] = descr.strip() or None

        payload.setdefault("st_is_deleted", False)
        payload.setdefault("st_version_number", 1)
        payload["st_created_by"] = actor_id
        payload["st_updated_by"] = actor_id

        now = datetime.utcnow()
        payload["st_created_at"] = now
        payload["st_updated_at"] = now
        payload["st_version"] = now

        entity = StatusData(**payload)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def update(
        self,
        db: Session,
        *,
        entity: StatusData,
        data: StatusUpdate,
        actor_id: Optional[str],
    ) -> StatusData:
        self._assert_user_exists(db, actor_id, "actor_id")

        update_data = data.model_dump(exclude_unset=True)

        if "st_statcd" in update_data:
            normalized_code = self._normalize_code(update_data["st_statcd"])
            if not normalized_code:
                raise ValueError("st_statcd cannot be blank.")
            self._assert_unique_code(
                db,
                normalized_code,
                exclude_id=entity.st_id,
            )
            update_data["st_statcd"] = normalized_code

        if "st_descr" in update_data:
            descr_value = update_data["st_descr"]
            if descr_value is None:
                update_data["st_descr"] = None
            elif isinstance(descr_value, str):
                update_data["st_descr"] = descr_value.strip() or None
            else:
                update_data["st_descr"] = None

        for key, value in update_data.items():
            setattr(entity, key, value)

        entity.st_updated_by = actor_id
        entity.st_version_number = (entity.st_version_number or 1) + 1
        now = datetime.utcnow()
        entity.st_updated_at = now
        entity.st_version = now

        db.commit()
        db.refresh(entity)
        return entity

    def soft_delete(
        self,
        db: Session,
        *,
        entity: StatusData,
        actor_id: Optional[str],
    ) -> StatusData:
        self._assert_user_exists(db, actor_id, "actor_id")

        entity.st_is_deleted = True
        entity.st_updated_by = actor_id
        entity.st_version_number = (entity.st_version_number or 1) + 1
        now = datetime.utcnow()
        entity.st_updated_at = now
        entity.st_version = now

        db.commit()
        db.refresh(entity)
        return entity

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _normalize_code(self, code: Optional[str]) -> Optional[str]:
        return code.strip() if isinstance(code, str) else None

    def _assert_user_exists(
        self,
        db: Session,
        user_id: Optional[str],
        field_name: str,
    ) -> None:
        if not user_id:
            raise ValueError(f"{field_name} is required.")

        exists = (
            db.query(UserAccount.ua_user_id)
            .filter(
                UserAccount.ua_user_id == user_id,
                UserAccount.ua_is_deleted.is_(False),
            )
            .first()
        )
        if not exists:
            raise ValueError(f"{field_name} '{user_id}' does not exist.")

    def _assert_unique_code(
        self,
        db: Session,
        st_statcd: Optional[str],
        *,
        exclude_id: Optional[int] = None,
    ) -> None:
        if not st_statcd:
            raise ValueError("st_statcd is required.")

        query = db.query(StatusData).filter(
            StatusData.st_statcd == st_statcd,
            StatusData.st_is_deleted.is_(False),
        )
        if exclude_id is not None:
            query = query.filter(StatusData.st_id != exclude_id)

        exists = query.first() is not None
        if exists:
            raise ValueError(f"st_statcd '{st_statcd}' already exists.")


status_repo = StatusRepository()
