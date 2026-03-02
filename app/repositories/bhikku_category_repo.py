from datetime import datetime
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.bhikku_category import BhikkuCategory
from app.schemas.bhikku_category import BhikkuCategoryCreate, BhikkuCategoryUpdate


class BhikkuCategoryRepository:
    """Data access helpers for the cmm_cat table."""

    def get(self, db: Session, cc_id: int) -> Optional[BhikkuCategory]:
        return (
            db.query(BhikkuCategory)
            .filter(
                BhikkuCategory.cc_id == cc_id,
                BhikkuCategory.cc_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_code(self, db: Session, cc_code: str) -> Optional[BhikkuCategory]:
        return (
            db.query(BhikkuCategory)
            .filter(
                BhikkuCategory.cc_code == cc_code,
                BhikkuCategory.cc_is_deleted.is_(False),
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
    ) -> list[BhikkuCategory]:
        query = db.query(BhikkuCategory).filter(
            BhikkuCategory.cc_is_deleted.is_(False)
        )

        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    BhikkuCategory.cc_code.ilike(pattern),
                    BhikkuCategory.cc_catogry.ilike(pattern),
                )
            )

        return (
            query.order_by(BhikkuCategory.cc_id)
            .offset(max(skip, 0))
            .limit(limit)
            .all()
        )

    def count(self, db: Session, *, search: Optional[str] = None) -> int:
        query = db.query(func.count(BhikkuCategory.cc_id)).filter(
            BhikkuCategory.cc_is_deleted.is_(False)
        )

        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    BhikkuCategory.cc_code.ilike(pattern),
                    BhikkuCategory.cc_catogry.ilike(pattern),
                )
            )

        return int(query.scalar() or 0)

    def create(
        self,
        db: Session,
        *,
        data: BhikkuCategoryCreate,
    ) -> BhikkuCategory:
        payload = data.model_dump(exclude_unset=True)
        now = datetime.utcnow()

        payload.setdefault("cc_is_deleted", False)
        payload.setdefault("cc_version_number", 1)
        payload.setdefault("cc_created_at", now)
        payload.setdefault("cc_updated_at", now)
        payload.setdefault("cc_version", now)

        entity = BhikkuCategory(**payload)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def update(
        self,
        db: Session,
        *,
        entity: BhikkuCategory,
        data: BhikkuCategoryUpdate,
    ) -> BhikkuCategory:
        update_data = data.model_dump(exclude_unset=True)
        update_data.pop("cc_id", None)
        update_data.pop("cc_version_number", None)

        for key, value in update_data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        now = datetime.utcnow()
        entity.cc_version_number = (entity.cc_version_number or 1) + 1
        entity.cc_updated_at = now
        entity.cc_version = now

        db.commit()
        db.refresh(entity)
        return entity

    def soft_delete(
        self, db: Session, *, entity: BhikkuCategory, actor_id: Optional[str]
    ) -> BhikkuCategory:
        now = datetime.utcnow()
        entity.cc_is_deleted = True
        entity.cc_updated_by = actor_id
        entity.cc_version_number = (entity.cc_version_number or 1) + 1
        entity.cc_updated_at = now
        entity.cc_version = now

        db.commit()
        db.refresh(entity)
        return entity


bhikku_category_repo = BhikkuCategoryRepository()
