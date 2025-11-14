# app/services/bhikku_id_card_workflow_service.py
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from app.models.bhikku_id_card import BhikkuIDCard
from app.models.bhikku_id_card_workflow_flag import BhikkuIDCardWorkflowFlag, IDCardWorkflowFlagEnum
from app.repositories.base import BaseRepository


class IDCardWorkflowFlag:
    """Workflow flag enumeration matching the database enum"""
    PENDING = IDCardWorkflowFlagEnum.PENDING.value
    APPROVED = IDCardWorkflowFlagEnum.APPROVED.value
    REJECTED = IDCardWorkflowFlagEnum.REJECTED.value
    PRINTED = IDCardWorkflowFlagEnum.PRINTED.value
    SCANNED = IDCardWorkflowFlagEnum.SCANNED.value
    COMPLETED = IDCardWorkflowFlagEnum.COMPLETED.value


class BhikkuIDCardWorkflowService:
    """Service for managing bhikku ID card workflow"""

    def __init__(self):
        self.workflow_repo = BaseRepository(BhikkuIDCardWorkflowFlag)

    def get_workflow_for_id_card(self, db: Session, bic_id: int) -> Optional[BhikkuIDCardWorkflowFlag]:
        """Get the workflow record for a specific ID card by numeric ID"""
        return db.query(BhikkuIDCardWorkflowFlag).filter(
            BhikkuIDCardWorkflowFlag.bicwf_bhikku_id_card_id == bic_id,
            BhikkuIDCardWorkflowFlag.bicwf_is_deleted == False
        ).first()

    def get_workflow_for_registration(self, db: Session, bic_regn: str) -> Optional[BhikkuIDCardWorkflowFlag]:
        """Get the workflow record for a specific ID card by registration number"""
        id_card = self._get_id_card_by_regn(db, bic_regn, raise_if_missing=False)
        if not id_card:
            return None
        return self.get_workflow_for_id_card(db, id_card.bic_id)

    def get_or_create_workflow(self, db: Session, id_card: BhikkuIDCard) -> BhikkuIDCardWorkflowFlag:
        """Get existing workflow or create new one with PENDING status"""
        workflow = self.get_workflow_for_id_card(db, id_card.bic_id)
        
        if workflow is None:
            # Create new workflow with PENDING status
            workflow = BhikkuIDCardWorkflowFlag(
                bicwf_bhikku_id_card_id=id_card.bic_id,
                bicwf_bhikku_id=id_card.bic_br_id,
                bicwf_current_flag=IDCardWorkflowFlagEnum.PENDING,
                bicwf_pending_date=datetime.now()
            )
            db.add(workflow)
            db.commit()
            db.refresh(workflow)
        
        return workflow

    def approve_workflow(
        self,
        db: Session,
        bic_regn: str,
        approved_by: str,
        notes: Optional[str] = None
    ) -> BhikkuIDCardWorkflowFlag:
        """Approve a pending ID card record"""
        id_card = self._get_id_card_by_regn(db, bic_regn)
        
        workflow = db.query(BhikkuIDCardWorkflowFlag).filter(
            BhikkuIDCardWorkflowFlag.bicwf_bhikku_id_card_id == id_card.bic_id,
            BhikkuIDCardWorkflowFlag.bicwf_is_deleted == False
        ).first()
        
        # Create workflow if it doesn't exist
        if not workflow:
            workflow = BhikkuIDCardWorkflowFlag(
                bicwf_bhikku_id_card_id=id_card.bic_id,
                bicwf_bhikku_id=id_card.bic_br_id,
                bicwf_current_flag=IDCardWorkflowFlagEnum.PENDING,
                bicwf_pending_date=datetime.now()
            )
            db.add(workflow)
            db.commit()
            db.refresh(workflow)
        
        if workflow.bicwf_current_flag != IDCardWorkflowFlagEnum.PENDING:
            raise ValueError(f"Can only approve PENDING records. Current status: {workflow.bicwf_current_flag}")
        
        workflow.bicwf_current_flag = IDCardWorkflowFlagEnum.APPROVED
        workflow.bicwf_approval_date = datetime.now()
        workflow.bicwf_approval_by = approved_by
        workflow.bicwf_approval_notes = notes
        workflow.bicwf_updated_by = approved_by
        workflow.bicwf_updated_at = datetime.now()
        
        db.commit()
        db.refresh(workflow)
        return workflow

    def reject_workflow(
        self,
        db: Session,
        bic_regn: str,
        rejected_by: str,
        rejection_notes: str
    ) -> BhikkuIDCardWorkflowFlag:
        """Reject a pending ID card record"""
        id_card = self._get_id_card_by_regn(db, bic_regn)
        
        workflow = db.query(BhikkuIDCardWorkflowFlag).filter(
            BhikkuIDCardWorkflowFlag.bicwf_bhikku_id_card_id == id_card.bic_id,
            BhikkuIDCardWorkflowFlag.bicwf_is_deleted == False
        ).first()
        
        # Create workflow if it doesn't exist
        if not workflow:
            workflow = BhikkuIDCardWorkflowFlag(
                bicwf_bhikku_id_card_id=id_card.bic_id,
                bicwf_bhikku_id=id_card.bic_br_id,
                bicwf_current_flag=IDCardWorkflowFlagEnum.PENDING,
                bicwf_pending_date=datetime.now()
            )
            db.add(workflow)
            db.commit()
            db.refresh(workflow)
        
        if workflow.bicwf_current_flag != IDCardWorkflowFlagEnum.PENDING:
            raise ValueError(f"Can only reject PENDING records. Current status: {workflow.bicwf_current_flag}")
        
        workflow.bicwf_current_flag = IDCardWorkflowFlagEnum.REJECTED
        workflow.bicwf_approval_date = datetime.now()
        workflow.bicwf_approval_by = rejected_by
        workflow.bicwf_approval_notes = rejection_notes
        workflow.bicwf_updated_by = rejected_by
        workflow.bicwf_updated_at = datetime.now()
        
        db.commit()
        db.refresh(workflow)
        return workflow

    def send_to_printing(
        self,
        db: Session,
        bic_regn: str,
        sent_by: str
    ) -> BhikkuIDCardWorkflowFlag:
        """Send an approved ID card record to printing"""
        id_card = self._get_id_card_by_regn(db, bic_regn)
        workflow = db.query(BhikkuIDCardWorkflowFlag).filter(
            BhikkuIDCardWorkflowFlag.bicwf_bhikku_id_card_id == id_card.bic_id,
            BhikkuIDCardWorkflowFlag.bicwf_is_deleted == False
        ).first()
        
        if not workflow:
            raise ValueError(f"Workflow not found for bic_id: {bic_id}")
        
        if workflow.bicwf_current_flag != IDCardWorkflowFlagEnum.APPROVED:
            raise ValueError(f"Can only send APPROVED records to printing. Current status: {workflow.bicwf_current_flag}")
        
        workflow.bicwf_current_flag = IDCardWorkflowFlagEnum.PRINTED
        workflow.bicwf_printing_date = datetime.now()
        workflow.bicwf_print_by = sent_by
        workflow.bicwf_updated_by = sent_by
        workflow.bicwf_updated_at = datetime.now()
        
        db.commit()
        db.refresh(workflow)
        return workflow

    def mark_as_scanned(
        self,
        db: Session,
        bic_regn: str,
        scanned_by: str
    ) -> BhikkuIDCardWorkflowFlag:
        """Mark a printed ID card record as scanned"""
        id_card = self._get_id_card_by_regn(db, bic_regn)
        workflow = db.query(BhikkuIDCardWorkflowFlag).filter(
            BhikkuIDCardWorkflowFlag.bicwf_bhikku_id_card_id == id_card.bic_id,
            BhikkuIDCardWorkflowFlag.bicwf_is_deleted == False
        ).first()
        
        if not workflow:
            raise ValueError(f"Workflow not found for bic_id: {bic_id}")
        
        if workflow.bicwf_current_flag != IDCardWorkflowFlagEnum.PRINTED:
            raise ValueError(f"Can only scan PRINTED records. Current status: {workflow.bicwf_current_flag}")
        
        workflow.bicwf_current_flag = IDCardWorkflowFlagEnum.SCANNED
        workflow.bicwf_scan_date = datetime.now()
        workflow.bicwf_scan_by = scanned_by
        workflow.bicwf_updated_by = scanned_by
        workflow.bicwf_updated_at = datetime.now()
        
        db.commit()
        db.refresh(workflow)
        return workflow

    def complete_workflow(
        self,
        db: Session,
        bic_regn: str,
        completed_by: str
    ) -> BhikkuIDCardWorkflowFlag:
        """Complete a scanned ID card record"""
        id_card = self._get_id_card_by_regn(db, bic_regn)
        workflow = db.query(BhikkuIDCardWorkflowFlag).filter(
            BhikkuIDCardWorkflowFlag.bicwf_bhikku_id_card_id == id_card.bic_id,
            BhikkuIDCardWorkflowFlag.bicwf_is_deleted == False
        ).first()
        
        if not workflow:
            raise ValueError(f"Workflow not found for bic_id: {bic_id}")
        
        if workflow.bicwf_current_flag != IDCardWorkflowFlagEnum.SCANNED:
            raise ValueError(f"Can only complete SCANNED records. Current status: {workflow.bicwf_current_flag}")
        
        workflow.bicwf_current_flag = IDCardWorkflowFlagEnum.COMPLETED
        workflow.bicwf_completion_date = datetime.now()
        workflow.bicwf_completed_by = completed_by
        workflow.bicwf_updated_by = completed_by
        workflow.bicwf_updated_at = datetime.now()
        
        db.commit()
        db.refresh(workflow)
        return workflow

    def get_pending_records(self, db: Session) -> List[BhikkuIDCardWorkflowFlag]:
        """Get all pending ID card records"""
        return db.query(BhikkuIDCardWorkflowFlag).filter(
            BhikkuIDCardWorkflowFlag.bicwf_current_flag == IDCardWorkflowFlagEnum.PENDING,
            BhikkuIDCardWorkflowFlag.bicwf_is_deleted == False
        ).all()

    def get_approved_records(self, db: Session) -> List[BhikkuIDCardWorkflowFlag]:
        """Get all approved ID card records"""
        return db.query(BhikkuIDCardWorkflowFlag).filter(
            BhikkuIDCardWorkflowFlag.bicwf_current_flag == IDCardWorkflowFlagEnum.APPROVED,
            BhikkuIDCardWorkflowFlag.bicwf_is_deleted == False
        ).all()

    def get_rejected_records(self, db: Session) -> List[BhikkuIDCardWorkflowFlag]:
        """Get all rejected ID card records"""
        return db.query(BhikkuIDCardWorkflowFlag).filter(
            BhikkuIDCardWorkflowFlag.bicwf_current_flag == IDCardWorkflowFlagEnum.REJECTED,
            BhikkuIDCardWorkflowFlag.bicwf_is_deleted == False
        ).all()

    def get_printed_records(self, db: Session) -> List[BhikkuIDCardWorkflowFlag]:
        """Get all printed ID card records"""
        return db.query(BhikkuIDCardWorkflowFlag).filter(
            BhikkuIDCardWorkflowFlag.bicwf_current_flag == IDCardWorkflowFlagEnum.PRINTED,
            BhikkuIDCardWorkflowFlag.bicwf_is_deleted == False
        ).all()

    def get_scanned_records(self, db: Session) -> List[BhikkuIDCardWorkflowFlag]:
        """Get all scanned ID card records"""
        return db.query(BhikkuIDCardWorkflowFlag).filter(
            BhikkuIDCardWorkflowFlag.bicwf_current_flag == IDCardWorkflowFlagEnum.SCANNED,
            BhikkuIDCardWorkflowFlag.bicwf_is_deleted == False
        ).all()

    def get_completed_records(self, db: Session) -> List[BhikkuIDCardWorkflowFlag]:
        """Get all completed ID card records"""
        return db.query(BhikkuIDCardWorkflowFlag).filter(
            BhikkuIDCardWorkflowFlag.bicwf_current_flag == IDCardWorkflowFlagEnum.COMPLETED,
            BhikkuIDCardWorkflowFlag.bicwf_is_deleted == False
        ).all()

    def _normalize_regn(self, bic_regn: str) -> str:
        if not bic_regn or not bic_regn.strip():
            raise ValueError("bic_regn is required.")
        return bic_regn.strip().upper()

    def _get_id_card_by_regn(
        self,
        db: Session,
        bic_regn: str,
        raise_if_missing: bool = True
    ) -> Optional[BhikkuIDCard]:
        normalized_regn = self._normalize_regn(bic_regn)
        id_card = db.query(BhikkuIDCard).filter(
            BhikkuIDCard.bic_regn == normalized_regn,
            BhikkuIDCard.bic_is_deleted.is_(False)
        ).first()

        if not id_card and raise_if_missing:
            raise ValueError(f"ID card not found for registration {normalized_regn}")
        return id_card


# Singleton instance
bhikku_id_card_workflow_service = BhikkuIDCardWorkflowService()
