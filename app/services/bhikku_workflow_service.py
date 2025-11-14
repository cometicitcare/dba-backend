# app/services/bhikku_workflow_service.py
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from app.models.bhikku import Bhikku
from app.models.bhikku_workflow_flag import BhikkuWorkflowFlag, WorkflowFlagEnum
from app.repositories.base import BaseRepository


class WorkflowFlag:
    """Workflow flag enumeration matching the database enum"""
    PENDING = WorkflowFlagEnum.PENDING.value
    APPROVED = WorkflowFlagEnum.APPROVED.value
    REJECTED = WorkflowFlagEnum.REJECTED.value
    PRINTED = WorkflowFlagEnum.PRINTED.value
    SCANNED = WorkflowFlagEnum.SCANNED.value
    COMPLETED = WorkflowFlagEnum.COMPLETED.value


class BhikkuWorkflowService:
    """Service for managing bhikku registration workflow"""

    def __init__(self):
        self.workflow_repo = BaseRepository(BhikkuWorkflowFlag)

    def get_workflow_for_bhikku(self, db: Session, bhikku_id: int) -> Optional[BhikkuWorkflowFlag]:
        """Get the workflow record for a specific bhikku"""
        return db.query(BhikkuWorkflowFlag).filter(
            BhikkuWorkflowFlag.bwf_bhikku_id == bhikku_id,
            BhikkuWorkflowFlag.bwf_is_deleted == False
        ).first()

    def get_or_create_workflow(self, db: Session, bhikku: Bhikku) -> BhikkuWorkflowFlag:
        """Get existing workflow or create new one with PENDING status"""
        workflow = self.get_workflow_for_bhikku(db, bhikku.br_id)
        
        if workflow is None:
            # Create new workflow with PENDING status
            workflow = BhikkuWorkflowFlag(
                bwf_bhikku_id=bhikku.br_id,
                bwf_bhikku_regn=bhikku.br_regn,
                bwf_current_flag=WorkflowFlagEnum.PENDING,
                bwf_pending_date=datetime.now()
            )
            db.add(workflow)
            db.commit()
            db.refresh(workflow)
        
        return workflow

    def approve_workflow(
        self,
        db: Session,
        bhikku_id: int,
        approved_by: str,
        notes: Optional[str] = None
    ) -> BhikkuWorkflowFlag:
        """Approve a pending bhikku record"""
        # Get bhikku to fetch registration number
        bhikku = db.query(Bhikku).filter(Bhikku.br_id == bhikku_id).first()
        if not bhikku:
            raise ValueError(f"Bhikku not found for bhikku_id: {bhikku_id}")
        
        workflow = db.query(BhikkuWorkflowFlag).filter(
            BhikkuWorkflowFlag.bwf_bhikku_id == bhikku_id,
            BhikkuWorkflowFlag.bwf_is_deleted == False
        ).first()
        
        # Create workflow if it doesn't exist
        if not workflow:
            workflow = BhikkuWorkflowFlag(
                bwf_bhikku_id=bhikku.br_id,
                bwf_bhikku_regn=bhikku.br_regn,
                bwf_current_flag=WorkflowFlagEnum.PENDING,
                bwf_pending_date=datetime.now()
            )
            db.add(workflow)
            db.commit()
            db.refresh(workflow)
        
        if workflow.bwf_current_flag != WorkflowFlagEnum.PENDING:
            raise ValueError(f"Can only approve PENDING records. Current status: {workflow.bwf_current_flag}")
        
        workflow.bwf_current_flag = WorkflowFlagEnum.APPROVED
        workflow.bwf_approval_date = datetime.now()
        workflow.bwf_approval_by = approved_by
        workflow.bwf_approval_notes = notes
        workflow.bwf_updated_by = approved_by
        workflow.bwf_updated_at = datetime.now()
        
        db.commit()
        db.refresh(workflow)
        return workflow

    def reject_workflow(
        self,
        db: Session,
        bhikku_id: int,
        rejected_by: str,
        rejection_notes: str
    ) -> BhikkuWorkflowFlag:
        """Reject a pending bhikku record"""
        # Get bhikku to fetch registration number
        bhikku = db.query(Bhikku).filter(Bhikku.br_id == bhikku_id).first()
        if not bhikku:
            raise ValueError(f"Bhikku not found for bhikku_id: {bhikku_id}")
        
        workflow = db.query(BhikkuWorkflowFlag).filter(
            BhikkuWorkflowFlag.bwf_bhikku_id == bhikku_id,
            BhikkuWorkflowFlag.bwf_is_deleted == False
        ).first()
        
        # Create workflow if it doesn't exist
        if not workflow:
            workflow = BhikkuWorkflowFlag(
                bwf_bhikku_id=bhikku.br_id,
                bwf_bhikku_regn=bhikku.br_regn,
                bwf_current_flag=WorkflowFlagEnum.PENDING,
                bwf_pending_date=datetime.now()
            )
            db.add(workflow)
            db.commit()
            db.refresh(workflow)
        
        if workflow.bwf_current_flag != WorkflowFlagEnum.PENDING:
            raise ValueError(f"Can only reject PENDING records. Current status: {workflow.bwf_current_flag}")
        
        workflow.bwf_current_flag = WorkflowFlagEnum.REJECTED
        workflow.bwf_approval_date = datetime.now()
        workflow.bwf_approval_by = rejected_by
        workflow.bwf_approval_notes = rejection_notes
        workflow.bwf_updated_by = rejected_by
        workflow.bwf_updated_at = datetime.now()
        
        db.commit()
        db.refresh(workflow)
        return workflow

    def send_to_printing(
        self,
        db: Session,
        bhikku_id: int,
        sent_by: str
    ) -> BhikkuWorkflowFlag:
        """Send an approved record to printing"""
        workflow = db.query(BhikkuWorkflowFlag).filter(
            BhikkuWorkflowFlag.bwf_bhikku_id == bhikku_id,
            BhikkuWorkflowFlag.bwf_is_deleted == False
        ).first()
        
        if not workflow:
            raise ValueError(f"Workflow not found for bhikku_id: {bhikku_id}")
        
        if workflow.bwf_current_flag != WorkflowFlagEnum.APPROVED:
            raise ValueError(f"Can only send APPROVED records to printing. Current status: {workflow.bwf_current_flag}")
        
        workflow.bwf_current_flag = WorkflowFlagEnum.PRINTED
        workflow.bwf_printing_date = datetime.now()
        workflow.bwf_print_by = sent_by
        workflow.bwf_updated_by = sent_by
        workflow.bwf_updated_at = datetime.now()
        
        db.commit()
        db.refresh(workflow)
        return workflow

    def mark_as_scanned(
        self,
        db: Session,
        bhikku_id: int,
        scanned_by: str
    ) -> BhikkuWorkflowFlag:
        """Mark a printed record as scanned"""
        workflow = db.query(BhikkuWorkflowFlag).filter(
            BhikkuWorkflowFlag.bwf_bhikku_id == bhikku_id,
            BhikkuWorkflowFlag.bwf_is_deleted == False
        ).first()
        
        if not workflow:
            raise ValueError(f"Workflow not found for bhikku_id: {bhikku_id}")
        
        if workflow.bwf_current_flag != WorkflowFlagEnum.PRINTED:
            raise ValueError(f"Can only scan PRINTED records. Current status: {workflow.bwf_current_flag}")
        
        workflow.bwf_current_flag = WorkflowFlagEnum.SCANNED
        workflow.bwf_scan_date = datetime.now()
        workflow.bwf_scan_by = scanned_by
        workflow.bwf_updated_by = scanned_by
        workflow.bwf_updated_at = datetime.now()
        
        db.commit()
        db.refresh(workflow)
        return workflow

    def complete_workflow(
        self,
        db: Session,
        bhikku_id: int,
        completed_by: str
    ) -> BhikkuWorkflowFlag:
        """Complete a scanned record"""
        workflow = db.query(BhikkuWorkflowFlag).filter(
            BhikkuWorkflowFlag.bwf_bhikku_id == bhikku_id,
            BhikkuWorkflowFlag.bwf_is_deleted == False
        ).first()
        
        if not workflow:
            raise ValueError(f"Workflow not found for bhikku_id: {bhikku_id}")
        
        if workflow.bwf_current_flag != WorkflowFlagEnum.SCANNED:
            raise ValueError(f"Can only complete SCANNED records. Current status: {workflow.bwf_current_flag}")
        
        workflow.bwf_current_flag = WorkflowFlagEnum.COMPLETED
        workflow.bwf_completion_date = datetime.now()
        workflow.bwf_completed_by = completed_by
        workflow.bwf_updated_by = completed_by
        workflow.bwf_updated_at = datetime.now()
        
        db.commit()
        db.refresh(workflow)
        return workflow

    def build_registration_flow(self, bhikku: Bhikku) -> Dict[str, Any]:
        """Build a registration workflow structure for display/documentation"""
        return {
            "registration": bhikku.br_regn,
            "monkName": bhikku.br_gihiname or "Unknown",
            "currentFlag": WorkflowFlag.PENDING,
            "steps": [
                {
                    "stage": "Data Entry Officer",
                    "flag": WorkflowFlag.PENDING,
                    "notifications": [
                        {
                            "message": "New data entry awaiting verification",
                            "type": "info"
                        }
                    ],
                    "details": [
                        "Bhikku information form submitted",
                        "Awaiting officer review and approval"
                    ]
                },
                {
                    "stage": "Authorizing Officer",
                    "flag": None,
                    "outcomes": [
                        {
                            "flag": WorkflowFlag.APPROVED,
                            "message": "Record approved for processing"
                        },
                        {
                            "flag": WorkflowFlag.REJECTED,
                            "message": "Record rejected - requires revision"
                        }
                    ],
                    "details": [
                        "Review submitted data",
                        "Approve or reject the registration"
                    ]
                },
                {
                    "stage": "Printing Officer",
                    "flag": WorkflowFlag.PRINTED,
                    "notifications": [
                        {
                            "message": "Form approved - ready for printing with QR code",
                            "type": "success"
                        }
                    ],
                    "details": [
                        "Print the bhikku registration form",
                        "Generate and embed QR code",
                        "Attach identification photo",
                        "Prepare for scanning and delivery"
                    ]
                },
                {
                    "stage": "Scanning Officer",
                    "flag": WorkflowFlag.SCANNED,
                    "notifications": [
                        {
                            "message": "Form scanned and digitized",
                            "type": "info"
                        }
                    ],
                    "details": [
                        "Scan the printed form",
                        "Verify QR code readability",
                        "Archive digital copy",
                        "Prepare for delivery"
                    ]
                },
                {
                    "stage": "Delivery Officer",
                    "flag": WorkflowFlag.COMPLETED,
                    "notifications": [
                        {
                            "message": "Form delivered to bhikku - registration complete",
                            "type": "success"
                        }
                    ],
                    "details": [
                        "Deliver form to beneficiary",
                        "Obtain delivery confirmation",
                        "Archive final documentation",
                        "Update registration status"
                    ]
                }
            ]
        }


# Global instance
bhikku_workflow_service = BhikkuWorkflowService()
