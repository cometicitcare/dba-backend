# app/repositories/temporary_vihara_repo.py
"""
Repository layer for Temporary Vihara
Handles database operations for temporary vihara records
"""
from typing import Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.temporary_vihara import TemporaryVihara
from app.schemas.temporary_vihara import TemporaryViharaCreate, TemporaryViharaUpdate


class TemporaryViharaRepository:
    """Database operations for TemporaryVihara model."""

    def create(
        self,
        db: Session,
        *,
        payload: TemporaryViharaCreate,
        actor_id: Optional[str],
    ) -> TemporaryVihara:
        """Create a new temporary vihara record"""
        entity = TemporaryVihara(
            tv_name=payload.tv_name,
            tv_address=payload.tv_address,
            tv_contact_number=payload.tv_contact_number,
            tv_district=payload.tv_district,
            tv_province=payload.tv_province,
            tv_viharadhipathi_name=payload.tv_viharadhipathi_name,
            tv_created_by=actor_id,
        )
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def get(self, db: Session, tv_id: int) -> Optional[TemporaryVihara]:
        """Get temporary vihara by ID"""
        return db.query(TemporaryVihara).filter(
            TemporaryVihara.tv_id == tv_id
        ).first()

    def list(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> list[TemporaryVihara]:
        """List temporary vihara records with optional search"""
        query = db.query(TemporaryVihara)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    TemporaryVihara.tv_name.ilike(search_pattern),
                    TemporaryVihara.tv_address.ilike(search_pattern),
                    TemporaryVihara.tv_contact_number.ilike(search_pattern),
                    TemporaryVihara.tv_district.ilike(search_pattern),
                    TemporaryVihara.tv_viharadhipathi_name.ilike(search_pattern),
                )
            )
        
        return query.order_by(TemporaryVihara.tv_id.desc()).offset(skip).limit(limit).all()

    def count(
        self,
        db: Session,
        *,
        search: Optional[str] = None,
    ) -> int:
        """Count temporary vihara records with optional search"""
        query = db.query(TemporaryVihara)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    TemporaryVihara.tv_name.ilike(search_pattern),
                    TemporaryVihara.tv_address.ilike(search_pattern),
                    TemporaryVihara.tv_contact_number.ilike(search_pattern),
                    TemporaryVihara.tv_district.ilike(search_pattern),
                    TemporaryVihara.tv_viharadhipathi_name.ilike(search_pattern),
                )
            )
        
        return query.count()

    def update(
        self,
        db: Session,
        *,
        entity: TemporaryVihara,
        payload: TemporaryViharaUpdate,
        actor_id: Optional[str],
    ) -> TemporaryVihara:
        """Update an existing temporary vihara record"""
        update_data = payload.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(entity, field, value)
        
        entity.tv_updated_by = actor_id
        db.commit()
        db.refresh(entity)
        return entity

    def delete(self, db: Session, *, entity: TemporaryVihara) -> None:
        """Delete a temporary vihara record"""
        db.delete(entity)
        db.commit()


# Singleton instance
temporary_vihara_repo = TemporaryViharaRepository()
