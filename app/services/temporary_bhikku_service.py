# app/services/temporary_bhikku_service.py
"""
Service layer for Temporary Bhikku
Handles business logic for temporary bhikku records
"""
from typing import Optional
from datetime import date

from sqlalchemy.orm import Session

from app.models.temporary_bhikku import TemporaryBhikku
from app.models.bhikku import Bhikku
from app.repositories.temporary_bhikku_repo import temporary_bhikku_repo
from app.schemas.temporary_bhikku import TemporaryBhikkuCreate, TemporaryBhikkuUpdate
from app.schemas.bhikku import BhikkuCreate
from app.repositories.bhikku_repo import bhikku_repo


class TemporaryBhikkuService:
    """Business logic layer for temporary bhikku management."""

    def create_temporary_bhikku(
        self,
        db: Session,
        *,
        payload: TemporaryBhikkuCreate,
        actor_id: Optional[str],
    ) -> Bhikku:
        """
        Create a new bhikku registration from temporary bhikku data.
        Now saves to bhikku_regist table instead of temporary_bhikku.
        Auto-generates BH number like normal bhikku registration.
        """
        # Map temporary bhikku fields to bhikku registration fields
        bhikku_data = {
            # Auto-generate br_regn (will be generated in repository if not provided)
            "br_regn": None,
            # Use current date as request date
            "br_reqstdate": date.today(),
            
            # Personal Information - map from temp bhikku fields
            "br_mahananame": payload.tb_name,  # Main bhikku name
            "br_gihiname": payload.tb_samanera_name,  # Samanera/lay name
            "br_mobile": payload.tb_contact_number[:10] if payload.tb_contact_number else None,  # Ensure max 10 chars
            "br_fathrsaddrs": payload.tb_address,
            
            # Temple Information
            "br_mahanatemple": None,  # Will be set from tb_living_temple if it's a valid vihara code
            
            # Required fields with defaults
            "br_currstat": "BKR",  # Default status for newly created bhikku
            "br_parshawaya": "N/A",  # Not applicable for temporary registrations
            "br_cat": "TEMP",  # Category flag to identify temp bhikku registrations
            
            # Remarks - store original temp bhikku data for reference
            "br_remarks": f"[TEMP_BHIKKU] Created from temp-bhikku registration. ID Number: {payload.tb_id_number or 'N/A'}, Living Temple: {payload.tb_living_temple or 'N/A'}",
            
            # Audit fields
            "br_created_by": actor_id,
            "br_updated_by": actor_id,
        }
        
        # If tb_living_temple looks like a vihara code (e.g., VH001234), use it
        # Otherwise, leave as None and it will be stored in remarks
        if payload.tb_living_temple:
            # Check if it looks like a valid vihara code format
            living_temple = payload.tb_living_temple.strip()
            if living_temple and not living_temple.startswith("TEMP-"):
                # Assume it's a valid vihara code
                bhikku_data["br_mahanatemple"] = living_temple
        
        # Create BhikkuCreate schema
        bhikku_create = BhikkuCreate(**bhikku_data)
        
        # Create bhikku using the standard repository
        # This will auto-generate br_regn in format: BH{YEAR}{SEQUENCE}
        created_bhikku = bhikku_repo.create(db, bhikku=bhikku_create)
        
        return created_bhikku

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
