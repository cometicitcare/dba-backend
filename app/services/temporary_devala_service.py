# app/services/temporary_devala_service.py
"""
Service layer for Temporary Devala
Handles business logic for temporary devala records
"""
from typing import Optional

from sqlalchemy.orm import Session

from app.models.temporary_devala import TemporaryDevala
from app.repositories.temporary_devala_repo import temporary_devala_repo
from app.schemas.temporary_devala import TemporaryDevalaCreate, TemporaryDevalaUpdate


class TemporaryDevalaService:
    """Business logic layer for temporary devala management."""

    def create_temporary_devala(
        self,
        db: Session,
        *,
        payload: TemporaryDevalaCreate,
        actor_id: Optional[str],
    ) -> TemporaryDevala:
        """Create a new temporary devala record"""
        return temporary_devala_repo.create(
            db, payload=payload, actor_id=actor_id
        )

    def get_temporary_devala(
        self, db: Session, td_id: int
    ) -> Optional[TemporaryDevala]:
        """Get temporary devala by ID"""
        return temporary_devala_repo.get(db, td_id)

    def list_temporary_devalas(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> list[TemporaryDevala]:
        """List temporary devala records with optional search"""
        # Ensure valid pagination parameters
        limit = max(1, min(limit, 200))
        skip = max(0, skip)
        
        return temporary_devala_repo.list(
            db,
            skip=skip,
            limit=limit,
            search=search,
        )

    def count_temporary_devalas(
        self,
        db: Session,
        *,
        search: Optional[str] = None,
    ) -> int:
        """Count temporary devala records with optional search"""
        return temporary_devala_repo.count(
            db,
            search=search,
        )

    def update_temporary_devala(
        self,
        db: Session,
        *,
        td_id: int,
        payload: TemporaryDevalaUpdate,
        actor_id: Optional[str],
    ) -> TemporaryDevala:
        """Update an existing temporary devala record"""
        entity = temporary_devala_repo.get(db, td_id)
        if not entity:
            raise ValueError("Temporary devala record not found.")
        
        return temporary_devala_repo.update(
            db, entity=entity, payload=payload, actor_id=actor_id
        )

    def delete_temporary_devala(
        self,
        db: Session,
        *,
        td_id: int,
    ) -> None:
        """Delete a temporary devala record"""
        entity = temporary_devala_repo.get(db, td_id)
        if not entity:
            raise ValueError("Temporary devala record not found.")
        
        temporary_devala_repo.delete(db, entity=entity)


# Singleton instance
temporary_devala_service = TemporaryDevalaService()
