# app/api/v1/routes/bhikku_workflow.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from app.api.deps import get_db
from app.api.auth_middleware import get_current_user
from app.models.user import UserAccount
from app.models.bhikku import Bhikku
from app.models.bhikku_workflow_flag import BhikkuWorkflowFlag
from app.services.bhikku_workflow_service import bhikku_workflow_service, WorkflowFlag
from pydantic import BaseModel

router = APIRouter()


# --- Request/Response Schemas ---
class WorkflowApprovalRequest(BaseModel):
    br_regn: str
    notes: Optional[str] = None
    
    class Config:
        example = {
            "br_regn": "BH2025000050",
            "notes": "All details verified and correct"
        }


class WorkflowRejectionRequest(BaseModel):
    br_regn: str
    rejection_notes: str
    
    class Config:
        example = {
            "br_regn": "BH2025000050",
            "rejection_notes": "Missing required documentation"
        }


class WorkflowActionRequest(BaseModel):
    br_regn: str
    
    class Config:
        example = {
            "br_regn": "BH2025000050"
        }


class WorkflowStatusResponse(BaseModel):
    status: str
    message: str
    data: Optional[dict] = None
    
    class Config:
        example = {
            "status": "success",
            "message": "Bhikku record approved successfully",
            "data": {
                "bhikku_id": 1,
                "workflow_status": "approved",
                "updated_at": "2025-01-14T10:30:00"
            }
        }


# --- Helper function to format workflow response ---
def _format_workflow_response(workflow: BhikkuWorkflowFlag) -> dict:
    """Convert workflow object to dictionary"""
    return {
        "bhikku_id": workflow.bwf_bhikku_id,
        "bhikku_regn": workflow.bwf_bhikku_regn,
        "workflow_status": workflow.bwf_current_flag.value,
        "pending_date": workflow.bwf_pending_date.isoformat() if workflow.bwf_pending_date else None,
        "approval_date": workflow.bwf_approval_date.isoformat() if workflow.bwf_approval_date else None,
        "approval_by": workflow.bwf_approval_by,
        "approval_notes": workflow.bwf_approval_notes,
        "printing_date": workflow.bwf_printing_date.isoformat() if workflow.bwf_printing_date else None,
        "print_by": workflow.bwf_print_by,
        "scan_date": workflow.bwf_scan_date.isoformat() if workflow.bwf_scan_date else None,
        "scan_by": workflow.bwf_scan_by,
        "completion_date": workflow.bwf_completion_date.isoformat() if workflow.bwf_completion_date else None,
        "completed_by": workflow.bwf_completed_by,
        "updated_at": workflow.bwf_updated_at.isoformat() if workflow.bwf_updated_at else None
    }


# --- Workflow Endpoints ---

