# app/repositories/religion_repo.py
from __future__ import annotations

import re
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.religion import Religion
from app.models.user import UserAccount
from app.schemas.religion import ReligionCreate, ReligionUpdate

CODE_PATTERN = re.compile(r"^REL(\d+)$")


class ReligionRepository:
    """Data access helpers for religion records."""

    def get(self, db: Session, rl_id: int) -> Optional[Religion]:
        return (
            db.query(Religion)
            .filter(
                Religion.rl_id == rl_id,
                Religion.rl_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_code(self, db: Session, rl_code: str) -> Optional[Religion]:
        normalized = (rl_code or "").strip()
        if not normalized:
            return None
        return (
            db.query(Religion)
            .filter(
                Religion.rl_code == normalized,
                Religion.rl_is_deleted.is_(False),
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
    ) -> list[Religion]:
        query = db.query(Religion).filter(Religion.rl_is_deleted.is_(False))

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Religion.rl_code.ilike(term),
                    Religion.rl_descr.ilike(term),
                )
            )

        return (
            query.order_by(Religion.rl_id)
            .offset(max(skip, 0))
            .limit(limit)
            .all()
        )

    def count(self, db: Session, *, search: Optional[str] = None) -> int:
        query = db.query(func.count(Religion.rl_id)).filter(
            Religion.rl_is_deleted.is_(False)
        )

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Religion.rl_code.ilike(term),
                    Religion.rl_descr.ilike(term),
                )
            )

        return query.scalar() or 0

    def create(
        self,
        db: Session,
        *,
        data: ReligionCreate,
        actor_id: Optional[str],
    ) -> Religion:
        self._assert_user_exists(db, actor_id, "actor_id")

        payload = data.model_dump()
        payload["rl_code"] = self._generate_next_code(db)
        payload.setdefault("rl_descr", None)
        payload.setdefault("rl_is_deleted", False)
        payload["rl_version_number"] = 1
        payload["rl_created_by"] = actor_id
        payload["rl_updated_by"] = actor_id

        entity = Religion(**payload)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def update(
        self,
        db: Session,
        *,
        entity: Religion,
        data: ReligionUpdate,
        actor_id: Optional[str],
    ) -> Religion:
        self._assert_user_exists(db, actor_id, "actor_id")

        update_data = data.model_dump(exclude_unset=True)
        if "rl_descr" in update_data:
            update_data["rl_descr"] = update_data["rl_descr"] or None

        for key, value in update_data.items():
            setattr(entity, key, value)

        entity.rl_updated_by = actor_id
        entity.rl_version_number = (entity.rl_version_number or 1) + 1
        db.commit()
        db.refresh(entity)
        return entity

    def soft_delete(
        self,
        db: Session,
        *,
        entity: Religion,
        actor_id: Optional[str],
    ) -> Religion:
        self._assert_user_exists(db, actor_id, "actor_id")

        entity.rl_is_deleted = True
        entity.rl_updated_by = actor_id
        entity.rl_version_number = (entity.rl_version_number or 1) + 1
        db.commit()
        db.refresh(entity)
        return entity

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _generate_next_code(self, db: Session) -> str:
        last_code: Optional[str] = (
            db.query(Religion.rl_code).order_by(Religion.rl_id.desc()).first()
        )

        if last_code:
            code_value = last_code[0]
            match = CODE_PATTERN.match(code_value or "")
            if match:
                next_number = int(match.group(1)) + 1
            else:
                next_number = 1
        else:
            next_number = 1

        return f"REL{next_number:03d}"

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


religion_repo = ReligionRepository()
