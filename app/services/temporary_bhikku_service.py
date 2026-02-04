# app/services/temporary_bhikku_service.py
"""
Service layer for Temporary Bhikku
Handles business logic for temporary bhikku records
"""
from typing import Optional, Dict, Any
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
    ) -> Dict[str, Any]:
        """
        Create a new bhikku registration from temporary bhikku data.
        Now saves to bhikku_regist table instead of temporary_bhikku.
        Auto-generates BH number like normal bhikku registration.
        Returns enriched bhikku data with nested objects for foreign keys.
        """
        # Extract district and province from payload if present
        # Handle both direct attributes and dict-like access
        tb_district = None
        tb_province = None
        tb_bname = None
        tb_vihara_name = None
        
        # Try to get from payload attributes
        if hasattr(payload, 'tb_district'):
            tb_district = payload.tb_district
        if hasattr(payload, 'tb_province'):
            tb_province = payload.tb_province
        if hasattr(payload, 'tb_bname'):
            tb_bname = payload.tb_bname
        if hasattr(payload, 'tb_vihara_name'):
            tb_vihara_name = payload.tb_vihara_name
        
        # Validate and lookup province/district codes from database
        province_code = None
        district_code = None
        
        if tb_province:
            # Try to find matching province by name
            from app.models.province import Province
            province = db.query(Province).filter(
                Province.cp_name.ilike(f"%{tb_province}%"),
                Province.cp_is_deleted.is_(False)
            ).first()
            if province:
                province_code = province.cp_code
        
        if tb_district:
            # Try to find matching district by name
            from app.models.district import District
            district = db.query(District).filter(
                District.dd_dname.ilike(f"%{tb_district}%"),
                District.dd_is_deleted.is_(False)
            ).first()
            if district:
                district_code = district.dd_dcode
            
        # Map temporary bhikku fields to bhikku registration fields
        bhikku_data = {
            # Auto-generate br_regn (will be generated in repository if not provided)
            "br_regn": None,
            # Use current date as request date
            "br_reqstdate": date.today(),
            
            # Personal Information - map from temp bhikku fields
            "br_mahananame": tb_bname or payload.tb_name,  # Main bhikku name (prioritize tb_bname)
            "br_gihiname": payload.tb_samanera_name,  # Samanera/lay name
            "br_mobile": payload.tb_contact_number[:10] if payload.tb_contact_number else None,  # Ensure max 10 chars
            "br_fathrsaddrs": payload.tb_address,
            
            # Geographic Information - Use validated codes if found
            "br_district": district_code,
            "br_province": province_code,
            
            # Temple Information
            "br_mahanatemple": None,  # Will only be set if valid vihara code provided (starts with VH)
            
            # Required fields with defaults
            "br_currstat": "ST01",  # Default status: Active (සක්‍රීය)
            "br_parshawaya": "SYM_P01",  # Default parshawa: Syamopali Maha Nikaya - Malwatu
            "br_cat": "CAT03",  # Category: Samanera (Novice Monk) - suitable for temporary registrations
            
            # Remarks - store original temp bhikku data for reference
            # Include temp data that couldn't be validated as FKs
            "br_remarks": (
                f"[TEMP_BHIKKU] Created from temp-bhikku registration. "
                f"ID Number: {payload.tb_id_number or 'N/A'}, "
                f"Vihara: {tb_vihara_name or payload.tb_living_temple or 'N/A'}"
                f"{'' if district_code else f', District (unvalidated): {tb_district}'}"
                f"{'' if province_code else f', Province (unvalidated): {tb_province}'}"
            ),
            
            # Audit fields
            "br_created_by": actor_id,
            "br_updated_by": actor_id,
        }
        
        # Try to use tb_vihara_name first, then tb_living_temple
        # Only set br_mahanatemple if it looks like a valid vihara code (starts with VH)
        vihara_code = tb_vihara_name or payload.tb_living_temple
        if vihara_code:
            vihara_code_clean = vihara_code.strip().upper()
            # Only accept codes that start with VH (valid vihara codes)
            if vihara_code_clean.startswith("VH") and len(vihara_code_clean) >= 4:
                # This looks like a valid vihara code, use it
                bhikku_data["br_mahanatemple"] = vihara_code_clean
            # Otherwise, leave as None - the vihara name is already in remarks
        
        # Create BhikkuCreate schema
        bhikku_create = BhikkuCreate(**bhikku_data)
        
        # Create bhikku using the standard repository
        # This will auto-generate br_regn in format: BH{YEAR}{SEQUENCE}
        created_bhikku = bhikku_repo.create(db, bhikku=bhikku_create)
        
        # Refresh to load relationships
        db.refresh(created_bhikku)
        
        # Import bhikku_service for enrichment
        from app.services.bhikku_service import bhikku_service
        
        # Return enriched bhikku data with nested objects for foreign keys
        return bhikku_service.enrich_bhikku_dict(created_bhikku, db=db)

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
