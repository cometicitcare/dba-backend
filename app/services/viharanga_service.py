# app/services/viharanga_service.py
from __future__ import annotations

from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.viharanga import Viharanga
from app.repositories.viharanga_repo import viharanga_repo
from app.schemas.viharanga import ViharangaCreate, ViharangaUpdate


class ViharangaService:
    """Business logic and validation helpers for viharanga records."""

    def get_viharanga(self, db: Session, vg_id: Optional[int] = None, vg_code: Optional[str] = None) -> Optional[Viharanga]:
        """Get a single viharanga record by ID or code"""
        if vg_id is not None:
            return viharanga_repo.get(db, vg_id)
        if vg_code:
            return viharanga_repo.get_by_code(db, vg_code)
        return None

    def list_viharangas(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
    ) -> List[Viharanga]:
        """List viharanga records with pagination and search"""
        return viharanga_repo.list(db, skip=skip, limit=limit, search=search)

    def count_viharangas(
        self,
        db: Session,
        search: Optional[str] = None,
    ) -> int:
        """Count viharanga records"""
        return viharanga_repo.count(db, search=search)

    def create_viharanga(
        self,
        db: Session,
        payload: ViharangaCreate,
        actor_id: Optional[str] = None,
    ) -> Viharanga:
        """Create a new viharanga record"""
        # Validate that vg_code is unique
        existing = viharanga_repo.get_by_code(db, payload.vg_code)
        if existing:
            raise ValueError(f"Viharanga with code '{payload.vg_code}' already exists")

        return viharanga_repo.create(db, obj_in=payload, actor_id=actor_id)

    def update_viharanga(
        self,
        db: Session,
        vg_id: Optional[int] = None,
        vg_code: Optional[str] = None,
        payload: Optional[ViharangaUpdate] = None,
        actor_id: Optional[str] = None,
    ) -> Viharanga:
        """Update an existing viharanga record"""
        if payload is None:
            raise ValueError("Update payload is required")

        # Get the viharanga record
        db_viharanga = self.get_viharanga(db, vg_id=vg_id, vg_code=vg_code)
        if not db_viharanga:
            raise ValueError("Viharanga not found")

        # If updating the code, validate uniqueness
        if payload.vg_code and payload.vg_code != db_viharanga.vg_code:
            existing = viharanga_repo.get_by_code(db, payload.vg_code)
            if existing:
                raise ValueError(f"Viharanga with code '{payload.vg_code}' already exists")

        return viharanga_repo.update(db, db_obj=db_viharanga, obj_in=payload, actor_id=actor_id)

    def delete_viharanga(
        self,
        db: Session,
        vg_id: Optional[int] = None,
        vg_code: Optional[str] = None,
        actor_id: Optional[str] = None,
    ) -> Viharanga:
        """Delete (soft delete) a viharanga record"""
        db_viharanga = self.get_viharanga(db, vg_id=vg_id, vg_code=vg_code)
        if not db_viharanga:
            raise ValueError("Viharanga not found")

        return viharanga_repo.delete(db, db_obj=db_viharanga, actor_id=actor_id)


viharanga_service = ViharangaService()
