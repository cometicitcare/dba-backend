# app/services/temporary_silmatha_service.py
"""
Service layer for Temporary Silmatha
Handles business logic for temporary silmatha records
"""
from typing import Optional

from sqlalchemy.orm import Session

from app.models.temporary_silmatha import TemporarySilmatha
from app.repositories.temporary_silmatha_repo import temporary_silmatha_repo
from app.schemas.temporary_silmatha import TemporarySilmathaCreate, TemporarySilmathaUpdate


class TemporarySilmathaService:
    """Business logic layer for temporary silmatha management."""

    def create_temporary_silmatha(
        self,
        db: Session,
        *,
        payload: TemporarySilmathaCreate,
        actor_id: Optional[str],
    ) -> TemporarySilmatha:
        """Create a new temporary silmatha record"""
        return temporary_silmatha_repo.create(
            db, payload=payload, actor_id=actor_id
        )

    def get_temporary_silmatha(
        self, db: Session, ts_id: int
    ) -> Optional[TemporarySilmatha]:
        """Get temporary silmatha by ID"""
        return temporary_silmatha_repo.get(db, ts_id)

    def list_temporary_silmathas(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> list[TemporarySilmatha]:
        """List temporary silmatha records with optional search"""
        # Ensure valid pagination parameters
        limit = max(1, min(limit, 200))
        skip = max(0, skip)
        
        return temporary_silmatha_repo.list(
            db,
            skip=skip,
            limit=limit,
            search=search,
        )

    def count_temporary_silmathas(
        self,
        db: Session,
        *,
        search: Optional[str] = None,
    ) -> int:
        """Count temporary silmatha records with optional search"""
        return temporary_silmatha_repo.count(
            db,
            search=search,
        )

    def update_temporary_silmatha(
        self,
        db: Session,
        *,
        ts_id: int,
        payload: TemporarySilmathaUpdate,
        actor_id: Optional[str],
    ) -> TemporarySilmatha:
        """Update an existing temporary silmatha record"""
        entity = temporary_silmatha_repo.get(db, ts_id)
        if not entity:
            raise ValueError("Temporary silmatha record not found.")
        
        return temporary_silmatha_repo.update(
            db, entity=entity, payload=payload, actor_id=actor_id
        )

    def delete_temporary_silmatha(
        self,
        db: Session,
        *,
        ts_id: int,
    ) -> None:
        """Delete a temporary silmatha record"""
        entity = temporary_silmatha_repo.get(db, ts_id)
        if not entity:
            raise ValueError("Temporary silmatha record not found.")
        
        temporary_silmatha_repo.delete(db, entity=entity)


# Singleton instance
temporary_silmatha_service = TemporarySilmathaService()
