# app/services/temporary_bhikku_service.py
"""
Service layer for Temporary Bhikku
Handles business logic for temporary bhikku records
"""
from typing import Optional

from sqlalchemy.orm import Session

from app.models.temporary_bhikku import TemporaryBhikku
from app.repositories.temporary_bhikku_repo import temporary_bhikku_repo
from app.schemas.temporary_bhikku import TemporaryBhikkuCreate, TemporaryBhikkuUpdate


class TemporaryBhikkuService:
    """Business logic layer for temporary bhikku management."""

    def create_temporary_bhikku(
        self,
        db: Session,
        *,
        payload: TemporaryBhikkuCreate,
        actor_id: Optional[str],
    ) -> TemporaryBhikku:
        """Create a new temporary bhikku record"""
        return temporary_bhikku_repo.create(
            db, payload=payload, actor_id=actor_id
        )

    def get_temporary_bhikku(
        self, db: Session, tb_id: int
    ) -> Optional[TemporaryBhikku]:
        """Get temporary bhikku by ID"""
        return temporary_bhikku_repo.get(db, tb_id)

    def list_temporary_bhikkus(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> list[TemporaryBhikku]:
        """List temporary bhikku records with optional search"""
        # Ensure valid pagination parameters
        limit = max(1, min(limit, 200))
        skip = max(0, skip)
        
        return temporary_bhikku_repo.list(
            db,
            skip=skip,
            limit=limit,
            search=search,
        )

    def count_temporary_bhikkus(
        self,
        db: Session,
        *,
        search: Optional[str] = None,
    ) -> int:
        """Count temporary bhikku records with optional search"""
        return temporary_bhikku_repo.count(
            db,
            search=search,
        )

    def update_temporary_bhikku(
        self,
        db: Session,
        *,
        tb_id: int,
        payload: TemporaryBhikkuUpdate,
        actor_id: Optional[str],
    ) -> TemporaryBhikku:
        """Update an existing temporary bhikku record"""
        entity = temporary_bhikku_repo.get(db, tb_id)
        if not entity:
            raise ValueError("Temporary bhikku record not found.")
        
        return temporary_bhikku_repo.update(
            db, entity=entity, payload=payload, actor_id=actor_id
        )

    def delete_temporary_bhikku(
        self, db: Session, *, tb_id: int
    ) -> None:
        """Delete a temporary bhikku record"""
        entity = temporary_bhikku_repo.get(db, tb_id)
        if not entity:
            raise ValueError("Temporary bhikku record not found.")
        
        temporary_bhikku_repo.delete(db, entity=entity)


# Singleton instance
temporary_bhikku_service = TemporaryBhikkuService()
