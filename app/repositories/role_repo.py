from __future__ import annotations

from datetime import datetime
from typing import Optional, Tuple

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.user import Role, UserAccount
from app.schemas.roles import RoleCreate, RoleUpdate


class RoleRepository:
    """Data access helpers for role entities."""

    ROLE_ID_PREFIX = "ROLE"
    ROLE_ID_PADDING = 5

    def _generate_role_id(self, db: Session) -> str:
        """Generate the next role identifier using the ROLExxxxx format."""
        stmt = (
            select(Role.ro_role_id)
            .where(Role.ro_role_id.like(f"{self.ROLE_ID_PREFIX}%"))
            .order_by(Role.ro_role_id.desc())
            .limit(1)
        )
        latest_id = db.execute(stmt).scalar_one_or_none()

        if not latest_id:
            next_number = 1
        else:
            suffix = latest_id[len(self.ROLE_ID_PREFIX) :]
            try:
                next_number = int(suffix) + 1
            except (TypeError, ValueError):
                count_stmt = select(func.count()).select_from(Role)
                next_number = (db.execute(count_stmt).scalar_one() or 0) + 1

        return f"{self.ROLE_ID_PREFIX}{next_number:0{self.ROLE_ID_PADDING}d}"

    def _validate_user(self, db: Session, user_id: Optional[str]) -> Optional[str]:
        """Ensure the provided user identifier exists and is active."""
        if user_id is None:
            return None

        stmt = select(UserAccount.ua_user_id).where(
            UserAccount.ua_user_id == user_id,
            UserAccount.ua_is_deleted.is_(False),
        )
        exists = db.execute(stmt).scalar_one_or_none()
        if not exists:
            raise ValueError(f"Invalid user identifier: {user_id}")
        return user_id

    def get(
        self, db: Session, role_id: str, *, include_deleted: bool = False
    ) -> Optional[Role]:
        query = db.query(Role).filter(Role.ro_role_id == role_id)
        if not include_deleted:
            query = query.filter(Role.ro_is_deleted.is_(False))
        return query.first()

    def list(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        include_deleted: bool = False,
    ) -> Tuple[list[Role], int]:
        skip = max(0, skip)
        limit = max(1, min(limit, 200))

        query = db.query(Role)
        if not include_deleted:
            query = query.filter(Role.ro_is_deleted.is_(False))

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(Role.ro_role_name.ilike(term), Role.ro_description.ilike(term))
            )

        total = query.count()
        records = (
            query.order_by(Role.ro_role_name.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return records, total

    def create(
        self,
        db: Session,
        *,
        data: RoleCreate,
        created_by: Optional[str],
        updated_by: Optional[str],
    ) -> Role:
        created_by = self._validate_user(db, created_by)
        updated_by = self._validate_user(db, updated_by)

        if (
            db.query(Role)
            .filter(Role.ro_role_name == data.ro_role_name)
            .first()
        ):
            raise ValueError(
                f"Role name '{data.ro_role_name}' already exists."
            )

        role_id = self._generate_role_id(db)
        now = datetime.utcnow()
        entity = Role(
            ro_role_id=role_id,
            ro_role_name=data.ro_role_name,
            ro_description=data.ro_description,
            ro_is_system_role=data.ro_is_system_role,
            ro_is_deleted=False,
            ro_created_at=now,
            ro_updated_at=now,
            ro_created_by=created_by,
            ro_updated_by=updated_by or created_by,
            ro_version_number=1,
        )

        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def update(
        self,
        db: Session,
        *,
        entity: Role,
        data: RoleUpdate,
        updated_by: Optional[str],
    ) -> Role:
        updated_by = self._validate_user(db, updated_by)

        update_data = data.model_dump(exclude_unset=True, exclude={"ro_updated_by"})
        if not update_data:
            return entity

        if "ro_role_name" in update_data:
            existing = (
                db.query(Role)
                .filter(
                    Role.ro_role_name == update_data["ro_role_name"],
                    Role.ro_role_id != entity.ro_role_id,
                )
                .first()
            )
            if existing:
                raise ValueError(
                    f"Role name '{update_data['ro_role_name']}' already exists."
                )

        for key, value in update_data.items():
            setattr(entity, key, value)

        entity.ro_updated_by = updated_by or entity.ro_updated_by
        entity.ro_updated_at = datetime.utcnow()
        entity.ro_version_number = (entity.ro_version_number or 0) + 1

        db.commit()
        db.refresh(entity)
        return entity

    def soft_delete(
        self,
        db: Session,
        *,
        entity: Role,
        updated_by: Optional[str],
    ) -> Role:
        updated_by = self._validate_user(db, updated_by)

        if entity.ro_is_deleted:
            return entity

        entity.ro_is_deleted = True
        entity.ro_updated_by = updated_by or entity.ro_updated_by
        entity.ro_updated_at = datetime.utcnow()
        entity.ro_version_number = (entity.ro_version_number or 0) + 1

        db.commit()
        db.refresh(entity)
        return entity


role_repo = RoleRepository()
