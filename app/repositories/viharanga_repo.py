# app/repositories/viharanga_repo.py
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.viharanga import Viharanga
from app.schemas.viharanga import ViharangaCreate, ViharangaUpdate


class ViharangaRepository:
    """Data access helpers for viharanga records."""

    def get(self, db: Session, vg_id: int) -> Optional[Viharanga]:
        """Get viharanga by ID"""
        return (
            db.query(Viharanga)
            .filter(
                Viharanga.vg_id == vg_id,
                Viharanga.vg_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_code(self, db: Session, vg_code: str) -> Optional[Viharanga]:
        """Get viharanga by code"""
        normalized = self._normalize_code(vg_code)
        if not normalized:
            return None
        return (
            db.query(Viharanga)
            .filter(
                Viharanga.vg_code == normalized,
                Viharanga.vg_is_deleted.is_(False),
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
    ) -> list[Viharanga]:
        """List viharanga records with optional search and pagination"""
        query = db.query(Viharanga).filter(Viharanga.vg_is_deleted.is_(False))

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Viharanga.vg_code.ilike(term),
                    Viharanga.vg_item.ilike(term),
                )
            )

        return (
            query.order_by(Viharanga.vg_id)
            .offset(max(skip, 0))
            .limit(limit)
            .all()
        )

    def count(self, db: Session, *, search: Optional[str] = None) -> int:
        """Count viharanga records"""
        query = db.query(func.count(Viharanga.vg_id)).filter(
            Viharanga.vg_is_deleted.is_(False)
        )

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Viharanga.vg_code.ilike(term),
                    Viharanga.vg_item.ilike(term),
                )
            )

        return query.scalar() or 0

    def create(
        self,
        db: Session,
        *,
        obj_in: ViharangaCreate,
        actor_id: Optional[str] = None,
    ) -> Viharanga:
        """Create a new viharanga record"""
        db_obj = Viharanga(
            vg_code=obj_in.vg_code,
            vg_item=obj_in.vg_item,
            vg_created_by=actor_id,
            vg_updated_by=actor_id,
            vg_version_number=1,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: Viharanga,
        obj_in: ViharangaUpdate,
        actor_id: Optional[str] = None,
    ) -> Viharanga:
        """Update an existing viharanga record"""
        update_data = obj_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        db_obj.vg_updated_by = actor_id
        db_obj.vg_version_number = (db_obj.vg_version_number or 1) + 1
        db_obj.vg_updated_at = datetime.utcnow()
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(
        self,
        db: Session,
        *,
        db_obj: Viharanga,
        actor_id: Optional[str] = None,
    ) -> Viharanga:
        """Soft delete a viharanga record"""
        db_obj.vg_is_deleted = True
        db_obj.vg_updated_by = actor_id
        db_obj.vg_version_number = (db_obj.vg_version_number or 1) + 1
        db_obj.vg_updated_at = datetime.utcnow()
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def _normalize_code(code: str) -> Optional[str]:
        """Normalize code for comparison"""
        if not code or not isinstance(code, str):
            return None
        normalized = code.strip().upper()
        return normalized if normalized else None


viharanga_repo = ViharangaRepository()
