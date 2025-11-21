# app/services/silmatha_regist_service.py
from __future__ import annotations

import re
from datetime import datetime, date
from typing import Any, Dict, Optional

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.silmatha_regist import SilmathaRegist
from app.models.user import UserAccount
from app.models.bhikku import Bhikku
from app.models.vihara import ViharaData
from app.models.province import Province
from app.models.district import District
from app.models.divisional_secretariat import DivisionalSecretariat
from app.models.gramasewaka import Gramasewaka
from app.models.status import StatusData
from app.repositories.silmatha_regist_repo import silmatha_regist_repo
from app.schemas.silmatha_regist import SilmathaRegistCreate, SilmathaRegistUpdate
from app.utils.file_storage import file_storage_service


class SilmathaRegistService:
    """Business logic and validation helpers for silmatha registrations."""

    MOBILE_PATTERN = re.compile(r"^0\d{9}$")

    def create_silmatha(
        self, db: Session, *, payload: SilmathaRegistCreate, actor_id: Optional[str], current_user: Optional[UserAccount] = None
    ) -> SilmathaRegist:
        payload_dict = payload.model_dump()
        payload_dict["sil_created_by"] = actor_id
        payload_dict["sil_updated_by"] = actor_id
        payload_dict = self._strip_strings(payload_dict)
        payload_dict = self._normalize_contact_fields(payload_dict)
        self._validate_contact_formats(payload_dict)
        
        # Validate foreign keys
        self._validate_foreign_keys(db, payload_dict)

        # Auto-populate location from current user (location-based access control)
        if current_user and current_user.ua_location_type == "DISTRICT_BRANCH" and current_user.ua_district_branch_id:
            from app.models.district_branch import DistrictBranch
            district_branch = db.query(DistrictBranch).filter(
                DistrictBranch.db_id == current_user.ua_district_branch_id
            ).first()
            if district_branch and district_branch.db_district_code:
                payload_dict["sil_created_by_district"] = district_branch.db_district_code

        explicit_regn = payload_dict.get("sil_regn")
        if explicit_regn:
            existing = silmatha_regist_repo.get_raw_by_regn(db, explicit_regn)
            if existing and not existing.sil_is_deleted:
                raise ValueError(f"sil_regn '{explicit_regn}' already exists.")
            if existing and existing.sil_is_deleted:
                raise ValueError(
                    f"sil_regn '{explicit_regn}' belongs to a deleted record and cannot be reused."
                )

        self._validate_unique_contact_fields(
            db,
            sil_mobile=payload_dict.get("sil_mobile"),
            sil_email=payload_dict.get("sil_email"),
            current_regn=None,
        )

        validated_payload = SilmathaRegistCreate(**payload_dict)
        return silmatha_regist_repo.create(db, validated_payload)

    def update_silmatha(
        self, db: Session, *, sil_regn: str, payload: SilmathaRegistUpdate, actor_id: Optional[str]
    ) -> SilmathaRegist:
        existing = silmatha_regist_repo.get_by_regn(db, sil_regn)
        if not existing:
            raise ValueError(f"Silmatha record with regn '{sil_regn}' not found.")

        payload_dict = payload.model_dump(exclude_unset=True)
        payload_dict["sil_updated_by"] = actor_id
        payload_dict = self._strip_strings(payload_dict)
        payload_dict = self._normalize_contact_fields(payload_dict)
        self._validate_contact_formats(payload_dict)
        
        # Validate foreign keys
        self._validate_foreign_keys(db, payload_dict)

        if "sil_mobile" in payload_dict or "sil_email" in payload_dict:
            self._validate_unique_contact_fields(
                db,
                sil_mobile=payload_dict.get("sil_mobile"),
                sil_email=payload_dict.get("sil_email"),
                current_regn=sil_regn,
            )

        validated_payload = SilmathaRegistUpdate(**payload_dict)
        updated = silmatha_regist_repo.update(db, sil_regn, validated_payload)
        if not updated:
            raise ValueError(f"Failed to update silmatha record '{sil_regn}'.")
        return updated

    def delete_silmatha(self, db: Session, *, sil_regn: str, actor_id: Optional[str]) -> SilmathaRegist:
        existing = silmatha_regist_repo.get_by_regn(db, sil_regn)
        if not existing:
            raise ValueError(f"Silmatha record with regn '{sil_regn}' not found.")

        deleted = silmatha_regist_repo.delete(db, sil_regn, updated_by=actor_id)
        if not deleted:
            raise ValueError(f"Failed to delete silmatha record '{sil_regn}'.")
        return deleted

    def enrich_silmatha_dict(self, silmatha: SilmathaRegist, db: Session = None) -> dict:
        """Transform SilmathaRegist model to dictionary with resolved foreign key names as nested objects"""
        
        # Handle multi_mahanaacharyacd - split and resolve names
        mahanaacharyacd_value = silmatha.sil_mahanaacharyacd
        if silmatha.sil_mahanaacharyacd and db:
            # Assuming comma-separated registration numbers
            regns = [r.strip() for r in silmatha.sil_mahanaacharyacd.split(',') if r.strip()]
            if regns:
                # Query all at once for efficiency
                bhikku_names = db.query(Bhikku.br_regn, Bhikku.br_mahananame, Bhikku.br_upasampadaname).filter(
                    Bhikku.br_regn.in_(regns),
                    Bhikku.br_is_deleted.is_(False)
                ).all()
                # For mahanaacharyacd, we can resolve to nested objects
                # But since it can be multiple, we'll keep it as is for now or create array
                mahanaacharyacd_value = silmatha.sil_mahanaacharyacd
        
        silmatha_dict = {
            "sil_id": silmatha.sil_id,
            "sil_regn": silmatha.sil_regn,
            "sil_reqstdate": silmatha.sil_reqstdate,
            
            # Personal Information
            "sil_gihiname": silmatha.sil_gihiname,
            "sil_dofb": silmatha.sil_dofb,
            "sil_fathrname": silmatha.sil_fathrname,
            "sil_email": silmatha.sil_email,
            "sil_mobile": silmatha.sil_mobile,
            "sil_fathrsaddrs": silmatha.sil_fathrsaddrs,
            "sil_fathrsmobile": silmatha.sil_fathrsmobile,
            
            # Geographic/Birth Information with nested objects
            "sil_birthpls": silmatha.sil_birthpls,
            "sil_province": {
                "cp_code": silmatha.province_rel.cp_code,
                "cp_name": silmatha.province_rel.cp_name
            } if silmatha.province_rel else silmatha.sil_province,
            "sil_district": {
                "dd_dcode": silmatha.district_rel.dd_dcode,
                "dd_dname": silmatha.district_rel.dd_dname
            } if silmatha.district_rel else silmatha.sil_district,
            "sil_korale": silmatha.sil_korale,
            "sil_pattu": silmatha.sil_pattu,
            "sil_division": {
                "dv_dvcode": silmatha.division_rel.dv_dvcode,
                "dv_dvname": silmatha.division_rel.dv_dvname
            } if silmatha.division_rel else silmatha.sil_division,
            "sil_vilage": silmatha.sil_vilage,
            "sil_gndiv": {
                "gn_gnc": silmatha.gndiv_rel.gn_gnc,
                "gn_gnname": silmatha.gndiv_rel.gn_gnname
            } if silmatha.gndiv_rel else silmatha.sil_gndiv,
            
            # Temple/Religious Information with nested objects
            "sil_viharadhipathi": {
                "br_regn": silmatha.viharadhipathi_rel.br_regn,
                "br_mahananame": silmatha.viharadhipathi_rel.br_mahananame or "",
                "br_upasampadaname": silmatha.viharadhipathi_rel.br_upasampadaname or ""
            } if silmatha.viharadhipathi_rel else silmatha.sil_viharadhipathi,
            "sil_cat": {
                "cc_code": silmatha.category_rel.cc_code,
                "cc_catogry": silmatha.category_rel.cc_catogry
            } if silmatha.category_rel else silmatha.sil_cat,
            "sil_currstat": {
                "st_statcd": silmatha.status_rel.st_statcd,
                "st_descr": silmatha.status_rel.st_descr
            } if silmatha.status_rel else silmatha.sil_currstat,
            "sil_declaration_date": silmatha.sil_declaration_date,
            "sil_remarks": silmatha.sil_remarks,
            "sil_mahanadate": silmatha.sil_mahanadate,
            "sil_mahananame": silmatha.sil_mahananame,
            "sil_mahanaacharyacd": mahanaacharyacd_value,
            "sil_robing_tutor_residence": {
                "vh_trn": silmatha.robing_tutor_residence_rel.vh_trn,
                "vh_vname": silmatha.robing_tutor_residence_rel.vh_vname
            } if silmatha.robing_tutor_residence_rel else silmatha.sil_robing_tutor_residence,
            "sil_mahanatemple": {
                "vh_trn": silmatha.mahanatemple_rel.vh_trn,
                "vh_vname": silmatha.mahanatemple_rel.vh_vname
            } if silmatha.mahanatemple_rel else silmatha.sil_mahanatemple,
            "sil_robing_after_residence_temple": {
                "vh_trn": silmatha.robing_after_residence_temple_rel.vh_trn,
                "vh_vname": silmatha.robing_after_residence_temple_rel.vh_vname
            } if silmatha.robing_after_residence_temple_rel else silmatha.sil_robing_after_residence_temple,
            
            # Document Storage
            "sil_scanned_document_path": silmatha.sil_scanned_document_path,
            
            # Workflow Fields
            "sil_workflow_status": silmatha.sil_workflow_status,
            "sil_approval_status": silmatha.sil_approval_status,
            "sil_approved_by": silmatha.sil_approved_by,
            "sil_approved_at": silmatha.sil_approved_at,
            "sil_rejected_by": silmatha.sil_rejected_by,
            "sil_rejected_at": silmatha.sil_rejected_at,
            "sil_rejection_reason": silmatha.sil_rejection_reason,
            "sil_printed_at": silmatha.sil_printed_at,
            "sil_printed_by": silmatha.sil_printed_by,
            "sil_scanned_at": silmatha.sil_scanned_at,
            "sil_scanned_by": silmatha.sil_scanned_by,
            
            # Reprint Workflow Fields
            "sil_reprint_status": silmatha.sil_reprint_status,
            "sil_reprint_requested_by": silmatha.sil_reprint_requested_by,
            "sil_reprint_requested_at": silmatha.sil_reprint_requested_at,
            "sil_reprint_request_reason": silmatha.sil_reprint_request_reason,
            "sil_reprint_approved_by": silmatha.sil_reprint_approved_by,
            "sil_reprint_approved_at": silmatha.sil_reprint_approved_at,
            "sil_reprint_rejected_by": silmatha.sil_reprint_rejected_by,
            "sil_reprint_rejected_at": silmatha.sil_reprint_rejected_at,
            "sil_reprint_rejection_reason": silmatha.sil_reprint_rejection_reason,
            "sil_reprint_completed_by": silmatha.sil_reprint_completed_by,
            "sil_reprint_completed_at": silmatha.sil_reprint_completed_at,
            
            # Audit Fields
            "sil_version": silmatha.sil_version,
            "sil_is_deleted": silmatha.sil_is_deleted,
            "sil_created_at": silmatha.sil_created_at,
            "sil_updated_at": silmatha.sil_updated_at,
            "sil_created_by": silmatha.sil_created_by,
            "sil_updated_by": silmatha.sil_updated_by,
            "sil_version_number": silmatha.sil_version_number,
        }
        
        return silmatha_dict

    def approve_silmatha(self, db: Session, *, sil_regn: str, actor_id: Optional[str]) -> SilmathaRegist:
        """Approve a silmatha registration - transitions workflow from SCANNED to COMPLETED with APPROVED status"""
        entity = silmatha_regist_repo.get_by_regn(db, sil_regn)
        if not entity:
            raise ValueError("Silmatha record not found.")

        if entity.sil_workflow_status != "SCANNED":
            raise ValueError(f"Cannot approve silmatha with workflow status: {entity.sil_workflow_status}. Must be SCANNED.")

        # Update workflow fields - goes to COMPLETED with APPROVED status
        entity.sil_workflow_status = "COMPLETED"
        entity.sil_approval_status = "APPROVED"
        entity.sil_approved_by = actor_id
        entity.sil_approved_at = datetime.utcnow()
        entity.sil_updated_by = actor_id
        entity.sil_updated_at = datetime.utcnow()
        entity.sil_version_number += 1
        
        db.commit()
        db.refresh(entity)
        return entity

    def reject_silmatha(self, db: Session, *, sil_regn: str, rejection_reason: str, actor_id: Optional[str]) -> SilmathaRegist:
        """Reject a silmatha registration - transitions workflow from SCANNED to REJECTED status"""
        entity = silmatha_regist_repo.get_by_regn(db, sil_regn)
        if not entity:
            raise ValueError("Silmatha record not found.")

        if entity.sil_workflow_status != "SCANNED":
            raise ValueError(f"Cannot reject silmatha with workflow status: {entity.sil_workflow_status}. Must be SCANNED.")

        # Update workflow fields
        entity.sil_workflow_status = "REJECTED"
        entity.sil_approval_status = "REJECTED"
        entity.sil_rejected_by = actor_id
        entity.sil_rejected_at = datetime.utcnow()
        entity.sil_rejection_reason = rejection_reason
        entity.sil_updated_by = actor_id
        entity.sil_updated_at = datetime.utcnow()
        entity.sil_version_number += 1
        
        db.commit()
        db.refresh(entity)
        return entity

    def mark_printed(self, db: Session, *, sil_regn: str, actor_id: Optional[str]) -> SilmathaRegist:
        """Mark a silmatha certificate as printed - transitions workflow from PENDING to PRINTED status"""
        entity = silmatha_regist_repo.get_by_regn(db, sil_regn)
        if not entity:
            raise ValueError("Silmatha record not found.")

        if entity.sil_workflow_status != "PENDING":
            raise ValueError(f"Cannot mark as printed silmatha with workflow status: {entity.sil_workflow_status}. Must be PENDING.")

        # Update workflow fields
        entity.sil_workflow_status = "PRINTED"
        entity.sil_printed_by = actor_id
        entity.sil_printed_at = datetime.utcnow()
        entity.sil_updated_by = actor_id
        entity.sil_updated_at = datetime.utcnow()
        entity.sil_version_number += 1
        
        db.commit()
        db.refresh(entity)
        return entity

    def mark_scanned(self, db: Session, *, sil_regn: str, scanned_document_path: str, actor_id: Optional[str]) -> SilmathaRegist:
        """Mark a silmatha certificate as scanned - transitions workflow from PRINTED to SCANNED status"""
        entity = silmatha_regist_repo.get_by_regn(db, sil_regn)
        if not entity:
            raise ValueError("Silmatha record not found.")

        if entity.sil_workflow_status != "PRINTED":
            raise ValueError(f"Cannot mark as scanned silmatha with workflow status: {entity.sil_workflow_status}. Must be PRINTED.")

        # Update workflow fields
        entity.sil_workflow_status = "SCANNED"
        entity.sil_scanned_by = actor_id
        entity.sil_scanned_at = datetime.utcnow()
        if scanned_document_path:
            entity.sil_scanned_document_path = scanned_document_path
        entity.sil_updated_by = actor_id
        entity.sil_updated_at = datetime.utcnow()
        entity.sil_version_number += 1
        
        db.commit()
        db.refresh(entity)
        return entity

    def mark_printing(
        self,
        db: Session,
        *,
        sil_regn: str,
        actor_id: Optional[str],
    ) -> SilmathaRegist:
        """Mark silmatha certificate as in printing process - transitions workflow from PENDING to PRINTING status"""
        entity = silmatha_regist_repo.get_by_regn(db, sil_regn)
        if not entity:
            raise ValueError("Silmatha record not found.")
        
        if entity.sil_workflow_status != "PENDING":
            raise ValueError(f"Cannot mark as printing silmatha with workflow status: {entity.sil_workflow_status}. Must be PENDING.")
        
        # Update workflow fields
        entity.sil_workflow_status = "PRINTING"
        entity.sil_updated_by = actor_id
        entity.sil_updated_at = datetime.utcnow()
        entity.sil_version_number += 1
        
        db.commit()
        db.refresh(entity)
        return entity

    def reset_to_pending(
        self,
        db: Session,
        *,
        sil_regn: str,
        actor_id: Optional[str],
    ) -> SilmathaRegist:
        """Reset silmatha workflow status to PENDING - for corrections or resubmissions"""
        entity = silmatha_regist_repo.get_by_regn(db, sil_regn)
        if not entity:
            raise ValueError("Silmatha record not found.")
        
        # Clear workflow fields
        entity.sil_workflow_status = "PENDING"
        entity.sil_approval_status = None
        entity.sil_approved_by = None
        entity.sil_approved_at = None
        entity.sil_rejected_by = None
        entity.sil_rejected_at = None
        entity.sil_rejection_reason = None
        entity.sil_printed_by = None
        entity.sil_printed_at = None
        entity.sil_scanned_by = None
        entity.sil_scanned_at = None
        entity.sil_updated_by = actor_id
        entity.sil_updated_at = datetime.utcnow()
        entity.sil_version_number += 1
        
        db.commit()
        db.refresh(entity)
        return entity

    # --------------------------------------------------------------------- #
    # Reprint Workflow Methods
    # --------------------------------------------------------------------- #
    def request_reprint(
        self,
        db: Session,
        *,
        sil_regn: str,
        actor_id: Optional[str],
        reprint_reason: str,
        reprint_amount: Optional[float] = None,
        reprint_remarks: Optional[str] = None,
    ) -> SilmathaRegist:
        """Request a reprint for a silmatha certificate - initiates reprint workflow"""
        entity = silmatha_regist_repo.get_by_regn(db, sil_regn)
        if not entity:
            raise ValueError("Silmatha record not found.")
        
        # Can only request reprint for completed records
        if entity.sil_workflow_status not in ["COMPLETED", "PRINTED"]:
            raise ValueError(f"Cannot request reprint for silmatha with workflow status: {entity.sil_workflow_status}. Must be COMPLETED or PRINTED.")
        
        # Check if there's already a pending reprint request
        if entity.sil_reprint_status == "REPRINT_PENDING":
            raise ValueError("There is already a pending reprint request for this silmatha.")
        
        # Generate reprint form number
        reprint_form_no = silmatha_regist_repo.generate_next_reprint_form_no(db)
        
        # Set reprint workflow fields
        entity.sil_reprint_status = "REPRINT_PENDING"
        entity.sil_reprint_form_no = reprint_form_no
        entity.sil_reprint_requested_by = actor_id
        entity.sil_reprint_requested_at = datetime.utcnow()
        entity.sil_reprint_request_reason = reprint_reason
        entity.sil_reprint_amount = reprint_amount
        entity.sil_reprint_remarks = reprint_remarks
        # Clear previous reprint approval/rejection data
        entity.sil_reprint_approved_by = None
        entity.sil_reprint_approved_at = None
        entity.sil_reprint_rejected_by = None
        entity.sil_reprint_rejected_at = None
        entity.sil_reprint_rejection_reason = None
        entity.sil_reprint_completed_by = None
        entity.sil_reprint_completed_at = None
        entity.sil_updated_by = actor_id
        entity.sil_updated_at = datetime.utcnow()
        entity.sil_version_number += 1
        
        db.commit()
        db.refresh(entity)
        return entity

    def accept_reprint(
        self,
        db: Session,
        *,
        sil_regn: str,
        actor_id: Optional[str],
    ) -> SilmathaRegist:
        """Accept a reprint request - transitions to REPRINT_ACCEPTED status"""
        entity = silmatha_regist_repo.get_by_regn(db, sil_regn)
        if not entity:
            raise ValueError("Silmatha record not found.")
        
        if entity.sil_reprint_status != "REPRINT_PENDING":
            raise ValueError(f"Cannot accept reprint with status: {entity.sil_reprint_status}. Must be REPRINT_PENDING.")
        
        # Update reprint workflow fields
        entity.sil_reprint_status = "REPRINT_ACCEPTED"
        entity.sil_reprint_approved_by = actor_id
        entity.sil_reprint_approved_at = datetime.utcnow()
        entity.sil_updated_by = actor_id
        entity.sil_updated_at = datetime.utcnow()
        entity.sil_version_number += 1
        
        db.commit()
        db.refresh(entity)
        return entity

    def reject_reprint(
        self,
        db: Session,
        *,
        sil_regn: str,
        actor_id: Optional[str],
        rejection_reason: Optional[str] = None,
    ) -> SilmathaRegist:
        """Reject a reprint request - transitions to REPRINT_REJECTED status"""
        entity = silmatha_regist_repo.get_by_regn(db, sil_regn)
        if not entity:
            raise ValueError("Silmatha record not found.")
        
        if entity.sil_reprint_status != "REPRINT_PENDING":
            raise ValueError(f"Cannot reject reprint with status: {entity.sil_reprint_status}. Must be REPRINT_PENDING.")
        
        # Update reprint workflow fields
        entity.sil_reprint_status = "REPRINT_REJECTED"
        entity.sil_reprint_rejected_by = actor_id
        entity.sil_reprint_rejected_at = datetime.utcnow()
        entity.sil_reprint_rejection_reason = rejection_reason
        entity.sil_updated_by = actor_id
        entity.sil_updated_at = datetime.utcnow()
        entity.sil_version_number += 1
        
        db.commit()
        db.refresh(entity)
        return entity

    def complete_reprint(
        self,
        db: Session,
        *,
        sil_regn: str,
        actor_id: Optional[str],
    ) -> SilmathaRegist:
        """Complete a reprint - transitions to REPRINT_COMPLETED status"""
        entity = silmatha_regist_repo.get_by_regn(db, sil_regn)
        if not entity:
            raise ValueError("Silmatha record not found.")
        
        if entity.sil_reprint_status != "REPRINT_ACCEPTED":
            raise ValueError(f"Cannot complete reprint with status: {entity.sil_reprint_status}. Must be REPRINT_ACCEPTED.")
        
        # Update reprint workflow fields
        entity.sil_reprint_status = "REPRINT_COMPLETED"
        entity.sil_reprint_completed_by = actor_id
        entity.sil_reprint_completed_at = datetime.utcnow()
        entity.sil_updated_by = actor_id
        entity.sil_updated_at = datetime.utcnow()
        entity.sil_version_number += 1
        
        db.commit()
        db.refresh(entity)
        return entity

    # --------------------------------------------------------------------- #
    # Validation Helpers
    # --------------------------------------------------------------------- #
    def _validate_foreign_keys(
        self,
        db: Session,
        payload: Dict[str, Any],
    ) -> None:
        """Validate foreign key references for the provided payload."""
        # Validate sil_province -> cmm_province.cp_code
        self._validate_province_reference(
            db, payload.get("sil_province"), "sil_province"
        )
        
        # Validate sil_district -> cmm_district.dd_dcode
        self._validate_district_reference(
            db, payload.get("sil_district"), "sil_district"
        )
        
        # Validate sil_division -> cmm_divsec.dv_dvcode
        self._validate_division_reference(
            db, payload.get("sil_division"), "sil_division"
        )
        
        # Validate sil_gndiv -> cmm_gndata.gn_gnc
        self._validate_gndiv_reference(
            db, payload.get("sil_gndiv"), "sil_gndiv"
        )
        
        # Validate sil_viharadhipathi -> bhikku_regist.br_regn
        self._validate_bhikku_reference(
            db, payload.get("sil_viharadhipathi"), "sil_viharadhipathi"
        )
        
        # Validate sil_cat -> cmm_cat.cc_code
        self._validate_category_reference(
            db, payload.get("sil_cat"), "sil_cat"
        )
        
        # Validate sil_currstat -> cmm_status.st_statcd
        self._validate_status_reference(
            db, payload.get("sil_currstat"), "sil_currstat"
        )
        
        # Validate sil_mahanaacharyacd -> bhikku_regist.br_regn (can be multiple comma-separated)
        self._validate_mahanaacharyacd_reference(
            db, payload.get("sil_mahanaacharyacd"), "sil_mahanaacharyacd"
        )
        
        # Validate sil_robing_tutor_residence -> vihaddata.vh_trn
        self._validate_vihara_reference(
            db, payload.get("sil_robing_tutor_residence"), "sil_robing_tutor_residence"
        )
        
        # Validate sil_mahanatemple -> vihaddata.vh_trn
        self._validate_vihara_reference(
            db, payload.get("sil_mahanatemple"), "sil_mahanatemple"
        )
        
        # Validate sil_robing_after_residence_temple -> vihaddata.vh_trn
        self._validate_vihara_reference(
            db, payload.get("sil_robing_after_residence_temple"), "sil_robing_after_residence_temple"
        )

    def _validate_province_reference(
        self, db: Session, value: Optional[str], field_name: str
    ) -> None:
        if not self._has_meaningful_value(value):
            return

        exists = (
            db.query(Province.cp_code)
            .filter(
                Province.cp_code == value,
                Province.cp_is_deleted.is_(False),
            )
            .first()
        )
        if not exists:
            raise ValueError(f"Invalid reference: {field_name} '{value}' not found in province table.")

    def _validate_district_reference(
        self, db: Session, value: Optional[str], field_name: str
    ) -> None:
        if not self._has_meaningful_value(value):
            return

        exists = (
            db.query(District.dd_dcode)
            .filter(
                District.dd_dcode == value,
                District.dd_is_deleted.is_(False),
            )
            .first()
        )
        if not exists:
            raise ValueError(f"Invalid reference: {field_name} '{value}' not found in district table.")

    def _validate_division_reference(
        self, db: Session, value: Optional[str], field_name: str
    ) -> None:
        if not self._has_meaningful_value(value):
            return

        exists = (
            db.query(DivisionalSecretariat.dv_dvcode)
            .filter(
                DivisionalSecretariat.dv_dvcode == value,
                DivisionalSecretariat.dv_is_deleted.is_(False),
            )
            .first()
        )
        if not exists:
            raise ValueError(f"Invalid reference: {field_name} '{value}' not found in divisional secretariat table.")

    def _validate_gndiv_reference(
        self, db: Session, value: Optional[str], field_name: str
    ) -> None:
        if not self._has_meaningful_value(value):
            return

        exists = (
            db.query(Gramasewaka.gn_gnc)
            .filter(
                Gramasewaka.gn_gnc == value,
                Gramasewaka.gn_is_deleted.is_(False),
            )
            .first()
        )
        if not exists:
            raise ValueError(f"Invalid reference: {field_name} '{value}' not found in GN division table.")

    def _validate_bhikku_reference(
        self, db: Session, value: Optional[str], field_name: str
    ) -> None:
        if not self._has_meaningful_value(value):
            return

        exists = (
            db.query(Bhikku.br_regn)
            .filter(
                Bhikku.br_regn == value,
                Bhikku.br_is_deleted.is_(False),
            )
            .first()
        )
        if not exists:
            raise ValueError(f"Invalid reference: {field_name} '{value}' not found in bhikku table.")

    def _validate_vihara_reference(
        self, db: Session, value: Optional[str], field_name: str
    ) -> None:
        if not self._has_meaningful_value(value):
            return

        exists = (
            db.query(ViharaData.vh_trn)
            .filter(
                ViharaData.vh_trn == value,
                ViharaData.vh_is_deleted.is_(False),
            )
            .first()
        )
        if not exists:
            raise ValueError(f"Invalid reference: {field_name} '{value}' not found in vihara table.")

    def _validate_category_reference(
        self, db: Session, value: Optional[str], field_name: str
    ) -> None:
        if not self._has_meaningful_value(value):
            return

        from sqlalchemy import text
        exists = db.execute(
            text("SELECT 1 FROM cmm_cat WHERE cc_code = :code AND cc_is_deleted = false LIMIT 1"),
            {"code": value}
        ).first()
        
        if not exists:
            raise ValueError(f"Invalid reference: {field_name} '{value}' not found in category table.")

    def _validate_status_reference(
        self, db: Session, value: Optional[str], field_name: str
    ) -> None:
        if not self._has_meaningful_value(value):
            return

        exists = (
            db.query(StatusData.st_statcd)
            .filter(
                StatusData.st_statcd == value,
                StatusData.st_is_deleted.is_(False),
            )
            .first()
        )
        if not exists:
            raise ValueError(f"Invalid reference: {field_name} '{value}' not found in status table.")

    def _validate_mahanaacharyacd_reference(
        self, db: Session, value: Optional[str], field_name: str
    ) -> None:
        """Validate mahanaacharyacd - can be single br_regn or comma-separated list of br_regn values"""
        if not self._has_meaningful_value(value):
            return

        # Split by comma in case multiple values are provided
        regns = [r.strip() for r in value.split(',') if r.strip()]
        
        for regn in regns:
            exists = (
                db.query(Bhikku.br_regn)
                .filter(
                    Bhikku.br_regn == regn,
                    Bhikku.br_is_deleted.is_(False),
                )
                .first()
            )
            if not exists:
                raise ValueError(f"Invalid reference: {field_name} contains invalid br_regn '{regn}' not found in bhikku table.")

    @staticmethod
    def _has_meaningful_value(value: Any) -> bool:
        """Check if a value is meaningful (not None or empty string)"""
        if value is None:
            return False
        if isinstance(value, str) and value.strip() == "":
            return False
        return True

    def _strip_strings(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Strip whitespace from all string values in the dictionary."""
        for key, value in data.items():
            if isinstance(value, str):
                data[key] = value.strip() if value else None
        return data

    def _normalize_contact_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize contact fields (mobile, email) to None if empty."""
        for field in ["sil_mobile", "sil_fathrsmobile", "sil_email"]:
            if field in data and not data[field]:
                data[field] = None
        return data

    def _validate_contact_formats(self, data: Dict[str, Any]) -> None:
        """Validate mobile number and email formats."""
        # Validate mobile numbers
        for field in ["sil_mobile", "sil_fathrsmobile"]:
            mobile = data.get(field)
            if mobile and not self.MOBILE_PATTERN.match(mobile):
                raise ValueError(f"{field} must be 10 digits starting with 0.")

    def _validate_unique_contact_fields(
        self, db: Session, *, sil_mobile: Optional[str], sil_email: Optional[str], current_regn: Optional[str]
    ) -> None:
        """Ensure mobile and email are unique (excluding current record if updating)."""
        if sil_mobile:
            existing = silmatha_regist_repo.get_by_mobile(db, sil_mobile)
            if existing and existing.sil_regn != current_regn:
                raise ValueError(f"sil_mobile '{sil_mobile}' is already in use.")

        if sil_email:
            existing = silmatha_regist_repo.get_by_email(db, sil_email)
            if existing and existing.sil_regn != current_regn:
                raise ValueError(f"sil_email '{sil_email}' is already in use.")


    # --------------------------------------------------------------------- #
    # File Upload Methods
    # --------------------------------------------------------------------- #
    async def upload_scanned_document(
        self,
        db: Session,
        *,
        sil_regn: str,
        file: UploadFile,
        actor_id: Optional[str],
    ) -> SilmathaRegist:
        """
        Upload a scanned document for a Silmatha record.
        
        Args:
            db: Database session
            sil_regn: Silmatha registration number
            file: Uploaded file (PDF, JPG, PNG - max 5MB)
            actor_id: User ID performing the upload
            
        Returns:
            Updated SilmathaRegist instance with file path stored
            
        Raises:
            ValueError: If silmatha record not found or file upload fails
        """
        # Get the silmatha record
        entity = silmatha_regist_repo.get_by_regn(db, sil_regn)
        if not entity:
            raise ValueError(f"Silmatha record with registration number '{sil_regn}' not found.")
        
        # Delete old file if exists
        if entity.sil_scanned_document_path:
            file_storage_service.delete_file(entity.sil_scanned_document_path)
        
        # Save new file using the file storage service
        # File will be stored at: app/storage/silmatha_update/<year>/<month>/<day>/<sil_regn>/scanned_document_*.*
        relative_path, _ = await file_storage_service.save_file(
            file,
            sil_regn,
            "scanned_document",
            subdirectory="silmatha_update"
        )
        
        # Update the silmatha record with the file path
        entity.sil_scanned_document_path = relative_path
        entity.sil_updated_by = actor_id
        entity.sil_updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(entity)
        
        return entity


silmatha_regist_service = SilmathaRegistService()
