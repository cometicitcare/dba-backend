# app/services/silmatha_regist_service.py
from __future__ import annotations

import re
from datetime import datetime, date
from typing import Any, Dict, Optional

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.silmatha_regist import SilmathaRegist
from app.models.user import UserAccount
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

        # Auto-assign district from user's location if user is a DISTRICT_BRANCH user
        if current_user:
            from app.services.location_access_control_service import LocationAccessControlService
            user_district_codes = LocationAccessControlService.get_user_district_codes(db, current_user)
            
            # If user has a specific district assignment, auto-assign it to the silmatha record
            if user_district_codes and len(user_district_codes) == 1:
                # Only auto-assign if sil_district is not explicitly provided in payload
                if not payload_dict.get("sil_district"):
                    payload_dict["sil_district"] = user_district_codes[0]
            
            # Auto-assign province from user's location if available
            user_province_codes = LocationAccessControlService.get_user_province_codes(db, current_user)
            if user_province_codes and len(user_province_codes) == 1:
                # Only auto-assign if sil_province is not explicitly provided in payload
                if not payload_dict.get("sil_province"):
                    payload_dict["sil_province"] = user_province_codes[0]

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

    def approve_silmatha(self, db: Session, *, sil_regn: str, actor_id: Optional[str]) -> SilmathaRegist:
        """Approve a silmatha registration."""
        existing = silmatha_regist_repo.get_by_regn(db, sil_regn)
        if not existing:
            raise ValueError(f"Silmatha record with regn '{sil_regn}' not found.")

        if existing.sil_workflow_status == "APPROVED":
            raise ValueError(f"Silmatha record '{sil_regn}' is already approved.")

        update_data = SilmathaRegistUpdate(
            sil_workflow_status="APPROVED",
            sil_approval_status="APPROVED",
            sil_approved_by=actor_id,
            sil_approved_at=datetime.utcnow(),
            sil_updated_by=actor_id
        )

        updated = silmatha_regist_repo.update(db, sil_regn, update_data)
        if not updated:
            raise ValueError(f"Failed to approve silmatha record '{sil_regn}'.")
        return updated

    def reject_silmatha(self, db: Session, *, sil_regn: str, rejection_reason: str, actor_id: Optional[str]) -> SilmathaRegist:
        """Reject a silmatha registration."""
        existing = silmatha_regist_repo.get_by_regn(db, sil_regn)
        if not existing:
            raise ValueError(f"Silmatha record with regn '{sil_regn}' not found.")

        if existing.sil_workflow_status == "REJECTED":
            raise ValueError(f"Silmatha record '{sil_regn}' is already rejected.")

        update_data = SilmathaRegistUpdate(
            sil_workflow_status="REJECTED",
            sil_approval_status="REJECTED",
            sil_rejected_by=actor_id,
            sil_rejected_at=datetime.utcnow(),
            sil_rejection_reason=rejection_reason,
            sil_updated_by=actor_id
        )

        updated = silmatha_regist_repo.update(db, sil_regn, update_data)
        if not updated:
            raise ValueError(f"Failed to reject silmatha record '{sil_regn}'.")
        return updated

    def mark_printed(self, db: Session, *, sil_regn: str, actor_id: Optional[str]) -> SilmathaRegist:
        """Mark a silmatha registration as printed."""
        existing = silmatha_regist_repo.get_by_regn(db, sil_regn)
        if not existing:
            raise ValueError(f"Silmatha record with regn '{sil_regn}' not found.")

        if existing.sil_workflow_status != "APPROVED":
            raise ValueError(f"Silmatha record '{sil_regn}' must be approved before printing.")

        update_data = SilmathaRegistUpdate(
            sil_workflow_status="PRINTED",
            sil_printed_by=actor_id,
            sil_printed_at=datetime.utcnow(),
            sil_updated_by=actor_id
        )

        updated = silmatha_regist_repo.update(db, sil_regn, update_data)
        if not updated:
            raise ValueError(f"Failed to mark silmatha record '{sil_regn}' as printed.")
        return updated

    def mark_scanned(self, db: Session, *, sil_regn: str, scanned_document_path: str, actor_id: Optional[str]) -> SilmathaRegist:
        """Mark a silmatha registration as scanned."""
        existing = silmatha_regist_repo.get_by_regn(db, sil_regn)
        if not existing:
            raise ValueError(f"Silmatha record with regn '{sil_regn}' not found.")

        update_data = SilmathaRegistUpdate(
            sil_workflow_status="SCANNED",
            sil_scanned_by=actor_id,
            sil_scanned_at=datetime.utcnow(),
            sil_scanned_document_path=scanned_document_path,
            sil_updated_by=actor_id
        )

        updated = silmatha_regist_repo.update(db, sil_regn, update_data)
        if not updated:
            raise ValueError(f"Failed to mark silmatha record '{sil_regn}' as scanned.")
        return updated

    def mark_printing(
        self,
        db: Session,
        *,
        sil_regn: str,
        actor_id: Optional[str],
    ) -> SilmathaRegist:
        """Mark silmatha certificate as in printing process - transitions workflow to PRINTING status"""
        entity = silmatha_regist_repo.get_by_regn(db, sil_regn)
        if not entity:
            raise ValueError("Silmatha record not found.")
        
        if entity.sil_workflow_status != "APPROVED":
            raise ValueError(f"Cannot mark as printing silmatha with workflow status: {entity.sil_workflow_status}. Must be APPROVED.")
        
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
        
        # Set reprint workflow fields
        entity.sil_reprint_status = "REPRINT_PENDING"
        entity.sil_reprint_requested_by = actor_id
        entity.sil_reprint_requested_at = datetime.utcnow()
        entity.sil_reprint_request_reason = reprint_reason
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
