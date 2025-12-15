# app/services/direct_bhikku_high_service.py
"""
Service layer for Direct High Bhikku Registration
Handles business logic, workflow transitions, and file uploads
"""
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.models.direct_bhikku_high import DirectBhikkuHigh
from app.repositories.direct_bhikku_high_repo import direct_bhikku_high_repo
from app.schemas.direct_bhikku_high import DirectBhikkuHighCreate, DirectBhikkuHighUpdate


class DirectBhikkuHighService:
    """Business logic layer for direct high bhikku registration."""

    def create_direct_bhikku_high(
        self,
        db: Session,
        *,
        payload: DirectBhikkuHighCreate,
        actor_id: Optional[str],
        current_user=None,
    ) -> DirectBhikkuHigh:
        """Create a new direct high bhikku record"""
        # Create the record with district tracking
        entity = direct_bhikku_high_repo.create(
            db, payload=payload, actor_id=actor_id, current_user=current_user
        )
        
        return entity

    def get_direct_bhikku_high(
        self, db: Session, dbh_id: int
    ) -> Optional[DirectBhikkuHigh]:
        """Get direct high bhikku by ID"""
        return direct_bhikku_high_repo.get(db, dbh_id)

    def get_direct_bhikku_high_by_regn(
        self, db: Session, dbh_regn: str
    ) -> Optional[DirectBhikkuHigh]:
        """Get direct high bhikku by registration number"""
        return direct_bhikku_high_repo.get_by_regn(db, dbh_regn)

    def list_direct_bhikku_highs(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        province: Optional[str] = None,
        district: Optional[str] = None,
        divisional_secretariat: Optional[str] = None,
        gn_division: Optional[str] = None,
        parshawaya: Optional[str] = None,
        status: Optional[str] = None,
        workflow_status: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        current_user=None,
    ) -> list[DirectBhikkuHigh]:
        """List direct high bhikku records with filters"""
        limit = max(1, min(limit, 200))
        skip = max(0, skip)
        
        return direct_bhikku_high_repo.list(
            db,
            skip=skip,
            limit=limit,
            search=search,
            province=province,
            district=district,
            divisional_secretariat=divisional_secretariat,
            gn_division=gn_division,
            parshawaya=parshawaya,
            status=status,
            workflow_status=workflow_status,
            date_from=date_from,
            date_to=date_to,
            current_user=current_user,
        )

    def count_direct_bhikku_highs(
        self,
        db: Session,
        *,
        search: Optional[str] = None,
        province: Optional[str] = None,
        district: Optional[str] = None,
        divisional_secretariat: Optional[str] = None,
        gn_division: Optional[str] = None,
        parshawaya: Optional[str] = None,
        status: Optional[str] = None,
        workflow_status: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        current_user=None,
    ) -> int:
        """Count direct high bhikku records with filters"""
        return direct_bhikku_high_repo.count(
            db,
            search=search,
            province=province,
            district=district,
            divisional_secretariat=divisional_secretariat,
            gn_division=gn_division,
            parshawaya=parshawaya,
            status=status,
            workflow_status=workflow_status,
            date_from=date_from,
            date_to=date_to,
            current_user=current_user,
        )

    def update_direct_bhikku_high(
        self,
        db: Session,
        *,
        dbh_id: int,
        payload: DirectBhikkuHighUpdate,
        actor_id: Optional[str],
    ) -> DirectBhikkuHigh:
        """Update an existing direct high bhikku record"""
        entity = direct_bhikku_high_repo.get(db, dbh_id)
        if not entity:
            raise ValueError("Direct high bhikku record not found.")
        
        return direct_bhikku_high_repo.update(
            db, entity=entity, payload=payload, actor_id=actor_id
        )

    def delete_direct_bhikku_high(
        self, db: Session, *, dbh_id: int, actor_id: Optional[str]
    ) -> None:
        """Soft delete a direct high bhikku record"""
        entity = direct_bhikku_high_repo.get(db, dbh_id)
        if not entity:
            raise ValueError("Direct high bhikku record not found.")
        
        direct_bhikku_high_repo.delete(db, entity=entity, actor_id=actor_id)

    # ==================== WORKFLOW METHODS ====================
    
    def approve_direct_bhikku_high(
        self,
        db: Session,
        *,
        dbh_id: int,
        actor_id: Optional[str],
    ) -> DirectBhikkuHigh:
        """
        Approve a direct high bhikku registration.
        Transitions: PEND-APPROVAL → COMPLETED
        """
        entity = direct_bhikku_high_repo.get(db, dbh_id)
        if not entity:
            raise ValueError("Direct high bhikku record not found.")
        
        if entity.dbh_workflow_status != "PEND-APPROVAL":
            raise ValueError(
                f"Cannot approve record with workflow status: {entity.dbh_workflow_status}. "
                "Must be PEND-APPROVAL."
            )
        
        # Update workflow fields
        entity.dbh_workflow_status = "COMPLETED"
        entity.dbh_approval_status = "APPROVED"
        entity.dbh_approved_by = actor_id
        entity.dbh_approved_at = datetime.utcnow()
        entity.dbh_updated_by = actor_id
        entity.dbh_updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(entity)
        return entity

    def reject_direct_bhikku_high(
        self,
        db: Session,
        *,
        dbh_id: int,
        actor_id: Optional[str],
        rejection_reason: Optional[str] = None,
    ) -> DirectBhikkuHigh:
        """
        Reject a direct high bhikku registration.
        Transitions: PEND-APPROVAL → REJECTED
        """
        entity = direct_bhikku_high_repo.get(db, dbh_id)
        if not entity:
            raise ValueError("Direct high bhikku record not found.")
        
        if entity.dbh_workflow_status != "PEND-APPROVAL":
            raise ValueError(
                f"Cannot reject record with workflow status: {entity.dbh_workflow_status}. "
                "Must be PEND-APPROVAL."
            )
        
        # Update workflow fields
        entity.dbh_workflow_status = "REJECTED"
        entity.dbh_approval_status = "REJECTED"
        entity.dbh_rejected_by = actor_id
        entity.dbh_rejected_at = datetime.utcnow()
        entity.dbh_rejection_reason = rejection_reason
        entity.dbh_updated_by = actor_id
        entity.dbh_updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(entity)
        return entity

    def mark_printed(
        self,
        db: Session,
        *,
        dbh_id: int,
        actor_id: Optional[str],
    ) -> DirectBhikkuHigh:
        """
        Mark certificate as printed.
        Transitions: PENDING → PRINTED
        """
        entity = direct_bhikku_high_repo.get(db, dbh_id)
        if not entity:
            raise ValueError("Direct high bhikku record not found.")
        
        if entity.dbh_workflow_status != "PENDING":
            raise ValueError(
                f"Cannot mark as printed record with workflow status: {entity.dbh_workflow_status}. "
                "Must be PENDING."
            )
        
        # Update workflow fields
        entity.dbh_workflow_status = "PRINTED"
        entity.dbh_printed_by = actor_id
        entity.dbh_printed_at = datetime.utcnow()
        entity.dbh_updated_by = actor_id
        entity.dbh_updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(entity)
        return entity

    def mark_scanned(
        self,
        db: Session,
        *,
        dbh_id: int,
        actor_id: Optional[str],
    ) -> DirectBhikkuHigh:
        """
        Mark certificate as scanned.
        Transitions: PRINTED → PEND-APPROVAL
        """
        entity = direct_bhikku_high_repo.get(db, dbh_id)
        if not entity:
            raise ValueError("Direct high bhikku record not found.")
        
        if entity.dbh_workflow_status != "PRINTED":
            raise ValueError(
                f"Cannot mark as scanned record with workflow status: {entity.dbh_workflow_status}. "
                "Must be PRINTED."
            )
        
        # Update workflow fields
        entity.dbh_workflow_status = "PEND-APPROVAL"
        entity.dbh_scanned_by = actor_id
        entity.dbh_scanned_at = datetime.utcnow()
        entity.dbh_updated_by = actor_id
        entity.dbh_updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(entity)
        return entity

    async def upload_scanned_document(
        self,
        db: Session,
        *,
        dbh_id: int,
        file: UploadFile,
        actor_id: Optional[str],
    ) -> DirectBhikkuHigh:
        """
        Upload a scanned document for a direct high bhikku record.
        AUTO-TRANSITIONS: PRINTED → PEND-APPROVAL when document is uploaded.
        
        Args:
            db: Database session
            dbh_id: Direct high bhikku ID
            file: Uploaded file (PDF, JPG, PNG - max 5MB)
            actor_id: User ID performing the upload
            
        Returns:
            Updated DirectBhikkuHigh instance with file path stored
            
        Raises:
            ValueError: If record not found or invalid workflow status
        """
        from pathlib import Path
        from app.utils.file_storage import file_storage_service
        
        # Get the record
        entity = direct_bhikku_high_repo.get(db, dbh_id)
        if not entity:
            raise ValueError(f"Direct high bhikku record with ID '{dbh_id}' not found.")
        
        if entity.dbh_workflow_status != "PRINTED":
            raise ValueError(
                f"Cannot upload document for record with workflow status: {entity.dbh_workflow_status}. "
                "Must be PRINTED."
            )
        
        # Archive old file with version suffix if exists
        if entity.dbh_scanned_document_path:
            old_file_path = entity.dbh_scanned_document_path
            
            # Remove leading /storage/ if present
            clean_path = old_file_path
            if clean_path.startswith("/storage/"):
                clean_path = clean_path[9:]
            
            # Parse the old file path to add version suffix
            path_obj = Path(clean_path)
            file_dir = path_obj.parent
            file_stem = path_obj.stem
            file_ext = path_obj.suffix
            
            # Determine next version number
            storage_dir = Path("app/storage") / file_dir
            max_version = 0
            
            if storage_dir.exists():
                for existing_file in storage_dir.glob("*_v*" + file_ext):
                    version_match = existing_file.stem.rsplit("_v", 1)
                    if len(version_match) == 2 and version_match[1].isdigit():
                        version_num = int(version_match[1])
                        max_version = max(max_version, version_num)
            
            # Use next version number
            next_version = max_version + 1
            versioned_name = f"{file_stem}_v{next_version}{file_ext}"
            versioned_relative_path = str(file_dir / versioned_name)
            
            # Rename the old file
            try:
                file_storage_service.rename_file(old_file_path, versioned_relative_path)
            except Exception as e:
                print(f"Warning: Could not rename old file {old_file_path}: {e}")
        
        # Save new file
        # File will be stored at: app/storage/direct_bhikku_high/<year>/<month>/<day>/<dbh_regn>/scanned_document_*.*
        relative_path, _ = await file_storage_service.save_file(
            file,
            entity.dbh_regn,
            "scanned_document",
            subdirectory="direct_bhikku_high"
        )
        
        # Update the record with file path
        entity.dbh_scanned_document_path = relative_path
        entity.dbh_updated_by = actor_id
        entity.dbh_updated_at = datetime.utcnow()
        
        # AUTO-TRANSITION workflow status from PRINTED to PEND-APPROVAL
        entity.dbh_workflow_status = "PEND-APPROVAL"
        entity.dbh_scanned_by = actor_id
        entity.dbh_scanned_at = datetime.utcnow()
        
        db.commit()
        db.refresh(entity)
        
        return entity

    def enrich_direct_bhikku_high_dict(self, entity: DirectBhikkuHigh, db: Session = None) -> dict:
        """Transform DirectBhikkuHigh model to dictionary with all foreign key relationships as nested objects"""
        from app.schemas.direct_bhikku_high import DirectBhikkuHighOut
        
        # Convert model to dict using the schema
        entity_dict = DirectBhikkuHighOut.model_validate(entity).model_dump()
        
        # Geographic relationships
        if entity.province_rel:
            entity_dict["dbh_province"] = {
                "cp_code": entity.province_rel.cp_code,
                "cp_name": entity.province_rel.cp_name
            }
        
        if entity.district_rel:
            entity_dict["dbh_district"] = {
                "dd_dcode": entity.district_rel.dd_dcode,
                "dd_dname": entity.district_rel.dd_dname
            }
        
        if entity.division_rel:
            entity_dict["dbh_division"] = {
                "dv_dvcode": entity.division_rel.dv_dvcode,
                "dv_dvname": entity.division_rel.dv_dvname
            }
        
        if entity.gndiv_rel:
            entity_dict["dbh_gndiv"] = {
                "gn_gnc": entity.gndiv_rel.gn_gnc,
                "gn_gnname": entity.gndiv_rel.gn_gnname
            }
        
        # Status and administrative relationships
        if entity.status_rel:
            entity_dict["dbh_currstat"] = {
                "st_statcd": entity.status_rel.st_statcd,
                "st_descr": entity.status_rel.st_descr
            }
        
        if entity.parshawaya_rel:
            entity_dict["dbh_parshawaya"] = {
                "code": entity.parshawaya_rel.pr_prn,
                "name": entity.parshawaya_rel.pr_pname
            }
        
        if entity.category_rel:
            entity_dict["dbh_cat"] = {
                "cc_code": entity.category_rel.cc_code,
                "cc_catogry": entity.category_rel.cc_catogry
            }
        
        if entity.nikaya_rel:
            entity_dict["dbh_nikaya"] = {
                "code": entity.nikaya_rel.nk_nkn,
                "name": entity.nikaya_rel.nk_nname
            }
        
        # Temple/Vihara relationships
        if entity.livtemple_rel:
            entity_dict["dbh_livtemple"] = {
                "vh_trn": entity.livtemple_rel.vh_trn,
                "vh_vname": entity.livtemple_rel.vh_vname
            }
        
        if entity.mahanatemple_rel:
            entity_dict["dbh_mahanatemple"] = {
                "vh_trn": entity.mahanatemple_rel.vh_trn,
                "vh_vname": entity.mahanatemple_rel.vh_vname
            }
        
        if entity.robing_tutor_residence_rel:
            entity_dict["dbh_robing_tutor_residence"] = {
                "vh_trn": entity.robing_tutor_residence_rel.vh_trn,
                "vh_vname": entity.robing_tutor_residence_rel.vh_vname
            }
        
        if entity.robing_after_residence_temple_rel:
            entity_dict["dbh_robing_after_residence_temple"] = {
                "vh_trn": entity.robing_after_residence_temple_rel.vh_trn,
                "vh_vname": entity.robing_after_residence_temple_rel.vh_vname
            }
        
        if entity.residence_higher_ordination_rel:
            entity_dict["dbh_residence_higher_ordination_trn"] = {
                "vh_trn": entity.residence_higher_ordination_rel.vh_trn,
                "vh_vname": entity.residence_higher_ordination_rel.vh_vname
            }
        
        if entity.residence_permanent_rel:
            entity_dict["dbh_residence_permanent_trn"] = {
                "vh_trn": entity.residence_permanent_rel.vh_trn,
                "vh_vname": entity.residence_permanent_rel.vh_vname
            }
        
        # Bhikku relationships
        if entity.mahanaacharyacd_rel:
            entity_dict["dbh_mahanaacharyacd"] = {
                "br_regn": entity.mahanaacharyacd_rel.br_regn,
                "br_mahananame": entity.mahanaacharyacd_rel.br_mahananame or "",
                "br_upasampadaname": ""
            }
        
        if entity.viharadhipathi_rel:
            entity_dict["dbh_viharadhipathi"] = {
                "br_regn": entity.viharadhipathi_rel.br_regn,
                "br_mahananame": entity.viharadhipathi_rel.br_mahananame or "",
                "br_upasampadaname": ""
            }
        
        return entity_dict


# Singleton instance
direct_bhikku_high_service = DirectBhikkuHighService()
