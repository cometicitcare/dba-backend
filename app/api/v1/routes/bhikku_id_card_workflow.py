# app/api/v1/routes/bhikku_id_card_workflow.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List

from app.api.deps import get_db
from app.api.auth_middleware import get_current_user
from app.models.user import UserAccount
from app.models.bhikku_id_card_workflow_flag import BhikkuIDCardWorkflowFlag
from app.services.bhikku_id_card_workflow_service import bhikku_id_card_workflow_service
from pydantic import BaseModel

router = APIRouter()


# --- Request/Response Schemas ---
class IDCardWorkflowApprovalRequest(BaseModel):
    bic_regn: str
    notes: Optional[str] = None
    
    class Config:
        example = {
            "bic_regn": "BH2025000048",
            "notes": "All details verified and correct"
        }


class IDCardWorkflowRejectionRequest(BaseModel):
    bic_regn: str
    rejection_notes: str
    
    class Config:
        example = {
            "bic_regn": "BH2025000048",
            "rejection_notes": "Missing required documentation"
        }


class IDCardWorkflowActionRequest(BaseModel):
    bic_regn: str
    
    class Config:
        example = {
            "bic_regn": "BH2025000048"
        }


class IDCardWorkflowStatusResponse(BaseModel):
    status: str
    message: str
    data: Optional[dict] = None
    
    class Config:
        example = {
            "status": "success",
            "message": "ID card record approved successfully",
            "data": {
                "bic_id": 1,
                "workflow_status": "approved",
                "updated_at": "2025-01-14T10:30:00"
            }
        }


class IDCardWorkflowListResponse(BaseModel):
    status: str
    message: str
    data: Optional[List[dict]] = None
    
    class Config:
        example = {
            "status": "success",
            "message": "Pending ID card records retrieved",
            "data": [
                {
                    "bic_id": 1,
                    "bhikku_id": 10,
                    "workflow_status": "pending",
                    "pending_date": "2025-01-14T09:00:00"
                }
            ]
        }


# --- Helper function to format workflow response ---
def _format_workflow_response(workflow: BhikkuIDCardWorkflowFlag) -> dict:
    """Convert workflow object to dictionary"""
    return {
        "bic_id": workflow.bicwf_bhikku_id_card_id,
        "bhikku_id": workflow.bicwf_bhikku_id,
        "workflow_status": workflow.bicwf_current_flag.value,
        "pending_date": workflow.bicwf_pending_date.isoformat() if workflow.bicwf_pending_date else None,
        "approval_date": workflow.bicwf_approval_date.isoformat() if workflow.bicwf_approval_date else None,
        "approval_by": workflow.bicwf_approval_by,
        "approval_notes": workflow.bicwf_approval_notes,
        "printing_date": workflow.bicwf_printing_date.isoformat() if workflow.bicwf_printing_date else None,
        "print_by": workflow.bicwf_print_by,
        "scan_date": workflow.bicwf_scan_date.isoformat() if workflow.bicwf_scan_date else None,
        "scan_by": workflow.bicwf_scan_by,
        "completion_date": workflow.bicwf_completion_date.isoformat() if workflow.bicwf_completion_date else None,
        "completed_by": workflow.bicwf_completed_by,
        "updated_at": workflow.bicwf_updated_at.isoformat() if workflow.bicwf_updated_at else None
    }


# --- Workflow Endpoints ---

