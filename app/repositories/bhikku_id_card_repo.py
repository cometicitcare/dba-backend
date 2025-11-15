# app/repositories/bhikku_id_card_repo.py
from datetime import datetime
from typing import Optional, List
from sqlalchemy import func, or_, and_
from sqlalchemy.orm import Session

from app.models.bhikku_id_card import BhikkuIDCard
from app.schemas.bhikku_id_card import BhikkuIDCardCreate, BhikkuIDCardUpdate


class BhikkuIDCardRepository:
    """
    Repository for Bhikku ID Card CRUD operations.
    Handles database interactions and form number generation.
    """

    def generate_next_form_no(self, db: Session) -> str:
        """
        Generate the next unique form number in format: FORM-{YEAR}-{SEQUENCE}.
        
        Example: FORM-2025-0001, FORM-2025-0002, etc.
        
        Args:
            db: Database session
            
        Returns:
            Unique form number string
        """
        current_year = datetime.utcnow().year
        prefix = f"FORM-{current_year}-"

        # Find the latest form number for this year
        latest = (
            db.query(BhikkuIDCard)
            .filter(BhikkuIDCard.bic_form_no.like(f"{prefix}%"))
            .order_by(BhikkuIDCard.bic_form_no.desc())
            .first()
        )

        if latest:
            try:
                # Extract sequence part after prefix
                sequence_part = latest.bic_form_no[len(prefix):]
                last_sequence = int(sequence_part)
                next_sequence = last_sequence + 1
            except (ValueError, IndexError):
                next_sequence = 1
        else:
            next_sequence = 1

        return f"{prefix}{next_sequence:04d}"

    def create(
        self, 
        db: Session, 
        bhikku_id_card: BhikkuIDCardCreate,
        created_by: Optional[str] = None
    ) -> BhikkuIDCard:
        """
        Create a new Bhikku ID Card record.
        Auto-generates form number and sets workflow status to PENDING.
        
        Args:
            db: Database session
            bhikku_id_card: Create schema with data
            created_by: Username of creator
            
        Returns:
            Created BhikkuIDCard model instance
        """
        # Generate unique form number
        form_no = self.generate_next_form_no(db)
        
        # Convert stay_history to dict format if present
        stay_history_data = None
        if bhikku_id_card.bic_stay_history:
            stay_history_data = [item.dict() for item in bhikku_id_card.bic_stay_history]
        
        # Create DB model
        db_bhikku_id_card = BhikkuIDCard(
            bic_br_regn=bhikku_id_card.bic_br_regn,
            bic_form_no=form_no,
            bic_divisional_secretariat=bhikku_id_card.bic_divisional_secretariat,
            bic_district=bhikku_id_card.bic_district,
            bic_full_bhikku_name=bhikku_id_card.bic_full_bhikku_name,
            bic_title_post=bhikku_id_card.bic_title_post,
            bic_lay_name_full=bhikku_id_card.bic_lay_name_full,
            bic_dob=bhikku_id_card.bic_dob,
            bic_birth_place=bhikku_id_card.bic_birth_place,
            bic_robing_date=bhikku_id_card.bic_robing_date,
            bic_robing_place=bhikku_id_card.bic_robing_place,
            bic_robing_nikaya=bhikku_id_card.bic_robing_nikaya,
            bic_robing_parshawaya=bhikku_id_card.bic_robing_parshawaya,
            bic_samanera_reg_no=bhikku_id_card.bic_samanera_reg_no,
            bic_upasampada_reg_no=bhikku_id_card.bic_upasampada_reg_no,
            bic_higher_ord_date=bhikku_id_card.bic_higher_ord_date,
            bic_higher_ord_name=bhikku_id_card.bic_higher_ord_name,
            bic_perm_residence=bhikku_id_card.bic_perm_residence,
            bic_national_id=bhikku_id_card.bic_national_id,
            bic_stay_history=stay_history_data,
            bic_workflow_status="PENDING",  # Default status
            bic_created_by=created_by,
        )
        
        db.add(db_bhikku_id_card)
        db.commit()
        db.refresh(db_bhikku_id_card)
        
        return db_bhikku_id_card

    def get_by_id(self, db: Session, bic_id: int) -> Optional[BhikkuIDCard]:
        """
        Get a Bhikku ID Card by ID (excluding soft-deleted records).
        
        Args:
            db: Database session
            bic_id: Primary key ID
            
        Returns:
            BhikkuIDCard instance or None
        """
        return (
            db.query(BhikkuIDCard)
            .filter(
                BhikkuIDCard.bic_id == bic_id,
                BhikkuIDCard.bic_is_deleted.is_(False)
            )
            .first()
        )

    def get_by_br_regn(self, db: Session, br_regn: str) -> Optional[BhikkuIDCard]:
        """
        Get a Bhikku ID Card by Bhikku registration number (excluding soft-deleted records).
        
        Args:
            db: Database session
            br_regn: Bhikku registration number
            
        Returns:
            BhikkuIDCard instance or None
        """
        return (
            db.query(BhikkuIDCard)
            .filter(
                BhikkuIDCard.bic_br_regn == br_regn,
                BhikkuIDCard.bic_is_deleted.is_(False)
            )
            .first()
        )

    def get_by_form_no(self, db: Session, form_no: str) -> Optional[BhikkuIDCard]:
        """
        Get a Bhikku ID Card by form number (excluding soft-deleted records).
        
        Args:
            db: Database session
            form_no: Form number
            
        Returns:
            BhikkuIDCard instance or None
        """
        return (
            db.query(BhikkuIDCard)
            .filter(
                BhikkuIDCard.bic_form_no == form_no,
                BhikkuIDCard.bic_is_deleted.is_(False)
            )
            .first()
        )

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        workflow_status: Optional[str] = None,
        search_key: Optional[str] = None,
    ) -> tuple[List[BhikkuIDCard], int]:
        """
        Get all Bhikku ID Cards with optional filtering, pagination, and search.
        
        Args:
            db: Database session
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            workflow_status: Filter by workflow status
            search_key: Search across multiple text fields
            
        Returns:
            Tuple of (list of BhikkuIDCard records, total count)
        """
        query = db.query(BhikkuIDCard).filter(BhikkuIDCard.bic_is_deleted.is_(False))
        
        # Apply workflow status filter
        if workflow_status:
            query = query.filter(BhikkuIDCard.bic_workflow_status == workflow_status)
        
        # Apply search filter across multiple fields
        if search_key and search_key.strip():
            search_pattern = f"%{search_key.strip()}%"
            query = query.filter(
                or_(
                    BhikkuIDCard.bic_br_regn.ilike(search_pattern),
                    BhikkuIDCard.bic_form_no.ilike(search_pattern),
                    BhikkuIDCard.bic_full_bhikku_name.ilike(search_pattern),
                    BhikkuIDCard.bic_lay_name_full.ilike(search_pattern),
                    BhikkuIDCard.bic_national_id.ilike(search_pattern),
                    BhikkuIDCard.bic_district.ilike(search_pattern),
                    BhikkuIDCard.bic_divisional_secretariat.ilike(search_pattern),
                )
            )
        
        # Get total count before pagination
        total = query.count()
        
        # Apply pagination and ordering
        records = query.order_by(BhikkuIDCard.bic_created_at.desc()).offset(skip).limit(limit).all()
        
        return records, total

    def update(
        self,
        db: Session,
        bic_id: int,
        bhikku_id_card_update: BhikkuIDCardUpdate,
        updated_by: Optional[str] = None
    ) -> Optional[BhikkuIDCard]:
        """
        Update an existing Bhikku ID Card record.
        
        Args:
            db: Database session
            bic_id: ID of the record to update
            bhikku_id_card_update: Update schema with data
            updated_by: Username of updater
            
        Returns:
            Updated BhikkuIDCard instance or None if not found
        """
        db_record = self.get_by_id(db, bic_id)
        if not db_record:
            return None
        
        # Update only provided fields
        update_data = bhikku_id_card_update.dict(exclude_unset=True)
        
        # Convert stay_history if present
        if "bic_stay_history" in update_data and update_data["bic_stay_history"] is not None:
            update_data["bic_stay_history"] = [
                item.dict() if hasattr(item, "dict") else item 
                for item in update_data["bic_stay_history"]
            ]
        
        for field, value in update_data.items():
            setattr(db_record, field, value)
        
        # Update audit fields
        db_record.bic_updated_by = updated_by
        db_record.bic_updated_at = datetime.utcnow()
        db_record.bic_version_number += 1
        
        db.commit()
        db.refresh(db_record)
        
        return db_record

    def delete(self, db: Session, bic_id: int) -> bool:
        """
        Soft delete a Bhikku ID Card record.
        
        Args:
            db: Database session
            bic_id: ID of the record to delete
            
        Returns:
            True if deleted, False if not found
        """
        db_record = self.get_by_id(db, bic_id)
        if not db_record:
            return False
        
        db_record.bic_is_deleted = True
        db_record.bic_updated_at = datetime.utcnow()
        
        db.commit()
        
        return True

    def approve(
        self, 
        db: Session, 
        bic_id: int, 
        approved_by: str
    ) -> Optional[BhikkuIDCard]:
        """
        Approve a Bhikku ID Card (change workflow status to APPROVED).
        
        Args:
            db: Database session
            bic_id: ID of the record to approve
            approved_by: Username of approver
            
        Returns:
            Updated BhikkuIDCard instance or None if not found
        """
        db_record = self.get_by_id(db, bic_id)
        if not db_record:
            return None
        
        db_record.bic_workflow_status = "APPROVED"
        db_record.bic_approved_by = approved_by
        db_record.bic_approved_at = datetime.utcnow()
        db_record.bic_updated_by = approved_by
        db_record.bic_updated_at = datetime.utcnow()
        db_record.bic_version_number += 1
        
        db.commit()
        db.refresh(db_record)
        
        return db_record

    def reject(
        self,
        db: Session,
        bic_id: int,
        rejected_by: str,
        rejection_reason: str
    ) -> Optional[BhikkuIDCard]:
        """
        Reject a Bhikku ID Card (change workflow status to REJECTED).
        
        Args:
            db: Database session
            bic_id: ID of the record to reject
            rejected_by: Username of rejecter
            rejection_reason: Reason for rejection
            
        Returns:
            Updated BhikkuIDCard instance or None if not found
        """
        db_record = self.get_by_id(db, bic_id)
        if not db_record:
            return None
        
        db_record.bic_workflow_status = "REJECTED"
        db_record.bic_rejected_by = rejected_by
        db_record.bic_rejected_at = datetime.utcnow()
        db_record.bic_rejection_reason = rejection_reason
        db_record.bic_updated_by = rejected_by
        db_record.bic_updated_at = datetime.utcnow()
        db_record.bic_version_number += 1
        
        db.commit()
        db.refresh(db_record)
        
        return db_record

    def mark_printed(
        self,
        db: Session,
        bic_id: int,
        printed_by: str
    ) -> Optional[BhikkuIDCard]:
        """
        Mark a Bhikku ID Card as printed.
        
        Args:
            db: Database session
            bic_id: ID of the record
            printed_by: Username who marked as printed
            
        Returns:
            Updated BhikkuIDCard instance or None if not found
        """
        db_record = self.get_by_id(db, bic_id)
        if not db_record:
            return None
        
        db_record.bic_workflow_status = "PRINTED"
        db_record.bic_printed_by = printed_by
        db_record.bic_printed_at = datetime.utcnow()
        db_record.bic_updated_by = printed_by
        db_record.bic_updated_at = datetime.utcnow()
        db_record.bic_version_number += 1
        
        db.commit()
        db.refresh(db_record)
        
        return db_record

    def update_file_paths(
        self,
        db: Session,
        bic_id: int,
        thumbprint_url: Optional[str] = None,
        photo_url: Optional[str] = None
    ) -> Optional[BhikkuIDCard]:
        """
        Update file paths for uploaded images.
        
        Args:
            db: Database session
            bic_id: ID of the record
            thumbprint_url: Path to thumbprint image
            photo_url: Path to applicant photo
            
        Returns:
            Updated BhikkuIDCard instance or None if not found
        """
        db_record = self.get_by_id(db, bic_id)
        if not db_record:
            return None
        
        if thumbprint_url is not None:
            db_record.bic_left_thumbprint_url = thumbprint_url
        
        if photo_url is not None:
            db_record.bic_applicant_photo_url = photo_url
        
        db_record.bic_updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_record)
        
        return db_record


# Singleton instance
bhikku_id_card_repository = BhikkuIDCardRepository()
