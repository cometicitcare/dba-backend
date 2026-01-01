# app/services/temporary_vihara_service.py
"""
Service layer for Temporary Vihara
Handles business logic for temporary vihara records
"""
from typing import Optional

from sqlalchemy.orm import Session

from app.models.temporary_vihara import TemporaryVihara
from app.repositories.temporary_vihara_repo import temporary_vihara_repo
from app.schemas.temporary_vihara import TemporaryViharaCreate, TemporaryViharaUpdate


class TemporaryViharaService:
    """Business logic layer for temporary vihara management."""

    def create_temporary_vihara(
        self,
        db: Session,
        *,
        payload: TemporaryViharaCreate,
        actor_id: Optional[str],
    ) -> TemporaryVihara:
        """Create a new temporary vihara record"""
        return temporary_vihara_repo.create(
            db, payload=payload, actor_id=actor_id
        )

    def get_temporary_vihara(
        self, db: Session, tv_id: int
    ) -> Optional[TemporaryVihara]:
        """Get temporary vihara by ID"""
        return temporary_vihara_repo.get(db, tv_id)

    def list_temporary_viharas(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> list[TemporaryVihara]:
        """List temporary vihara records with optional search"""
        # Ensure valid pagination parameters
        limit = max(1, min(limit, 200))
        skip = max(0, skip)
        
        return temporary_vihara_repo.list(
            db,
            skip=skip,
            limit=limit,
            search=search,
        )

    def count_temporary_viharas(
        self,
        db: Session,
        *,
        search: Optional[str] = None,
    ) -> int:
        """Count temporary vihara records with optional search"""
        return temporary_vihara_repo.count(
            db,
            search=search,
        )

    def update_temporary_vihara(
        self,
        db: Session,
        *,
        tv_id: int,
        payload: TemporaryViharaUpdate,
        actor_id: Optional[str],
    ) -> TemporaryVihara:
        """Update an existing temporary vihara record"""
        entity = temporary_vihara_repo.get(db, tv_id)
        if not entity:
            raise ValueError("Temporary vihara record not found.")
        
        return temporary_vihara_repo.update(
            db, entity=entity, payload=payload, actor_id=actor_id
        )

    def delete_temporary_vihara(
        self, db: Session, *, tv_id: int
    ) -> None:
        """Delete a temporary vihara record"""
        entity = temporary_vihara_repo.get(db, tv_id)
        if not entity:
            raise ValueError("Temporary vihara record not found.")
        
        temporary_vihara_repo.delete(db, entity=entity)


# Singleton instance
temporary_vihara_service = TemporaryViharaService()
