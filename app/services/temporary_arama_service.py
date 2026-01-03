# app/services/temporary_arama_service.py
"""
Service layer for Temporary Arama
Handles business logic for temporary arama records
"""
from typing import Optional

from sqlalchemy.orm import Session

from app.models.temporary_arama import TemporaryArama
from app.repositories.temporary_arama_repo import temporary_arama_repo
from app.schemas.temporary_arama import TemporaryAramaCreate, TemporaryAramaUpdate


class TemporaryAramaService:
    """Business logic layer for temporary arama management."""

    def create_temporary_arama(
        self,
        db: Session,
        *,
        payload: TemporaryAramaCreate,
        actor_id: Optional[str],
    ) -> TemporaryArama:
        """Create a new temporary arama record"""
        return temporary_arama_repo.create(
            db, payload=payload, actor_id=actor_id
        )

    def get_temporary_arama(
        self, db: Session, ta_id: int
    ) -> Optional[TemporaryArama]:
        """Get temporary arama by ID"""
        return temporary_arama_repo.get(db, ta_id)

    def list_temporary_aramas(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> list[TemporaryArama]:
        """List temporary arama records with optional search"""
        # Ensure valid pagination parameters
        limit = max(1, min(limit, 200))
        skip = max(0, skip)
        
        return temporary_arama_repo.list(
            db,
            skip=skip,
            limit=limit,
            search=search,
        )

    def count_temporary_aramas(
        self,
        db: Session,
        *,
        search: Optional[str] = None,
    ) -> int:
        """Count temporary arama records with optional search"""
        return temporary_arama_repo.count(
            db,
            search=search,
        )

    def update_temporary_arama(
        self,
        db: Session,
        *,
        ta_id: int,
        payload: TemporaryAramaUpdate,
        actor_id: Optional[str],
    ) -> TemporaryArama:
        """Update an existing temporary arama record"""
        entity = temporary_arama_repo.get(db, ta_id)
        if not entity:
            raise ValueError("Temporary arama record not found.")
        
        return temporary_arama_repo.update(
            db, entity=entity, payload=payload, actor_id=actor_id
        )

    def delete_temporary_arama(
        self,
        db: Session,
        *,
        ta_id: int,
    ) -> None:
        """Delete a temporary arama record"""
        entity = temporary_arama_repo.get(db, ta_id)
        if not entity:
            raise ValueError("Temporary arama record not found.")
        
        temporary_arama_repo.delete(db, entity=entity)


# Singleton instance
temporary_arama_service = TemporaryAramaService()
