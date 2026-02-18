# app/repositories/silmatha_id_card_repo.py
from datetime import datetime
from typing import Optional, List
from sqlalchemy import func, or_, and_
from sqlalchemy.orm import Session

from app.models.silmatha_id_card import SilmathaIDCard
from app.schemas.silmatha_id_card import SilmathaIDCardCreate, SilmathaIDCardUpdate


class SilmathaIDCardRepository:
    """
    Repository for Silmatha ID Card CRUD operations.
    Handles database interactions and form number generation.
    """

    def generate_next_form_no(self, db: Session) -> str:
        """
        Generate the next unique form number in format: SIC{YEAR}{SEQUENCE}.
        
        Example: SIC2025000001, SIC2025000002, etc.
        
        Args:
            db: Database session
            
        Returns:
            Unique form number string
        """
        current_year = datetime.utcnow().year
        prefix = f"SIC{current_year}"

        # Find the latest form number for this year
        latest = (
            db.query(SilmathaIDCard)
            .filter(SilmathaIDCard.sic_form_no.like(f"{prefix}%"))
            .order_by(SilmathaIDCard.sic_form_no.desc())
            .first()
        )

        if latest:
            try:
                # Extract sequence part after prefix (SIC2025000001 -> 000001)
                sequence_part = latest.sic_form_no[len(prefix):]
                last_sequence = int(sequence_part)
                next_sequence = last_sequence + 1
            except (ValueError, IndexError):
                next_sequence = 1
        else:
            next_sequence = 1

        return f"{prefix}{next_sequence:06d}"

    def create(
        self, 
        db: Session, 
        silmatha_id_card: SilmathaIDCardCreate,
        created_by: Optional[str] = None
    ) -> SilmathaIDCard:
        """
        Create a new Silmatha ID Card record.
        Auto-generates form number and sets workflow status to PENDING.
        
        Args:
            db: Database session
            silmatha_id_card: Create schema with data
            created_by: Username of creator
            
        Returns:
            Created SilmathaIDCard model instance
        """
        # Generate unique form number
        form_no = self.generate_next_form_no(db)
        
        # Convert stay_history to dict format if present
        stay_history_data = None
        if silmatha_id_card.sic_stay_history:
            stay_history_data = [item.model_dump() for item in silmatha_id_card.sic_stay_history]
        
        # Create DB model
        db_silmatha_id_card = SilmathaIDCard(
            sic_sil_regn=silmatha_id_card.sic_sil_regn,
            sic_form_no=form_no,
            sic_divisional_secretariat=silmatha_id_card.sic_divisional_secretariat,
            sic_district=silmatha_id_card.sic_district,
            sic_full_silmatha_name=silmatha_id_card.sic_full_silmatha_name,
            sic_title_post=silmatha_id_card.sic_title_post,
            sic_lay_name_full=silmatha_id_card.sic_lay_name_full,
            sic_dob=silmatha_id_card.sic_dob,
            sic_birth_place=silmatha_id_card.sic_birth_place,
            sic_robing_date=silmatha_id_card.sic_robing_date,
            sic_robing_place=silmatha_id_card.sic_robing_place,
            sic_robing_nikaya=silmatha_id_card.sic_robing_nikaya,
            sic_robing_parshawaya=silmatha_id_card.sic_robing_parshawaya,
            sic_samaneri_reg_no=silmatha_id_card.sic_samaneri_reg_no,
            sic_dasa_sil_mata_reg_no=silmatha_id_card.sic_dasa_sil_mata_reg_no,
            sic_higher_ord_date=silmatha_id_card.sic_higher_ord_date,
            sic_higher_ord_name=silmatha_id_card.sic_higher_ord_name,
            sic_perm_residence=silmatha_id_card.sic_perm_residence,
            sic_national_id=silmatha_id_card.sic_national_id,
            sic_stay_history=stay_history_data,
            # New ID Card Print Fields
            sic_category=silmatha_id_card.sic_category,
            sic_name_s=silmatha_id_card.sic_name_s,
            sic_arama_name_e=silmatha_id_card.sic_arama_name_e,
            sic_arama_name_s=silmatha_id_card.sic_arama_name_s,
            sic_sasun_date=silmatha_id_card.sic_sasun_date,
            sic_district_s=silmatha_id_card.sic_district_s,
            sic_division_s=silmatha_id_card.sic_division_s,
            sic_reg_no=silmatha_id_card.sic_reg_no,
            sic_reg_date=silmatha_id_card.sic_reg_date,
            sic_issue_date=silmatha_id_card.sic_issue_date,
            sic_workflow_status="PENDING",  # Default status
            sic_created_by=created_by,
        )
        
        db.add(db_silmatha_id_card)
        db.commit()
        db.refresh(db_silmatha_id_card)
        
        return db_silmatha_id_card

    def get_by_id(self, db: Session, sic_id: int) -> Optional[SilmathaIDCard]:
        """
        Get a Silmatha ID Card by ID.
        
        Args:
            db: Database session
            sic_id: Primary key ID
            
        Returns:
            SilmathaIDCard instance or None
        """
        return (
            db.query(SilmathaIDCard)
            .filter(SilmathaIDCard.sic_id == sic_id)
            .first()
        )

    def get_by_sil_regn(self, db: Session, sil_regn: str) -> Optional[SilmathaIDCard]:
        """
        Get a Silmatha ID Card by Silmatha registration number.
        
        Args:
            db: Database session
            sil_regn: Silmatha registration number
            
        Returns:
            SilmathaIDCard instance or None
        """
        return (
            db.query(SilmathaIDCard)
            .filter(SilmathaIDCard.sic_sil_regn == sil_regn)
            .first()
        )

    def get_by_form_no(self, db: Session, form_no: str) -> Optional[SilmathaIDCard]:
        """
        Get a Silmatha ID Card by form number.
        
        Args:
            db: Database session
            form_no: Form number
            
        Returns:
            SilmathaIDCard instance or None
        """
        return (
            db.query(SilmathaIDCard)
            .filter(SilmathaIDCard.sic_form_no == form_no)
            .first()
        )

    def get_all(
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
            workflow_status: Filter by workflow status
            search_key: Search in name, regn, form_no, national_id
            
        Returns:
            Tuple of (list of records, total count)
        """
        query = db.query(SilmathaIDCard)

        # Filter by workflow status
        if workflow_status:
            query = query.filter(SilmathaIDCard.sic_workflow_status == workflow_status)

        # Search filter
        if search_key:
            search_pattern = f"%{search_key}%"
            query = query.filter(
                or_(
                    SilmathaIDCard.sic_full_silmatha_name.ilike(search_pattern),
                    SilmathaIDCard.sic_sil_regn.ilike(search_pattern),
                    SilmathaIDCard.sic_form_no.ilike(search_pattern),
                    SilmathaIDCard.sic_national_id.ilike(search_pattern),
                    SilmathaIDCard.sic_lay_name_full.ilike(search_pattern)
                )
            )

        # Get total count
        total = query.count()

        # Apply pagination
        records = query.order_by(SilmathaIDCard.sic_created_at.desc()).offset(skip).limit(limit).all()

        return records, total

    def update(
        self,
        db: Session,
        sic_id: int,
        silmatha_id_card: SilmathaIDCardUpdate,
        updated_by: Optional[str] = None
    ) -> Optional[SilmathaIDCard]:
        """
        Update an existing Silmatha ID Card.
        
        Args:
            db: Database session
            sic_id: ID of the card to update
            silmatha_id_card: Update schema with new data
            updated_by: Username of updater
            
        Returns:
            Updated SilmathaIDCard instance or None if not found
        """
        db_record = self.get_by_id(db, sic_id)
        if not db_record:
            return None

        # Update fields
        update_data = silmatha_id_card.model_dump(exclude_unset=True)
        
        # Handle stay_history conversion
        if "sic_stay_history" in update_data and update_data["sic_stay_history"] is not None:
            update_data["sic_stay_history"] = [
                item.model_dump() for item in update_data["sic_stay_history"]
            ]
        
        for field, value in update_data.items():
            setattr(db_record, field, value)

        db_record.sic_updated_by = updated_by
        
        db.commit()
        db.refresh(db_record)
        
        return db_record

    def delete(self, db: Session, sic_id: int) -> bool:
        """
        Hard delete a Silmatha ID Card.
        
        Args:
            db: Database session
            sic_id: ID of the card to delete
            
        Returns:
            True if deleted, False if not found
        """
        db_record = self.get_by_id(db, sic_id)
        if not db_record:
            return False

        db.delete(db_record)
        db.commit()
        
        return True

    def update_thumbprint_url(
        self,
        db: Session,
        sic_id: int,
        thumbprint_url: str
    ) -> Optional[SilmathaIDCard]:
        """
        Update the left thumbprint URL for an ID card.
        
        Args:
            db: Database session
            sic_id: ID of the card
            thumbprint_url: URL of the uploaded thumbprint
            
        Returns:
            Updated SilmathaIDCard instance or None
        """
        db_record = self.get_by_id(db, sic_id)
        if not db_record:
            return None

        db_record.sic_left_thumbprint_url = thumbprint_url
        db.commit()
        db.refresh(db_record)
        
        return db_record

    def update_photo_url(
        self,
        db: Session,
        sic_id: int,
        photo_url: str
    ) -> Optional[SilmathaIDCard]:
        """
        Update the applicant photo URL for an ID card.
        
        Args:
            db: Database session
            sic_id: ID of the card
            photo_url: URL of the uploaded photo
            
        Returns:
            Updated SilmathaIDCard instance or None
        """
        db_record = self.get_by_id(db, sic_id)
        if not db_record:
            return None

        db_record.sic_applicant_photo_url = photo_url
        db.commit()
        db.refresh(db_record)
        
        return db_record

    def approve(
        self,
        db: Session,
        sic_id: int,
        approved_by: str
    ) -> Optional[SilmathaIDCard]:
        """
        Approve a Silmatha ID Card.
        
        Args:
            db: Database session
            sic_id: ID of the card
            approved_by: Username of approver
            
        Returns:
            Updated SilmathaIDCard instance or None
        """
        db_record = self.get_by_id(db, sic_id)
        if not db_record:
            return None

        db_record.sic_workflow_status = "APPROVED"
        db_record.sic_approved_by = approved_by
        db_record.sic_approved_at = datetime.utcnow()
        # Clear any previous rejection
        db_record.sic_rejection_reason = None
        db_record.sic_rejected_by = None
        db_record.sic_rejected_at = None
        
        db.commit()
        db.refresh(db_record)
        
        return db_record

    def reject(
        self,
        db: Session,
        sic_id: int,
        rejected_by: str,
        rejection_reason: str
    ) -> Optional[SilmathaIDCard]:
        """
        Reject a Silmatha ID Card.
        
        Args:
            db: Database session
            sic_id: ID of the card
            rejected_by: Username of rejecter
            rejection_reason: Reason for rejection
            
        Returns:
            Updated SilmathaIDCard instance or None
        """
        db_record = self.get_by_id(db, sic_id)
        if not db_record:
            return None

        db_record.sic_workflow_status = "REJECTED"
        db_record.sic_rejected_by = rejected_by
        db_record.sic_rejected_at = datetime.utcnow()
        db_record.sic_rejection_reason = rejection_reason
        # Clear any previous approval
        db_record.sic_approved_by = None
        db_record.sic_approved_at = None
        
        db.commit()
        db.refresh(db_record)
        
        return db_record

    def mark_printed(
        self,
        db: Session,
        sic_id: int,
        printed_by: str
    ) -> Optional[SilmathaIDCard]:
        """
        Mark a Silmatha ID Card as printed.
        
        Args:
            db: Database session
            sic_id: ID of the card
            printed_by: Username of printer
            
        Returns:
            Updated SilmathaIDCard instance or None
        """
        db_record = self.get_by_id(db, sic_id)
        if not db_record:
            return None

        db_record.sic_workflow_status = "PRINTING_COMPLETE"
        db_record.sic_printed_by = printed_by
        db_record.sic_printed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_record)
        
        return db_record


    def update_file_paths(
        self,
        db: Session,
        sic_id: int,
        thumbprint_url: Optional[str] = None,
        photo_url: Optional[str] = None,
        signature_url: Optional[bool] = None,
        authorized_signature_url: Optional[bool] = None,
    ) -> Optional[SilmathaIDCard]:
        """
        Update file/boolean fields for an ID card after creation or update.

        Args:
            db: Database session
            sic_id: ID of the card
            thumbprint_url: URL of left thumbprint (optional)
            photo_url: URL of applicant photo (optional)
            signature_url: Signature present boolean (optional)
            authorized_signature_url: Authorized signature present boolean (optional)

        Returns:
            Updated SilmathaIDCard instance or None
        """
        db_record = self.get_by_id(db, sic_id)
        if not db_record:
            return None

        if thumbprint_url is not None:
            db_record.sic_left_thumbprint_url = thumbprint_url
        if photo_url is not None:
            db_record.sic_applicant_photo_url = photo_url
        if signature_url is not None:
            db_record.sic_signature_url = signature_url
        if authorized_signature_url is not None:
            db_record.sic_authorized_signature_url = authorized_signature_url

        db.commit()
        db.refresh(db_record)

        return db_record


# Singleton instance
silmatha_id_card_repository = SilmathaIDCardRepository()