@router.post(
    "/approve",
    response_model=IDCardWorkflowStatusResponse,
    summary="Approve an ID card record",
    description="Officer approves a pending ID card record"
)
def approve_id_card(
    request: IDCardWorkflowApprovalRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Approve a pending ID card record.
    Transitions workflow status from PENDING to APPROVED.
    """
    try:
        workflow = bhikku_id_card_workflow_service.approve_workflow(
            db=db,
            bic_regn=request.bic_regn,
            approved_by=current_user.ua_user_id,
            notes=request.notes
        )
        
        return {
            "status": "success",
            "message": f"ID card record ({request.bic_regn}) approved successfully",
            "data": _format_workflow_response(workflow)
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error approving ID card: {str(e)}")


@router.post(
    "/reject",
    response_model=IDCardWorkflowStatusResponse,
    summary="Reject an ID card record",
    description="Officer rejects a pending ID card record"
)
def reject_id_card(
    request: IDCardWorkflowRejectionRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Reject a pending ID card record.
    Transitions workflow status from PENDING to REJECTED.
    """
    try:
        workflow = bhikku_id_card_workflow_service.reject_workflow(
            db=db,
            bic_regn=request.bic_regn,
            rejected_by=current_user.ua_user_id,
            rejection_notes=request.rejection_notes
        )
        
        return {
            "status": "success",
            "message": f"ID card record ({request.bic_regn}) rejected",
            "data": _format_workflow_response(workflow)
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rejecting ID card: {str(e)}")


@router.post(
    "/send-to-printing",
    response_model=IDCardWorkflowStatusResponse,
    summary="Send approved ID card record to printing",
    description="Send an approved ID card record to the printing officer"
)
def send_to_printing(
    request: IDCardWorkflowActionRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Send an approved ID card record to printing.
    Transitions workflow status from APPROVED to PRINTED.
    """
    try:
        workflow = bhikku_id_card_workflow_service.send_to_printing(
            db=db,
            bic_regn=request.bic_regn,
            sent_by=current_user.ua_user_id
        )
        
        return {
            "status": "success",
            "message": f"ID card record ({request.bic_regn}) sent to printing",
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
    response_model=IDCardWorkflowStatusResponse,
    summary="Mark ID card record as scanned",
    description="Mark a printed ID card record as scanned"
)
def mark_scanned(
    request: IDCardWorkflowActionRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Mark a printed ID card record as scanned.
    Transitions workflow status from PRINTED to SCANNED.
    """
    try:
        workflow = bhikku_id_card_workflow_service.mark_as_scanned(
            db=db,
            bic_regn=request.bic_regn,
            scanned_by=current_user.ua_user_id
        )
        
        return {
            "status": "success",
            "message": f"ID card record ({request.bic_regn}) marked as scanned",
            "data": _format_workflow_response(workflow)
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking as scanned: {str(e)}")


@router.post(
    "/complete",
    response_model=IDCardWorkflowStatusResponse,
    summary="Complete ID card workflow",
    description="Complete a scanned ID card record"
)
def complete_workflow(
    request: IDCardWorkflowActionRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Complete a scanned ID card record.
    Transitions workflow status from SCANNED to COMPLETED.
    """
    try:
        workflow = bhikku_id_card_workflow_service.complete_workflow(
            db=db,
            bic_regn=request.bic_regn,
            completed_by=current_user.ua_user_id
        )
        
        return {
            "status": "success",
            "message": f"ID card record ({request.bic_regn}) workflow completed",
            "data": _format_workflow_response(workflow)
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error completing workflow: {str(e)}")


@router.get(
    "/status/{bic_regn}",
    response_model=IDCardWorkflowStatusResponse,
    summary="Get ID card workflow status",
    description="Get the current workflow status of an ID card record"
)
def get_status(
    bic_regn: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Get the current workflow status of an ID card record.
    """
    try:
        workflow = bhikku_id_card_workflow_service.get_workflow_for_registration(db, bic_regn)
        if not workflow:
            raise HTTPException(status_code=404, detail=f"Workflow not found for registration {bic_regn}")
    
        return {
            "status": "success",
            "message": f"Workflow status retrieved for ID card {bic_regn}",
            "data": _format_workflow_response(workflow)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving workflow status: {str(e)}")


@router.get(
    "/pending",
    response_model=IDCardWorkflowListResponse,
    summary="Get all pending ID card records",
    description="Get all ID card records with pending status"
)
def get_pending(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Get all ID card records with pending status.
    """
    try:
        workflows = bhikku_id_card_workflow_service.get_pending_records(db)
        data = [_format_workflow_response(w) for w in workflows]
        
        return {
            "status": "success",
            "message": f"Found {len(data)} pending ID card records",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving pending records: {str(e)}")


@router.get(
    "/approved",
    response_model=IDCardWorkflowListResponse,
    summary="Get all approved ID card records",
    description="Get all ID card records with approved status"
)
def get_approved(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Get all ID card records with approved status.
    """
    try:
        workflows = bhikku_id_card_workflow_service.get_approved_records(db)
        data = [_format_workflow_response(w) for w in workflows]
        
        return {
            "status": "success",
            "message": f"Found {len(data)} approved ID card records",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving approved records: {str(e)}")


@router.get(
    "/rejected",
    response_model=IDCardWorkflowListResponse,
    summary="Get all rejected ID card records",
    description="Get all ID card records with rejected status"
)
def get_rejected(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Get all ID card records with rejected status.
    """
    try:
        workflows = bhikku_id_card_workflow_service.get_rejected_records(db)
        data = [_format_workflow_response(w) for w in workflows]
        
        return {
            "status": "success",
            "message": f"Found {len(data)} rejected ID card records",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving rejected records: {str(e)}")


@router.get(
    "/printed",
    response_model=IDCardWorkflowListResponse,
    summary="Get all printed ID card records",
    description="Get all ID card records with printed status"
)
def get_printed(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Get all ID card records with printed status.
    """
    try:
        workflows = bhikku_id_card_workflow_service.get_printed_records(db)
        data = [_format_workflow_response(w) for w in workflows]
        
        return {
            "status": "success",
            "message": f"Found {len(data)} printed ID card records",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving printed records: {str(e)}")


@router.get(
    "/scanned",
    response_model=IDCardWorkflowListResponse,
    summary="Get all scanned ID card records",
    description="Get all ID card records with scanned status"
)
def get_scanned(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Get all ID card records with scanned status.
    """
    try:
        workflows = bhikku_id_card_workflow_service.get_scanned_records(db)
        data = [_format_workflow_response(w) for w in workflows]
        
        return {
            "status": "success",
            "message": f"Found {len(data)} scanned ID card records",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving scanned records: {str(e)}")


@router.get(
    "/completed",
    response_model=IDCardWorkflowListResponse,
    summary="Get all completed ID card records",
    description="Get all ID card records with completed status"
)
def get_completed(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Get all ID card records with completed status.
    """
    try:
        workflows = bhikku_id_card_workflow_service.get_completed_records(db)
        data = [_format_workflow_response(w) for w in workflows]
        
        return {
            "status": "success",
            "message": f"Found {len(data)} completed ID card records",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving completed records: {str(e)}")
