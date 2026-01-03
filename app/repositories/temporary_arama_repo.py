# app/repositories/temporary_arama_repo.py
"""
Repository layer for Temporary Arama
Handles database operations for temporary arama records
"""
from typing import Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.temporary_arama import TemporaryArama
from app.schemas.temporary_arama import TemporaryAramaCreate, TemporaryAramaUpdate


class TemporaryAramaRepository:
    """Database operations for TemporaryArama model."""

    def create(
        self,
        db: Session,
        *,
        payload: TemporaryAramaCreate,
        actor_id: Optional[str],
    ) -> TemporaryArama:
        """Create a new temporary arama record"""
        entity = TemporaryArama(
            ta_name=payload.ta_name,
            ta_address=payload.ta_address,
            ta_contact_number=payload.ta_contact_number,
            ta_district=payload.ta_district,
            ta_province=payload.ta_province,
            ta_aramadhipathi_name=payload.ta_aramadhipathi_name,
            ta_created_by=actor_id,
        )
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def get(self, db: Session, ta_id: int) -> Optional[TemporaryArama]:
        """Get temporary arama by ID"""
        return db.query(TemporaryArama).filter(
            TemporaryArama.ta_id == ta_id
        ).first()

    def list(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> list[TemporaryArama]:
        """List temporary arama records with optional search"""
        query = db.query(TemporaryArama)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    TemporaryArama.ta_name.ilike(search_pattern),
                    TemporaryArama.ta_address.ilike(search_pattern),
                    TemporaryArama.ta_contact_number.ilike(search_pattern),
                    TemporaryArama.ta_district.ilike(search_pattern),
                    TemporaryArama.ta_aramadhipathi_name.ilike(search_pattern),
                )
            )
        
        return query.order_by(TemporaryArama.ta_id.desc()).offset(skip).limit(limit).all()

    def count(
        self,
        db: Session,
        *,
        search: Optional[str] = None,
    ) -> int:
        """Count temporary arama records with optional search"""
        query = db.query(TemporaryArama)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    TemporaryArama.ta_name.ilike(search_pattern),
                    TemporaryArama.ta_address.ilike(search_pattern),
                    TemporaryArama.ta_contact_number.ilike(search_pattern),
                    TemporaryArama.ta_district.ilike(search_pattern),
                    TemporaryArama.ta_aramadhipathi_name.ilike(search_pattern),
                )
            )
        
        return query.count()

    def update(
        self,
        db: Session,
        *,
        entity: TemporaryArama,
        payload: TemporaryAramaUpdate,
        actor_id: Optional[str],
    ) -> TemporaryArama:
        """Update an existing temporary arama record"""
        update_data = payload.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(entity, field, value)
        
        entity.ta_updated_by = actor_id
        db.commit()
        db.refresh(entity)
        return entity

    def delete(self, db: Session, *, entity: TemporaryArama) -> None:
        """Delete a temporary arama record"""
        db.delete(entity)
        db.commit()


# Singleton instance
temporary_arama_repo = TemporaryAramaRepository()