@router.post(
    "/approve",
    response_model=WorkflowStatusResponse,
    summary="Approve a bhikku record",
    description="Officer approves a pending bhikku registration record"
)
def approve_bhikku(
    request: WorkflowApprovalRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Approve a pending bhikku record.
    Transitions workflow status from PENDING to APPROVED.
    """
    try:
        # Lookup bhikku by registration number
        bhikku = db.query(Bhikku).filter(Bhikku.br_regn == request.br_regn).first()
        if not bhikku:
            raise HTTPException(status_code=404, detail=f"Bhikku with registration {request.br_regn} not found")
        
        workflow = bhikku_workflow_service.approve_workflow(
            db=db,
            bhikku_id=bhikku.br_id,
            approved_by=current_user.ua_user_id,
            notes=request.notes
        )
        
        return {
            "status": "success",
            "message": f"Bhikku record ({request.br_regn}) approved successfully",
            "data": _format_workflow_response(workflow)
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error approving bhikku: {str(e)}")


@router.post(
    "/reject",
    response_model=WorkflowStatusResponse,
    summary="Reject a bhikku record",
    description="Officer rejects a pending bhikku registration record"
)
def reject_bhikku(
    request: WorkflowRejectionRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Reject a pending bhikku record.
    Transitions workflow status from PENDING to REJECTED.
    """
    try:
        # Lookup bhikku by registration number
        bhikku = db.query(Bhikku).filter(Bhikku.br_regn == request.br_regn).first()
        if not bhikku:
            raise HTTPException(status_code=404, detail=f"Bhikku with registration {request.br_regn} not found")
        
        workflow = bhikku_workflow_service.reject_workflow(
            db=db,
            bhikku_id=bhikku.br_id,
            rejected_by=current_user.ua_user_id,
            rejection_notes=request.rejection_notes
        )
        
        return {
            "status": "success",
            "message": f"Bhikku record ({request.br_regn}) rejected",
            "data": _format_workflow_response(workflow)
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rejecting bhikku: {str(e)}")


@router.post(
    "/send-to-printing",
    response_model=WorkflowStatusResponse,
    summary="Send approved record to printing",
    description="Send an approved bhikku record to the printing officer"
)
def send_to_printing(
    request: WorkflowActionRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Send an approved bhikku record to printing.
    Transitions workflow status from APPROVED to PRINTED.
    """
    try:
        # Lookup bhikku by registration number
        bhikku = db.query(Bhikku).filter(Bhikku.br_regn == request.br_regn).first()
        if not bhikku:
            raise HTTPException(status_code=404, detail=f"Bhikku with registration {request.br_regn} not found")
        
        workflow = bhikku_workflow_service.send_to_printing(
            db=db,
            bhikku_id=bhikku.br_id,
            sent_by=current_user.ua_user_id
        )
        
        return {
            "status": "success",
            "message": f"Bhikku record ({request.br_regn}) sent to printing",
            "data": _format_workflow_response(workflow)
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending to printing: {str(e)}")


@router.post(
    "/mark-scanned",
    response_model=WorkflowStatusResponse,
    summary="Mark record as scanned",
    description="Mark a printed bhikku record as scanned"
)
def mark_scanned(
    request: WorkflowActionRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Mark a printed bhikku record as scanned.
    Transitions workflow status from PRINTED to SCANNED.
    """
    try:
        # Lookup bhikku by registration number
        bhikku = db.query(Bhikku).filter(Bhikku.br_regn == request.br_regn).first()
        if not bhikku:
            raise HTTPException(status_code=404, detail=f"Bhikku with registration {request.br_regn} not found")
        
        workflow = bhikku_workflow_service.mark_as_scanned(
            db=db,
            bhikku_id=bhikku.br_id,
            scanned_by=current_user.ua_user_id
        )
        
        return {
            "status": "success",
            "message": f"Bhikku record ({request.br_regn}) marked as scanned",
            "data": _format_workflow_response(workflow)
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking scanned: {str(e)}")


@router.post(
    "/complete",
    response_model=WorkflowStatusResponse,
    summary="Complete workflow",
    description="Complete a scanned bhikku registration workflow"
)
def complete_workflow(
    request: WorkflowActionRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Complete a scanned bhikku registration workflow.
    Transitions workflow status from SCANNED to COMPLETED.
    """
    try:
        # Lookup bhikku by registration number
        bhikku = db.query(Bhikku).filter(Bhikku.br_regn == request.br_regn).first()
        if not bhikku:
            raise HTTPException(status_code=404, detail=f"Bhikku with registration {request.br_regn} not found")
        
        workflow = bhikku_workflow_service.complete_workflow(
            db=db,
            bhikku_id=bhikku.br_id,
            completed_by=current_user.ua_user_id
        )
        
        return {
            "status": "success",
            "message": f"Bhikku record ({request.br_regn}) workflow completed",
            "data": _format_workflow_response(workflow)
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error completing workflow: {str(e)}")


@router.get(
    "/status",
    response_model=WorkflowStatusResponse,
    summary="Get workflow status",
    description="Get the current workflow status of a bhikku record by registration number"
)
def get_workflow_status(
    br_regn: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Get the current workflow status of a bhikku record by registration number.
    """
    try:
        # Lookup bhikku by registration number
        bhikku = db.query(Bhikku).filter(Bhikku.br_regn == br_regn).first()
        if not bhikku:
            raise HTTPException(status_code=404, detail=f"Bhikku with registration {br_regn} not found")
        
        workflow = bhikku_workflow_service.get_workflow_for_bhikku(db, bhikku.br_id)
        
        if not workflow:
            raise HTTPException(
                status_code=404,
                detail=f"Workflow not found for registration {br_regn}"
            )
        
        return {
            "status": "success",
            "message": f"Workflow status retrieved for registration {br_regn}",
            "data": _format_workflow_response(workflow)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving workflow status: {str(e)}")


@router.get(
    "/flow-definition",
    summary="Get workflow flow definition",
    description="Get the complete workflow flow definition with all stages and transitions"
)
def get_workflow_definition(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Get the complete workflow flow definition showing all stages, transitions, and requirements.
    Useful for UI to display the workflow steps.
    """
    return {
        "status": "success",
        "message": "Workflow definition retrieved successfully",
        "data": {
            "stages": [
                {
                    "stage_number": 1,
                    "stage_name": "Data Entry",
                    "flag": WorkflowFlag.PENDING,
                    "description": "New bhikku registration submitted",
                    "next_possible_states": [WorkflowFlag.APPROVED, WorkflowFlag.REJECTED]
                },
                {
                    "stage_number": 2,
                    "stage_name": "Officer Review & Approval",
                    "flag": WorkflowFlag.APPROVED,
                    "description": "Officer reviews and approves the registration",
                    "previous_state": WorkflowFlag.PENDING,
                    "next_possible_states": [WorkflowFlag.PRINTED]
                },
                {
                    "stage_number": 2,
                    "stage_name": "Officer Review & Rejection",
                    "flag": WorkflowFlag.REJECTED,
                    "description": "Officer reviews and rejects the registration",
                    "previous_state": WorkflowFlag.PENDING,
                    "next_possible_states": []
                },
                {
                    "stage_number": 3,
                    "stage_name": "Printing",
                    "flag": WorkflowFlag.PRINTED,
                    "description": "Form is printed with QR code",
                    "previous_state": WorkflowFlag.APPROVED,
                    "next_possible_states": [WorkflowFlag.SCANNED]
                },
                {
                    "stage_number": 4,
                    "stage_name": "Scanning",
                    "flag": WorkflowFlag.SCANNED,
                    "description": "Printed form is scanned and digitized",
                    "previous_state": WorkflowFlag.PRINTED,
                    "next_possible_states": [WorkflowFlag.COMPLETED]
                },
                {
                    "stage_number": 5,
                    "stage_name": "Completion & Delivery",
                    "flag": WorkflowFlag.COMPLETED,
                    "description": "Form delivered to bhikku - process complete",
                    "previous_state": WorkflowFlag.SCANNED,
                    "next_possible_states": []
                }
            ]
        }
    }
