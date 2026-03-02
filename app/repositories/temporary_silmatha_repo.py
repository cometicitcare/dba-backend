# app/repositories/temporary_silmatha_repo.py
"""
Repository layer for Temporary Silmatha
Handles database operations for temporary silmatha records
"""
from typing import Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.temporary_silmatha import TemporarySilmatha
from app.schemas.temporary_silmatha import TemporarySilmathaCreate, TemporarySilmathaUpdate


class TemporarySilmathaRepository:
    """Database operations for TemporarySilmatha model."""

    def create(
        self,
        db: Session,
        *,
        payload: TemporarySilmathaCreate,
        actor_id: Optional[str],
    ) -> TemporarySilmatha:
        """Create a new temporary silmatha record"""
        entity = TemporarySilmatha(
            ts_name=payload.ts_name,
            ts_nic=payload.ts_nic,
            ts_contact_number=payload.ts_contact_number,
            ts_address=payload.ts_address,
            ts_district=payload.ts_district,
            ts_province=payload.ts_province,
            ts_arama_name=payload.ts_arama_name,
            ts_ordained_date=payload.ts_ordained_date,
            ts_created_by=actor_id,
        )
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def get(self, db: Session, ts_id: int) -> Optional[TemporarySilmatha]:
        """Get temporary silmatha by ID"""
        return db.query(TemporarySilmatha).filter(
            TemporarySilmatha.ts_id == ts_id
        ).first()

    def list(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> list[TemporarySilmatha]:
        """List temporary silmatha records with optional search"""
        query = db.query(TemporarySilmatha)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    TemporarySilmatha.ts_name.ilike(search_pattern),
                    TemporarySilmatha.ts_nic.ilike(search_pattern),
                    TemporarySilmatha.ts_contact_number.ilike(search_pattern),
                    TemporarySilmatha.ts_address.ilike(search_pattern),
                    TemporarySilmatha.ts_district.ilike(search_pattern),
                    TemporarySilmatha.ts_arama_name.ilike(search_pattern),
                )
            )
        
        return query.order_by(TemporarySilmatha.ts_id.desc()).offset(skip).limit(limit).all()

    def count(
        self,
        db: Session,
        *,
        search: Optional[str] = None,
    ) -> int:
        """Count temporary silmatha records with optional search"""
        query = db.query(TemporarySilmatha)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    TemporarySilmatha.ts_name.ilike(search_pattern),
                    TemporarySilmatha.ts_nic.ilike(search_pattern),
                    TemporarySilmatha.ts_contact_number.ilike(search_pattern),
                    TemporarySilmatha.ts_address.ilike(search_pattern),
                    TemporarySilmatha.ts_district.ilike(search_pattern),
                    TemporarySilmatha.ts_arama_name.ilike(search_pattern),
                )
            )
        
        return query.count()

    def update(
        self,
        db: Session,
        *,
        entity: TemporarySilmatha,
        payload: TemporarySilmathaUpdate,
        actor_id: Optional[str],
    ) -> TemporarySilmatha:
        """Update an existing temporary silmatha record"""
        update_data = payload.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(entity, field, value)
        
        entity.ts_updated_by = actor_id
        db.commit()
        db.refresh(entity)
        return entity

    def delete(self, db: Session, *, entity: TemporarySilmatha) -> None:
        """Delete a temporary silmatha record"""
        db.delete(entity)
        db.commit()


# Singleton instance
temporary_silmatha_repo = TemporarySilmathaRepository()
