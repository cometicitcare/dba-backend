# app/services/silmatha_id_card_service.py
from typing import Optional, List
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.repositories.silmatha_id_card_repo import silmatha_id_card_repository
from app.repositories.silmatha_regist_repo import silmatha_regist_repo
from app.schemas.silmatha_id_card import (
    SilmathaIDCardCreate,
    SilmathaIDCardUpdate,
    SilmathaIDCardResponse
)
from app.utils.file_storage import file_storage_service
from app.models.silmatha_id_card import SilmathaIDCard


class SilmathaIDCardService:
    """
    Service layer for Silmatha ID Card business logic.
    Handles validation, file uploads, and orchestration between repository and storage.
    """

    def __init__(self):
        self.repository = silmatha_id_card_repository
        self.silmatha_repository = silmatha_regist_repo
        self.file_storage = file_storage_service

    def create_silmatha_id_card(
        self,
        db: Session,
        silmatha_id_card: SilmathaIDCardCreate,
        created_by: Optional[str] = None
    ) -> SilmathaIDCard:
        """
        Create a new Silmatha ID Card.
        
        Validates that:
        1. The sil_regn exists in silmatha_regist table
        2. No ID card already exists for this sil_regn
        
        Args:
            db: Database session
            silmatha_id_card: Create schema
            created_by: Username of creator
            
        Returns:
            Created SilmathaIDCard instance
            
        Raises:
            HTTPException: If validation fails
        """
        # 1. Validate that sil_regn exists
        silmatha = self.silmatha_repository.get_by_regn(db, silmatha_id_card.sic_sil_regn)
        if not silmatha:
            raise HTTPException(
                status_code=404,
                detail=f"Silmatha with registration number '{silmatha_id_card.sic_sil_regn}' not found"
            )
        
        # 2. Check if ID card already exists for this silmatha
        existing_id_card = self.repository.get_by_sil_regn(db, silmatha_id_card.sic_sil_regn)
        if existing_id_card:
            raise HTTPException(
                status_code=400,
                detail=f"ID Card already exists for Silmatha '{silmatha_id_card.sic_sil_regn}'"
            )
        
        # 3. Create the ID card
        try:
            new_id_card = self.repository.create(db, silmatha_id_card, created_by)
            return new_id_card
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Database integrity error: {str(e)}"
            )

    def get_silmatha_id_card_by_id(
        self,
        db: Session,
        sic_id: int
    ) -> SilmathaIDCard:
        """
        Get a Silmatha ID Card by ID.
        
        Args:
            db: Database session
            sic_id: ID of the card
            
        Returns:
            SilmathaIDCard instance
            
        Raises:
            HTTPException: If not found
        """
        id_card = self.repository.get_by_id(db, sic_id)
        if not id_card:
            raise HTTPException(
                status_code=404,
                detail=f"Silmatha ID Card with ID {sic_id} not found"
            )
        return id_card

    def get_silmatha_id_card_by_sil_regn(
        self,
        db: Session,
        sil_regn: str
    ) -> SilmathaIDCard:
        """
        Get a Silmatha ID Card by Silmatha registration number.
        
        Args:
            db: Database session
            sil_regn: Silmatha registration number
            
        Returns:
            SilmathaIDCard instance
            
        Raises:
            HTTPException: If not found
        """
        id_card = self.repository.get_by_sil_regn(db, sil_regn)
        if not id_card:
            raise HTTPException(
                status_code=404,
                detail=f"Silmatha ID Card for registration '{sil_regn}' not found"
            )
        return id_card

    def get_all_silmatha_id_cards(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        workflow_status: Optional[str] = None,
        search_key: Optional[str] = None
    ) -> tuple[List[SilmathaIDCard], int]:
        """
        Get all Silmatha ID Cards with filtering and pagination.
        
        Args:
            db: Database session
            skip: Records to skip
            limit: Max records to return
            workflow_status: Filter by status
            search_key: Search text
            
        Returns:
            Tuple of (list of records, total count)
        """
        return self.repository.get_all(db, skip, limit, workflow_status, search_key)

    def update_silmatha_id_card(
        self,
        db: Session,
        sic_id: int,
        silmatha_id_card: SilmathaIDCardUpdate,
        updated_by: Optional[str] = None
    ) -> SilmathaIDCard:
        """
        Update an existing Silmatha ID Card.
        
        Args:
            db: Database session
            sic_id: ID of the card to update
            silmatha_id_card: Update schema with new data
            updated_by: Username of updater
            
        Returns:
            Updated SilmathaIDCard instance
            
        Raises:
            HTTPException: If not found
        """
        updated_card = self.repository.update(db, sic_id, silmatha_id_card, updated_by)
        if not updated_card:
            raise HTTPException(
                status_code=404,
                detail=f"Silmatha ID Card with ID {sic_id} not found"
            )
        return updated_card

    def delete_silmatha_id_card(
        self,
        db: Session,
        sic_id: int
    ) -> bool:
        """
        Delete a Silmatha ID Card.
        
        Args:
            db: Database session
            sic_id: ID of the card to delete
            
        Returns:
            True if deleted
            
        Raises:
            HTTPException: If not found
        """
        deleted = self.repository.delete(db, sic_id)
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"Silmatha ID Card with ID {sic_id} not found"
            )
        return True

    async def upload_thumbprint(
        self,
        db: Session,
        sic_id: int,
        file: UploadFile
    ) -> SilmathaIDCard:
        """
        Upload left thumbprint image for a Silmatha ID Card.
        
        Args:
            db: Database session
            sic_id: ID of the card
            file: Thumbprint image file
            
        Returns:
            Updated SilmathaIDCard instance
            
        Raises:
            HTTPException: If card not found or upload fails
        """
        # 1. Verify card exists
        id_card = self.get_silmatha_id_card_by_id(db, sic_id)
        
        # 2. Upload file
        try:
            relative_path, _ = await self.file_storage.save_file(
                file,
                id_card.sic_sil_regn,
                "left_thumbprint",
                subdirectory="silmatha_id"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"File upload failed: {str(e)}"
            )
        
        # 3. Update database
        updated_card = self.repository.update_thumbprint_url(db, sic_id, relative_path)
        if not updated_card:
            raise HTTPException(
                status_code=404,
                detail=f"Silmatha ID Card with ID {sic_id} not found"
            )
        
        return updated_card

    async def upload_applicant_photo(
        self,
        db: Session,
        sic_id: int,
        file: UploadFile
    ) -> SilmathaIDCard:
        """
        Upload applicant photo for a Silmatha ID Card.
        
        Args:
            db: Database session
            sic_id: ID of the card
            file: Photo file
            
        Returns:
            Updated SilmathaIDCard instance
            
        Raises:
            HTTPException: If card not found or upload fails
        """
        # 1. Verify card exists
        id_card = self.get_silmatha_id_card_by_id(db, sic_id)
        
        # 2. Upload file
        try:
            relative_path, _ = await self.file_storage.save_file(
                file,
                id_card.sic_sil_regn,
                "applicant_photo",
                subdirectory="silmatha_id"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"File upload failed: {str(e)}"
            )
        
        # 3. Update database
        updated_card = self.repository.update_photo_url(db, sic_id, relative_path)
        if not updated_card:
            raise HTTPException(
                status_code=404,
                detail=f"Silmatha ID Card with ID {sic_id} not found"
            )
        
        return updated_card

    def approve_silmatha_id_card(
        self,
        db: Session,
        sic_id: int,
        approved_by: str
    ) -> SilmathaIDCard:
        """
        Approve a Silmatha ID Card.
        
        Args:
            db: Database session
            sic_id: ID of the card
            approved_by: Username of approver
            
        Returns:
            Updated SilmathaIDCard instance
            
        Raises:
            HTTPException: If not found or workflow error
        """
        # Verify card exists and check status
        id_card = self.get_silmatha_id_card_by_id(db, sic_id)
        
        if id_card.sic_workflow_status == "APPROVED":
            raise HTTPException(
                status_code=400,
                detail=f"ID Card {id_card.sic_form_no} is already approved"
            )
        
        approved_card = self.repository.approve(db, sic_id, approved_by)
        if not approved_card:
            raise HTTPException(
                status_code=404,
                detail=f"Silmatha ID Card with ID {sic_id} not found"
            )
        
        return approved_card

    def reject_silmatha_id_card(
        self,
        db: Session,
        sic_id: int,
        rejected_by: str,
        rejection_reason: str
    ) -> SilmathaIDCard:
        """
        Reject a Silmatha ID Card.
        
        Args:
            db: Database session
            sic_id: ID of the card
            rejected_by: Username of rejecter
            rejection_reason: Reason for rejection
            
        Returns:
            Updated SilmathaIDCard instance
            
        Raises:
            HTTPException: If not found or workflow error
        """
        # Verify card exists
        id_card = self.get_silmatha_id_card_by_id(db, sic_id)
        
        if not rejection_reason or rejection_reason.strip() == "":
            raise HTTPException(
                status_code=400,
                detail="Rejection reason is required"
            )
        
        rejected_card = self.repository.reject(db, sic_id, rejected_by, rejection_reason)
        if not rejected_card:
            raise HTTPException(
                status_code=404,
                detail=f"Silmatha ID Card with ID {sic_id} not found"
            )
        
        return rejected_card

    def mark_silmatha_id_card_printed(
        self,
        db: Session,
        sic_id: int,
        printed_by: str
    ) -> SilmathaIDCard:
        """
        Mark a Silmatha ID Card as printed.
        
        Args:
            db: Database session
            sic_id: ID of the card
            printed_by: Username of printer
            
        Returns:
            Updated SilmathaIDCard instance
            
        Raises:
            HTTPException: If not found or workflow error
        """
        # Verify card exists and is approved
        id_card = self.get_silmatha_id_card_by_id(db, sic_id)
        
        if id_card.sic_workflow_status != "APPROVED":
            raise HTTPException(
                status_code=400,
                detail=f"ID Card {id_card.sic_form_no} must be approved before marking as printed. Current status: {id_card.sic_workflow_status}"
            )
        
        printed_card = self.repository.mark_printed(db, sic_id, printed_by)
        if not printed_card:
            raise HTTPException(
                status_code=404,
                detail=f"Silmatha ID Card with ID {sic_id} not found"
            )
        
        return printed_card


# Singleton instance
silmatha_id_card_service = SilmathaIDCardService()
