# app/services/bhikku_id_card_service.py
from typing import Optional, List
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.repositories.bhikku_id_card_repo import bhikku_id_card_repository
from app.repositories.bhikku_repo import BhikkuRepository
from app.schemas.bhikku_id_card import (
    BhikkuIDCardCreate,
    BhikkuIDCardUpdate,
    BhikkuIDCardResponse
)
from app.utils.file_storage import file_storage_service
from app.models.bhikku_id_card import BhikkuIDCard


class BhikkuIDCardService:
    """
    Service layer for Bhikku ID Card business logic.
    Handles validation, file uploads, and orchestration between repository and storage.
    """

    def __init__(self):
        self.repository = bhikku_id_card_repository
        self.bhikku_repository = BhikkuRepository()
        self.file_storage = file_storage_service

    def create_bhikku_id_card(
        self,
        db: Session,
        bhikku_id_card: BhikkuIDCardCreate,
        created_by: Optional[str] = None
    ) -> BhikkuIDCard:
        """
        Create a new Bhikku ID Card.
        
        Validates that:
        1. The br_regn exists in bhikku_regist table
        2. No ID card already exists for this br_regn
        
        Args:
            db: Database session
            bhikku_id_card: Create schema
            created_by: Username of creator
            
        Returns:
            Created BhikkuIDCard instance
            
        Raises:
            HTTPException: If validation fails
        """
        # 1. Validate that br_regn exists
        bhikku = self.bhikku_repository.get_by_regn(db, bhikku_id_card.bic_br_regn)
        if not bhikku:
            raise HTTPException(
                status_code=404,
                detail=f"Bhikku with registration number '{bhikku_id_card.bic_br_regn}' not found"
            )
        
        # 2. Check if ID card already exists for this bhikku
        existing_id_card = self.repository.get_by_br_regn(db, bhikku_id_card.bic_br_regn)
        if existing_id_card:
            raise HTTPException(
                status_code=400,
                detail=f"ID Card already exists for Bhikku '{bhikku_id_card.bic_br_regn}'"
            )
        
        # 3. Create the ID card
        try:
            new_id_card = self.repository.create(db, bhikku_id_card, created_by)
            return new_id_card
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Database integrity error: {str(e)}"
            )

    def get_bhikku_id_card_by_id(
        self,
        db: Session,
        bic_id: int
    ) -> BhikkuIDCard:
        """
        Get a Bhikku ID Card by ID.
        
        Args:
            db: Database session
            bic_id: ID of the card
            
        Returns:
            BhikkuIDCard instance
            
        Raises:
            HTTPException: If not found
        """
        id_card = self.repository.get_by_id(db, bic_id)
        if not id_card:
            raise HTTPException(
                status_code=404,
                detail=f"Bhikku ID Card with ID {bic_id} not found"
            )
        return id_card

    def get_bhikku_id_card_by_br_regn(
        self,
        db: Session,
        br_regn: str
    ) -> BhikkuIDCard:
        """
        Get a Bhikku ID Card by Bhikku registration number.
        
        Args:
            db: Database session
            br_regn: Bhikku registration number
            
        Returns:
            BhikkuIDCard instance
            
        Raises:
            HTTPException: If not found
        """
        id_card = self.repository.get_by_br_regn(db, br_regn)
        if not id_card:
            raise HTTPException(
                status_code=404,
                detail=f"Bhikku ID Card for registration '{br_regn}' not found"
            )
        return id_card

    def get_all_bhikku_id_cards(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        workflow_status: Optional[str] = None,
        search_key: Optional[str] = None
    ) -> tuple[List[BhikkuIDCard], int]:
        """
        Get all Bhikku ID Cards with filtering and pagination.
        
        Args:
            db: Database session
            skip: Records to skip
            limit: Max records to return
            workflow_status: Filter by status
            search_key: Search text
            
        Returns:
            Tuple of (list of cards, total count)
        """
        return self.repository.get_all(
            db,
            skip=skip,
            limit=limit,
            workflow_status=workflow_status,
            search_key=search_key
        )

    def update_bhikku_id_card(
        self,
        db: Session,
        bic_id: int,
        bhikku_id_card_update: BhikkuIDCardUpdate,
        updated_by: Optional[str] = None
    ) -> BhikkuIDCard:
        """
        Update a Bhikku ID Card.
        
        Args:
            db: Database session
            bic_id: ID of the card to update
            bhikku_id_card_update: Update data
            updated_by: Username of updater
            
        Returns:
            Updated BhikkuIDCard instance
            
        Raises:
            HTTPException: If not found
        """
        updated_card = self.repository.update(db, bic_id, bhikku_id_card_update, updated_by)
        if not updated_card:
            raise HTTPException(
                status_code=404,
                detail=f"Bhikku ID Card with ID {bic_id} not found"
            )
        return updated_card

    def delete_bhikku_id_card(
        self,
        db: Session,
        bic_id: int
    ) -> dict:
        """
        Soft delete a Bhikku ID Card.
        
        Args:
            db: Database session
            bic_id: ID of the card to delete
            
        Returns:
            Success message dict
            
        Raises:
            HTTPException: If not found
        """
        success = self.repository.delete(db, bic_id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Bhikku ID Card with ID {bic_id} not found"
            )
        return {"message": "Bhikku ID Card deleted successfully"}

    def approve_bhikku_id_card(
        self,
        db: Session,
        bic_id: int,
        approved_by: str
    ) -> BhikkuIDCard:
        """
        Approve a Bhikku ID Card.
        
        Args:
            db: Database session
            bic_id: ID of the card
            approved_by: Username of approver
            
        Returns:
            Updated BhikkuIDCard instance
            
        Raises:
            HTTPException: If not found or invalid state
        """
        # Check if card exists and is in valid state for approval
        card = self.get_bhikku_id_card_by_id(db, bic_id)
        
        if card.bic_workflow_status == "APPROVED":
            raise HTTPException(
                status_code=400,
                detail="ID Card is already approved"
            )
        
        if card.bic_workflow_status == "REJECTED":
            raise HTTPException(
                status_code=400,
                detail="Cannot approve a rejected ID Card. Please create a new one."
            )
        
        approved_card = self.repository.approve(db, bic_id, approved_by)
        if not approved_card:
            raise HTTPException(
                status_code=404,
                detail=f"Bhikku ID Card with ID {bic_id} not found"
            )
        return approved_card

    def reject_bhikku_id_card(
        self,
        db: Session,
        bic_id: int,
        rejected_by: str,
        rejection_reason: str
    ) -> BhikkuIDCard:
        """
        Reject a Bhikku ID Card.
        
        Args:
            db: Database session
            bic_id: ID of the card
            rejected_by: Username of rejecter
            rejection_reason: Reason for rejection
            
        Returns:
            Updated BhikkuIDCard instance
            
        Raises:
            HTTPException: If not found or invalid state
        """
        # Check if card exists
        card = self.get_bhikku_id_card_by_id(db, bic_id)
        
        if card.bic_workflow_status == "REJECTED":
            raise HTTPException(
                status_code=400,
                detail="ID Card is already rejected"
            )
        
        if not rejection_reason or not rejection_reason.strip():
            raise HTTPException(
                status_code=400,
                detail="Rejection reason is required"
            )
        
        rejected_card = self.repository.reject(db, bic_id, rejected_by, rejection_reason)
        if not rejected_card:
            raise HTTPException(
                status_code=404,
                detail=f"Bhikku ID Card with ID {bic_id} not found"
            )
        return rejected_card

    def mark_bhikku_id_card_printed(
        self,
        db: Session,
        bic_id: int,
        printed_by: str
    ) -> BhikkuIDCard:
        """
        Mark a Bhikku ID Card as printed.
        
        Args:
            db: Database session
            bic_id: ID of the card
            printed_by: Username who marked as printed
            
        Returns:
            Updated BhikkuIDCard instance
            
        Raises:
            HTTPException: If not found or not approved
        """
        # Check if card exists and is approved
        card = self.get_bhikku_id_card_by_id(db, bic_id)
        
        if card.bic_workflow_status != "APPROVED":
            raise HTTPException(
                status_code=400,
                detail="Only approved ID Cards can be marked as printed"
            )
        
        printed_card = self.repository.mark_printed(db, bic_id, printed_by)
        if not printed_card:
            raise HTTPException(
                status_code=404,
                detail=f"Bhikku ID Card with ID {bic_id} not found"
            )
        return printed_card

    async def upload_thumbprint(
        self,
        db: Session,
        bic_id: int,
        file: UploadFile
    ) -> BhikkuIDCard:
        """
        Upload left thumbprint image for a Bhikku ID Card.
        
        Args:
            db: Database session
            bic_id: ID of the card
            file: Uploaded file
            
        Returns:
            Updated BhikkuIDCard instance
            
        Raises:
            HTTPException: If card not found or upload fails
        """
        # Get the card
        card = self.get_bhikku_id_card_by_id(db, bic_id)
        
        # Delete old file if exists
        if card.bic_left_thumbprint_url:
            self.file_storage.delete_file(card.bic_left_thumbprint_url)
        
        # Save new file
        # File will be stored at: app/storage/bhikku_id/<year>/<month>/<day>/<br_regn>/left_thumbprint_*.*
        relative_path, _ = await self.file_storage.save_file(
            file,
            card.bic_br_regn,
            "left_thumbprint",
            subdirectory="bhikku_id"
        )
        
        # Update database
        updated_card = self.repository.update_file_paths(
            db,
            bic_id,
            thumbprint_url=relative_path
        )
        
        if not updated_card:
            raise HTTPException(
                status_code=404,
                detail=f"Bhikku ID Card with ID {bic_id} not found"
            )
        
        return updated_card

    async def upload_applicant_photo(
        self,
        db: Session,
        bic_id: int,
        file: UploadFile
    ) -> BhikkuIDCard:
        """
        Upload applicant photo for a Bhikku ID Card.
        
        Args:
            db: Database session
            bic_id: ID of the card
            file: Uploaded file
            
        Returns:
            Updated BhikkuIDCard instance
            
        Raises:
            HTTPException: If card not found or upload fails
        """
        # Get the card
        card = self.get_bhikku_id_card_by_id(db, bic_id)
        
        # Delete old file if exists
        if card.bic_applicant_photo_url:
            self.file_storage.delete_file(card.bic_applicant_photo_url)
        
        # Save new file
        # File will be stored at: app/storage/bhikku_id/<year>/<month>/<day>/<br_regn>/applicant_photo_*.*
        relative_path, _ = await self.file_storage.save_file(
            file,
            card.bic_br_regn,
            "applicant_photo",
            subdirectory="bhikku_id"
        )
        
        # Update database
        updated_card = self.repository.update_file_paths(
            db,
            bic_id,
            photo_url=relative_path
        )
        
        if not updated_card:
            raise HTTPException(
                status_code=404,
                detail=f"Bhikku ID Card with ID {bic_id} not found"
            )
        
        return updated_card


    # ===== Workflow Methods =====

    def approve_bhikku_id_card(
        self,
        db: Session,
        *,
        bic_id: Optional[int] = None,
        bic_form_no: Optional[str] = None,
        actor_id: Optional[str],
    ) -> BhikkuIDCard:
        """
        Approve a Bhikku ID Card - transitions workflow to APPROVED status.
        
        Args:
            db: Database session
            bic_id: ID of the card (optional if form_no provided)
            bic_form_no: Form number of the card (optional if bic_id provided)
            actor_id: Username of the approver
            
        Returns:
            Updated BhikkuIDCard instance
            
        Raises:
            ValueError: If card not found or not in PENDING status
        """
        # Get the card by ID or form number
        if bic_id:
            entity = self.repository.get_by_id(db, bic_id)
        elif bic_form_no:
            entity = self.repository.get_by_form_no(db, bic_form_no)
        else:
            raise ValueError("Either bic_id or bic_form_no must be provided")
        
        if not entity:
            raise ValueError("Bhikku ID Card record not found.")
        
        if entity.bic_workflow_status != "PENDING":
            raise ValueError(
                f"Cannot approve ID card with workflow status: {entity.bic_workflow_status}. Must be PENDING."
            )
        
        # Update workflow fields
        from datetime import datetime
        entity.bic_workflow_status = "APPROVED"
        entity.bic_approved_by = actor_id
        entity.bic_approved_at = datetime.utcnow()
        entity.bic_updated_by = actor_id
        entity.bic_updated_at = datetime.utcnow()
        entity.bic_version_number += 1
        
        db.commit()
        db.refresh(entity)
        return entity

    def reject_bhikku_id_card(
        self,
        db: Session,
        *,
        bic_id: Optional[int] = None,
        bic_form_no: Optional[str] = None,
        actor_id: Optional[str],
        rejection_reason: Optional[str] = None,
    ) -> BhikkuIDCard:
        """
        Reject a Bhikku ID Card - transitions workflow to REJECTED status.
        
        Args:
            db: Database session
            bic_id: ID of the card (optional if form_no provided)
            bic_form_no: Form number of the card (optional if bic_id provided)
            actor_id: Username of the rejector
            rejection_reason: Reason for rejection
            
        Returns:
            Updated BhikkuIDCard instance
            
        Raises:
            ValueError: If card not found or not in PENDING status
        """
        # Get the card by ID or form number
        if bic_id:
            entity = self.repository.get_by_id(db, bic_id)
        elif bic_form_no:
            entity = self.repository.get_by_form_no(db, bic_form_no)
        else:
            raise ValueError("Either bic_id or bic_form_no must be provided")
        
        if not entity:
            raise ValueError("Bhikku ID Card record not found.")
        
        if entity.bic_workflow_status != "PENDING":
            raise ValueError(
                f"Cannot reject ID card with workflow status: {entity.bic_workflow_status}. Must be PENDING."
            )
        
        # Update workflow fields
        from datetime import datetime
        entity.bic_workflow_status = "REJECTED"
        entity.bic_rejected_by = actor_id
        entity.bic_rejected_at = datetime.utcnow()
        entity.bic_rejection_reason = rejection_reason
        entity.bic_updated_by = actor_id
        entity.bic_updated_at = datetime.utcnow()
        entity.bic_version_number += 1
        
        db.commit()
        db.refresh(entity)
        return entity

    def mark_printing_complete(
        self,
        db: Session,
        *,
        bic_id: Optional[int] = None,
        bic_form_no: Optional[str] = None,
        actor_id: Optional[str],
    ) -> BhikkuIDCard:
        """
        Mark Bhikku ID Card printing as complete - transitions workflow to PRINTING_COMPLETE status.
        
        Args:
            db: Database session
            bic_id: ID of the card (optional if form_no provided)
            bic_form_no: Form number of the card (optional if bic_id provided)
            actor_id: Username who completed printing
            
        Returns:
            Updated BhikkuIDCard instance
            
        Raises:
            ValueError: If card not found or not in APPROVED status
        """
        # Get the card by ID or form number
        if bic_id:
            entity = self.repository.get_by_id(db, bic_id)
        elif bic_form_no:
            entity = self.repository.get_by_form_no(db, bic_form_no)
        else:
            raise ValueError("Either bic_id or bic_form_no must be provided")
        
        if not entity:
            raise ValueError("Bhikku ID Card record not found.")
        
        if entity.bic_workflow_status != "APPROVED":
            raise ValueError(
                f"Cannot mark as printing complete for ID card with workflow status: {entity.bic_workflow_status}. Must be APPROVED."
            )
        
        # Update workflow fields
        from datetime import datetime
        entity.bic_workflow_status = "PRINTING_COMPLETE"
        entity.bic_printed_by = actor_id
        entity.bic_printed_at = datetime.utcnow()
        entity.bic_updated_by = actor_id
        entity.bic_updated_at = datetime.utcnow()
        entity.bic_version_number += 1
        
        db.commit()
        db.refresh(entity)
        return entity

    def mark_completed(
        self,
        db: Session,
        *,
        bic_id: Optional[int] = None,
        bic_form_no: Optional[str] = None,
        actor_id: Optional[str],
    ) -> BhikkuIDCard:
        """
        Mark Bhikku ID Card as completed - final workflow status.
        
        Args:
            db: Database session
            bic_id: ID of the card (optional if form_no provided)
            bic_form_no: Form number of the card (optional if bic_id provided)
            actor_id: Username who completed the workflow
            
        Returns:
            Updated BhikkuIDCard instance
            
        Raises:
            ValueError: If card not found or not in PRINTING_COMPLETE status
        """
        # Get the card by ID or form number
        if bic_id:
            entity = self.repository.get_by_id(db, bic_id)
        elif bic_form_no:
            entity = self.repository.get_by_form_no(db, bic_form_no)
        else:
            raise ValueError("Either bic_id or bic_form_no must be provided")
        
        if not entity:
            raise ValueError("Bhikku ID Card record not found.")
        
        if entity.bic_workflow_status != "PRINTING_COMPLETE":
            raise ValueError(
                f"Cannot mark as completed for ID card with workflow status: {entity.bic_workflow_status}. Must be PRINTING_COMPLETE."
            )
        
        # Update workflow fields
        from datetime import datetime
        entity.bic_workflow_status = "COMPLETED"
        entity.bic_completed_by = actor_id
        entity.bic_completed_at = datetime.utcnow()
        entity.bic_updated_by = actor_id
        entity.bic_updated_at = datetime.utcnow()
        entity.bic_version_number += 1
        
        db.commit()
        db.refresh(entity)
        return entity


# Singleton instance
bhikku_id_card_service = BhikkuIDCardService()
