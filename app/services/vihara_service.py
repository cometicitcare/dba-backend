from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import MetaData, Table, inspect, select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app.models.vihara import ViharaData
from app.repositories.vihara_repo import vihara_repo
from app.schemas.vihara import ViharaCreate, ViharaCreatePayload, ViharaUpdate


class ViharaService:
    """
    Business logic layer for vihara data with staged workflow.
    
    Workflow States:
    - S1_PENDING: Stage 1 data saved, waiting for printing
    - S1_PRINTING: Stage 1 form printed, waiting for scan upload
    - S1_PEND_APPROVAL: Stage 1 document uploaded, waiting for approval
    - S1_APPROVED: Stage 1 approved, ready for Stage 2
    - S1_REJECTED: Stage 1 rejected
    - S2_PENDING: Stage 2 data saved, waiting for scan upload
    - S2_PEND_APPROVAL: Stage 2 document uploaded, waiting for approval
    - COMPLETED: Both stages approved, registration complete
    - REJECTED: Final rejection
    """

    def __init__(self) -> None:
        self._fk_targets: Optional[dict[str, tuple[Optional[str], str, str]]] = None

    # =================================================================
    # STAGE ONE METHODS
    # =================================================================
    
    def save_stage_one(
        self, db: Session, *, payload_data: dict, actor_id: Optional[str], vh_id: Optional[int] = None
    ) -> ViharaData:
        """
        Save or create Stage 1: Basic Profile (steps 1–4)
        Creates new record with status S1_PENDING or updates existing.
        """
        from app.schemas.vihara import ViharaCreate
        
        now = datetime.utcnow()
        
        if vh_id:
            # Update existing record - stage one fields only
            entity = vihara_repo.get(db, vh_id)
            if not entity:
                raise ValueError("Vihara record not found.")
            
            # Only allow updates in S1_PENDING or S1_REJECTED status
            if entity.vh_workflow_status not in ["S1_PENDING", "S1_REJECTED", "PENDING"]:
                raise ValueError(f"Cannot update Stage 1 when status is {entity.vh_workflow_status}. Must be S1_PENDING or S1_REJECTED.")
            
            # Validate foreign keys before applying changes
            self._validate_foreign_keys(db, payload_data)
            
            # Only update stage one fields (skip None values to avoid overwriting existing data)
            for key, value in payload_data.items():
                if hasattr(entity, key) and key not in ('vh_id', 'vh_created_at', 'vh_created_by'):
                    setattr(entity, key, value)
            
            entity.vh_updated_by = actor_id
            entity.vh_updated_at = now
            entity.vh_workflow_status = "S1_PENDING"  # Reset to pending on update
            try:
                db.commit()
            except IntegrityError as exc:
                db.rollback()
                raise ValueError("Failed to update Stage 1 due to a database constraint violation. Please check province, district, and GN division values.") from exc
            db.refresh(entity)
            return entity
        else:
            # Create new draft record
            # Validate duplicate vihara: same name + mobile
            vh_vname = payload_data.get("vh_vname")
            vh_mobile = payload_data.get("vh_mobile")
            
            if vh_vname and vh_mobile:
                existing = db.query(ViharaData).filter(
                    ViharaData.vh_vname == vh_vname,
                    ViharaData.vh_mobile == vh_mobile,
                    ViharaData.vh_is_deleted == False
                ).first()
                if existing:
                    raise ValueError(f"A vihara with name '{vh_vname}' and mobile '{vh_mobile}' already exists.")
            
            payload_data["vh_created_by"] = actor_id
            payload_data["vh_updated_by"] = actor_id
            payload_data["vh_created_at"] = now
            payload_data["vh_updated_at"] = now
            payload_data["vh_is_deleted"] = False
            payload_data["vh_version_number"] = 1
            payload_data["vh_workflow_status"] = "S1_PENDING"  # New staged workflow status
            payload_data.pop("vh_trn", None)
            payload_data.pop("vh_id", None)
            
            # Set default values for required fields that are not in Stage 1
            payload_data.setdefault("temple_owned_land", [])
            payload_data.setdefault("resident_bhikkhus", [])
            
            self._validate_foreign_keys(db, payload_data)
            enriched_payload = ViharaCreate(**payload_data)
            return vihara_repo.create(db, data=enriched_payload)

    def mark_stage1_printed(
        self,
        db: Session,
        *,
        vh_id: int,
        actor_id: Optional[str],
    ) -> ViharaData:
        """
        Mark Stage 1 form as printed.
        Workflow: S1_PENDING → S1_PRINTING
        """
        entity = vihara_repo.get(db, vh_id)
        if not entity:
            raise ValueError("Vihara record not found.")
        
        # Allow marking as printed only from S1_PENDING (or legacy PENDING)
        # Works independently of Stage 2 status
        if entity.vh_workflow_status not in ["S1_PENDING", "PENDING"]:
            raise ValueError(f"Cannot mark Stage 1 as printed. Current status: {entity.vh_workflow_status}. Must be S1_PENDING.")
        
        entity.vh_workflow_status = "S1_PRINTING"
        entity.vh_s1_printed_by = actor_id
        entity.vh_s1_printed_at = datetime.utcnow()
        entity.vh_printed_by = actor_id  # Legacy field
        entity.vh_printed_at = datetime.utcnow()  # Legacy field
        entity.vh_updated_by = actor_id
        entity.vh_updated_at = datetime.utcnow()
        entity.vh_version_number = (entity.vh_version_number or 1) + 1
        
        db.commit()
        db.refresh(entity)
        return entity

    async def upload_stage1_document(
        self,
        db: Session,
        *,
        vh_id: int,
        file,
        actor_id: Optional[str],
    ) -> ViharaData:
        """
        Upload scanned Stage 1 document.
        Workflow: S1_PRINTING → S1_PEND_APPROVAL
        """
        from pathlib import Path
        from app.utils.file_storage import file_storage_service
        
        entity = vihara_repo.get(db, vh_id)
        if not entity:
            raise ValueError(f"Vihara with ID '{vh_id}' not found.")
        
        # Works independently of Stage 2 status
        if entity.vh_workflow_status not in ["S1_PRINTING", "PRINTED"]:
            raise ValueError(f"Cannot upload Stage 1 document. Current status: {entity.vh_workflow_status}. Must be S1_PRINTING.")
        
        # Archive old file if exists
        if entity.vh_scanned_document_path:
            await self._archive_old_file(entity.vh_scanned_document_path)
        
        # Save new file
        relative_path, _ = await file_storage_service.save_file(
            file,
            entity.vh_trn,
            "stage1_document",
            subdirectory="vihara_data"
        )
        
        # Update record
        entity.vh_scanned_document_path = relative_path
        entity.vh_workflow_status = "S1_PEND_APPROVAL"
        entity.vh_s1_scanned_by = actor_id
        entity.vh_s1_scanned_at = datetime.utcnow()
        entity.vh_scanned_by = actor_id  # Legacy field
        entity.vh_scanned_at = datetime.utcnow()  # Legacy field
        entity.vh_updated_by = actor_id
        entity.vh_updated_at = datetime.utcnow()
        entity.vh_version_number = (entity.vh_version_number or 1) + 1
        
        db.commit()
        db.refresh(entity)
        return entity

    def mark_stage2_printed(
        self,
        db: Session,
        *,
        vh_id: int,
        actor_id: Optional[str],
    ) -> ViharaData:
        """
        Mark Stage 2 form as printed.
        Can be done even when Stage 1 is pending.
        Workflow: S2_PENDING → S2_PRINTING
        """
        entity = vihara_repo.get(db, vh_id)
        if not entity:
            raise ValueError("Vihara record not found.")
        
        # Works independently of Stage 1 status
        if entity.vh_workflow_status != "S2_PENDING":
            raise ValueError(f"Cannot mark Stage 2 as printed. Current status: {entity.vh_workflow_status}. Must be S2_PENDING.")
        
        entity.vh_workflow_status = "S2_PRINTING"
        entity.vh_s2_printed_by = actor_id
        entity.vh_s2_printed_at = datetime.utcnow()
        entity.vh_updated_by = actor_id
        entity.vh_updated_at = datetime.utcnow()
        entity.vh_version_number = (entity.vh_version_number or 1) + 1
        
        db.commit()
        db.refresh(entity)
        return entity

    def approve_stage_one(
        self,
        db: Session,
        *,
        vh_id: int,
        actor_id: Optional[str],
    ) -> ViharaData:
        """
        Approve Stage 1.
        Workflow: S1_PEND_APPROVAL → S1_APPROVED
        If Stage 2 is also already approved (S2_APPROVED), automatically sets to COMPLETED.
        """
        entity = vihara_repo.get(db, vh_id)
        if not entity:
            raise ValueError("Vihara record not found.")
        
        # Works independently of Stage 2 status
        if entity.vh_workflow_status != "S1_PEND_APPROVAL":
            raise ValueError(f"Cannot approve Stage 1. Current status: {entity.vh_workflow_status}. Must be S1_PEND_APPROVAL.")
        
        # Check if Stage 2 is already approved
        stage2_approved = entity.vh_s2_approved_at is not None
        
        # Set Stage 1 approval fields
        entity.vh_s1_approved_by = actor_id
        entity.vh_s1_approved_at = datetime.utcnow()
        
        # Determine status based on Stage 2 progress
        current_status = entity.vh_workflow_status
        
        # If both stages are approved, go to COMPLETED
        if stage2_approved:
            entity.vh_workflow_status = "COMPLETED"
            entity.vh_approval_status = "APPROVED"
            entity.vh_approved_by = actor_id  # Legacy field
            entity.vh_approved_at = datetime.utcnow()  # Legacy field
        # If Stage 2 is in progress (S2_PENDING, S2_PRINTING, S2_PEND_APPROVAL), preserve it
        elif current_status in ["S2_PENDING", "S2_PRINTING", "S2_PEND_APPROVAL"]:
            # Keep Stage 2 status - don't override it
            pass  # entity.vh_workflow_status stays as is
        else:
            # Stage 2 not started yet, set to S1_APPROVED
            entity.vh_workflow_status = "S1_APPROVED"
        
        entity.vh_updated_by = actor_id
        entity.vh_updated_at = datetime.utcnow()
        entity.vh_version_number = (entity.vh_version_number or 1) + 1
        
        db.commit()
        db.refresh(entity)
        return entity

    def reject_stage_one(
        self,
        db: Session,
        *,
        vh_id: int,
        actor_id: Optional[str],
        rejection_reason: Optional[str] = None,
    ) -> ViharaData:
        """
        Reject Stage 1.
        Workflow: S1_PEND_APPROVAL → S1_REJECTED
        """
        entity = vihara_repo.get(db, vh_id)
        if not entity:
            raise ValueError("Vihara record not found.")
        
        # Works independently of Stage 2 status
        if entity.vh_workflow_status != "S1_PEND_APPROVAL":
            raise ValueError(f"Cannot reject Stage 1. Current status: {entity.vh_workflow_status}. Must be S1_PEND_APPROVAL.")
        
        entity.vh_workflow_status = "S1_REJECTED"
        entity.vh_s1_rejected_by = actor_id
        entity.vh_s1_rejected_at = datetime.utcnow()
        entity.vh_s1_rejection_reason = rejection_reason
        entity.vh_updated_by = actor_id
        entity.vh_updated_at = datetime.utcnow()
        entity.vh_version_number = (entity.vh_version_number or 1) + 1
        
        db.commit()
        db.refresh(entity)
        return entity

    # =================================================================
    # STAGE TWO METHODS
    # =================================================================
    
    def save_stage_two(
        self, db: Session, *, vh_id: int, payload_data: dict, actor_id: Optional[str]
    ) -> ViharaData:
        """
        Save Stage 2: Assets, Certification & Annex (steps 5–10)
        Requires vh_id from stage one. Can be done in parallel with stage 1 approval.
        """
        entity = vihara_repo.get(db, vh_id)
        if not entity:
            raise ValueError("Vihara record not found. Please save Stage 1 first.")
        
        # Allow stage 2 data entry while stage 1 is pending/in progress
        # Also allow when stage 2 is already in progress (for updates)
        # Only block if stage 1 was explicitly rejected or workflow is completed/final rejected
        allowed_statuses = [
            "S1_PENDING", "S1_PRINTING", "S1_PEND_APPROVAL", "S1_APPROVED",
            "S2_PENDING", "S2_PRINTING", "S2_PEND_APPROVAL", "S2_APPROVED"
        ]
        if entity.vh_workflow_status not in allowed_statuses:
            raise ValueError(f"Cannot save Stage 2. Current status: {entity.vh_workflow_status}. Stage 1 must not be rejected.")
        
        now = datetime.utcnow()
        
        # Extract nested data
        temple_lands = payload_data.pop("temple_owned_land", [])
        resident_bhikkhus = payload_data.pop("resident_bhikkhus", [])
        
        # Define Stage 2 specific fields (only update these)
        stage2_fields = {
            'vh_buildings_description',
            'vh_dayaka_families_count',
            'vh_fmlycnt',
            'vh_kulangana_committee',
            'vh_dayaka_sabha',
            'vh_temple_working_committee',
            'vh_other_associations',
            'vh_land_info_certified',
            'vh_resident_bhikkhus_certified',
            'vh_inspection_report',
            'vh_inspection_code',
            'vh_grama_niladhari_division_ownership',
            'vh_sanghika_donation_deed',
            'vh_government_donation_deed',
            'vh_government_donation_deed_in_progress',
            'vh_authority_consent_attached',
            'vh_recommend_new_center',
            'vh_recommend_registered_temple',
            'vh_annex2_recommend_construction',
            'vh_annex2_land_ownership_docs',
            'vh_annex2_chief_incumbent_letter',
            'vh_annex2_coordinator_recommendation',
            'vh_annex2_divisional_secretary_recommendation',
            'vh_annex2_approval_construction',
            'vh_annex2_referral_resubmission',
        }
        
        # Update only stage two specific fields, ignore Stage 1 fields from payload
        for key, value in payload_data.items():
            if key in stage2_fields and hasattr(entity, key):
                setattr(entity, key, value)
        
        entity.vh_workflow_status = "S2_PENDING"
        entity.vh_updated_by = actor_id
        entity.vh_updated_at = now
        
        # Handle nested relationships - use TempleLand
        if temple_lands:
            entity.temple_lands = []
            for land_data in temple_lands:
                from app.models.temple_land import TempleLand
                land_data.pop('id', None)
                land_data.pop('vh_id', None)
                
                snake_case_land = {
                    'serial_number': land_data.get('serialNumber', land_data.get('serial_number')),
                    'land_name': land_data.get('landName', land_data.get('land_name')),
                    'village': land_data.get('village'),
                    'district': land_data.get('district'),
                    'extent': land_data.get('extent'),
                    'cultivation_description': land_data.get('cultivationDescription', land_data.get('cultivation_description')),
                    'ownership_nature': land_data.get('ownershipNature', land_data.get('ownership_nature')),
                    'deed_number': land_data.get('deedNumber', land_data.get('deed_number')),
                    'title_registration_number': land_data.get('titleRegistrationNumber', land_data.get('title_registration_number')),
                    'tax_details': land_data.get('taxDetails', land_data.get('tax_details')),
                    'land_occupants': land_data.get('landOccupants', land_data.get('land_occupants')),
                }
                snake_case_land = {k: v for k, v in snake_case_land.items() if v is not None}
                land = TempleLand(vh_id=vh_id, **snake_case_land)
                entity.temple_lands.append(land)
        
        if resident_bhikkhus:
            entity.resident_bhikkhus = []
            for bhikkhu_data in resident_bhikkhus:
                from app.models.resident_bhikkhu import ResidentBhikkhu
                bhikkhu_data.pop('id', None)
                bhikkhu_data.pop('vh_id', None)
                
                snake_case_bhikkhu = {
                    'serial_number': bhikkhu_data.get('serialNumber', bhikkhu_data.get('serial_number')),
                    'bhikkhu_name': bhikkhu_data.get('bhikkhuName', bhikkhu_data.get('bhikkhu_name')),
                    'registration_number': bhikkhu_data.get('registrationNumber', bhikkhu_data.get('registration_number')),
                    'occupation_education': bhikkhu_data.get('occupationEducation', bhikkhu_data.get('occupation_education')),
                }
                snake_case_bhikkhu = {k: v for k, v in snake_case_bhikkhu.items() if v is not None}
                bhikkhu = ResidentBhikkhu(vh_id=vh_id, **snake_case_bhikkhu)
                entity.resident_bhikkhus.append(bhikkhu)
        
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise ValueError("Failed to save Stage 2 due to a database constraint violation.") from exc
        db.refresh(entity)
        return entity

    async def upload_stage2_document(
        self,
        db: Session,
        *,
        vh_id: int,
        file,
        actor_id: Optional[str],
    ) -> ViharaData:
        """
        Upload scanned Stage 2 document.
        Can be uploaded even when stage 1 is pending.
        Workflow: S1_PENDING/S1_PRINTING/S1_PEND_APPROVAL/S1_APPROVED/S2_PENDING → S2_PEND_APPROVAL
        """
        from app.utils.file_storage import file_storage_service
        
        entity = vihara_repo.get(db, vh_id)
        if not entity:
            raise ValueError(f"Vihara with ID '{vh_id}' not found.")
        
        # Allow stage 2 document upload from various statuses
        # Works independently of Stage 1 status
        allowed_statuses = ["S1_PENDING", "S1_PRINTING", "S1_PEND_APPROVAL", "S1_APPROVED", "S2_PENDING", "S2_PRINTING", "S2_PEND_APPROVAL"]
        if entity.vh_workflow_status not in allowed_statuses:
            raise ValueError(f"Cannot upload Stage 2 document. Current status: {entity.vh_workflow_status}. Must be in stage 1 or stage 2 pending/printing/approval status.")
        
        # Archive old stage2 file if exists
        if entity.vh_stage2_document_path:
            await self._archive_old_file(entity.vh_stage2_document_path)
        
        # Save new file
        relative_path, _ = await file_storage_service.save_file(
            file,
            entity.vh_trn,
            "stage2_document",
            subdirectory="vihara_data"
        )
        
        # Update record
        entity.vh_stage2_document_path = relative_path
        entity.vh_workflow_status = "S2_PEND_APPROVAL"
        entity.vh_s2_scanned_by = actor_id
        entity.vh_s2_scanned_at = datetime.utcnow()
        entity.vh_updated_by = actor_id
        entity.vh_updated_at = datetime.utcnow()
        entity.vh_version_number = (entity.vh_version_number or 1) + 1
        
        db.commit()
        db.refresh(entity)
        return entity

    def approve_stage_two(
        self,
        db: Session,
        *,
        vh_id: int,
        actor_id: Optional[str],
    ) -> ViharaData:
        """
        Approve Stage 2.
        Workflow: S2_PEND_APPROVAL → S2_APPROVED or COMPLETED
        If Stage 1 is also already approved (S1_APPROVED), automatically sets to COMPLETED.
        """
        entity = vihara_repo.get(db, vh_id)
        if not entity:
            raise ValueError("Vihara record not found.")
        
        # Works independently of Stage 1 status
        if entity.vh_workflow_status != "S2_PEND_APPROVAL":
            raise ValueError(f"Cannot approve Stage 2. Current status: {entity.vh_workflow_status}. Must be S2_PEND_APPROVAL.")
        
        # Check if Stage 1 is already approved
        stage1_approved = entity.vh_s1_approved_at is not None
        
        # Set Stage 2 approval fields
        entity.vh_s2_approved_by = actor_id
        entity.vh_s2_approved_at = datetime.utcnow()
        
        # Determine status based on Stage 1 progress
        current_status = entity.vh_workflow_status
        
        # If both stages are approved, go to COMPLETED
        if stage1_approved:
            entity.vh_workflow_status = "COMPLETED"
            entity.vh_approval_status = "APPROVED"
            entity.vh_approved_by = actor_id  # Legacy field
            entity.vh_approved_at = datetime.utcnow()  # Legacy field
        # If Stage 1 is in progress (S1_PENDING, S1_PRINTING, S1_PEND_APPROVAL), preserve it
        elif current_status in ["S1_PENDING", "S1_PRINTING", "S1_PEND_APPROVAL"]:
            # Keep Stage 1 status - don't override it
            pass  # entity.vh_workflow_status stays as is
        else:
            # Stage 1 already approved or Stage 2 is current, set to S2_APPROVED
            entity.vh_workflow_status = "S2_APPROVED"
        
        entity.vh_updated_by = actor_id
        entity.vh_updated_at = datetime.utcnow()
        entity.vh_version_number = (entity.vh_version_number or 1) + 1
        
        db.commit()
        db.refresh(entity)
        return entity

    def reject_stage_two(
        self,
        db: Session,
        *,
        vh_id: int,
        actor_id: Optional[str],
        rejection_reason: Optional[str] = None,
    ) -> ViharaData:
        """
        Reject Stage 2.
        Workflow: S2_PEND_APPROVAL → REJECTED
        """
        entity = vihara_repo.get(db, vh_id)
        if not entity:
            raise ValueError("Vihara record not found.")
        
        if entity.vh_workflow_status != "S2_PEND_APPROVAL":
            raise ValueError(f"Cannot reject Stage 2. Current status: {entity.vh_workflow_status}. Must be S2_PEND_APPROVAL.")
        
        entity.vh_workflow_status = "REJECTED"
        entity.vh_approval_status = "REJECTED"
        entity.vh_s2_rejected_by = actor_id
        entity.vh_s2_rejected_at = datetime.utcnow()
        entity.vh_s2_rejection_reason = rejection_reason
        entity.vh_rejected_by = actor_id  # Legacy field
        entity.vh_rejected_at = datetime.utcnow()  # Legacy field
        entity.vh_rejection_reason = rejection_reason  # Legacy field
        entity.vh_updated_by = actor_id
        entity.vh_updated_at = datetime.utcnow()
        entity.vh_version_number = (entity.vh_version_number or 1) + 1
        
        db.commit()
        db.refresh(entity)
        return entity

    # =================================================================
    # HELPER METHOD FOR FILE ARCHIVING
    # =================================================================
    
    async def _archive_old_file(self, old_file_path: str) -> None:
        """Archive old file with version suffix instead of deleting"""
        from pathlib import Path
        from app.utils.file_storage import file_storage_service
        
        clean_path = old_file_path
        if clean_path.startswith("/storage/"):
            clean_path = clean_path[9:]
        
        path_obj = Path(clean_path)
        file_dir = path_obj.parent
        file_stem = path_obj.stem
        file_ext = path_obj.suffix
        
        storage_dir = Path("app/storage") / file_dir
        max_version = 0
        
        if storage_dir.exists():
            for existing_file in storage_dir.glob("*_v*" + file_ext):
                version_match = existing_file.stem.rsplit("_v", 1)
                if len(version_match) == 2 and version_match[1].isdigit():
                    version_num = int(version_match[1])
                    max_version = max(max_version, version_num)
        
        next_version = max_version + 1
        versioned_name = f"{file_stem}_v{next_version}{file_ext}"
        versioned_relative_path = str(file_dir / versioned_name)
        
        try:
            file_storage_service.rename_file(old_file_path, versioned_relative_path)
        except Exception as e:
            print(f"Warning: Could not rename old file {old_file_path}: {e}")

    # =================================================================
    # LEGACY METHODS (kept for backward compatibility)
    # =================================================================

    def create_vihara(
        self, db: Session, *, payload: ViharaCreate | ViharaCreatePayload, actor_id: Optional[str]
    ) -> ViharaData:
        """Legacy create method - creates with S1_PENDING status"""
        if isinstance(payload, ViharaCreatePayload):
            payload_dict = {
                "vh_vname": payload.temple_name,
                "vh_addrs": payload.temple_address,
                "vh_mobile": payload.telephone_number,
                "vh_whtapp": payload.whatsapp_number,
                "vh_email": payload.email_address,
                "vh_typ": payload.temple_type,
                "vh_ownercd": payload.owner_code,
                "vh_province": payload.province,
                "vh_district": payload.district,
                "vh_divisional_secretariat": payload.divisional_secretariat,
                "vh_pradeshya_sabha": payload.pradeshya_sabha,
                "vh_gndiv": payload.grama_niladhari_division,
                "vh_nikaya": payload.nikaya,
                "vh_parshawa": payload.parshawaya,
                "vh_viharadhipathi_name": payload.viharadhipathi_name,
                "vh_viharadhipathi_regn": payload.viharadhipathi_regn,
                "vh_period_established": payload.period_established,
                "vh_buildings_description": payload.buildings_description,
                "vh_dayaka_families_count": payload.dayaka_families_count,
                "vh_kulangana_committee": payload.kulangana_committee,
                "vh_dayaka_sabha": payload.dayaka_sabha,
                "vh_temple_working_committee": payload.temple_working_committee,
                "vh_other_associations": payload.other_associations,
                "temple_owned_land": [land.model_dump(by_alias=False) for land in payload.temple_owned_land],
                "vh_land_info_certified": payload.land_info_certified,
                "resident_bhikkhus": [bhikkhu.model_dump(by_alias=False) for bhikkhu in payload.resident_bhikkhus],
                "vh_resident_bhikkhus_certified": payload.resident_bhikkhus_certified,
                "vh_inspection_report": payload.inspection_report,
                "vh_inspection_code": payload.inspection_code,
                "vh_grama_niladhari_division_ownership": payload.grama_niladhari_division_ownership,
                "vh_sanghika_donation_deed": payload.sanghika_donation_deed,
                "vh_government_donation_deed": payload.government_donation_deed,
                "vh_government_donation_deed_in_progress": payload.government_donation_deed_in_progress,
                "vh_authority_consent_attached": payload.authority_consent_attached,
                "vh_recommend_new_center": payload.recommend_new_center,
                "vh_recommend_registered_temple": payload.recommend_registered_temple,
                "vh_annex2_recommend_construction": payload.annex2_recommend_construction,
                "vh_annex2_land_ownership_docs": payload.annex2_land_ownership_docs,
                "vh_annex2_chief_incumbent_letter": payload.annex2_chief_incumbent_letter,
                "vh_annex2_coordinator_recommendation": payload.annex2_coordinator_recommendation,
                "vh_annex2_divisional_secretary_recommendation": payload.annex2_divisional_secretary_recommendation,
                "vh_annex2_approval_construction": payload.annex2_approval_construction,
                "vh_annex2_referral_resubmission": payload.annex2_referral_resubmission,
                "vh_form_id": payload.form_id,
            }
        else:
            payload_dict = payload.model_dump(exclude_unset=True)
        
        vh_mobile = payload_dict.get("vh_mobile")
        vh_whtapp = payload_dict.get("vh_whtapp")
        vh_email = payload_dict.get("vh_email")
        
        contact_fields = (
            ("vh_mobile", vh_mobile, vihara_repo.get_by_mobile),
            ("vh_whtapp", vh_whtapp, vihara_repo.get_by_whtapp),
            ("vh_email", vh_email, vihara_repo.get_by_email),
        )
        for field_name, value, getter in contact_fields:
            if value and getter(db, value):
                raise ValueError(f"{field_name} '{value}' is already registered.")

        now = datetime.utcnow()
        payload_dict.pop("vh_trn", None)
        payload_dict.pop("vh_id", None)
        payload_dict.pop("vh_version_number", None)
        
        payload_dict["vh_created_by"] = actor_id
        payload_dict["vh_updated_by"] = actor_id
        payload_dict.setdefault("vh_created_at", now)
        payload_dict.setdefault("vh_updated_at", now)
        payload_dict.setdefault("vh_is_deleted", False)
        payload_dict["vh_version_number"] = 1
        payload_dict.setdefault("vh_workflow_status", "S1_PENDING")

        self._validate_foreign_keys(db, payload_dict)
        enriched_payload = ViharaCreate(**payload_dict)
        return vihara_repo.create(db, data=enriched_payload)

    def list_viharas(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        vh_trn: Optional[str] = None,
        province: Optional[str] = None,
        district: Optional[str] = None,
        divisional_secretariat: Optional[str] = None,
        gn_division: Optional[str] = None,
        temple: Optional[str] = None,
        child_temple: Optional[str] = None,
        nikaya: Optional[str] = None,
        parshawaya: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        vh_typ: Optional[str] = None,
        date_from: Optional[Any] = None,
        date_to: Optional[Any] = None,
        current_user = None,
    ) -> list[ViharaData]:
        limit = max(1, min(limit, 200))
        skip = max(0, skip)
        return vihara_repo.list(
            db,
            skip=skip,
            limit=limit,
            search=search,
            vh_trn=vh_trn,
            province=province,
            district=district,
            divisional_secretariat=divisional_secretariat,
            gn_division=gn_division,
            temple=temple,
            child_temple=child_temple,
            nikaya=nikaya,
            parshawaya=parshawaya,
            category=category,
            status=status,
            vh_typ=vh_typ,
            date_from=date_from,
            date_to=date_to,
            current_user=current_user,
        )

    def count_viharas(
        self, 
        db: Session, 
        *, 
        search: Optional[str] = None,
        vh_trn: Optional[str] = None,
        province: Optional[str] = None,
        district: Optional[str] = None,
        divisional_secretariat: Optional[str] = None,
        gn_division: Optional[str] = None,
        temple: Optional[str] = None,
        child_temple: Optional[str] = None,
        nikaya: Optional[str] = None,
        parshawaya: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        vh_typ: Optional[str] = None,
        date_from: Optional[Any] = None,
        date_to: Optional[Any] = None,
        current_user = None,
    ) -> int:
        return vihara_repo.count(
            db,
            search=search,
            vh_trn=vh_trn,
            province=province,
            district=district,
            divisional_secretariat=divisional_secretariat,
            gn_division=gn_division,
            temple=temple,
            child_temple=child_temple,
            nikaya=nikaya,
            parshawaya=parshawaya,
            category=category,
            status=status,
            vh_typ=vh_typ,
            date_from=date_from,
            date_to=date_to,
            current_user=current_user,
        )

    def get_vihara(self, db: Session, vh_id: int) -> Optional[ViharaData]:
        return vihara_repo.get(db, vh_id)

    def get_vihara_by_trn(self, db: Session, vh_trn: str) -> Optional[ViharaData]:
        return vihara_repo.get_by_trn(db, vh_trn)

    def list_viharas_simple(
        self, 
        db: Session,
        *,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
    ) -> tuple[list[dict[str, Any]], int]:
        """Return simplified list of viharas with just vh_trn and vh_vname, with pagination."""
        limit = max(1, min(limit, 200))
        skip = max(0, skip)
        
        viharas = vihara_repo.list(db, skip=skip, limit=limit, search=search)
        total_count = vihara_repo.count(db, search=search)
        
        simplified_viharas = [
            {"vh_trn": vihara.vh_trn, "vh_vname": vihara.vh_vname}
            for vihara in viharas
            if not vihara.vh_is_deleted
        ]
        
        return simplified_viharas, total_count

    def update_vihara(
        self,
        db: Session,
        *,
        vh_id: int,
        payload: ViharaUpdate,
        actor_id: Optional[str],
    ) -> ViharaData:
        entity = vihara_repo.get(db, vh_id)
        if not entity:
            raise ValueError("Vihara record not found.")

        if payload.vh_trn and payload.vh_trn != entity.vh_trn:
            raise ValueError("vh_trn cannot be modified once generated.")

        if payload.vh_mobile and payload.vh_mobile != entity.vh_mobile:
            conflict = vihara_repo.get_by_mobile(db, payload.vh_mobile)
            if conflict and conflict.vh_id != entity.vh_id:
                raise ValueError(f"vh_mobile '{payload.vh_mobile}' is already registered.")

        if payload.vh_whtapp and payload.vh_whtapp != entity.vh_whtapp:
            conflict = vihara_repo.get_by_whtapp(db, payload.vh_whtapp)
            if conflict and conflict.vh_id != entity.vh_id:
                raise ValueError(f"vh_whtapp '{payload.vh_whtapp}' is already registered.")

        if payload.vh_email and payload.vh_email != entity.vh_email:
            conflict = vihara_repo.get_by_email(db, payload.vh_email)
            if conflict and conflict.vh_id != entity.vh_id:
                raise ValueError(f"vh_email '{payload.vh_email}' is already registered.")

        update_data = payload.model_dump(exclude_unset=True)
        update_data.pop("vh_version_number", None)
        update_data["vh_updated_by"] = actor_id
        update_data["vh_updated_at"] = datetime.utcnow()

        # Only validate FK fields that are actually being updated
        # (don't re-validate existing entity values - they're already in DB)
        self._validate_foreign_keys(db, update_data)

        patched_payload = ViharaUpdate(**update_data)
        return vihara_repo.update(db, entity=entity, data=patched_payload)

    def delete_vihara(
        self, db: Session, *, vh_id: int, actor_id: Optional[str]
    ) -> ViharaData:
        entity = vihara_repo.get(db, vh_id)
        if not entity:
            raise ValueError("Vihara record not found.")

        entity.vh_updated_by = actor_id
        entity.vh_updated_at = datetime.utcnow()
        return vihara_repo.soft_delete(db, entity=entity)

    # Legacy workflow methods
    def approve_vihara(
        self,
        db: Session,
        *,
        vh_id: int,
        actor_id: Optional[str],
    ) -> ViharaData:
        """Legacy approve - routes to appropriate stage approval"""
        entity = vihara_repo.get(db, vh_id)
        if not entity:
            raise ValueError("Vihara record not found.")
        
        if entity.vh_workflow_status == "S1_PEND_APPROVAL":
            return self.approve_stage_one(db, vh_id=vh_id, actor_id=actor_id)
        elif entity.vh_workflow_status == "S2_PEND_APPROVAL":
            return self.approve_stage_two(db, vh_id=vh_id, actor_id=actor_id)
        elif entity.vh_workflow_status in ["PRINTED", "PEND-APPROVAL"]:
            # Old workflow compatibility
            entity.vh_workflow_status = "COMPLETED"
            entity.vh_approval_status = "APPROVED"
            entity.vh_approved_by = actor_id
            entity.vh_approved_at = datetime.utcnow()
            entity.vh_updated_by = actor_id
            entity.vh_updated_at = datetime.utcnow()
            entity.vh_version_number += 1
            db.commit()
            db.refresh(entity)
            return entity
        else:
            raise ValueError(f"Cannot approve vihara with workflow status: {entity.vh_workflow_status}")

    def reject_vihara(
        self,
        db: Session,
        *,
        vh_id: int,
        actor_id: Optional[str],
        rejection_reason: Optional[str] = None,
    ) -> ViharaData:
        """Legacy reject - routes to appropriate stage rejection"""
        entity = vihara_repo.get(db, vh_id)
        if not entity:
            raise ValueError("Vihara record not found.")
        
        if entity.vh_workflow_status == "S1_PEND_APPROVAL":
            return self.reject_stage_one(db, vh_id=vh_id, actor_id=actor_id, rejection_reason=rejection_reason)
        elif entity.vh_workflow_status == "S2_PEND_APPROVAL":
            return self.reject_stage_two(db, vh_id=vh_id, actor_id=actor_id, rejection_reason=rejection_reason)
        elif entity.vh_workflow_status == "PEND-APPROVAL":
            entity.vh_workflow_status = "REJECTED"
            entity.vh_approval_status = "REJECTED"
            entity.vh_rejected_by = actor_id
            entity.vh_rejected_at = datetime.utcnow()
            entity.vh_rejection_reason = rejection_reason
            entity.vh_updated_by = actor_id
            entity.vh_updated_at = datetime.utcnow()
            entity.vh_version_number += 1
            db.commit()
            db.refresh(entity)
            return entity
        else:
            raise ValueError(f"Cannot reject vihara with workflow status: {entity.vh_workflow_status}")

    def mark_printed(
        self,
        db: Session,
        *,
        vh_id: int,
        actor_id: Optional[str],
    ) -> ViharaData:
        """Legacy mark printed - routes to stage 1 printed"""
        return self.mark_stage1_printed(db, vh_id=vh_id, actor_id=actor_id)

    def mark_scanned(
        self,
        db: Session,
        *,
        vh_id: int,
        actor_id: Optional[str],
    ) -> ViharaData:
        """Legacy mark scanned"""
        entity = vihara_repo.get(db, vh_id)
        if not entity:
            raise ValueError("Vihara record not found.")
        
        if entity.vh_workflow_status in ["PRINTED", "S1_PRINTING"]:
            entity.vh_workflow_status = "S1_PEND_APPROVAL" if entity.vh_workflow_status == "S1_PRINTING" else "PEND-APPROVAL"
            entity.vh_scanned_by = actor_id
            entity.vh_scanned_at = datetime.utcnow()
            entity.vh_updated_by = actor_id
            entity.vh_updated_at = datetime.utcnow()
            entity.vh_version_number += 1
            db.commit()
            db.refresh(entity)
            return entity
        else:
            raise ValueError(f"Cannot mark as scanned with workflow status: {entity.vh_workflow_status}")

    async def upload_scanned_document(
        self,
        db: Session,
        *,
        vh_id: int,
        file,
        actor_id: Optional[str],
    ) -> ViharaData:
        """Legacy upload - routes to appropriate stage upload"""
        from app.utils.file_storage import file_storage_service
        
        entity = vihara_repo.get(db, vh_id)
        if not entity:
            raise ValueError(f"Vihara with ID '{vh_id}' not found.")
        
        # Route to appropriate stage upload based on status
        if entity.vh_workflow_status in ["S1_PRINTING", "PRINTED"]:
            return await self.upload_stage1_document(db, vh_id=vh_id, file=file, actor_id=actor_id)
        elif entity.vh_workflow_status == "S2_PENDING":
            return await self.upload_stage2_document(db, vh_id=vh_id, file=file, actor_id=actor_id)
        else:
            # Fallback to old behavior
            if entity.vh_scanned_document_path:
                await self._archive_old_file(entity.vh_scanned_document_path)
            
            relative_path, _ = await file_storage_service.save_file(
                file,
                entity.vh_trn,
                "scanned_document",
                subdirectory="vihara_data"
            )
            
            entity.vh_scanned_document_path = relative_path
            entity.vh_updated_by = actor_id
            entity.vh_updated_at = datetime.utcnow()
            entity.vh_version_number = (entity.vh_version_number or 0) + 1
            
            if entity.vh_workflow_status == "PRINTED":
                entity.vh_workflow_status = "PEND-APPROVAL"
                entity.vh_scanned_by = actor_id
                entity.vh_scanned_at = datetime.utcnow()
            
            db.commit()
            db.refresh(entity)
            return entity

    # =================================================================
    # VALIDATION METHODS
    # =================================================================

    def _validate_foreign_keys(self, db: Session, values: Dict[str, Any]) -> None:
        # Known FK mappings as fallback (column -> (schema, table, ref_column))
        # These are used if the DB introspection cache doesn't include them
        KNOWN_FK_MAP = {
            "vh_gndiv": (None, "cmm_gndata", "gn_gnc"),
            "vh_province": (None, "cmm_province", "cp_code"),
            "vh_district": (None, "cmm_districtdata", "dd_dcode"),
            "vh_divisional_secretariat": (None, "cmm_dvsec", "dv_dvcode"),
            "vh_nikaya": (None, "cmm_nikayadata", "nk_nkn"),
            "vh_parshawa": (None, "cmm_parshawadata", "pr_prn"),
            "vh_ssbmcode": (None, "cmm_sasanarbm", "sr_ssbmcode"),
        }
        
        try:
            fk_targets = self._get_foreign_key_targets(db)
        except OperationalError as exc:
            raise ValueError(
                "Unable to verify references due to temporary database connectivity issues."
            ) from exc
        
        # Merge known FK map with DB-introspected FK targets (DB takes precedence)
        merged_targets = {**KNOWN_FK_MAP, **fk_targets}
        
        fields_to_validate = {
            "vh_gndiv": values.get("vh_gndiv"),
            "vh_ownercd": values.get("vh_ownercd"),
            "vh_parshawa": values.get("vh_parshawa"),
            "vh_ssbmcode": values.get("vh_ssbmcode"),
            "vh_province": values.get("vh_province"),
            "vh_district": values.get("vh_district"),
            "vh_divisional_secretariat": values.get("vh_divisional_secretariat"),
            "vh_nikaya": values.get("vh_nikaya"),
        }

        for field, raw_value in fields_to_validate.items():
            value = raw_value
            if value is None:
                continue
            if isinstance(value, str):
                value = value.strip()
                if not value:
                    continue
                
                # For TEMP- prefixed values, validate against temporary tables
                if value.startswith("TEMP-"):
                    try:
                        temp_id = int(value.split("-")[1])
                        
                        # Check temporary bhikku for vh_ownercd (bhikku registration)
                        if field == "vh_ownercd":
                            from app.models.temporary_bhikku import TemporaryBhikku
                            temp_exists = db.query(TemporaryBhikku).filter(
                                TemporaryBhikku.tb_id == temp_id
                            ).first()
                            if not temp_exists:
                                raise ValueError(f"Temporary Bhikku with ID {temp_id} not found. Please create the temporary bhikku entry first.")
                        
                        # Skip regular FK validation for TEMP values
                        continue
                    except (ValueError, IndexError) as e:
                        if "not found" in str(e).lower():
                            raise
                        raise ValueError(f"Invalid TEMP reference format: {value}")

            target = merged_targets.get(field)
            if not target:
                continue

            schema, table_name, column_name = target
            try:
                exists = self._reference_exists(
                    db,
                    schema=schema,
                    table_name=table_name,
                    column_name=column_name,
                    value=value,
                )
            except OperationalError as exc:
                raise ValueError(
                    "Unable to verify references due to temporary database connectivity issues."
                ) from exc

            if not exists:
                raise ValueError(f"Invalid reference: {field} value '{value}' not found in lookup table")

    def _build_fk_validation_payload(
        self, entity: ViharaData, update_values: Dict[str, Any]
    ) -> Dict[str, Any]:
        fk_fields = ["vh_gndiv", "vh_ownercd", "vh_parshawa", "vh_ssbmcode", "vh_province", "vh_district", "vh_divisional_secretariat", "vh_nikaya"]
        payload: Dict[str, Any] = {}
        for field in fk_fields:
            if field in update_values:
                payload[field] = update_values[field]
            else:
                payload[field] = getattr(entity, field, None)
        return payload

    def _get_foreign_key_targets(
        self, db: Session
    ) -> dict[str, tuple[Optional[str], str, str]]:
        if self._fk_targets is not None:
            return self._fk_targets

        inspector = inspect(db.get_bind())
        mapping: dict[str, tuple[Optional[str], str, str]] = {}
        for fk in inspector.get_foreign_keys(ViharaData.__tablename__):
            constrained_columns = fk.get("constrained_columns") or []
            referred_columns = fk.get("referred_columns") or []
            table_name = fk.get("referred_table")
            schema = fk.get("referred_schema")
            if not table_name:
                continue

            for column, referred_column in zip(constrained_columns, referred_columns):
                if not column or not referred_column:
                    continue
                mapping[column] = (schema, table_name, referred_column)

        self._fk_targets = mapping
        return mapping

    def _reference_exists(
        self,
        db: Session,
        *,
        schema: Optional[str],
        table_name: str,
        column_name: str,
        value: Any,
    ) -> bool:
        metadata = MetaData()
        table = Table(table_name, metadata, schema=schema, autoload_with=db.get_bind())
        column = table.c.get(column_name)
        if column is None:
            raise RuntimeError(
                f"Invalid foreign key configuration: column '{column_name}' "
                f"not found in table '{table_name}'."
            )

        stmt = select(column).where(column == value).limit(1)
        result = db.execute(stmt).first()
        return result is not None
    
    def enrich_with_temp_entities(self, db: Session, vihara: ViharaData) -> Dict[str, Any]:
        """
        Enrich vihara data with temporary entity information for TEMP- references.
        """
        from app.models.temporary_vihara import TemporaryVihara
        from app.models.temporary_bhikku import TemporaryBhikku
        
        result = {}
        
        # Check vh_ownercd for temporary vihara
        if vihara.vh_ownercd and vihara.vh_ownercd.startswith("TEMP-"):
            temp_id = vihara.vh_ownercd.replace("TEMP-", "")
            if temp_id.isdigit():
                temp_vihara = db.query(TemporaryVihara).filter(
                    TemporaryVihara.tv_id == int(temp_id)
                ).first()
                if temp_vihara:
                    result["owner_temp_vihara_info"] = {
                        "tv_id": temp_vihara.tv_id,
                        "tv_name": temp_vihara.tv_name,
                        "tv_address": temp_vihara.tv_address,
                        "tv_contact_number": temp_vihara.tv_contact_number,
                        "tv_district": temp_vihara.tv_district,
                        "tv_province": temp_vihara.tv_province,
                    }
        
        # Check vh_viharadhipathi_regn for temporary bhikku
        if vihara.vh_viharadhipathi_regn and vihara.vh_viharadhipathi_regn.startswith("TEMP-"):
            temp_id = vihara.vh_viharadhipathi_regn.replace("TEMP-", "")
            if temp_id.isdigit():
                temp_bhikku = db.query(TemporaryBhikku).filter(
                    TemporaryBhikku.tb_id == int(temp_id)
                ).first()
                if temp_bhikku:
                    result["viharadhipathi_temp_bhikku_info"] = {
                        "tb_id": temp_bhikku.tb_id,
                        "tb_name": temp_bhikku.tb_name,
                        "tb_id_number": temp_bhikku.tb_id_number,
                        "tb_contact_number": temp_bhikku.tb_contact_number,
                        "tb_samanera_name": temp_bhikku.tb_samanera_name,
                        "tb_address": temp_bhikku.tb_address,
                        "tb_living_temple": temp_bhikku.tb_living_temple,
                    }
        
        return result
    
    def enrich_with_viharanga_data(self, db: Session, vihara: ViharaData) -> Dict[str, Any]:
        """
        Enrich vihara data with viharanga information parsed from vh_buildings_description.
        Expects vh_buildings_description to contain comma-separated viharanga codes.
        """
        from app.models.viharanga import Viharanga
        
        result = {"viharanga_list": []}
        
        if not vihara.vh_buildings_description:
            return result
        
        # Parse viharanga codes from buildings_description (comma-separated)
        viharanga_codes = [code.strip().upper() for code in vihara.vh_buildings_description.split(',') if code.strip()]
        
        if not viharanga_codes:
            return result
        
        # Fetch viharanga objects for the codes
        viharangas = db.query(Viharanga).filter(
            Viharanga.vg_code.in_(viharanga_codes),
            Viharanga.vg_is_deleted.is_(False)
        ).all()
        
        # Convert to nested response format
        result["viharanga_list"] = [
            {
                "vg_id": v.vg_id,
                "vg_code": v.vg_code,
                "vg_item": v.vg_item
            }
            for v in viharangas
        ]
        
        return result
    
    def _ensure_temp_bhikku_placeholders(self, db: Session, payload_data: dict) -> None:
        """
        Verify that TEMP- bhikku references in vh_ownercd exist in bhikku_regist table.
        
        Note: vh_ownercd has a FK constraint to bhikku_regist.br_regn, so TEMP values
        must exist there (created via Bhikku Registration system).
        
        vh_viharadhipathi_regn does NOT have a FK constraint, so TEMP values work directly.
        """
        from sqlalchemy import text
        
        vh_ownercd = payload_data.get("vh_ownercd")
        if vh_ownercd and isinstance(vh_ownercd, str) and vh_ownercd.startswith("TEMP-"):
            # Check if it exists in bhikku_regist (must be created via bhikku registration)
            result = db.execute(
                text("SELECT br_regn FROM bhikku_regist WHERE br_regn = :regn"),
                {"regn": vh_ownercd}
            ).first()
            
            if not result:
                raise ValueError(
                    f"Cannot use {vh_ownercd} for Temple Owner (vh_ownercd). "
                    f"Temporary bhikkus can be used for Chief Incumbent (vh_viharadhipathi_regn), "
                    f"but Temple Owner must reference a fully registered bhikku in the Bhikku Registration system. "
                    f"Please either: 1) Complete the bhikku registration for {vh_ownercd}, or "
                    f"2) Leave Temple Owner empty and only use the temporary bhikku for Chief Incumbent."
                )


vihara_service = ViharaService()
