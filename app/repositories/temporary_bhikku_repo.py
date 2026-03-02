# app/repositories/temporary_bhikku_repo.py
"""
Repository for Temporary Bhikku
Handles data access operations for temporary bhikku records
"""
from typing import Optional
from datetime import datetime

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.temporary_bhikku import TemporaryBhikku
from app.schemas.temporary_bhikku import TemporaryBhikkuCreate, TemporaryBhikkuUpdate


class TemporaryBhikkuRepository:
    """Data access helpers for temporary bhikku records."""

    def get(self, db: Session, tb_id: int) -> Optional[TemporaryBhikku]:
        """Get temporary bhikku by ID"""
        return db.query(TemporaryBhikku).filter(TemporaryBhikku.tb_id == tb_id).first()

    def list(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> list[TemporaryBhikku]:
        """List temporary bhikku records with optional search"""
        query = db.query(TemporaryBhikku)

        # Search filter
        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    TemporaryBhikku.tb_name.ilike(search_term),
                    TemporaryBhikku.tb_id_number.ilike(search_term),
                    TemporaryBhikku.tb_contact_number.ilike(search_term),
                    TemporaryBhikku.tb_samanera_name.ilike(search_term),
                    TemporaryBhikku.tb_living_temple.ilike(search_term),
                )
            )

        # Order by most recent first
        query = query.order_by(TemporaryBhikku.tb_id.desc())

        return query.offset(max(skip, 0)).limit(limit).all()

    def count(
        self,
        db: Session,
        *,
        search: Optional[str] = None,
    ) -> int:
        """Count temporary bhikku records with optional search"""
        query = db.query(TemporaryBhikku)

        # Search filter
        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    TemporaryBhikku.tb_name.ilike(search_term),
                    TemporaryBhikku.tb_id_number.ilike(search_term),
                    TemporaryBhikku.tb_contact_number.ilike(search_term),
                    TemporaryBhikku.tb_samanera_name.ilike(search_term),
                    TemporaryBhikku.tb_living_temple.ilike(search_term),
                )
            )

        return query.count()

    def create(
        self,
        db: Session,
        *,
        payload: TemporaryBhikkuCreate,
        actor_id: Optional[str],
    ) -> TemporaryBhikku:
        """Create a new temporary bhikku record"""
        entity = TemporaryBhikku(
            tb_name=payload.tb_name,
            tb_id_number=payload.tb_id_number,
            tb_contact_number=payload.tb_contact_number,
            tb_samanera_name=payload.tb_samanera_name,
            tb_address=payload.tb_address,
            tb_living_temple=payload.tb_living_temple,
            tb_created_by=actor_id,
            tb_created_at=datetime.utcnow(),
        )

        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def update(
        self,
        db: Session,
        *,
        entity: TemporaryBhikku,
        payload: TemporaryBhikkuUpdate,
        actor_id: Optional[str],
    ) -> TemporaryBhikku:
        """Update an existing temporary bhikku record"""
        update_data = payload.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(entity, field, value)
        
        entity.tb_updated_by = actor_id
        entity.tb_updated_at = datetime.utcnow()

        db.commit()
        db.refresh(entity)
        return entity

    def delete(
        self,
        db: Session,
        *,
        entity: TemporaryBhikku,
    ) -> None:
        """Delete a temporary bhikku record (hard delete)"""
        db.delete(entity)
        db.commit()


# Singleton instance
temporary_bhikku_repo = TemporaryBhikkuRepository()
