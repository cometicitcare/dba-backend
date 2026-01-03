# app/repositories/temporary_devala_repo.py
"""
Repository layer for Temporary Devala
Handles database operations for temporary devala records
"""
from typing import Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.temporary_devala import TemporaryDevala
from app.schemas.temporary_devala import TemporaryDevalaCreate, TemporaryDevalaUpdate


class TemporaryDevalaRepository:
    """Database operations for TemporaryDevala model."""

    def create(
        self,
        db: Session,
        *,
        payload: TemporaryDevalaCreate,
        actor_id: Optional[str],
    ) -> TemporaryDevala:
        """Create a new temporary devala record"""
        entity = TemporaryDevala(
            td_name=payload.td_name,
            td_address=payload.td_address,
            td_contact_number=payload.td_contact_number,
            td_district=payload.td_district,
            td_province=payload.td_province,
            td_basnayake_nilame_name=payload.td_basnayake_nilame_name,
            td_created_by=actor_id,
        )
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def get(self, db: Session, td_id: int) -> Optional[TemporaryDevala]:
        """Get temporary devala by ID"""
        return db.query(TemporaryDevala).filter(
            TemporaryDevala.td_id == td_id
        ).first()

    def list(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> list[TemporaryDevala]:
        """List temporary devala records with optional search"""
        query = db.query(TemporaryDevala)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    TemporaryDevala.td_name.ilike(search_pattern),
                    TemporaryDevala.td_address.ilike(search_pattern),
                    TemporaryDevala.td_contact_number.ilike(search_pattern),
                    TemporaryDevala.td_district.ilike(search_pattern),
                    TemporaryDevala.td_basnayake_nilame_name.ilike(search_pattern),
                )
            )
        
        return query.order_by(TemporaryDevala.td_id.desc()).offset(skip).limit(limit).all()

    def count(
        self,
        db: Session,
        *,
        search: Optional[str] = None,
    ) -> int:
        """Count temporary devala records with optional search"""
        query = db.query(TemporaryDevala)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    TemporaryDevala.td_name.ilike(search_pattern),
                    TemporaryDevala.td_address.ilike(search_pattern),
                    TemporaryDevala.td_contact_number.ilike(search_pattern),
                    TemporaryDevala.td_district.ilike(search_pattern),
                    TemporaryDevala.td_basnayake_nilame_name.ilike(search_pattern),
                )
            )
        
        return query.count()

    def update(
        self,
        db: Session,
        *,
        entity: TemporaryDevala,
        payload: TemporaryDevalaUpdate,
        actor_id: Optional[str],
    ) -> TemporaryDevala:
        """Update an existing temporary devala record"""
        update_data = payload.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(entity, field, value)
        
        entity.td_updated_by = actor_id
        db.commit()
        db.refresh(entity)
        return entity

    def delete(self, db: Session, *, entity: TemporaryDevala) -> None:
        """Delete a temporary devala record"""
        db.delete(entity)
        db.commit()


# Singleton instance
temporary_devala_repo = TemporaryDevalaRepository()
