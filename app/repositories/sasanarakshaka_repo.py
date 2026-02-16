# app/repositories/sasanarakshaka_repo.py
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.sasanarakshaka import SasanarakshakaBalaMandalaya
from app.schemas.sasanarakshaka import SasanarakshakaBalaMandalayaCreate, SasanarakshakaBalaMandalayaUpdate


class SasanarakshakaBalaMandalayaRepository:
    """
    Data access helper for the `cmm_sasanarbm` table.
    """

    def get_by_id(self, db: Session, sr_id: int) -> Optional[SasanarakshakaBalaMandalaya]:
        """Get a single record by ID"""
        return (
            db.query(SasanarakshakaBalaMandalaya)
            .filter(
                SasanarakshakaBalaMandalaya.sr_id == sr_id,
                SasanarakshakaBalaMandalaya.sr_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_code(self, db: Session, sr_ssbmcode: str) -> Optional[SasanarakshakaBalaMandalaya]:
        """Get a single record by code"""
        return (
            db.query(SasanarakshakaBalaMandalaya)
            .filter(
                SasanarakshakaBalaMandalaya.sr_ssbmcode == sr_ssbmcode,
                SasanarakshakaBalaMandalaya.sr_is_deleted.is_(False),
            )
            .first()
        )

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search_key: Optional[str] = None,
        sr_dvcd: Optional[str] = None,
    ) -> tuple[List[SasanarakshakaBalaMandalaya], int]:
        """
        Get paginated list of records with optional search and filters.
        Returns (records, total_count).
        """
        query = db.query(SasanarakshakaBalaMandalaya).filter(
            SasanarakshakaBalaMandalaya.sr_is_deleted.is_(False)
        )

        # Apply search filter
        if search_key and search_key.strip():
            search_pattern = f"%{search_key.strip()}%"
            query = query.filter(
                or_(
                    SasanarakshakaBalaMandalaya.sr_ssbmcode.ilike(search_pattern),
                    SasanarakshakaBalaMandalaya.sr_ssbname.ilike(search_pattern),
                    SasanarakshakaBalaMandalaya.sr_dvcd.ilike(search_pattern),
                    SasanarakshakaBalaMandalaya.sr_sbmnayakahimi.ilike(search_pattern),
                )
            )

        # Apply divisional secretariat filter
        if sr_dvcd:
            query = query.filter(SasanarakshakaBalaMandalaya.sr_dvcd == sr_dvcd)

        # Get total count
        total = query.count()

        # Apply pagination and ordering
        records = (
            query.order_by(SasanarakshakaBalaMandalaya.sr_id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return records, total

    def get_by_divisional_secretariat(
        self,
        db: Session,
        sr_dvcd: str,
    ) -> List[SasanarakshakaBalaMandalaya]:
        """
        Get all Sasanarakshaka records for a given divisional secretariat code.
        Returns all records (no pagination) with relationships eagerly loaded.
        """
        return (
            db.query(SasanarakshakaBalaMandalaya)
            .filter(
                SasanarakshakaBalaMandalaya.sr_dvcd == sr_dvcd,
                SasanarakshakaBalaMandalaya.sr_is_deleted.is_(False),
            )
            .order_by(SasanarakshakaBalaMandalaya.sr_id.asc())
            .all()
        )

    def create(
        self, 
        db: Session, 
        *, 
        obj_in: SasanarakshakaBalaMandalayaCreate,
        created_by: Optional[str] = None
    ) -> SasanarakshakaBalaMandalaya:
        """Create a new record"""
        db_obj = SasanarakshakaBalaMandalaya(
            **obj_in.model_dump(),
            sr_created_by=created_by,
            sr_updated_by=created_by,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: SasanarakshakaBalaMandalaya,
        obj_in: SasanarakshakaBalaMandalayaUpdate,
        updated_by: Optional[str] = None
    ) -> SasanarakshakaBalaMandalaya:
        """Update an existing record"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        
        if updated_by:
            db_obj.sr_updated_by = updated_by
        
        # Increment version number
        if db_obj.sr_version_number:
            db_obj.sr_version_number += 1
        else:
            db_obj.sr_version_number = 1
        
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(
        self, 
        db: Session, 
        *, 
        sr_id: int,
        deleted_by: Optional[str] = None
    ) -> Optional[SasanarakshakaBalaMandalaya]:
        """Soft delete a record"""
        db_obj = self.get_by_id(db, sr_id)
        if db_obj:
            db_obj.sr_is_deleted = True
            db_obj.sr_updated_by = deleted_by
            db.commit()
            db.refresh(db_obj)
        return db_obj


# Create a singleton instance
sasanarakshaka_repo = SasanarakshakaBalaMandalayaRepository()
