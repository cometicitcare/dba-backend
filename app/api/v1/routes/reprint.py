# app/api/v1/routes/reprint.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.api.auth_dependencies import has_any_permission
from app.api.auth_middleware import get_current_user
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas import reprint as schemas
from app.services.reprint_service import reprint_service

router = APIRouter()


@router.get(
    "",
    response_model=schemas.ReprintRequestListResponse,
    dependencies=[
        has_any_permission(
            "bhikku:read",
            "bhikku:update",
            "bhikku:approve",
            "bhikku_high:read",
            "bhikku_high:update",
            "bhikku_high:approve",
        )
    ],
)
def list_reprint_requests(
    flow_status: Optional[schemas.ReprintFlowStatus] = Query(None),
    request_type: Optional[schemas.ReprintType] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """List reprint requests with optional status/type filters."""
    records = reprint_service.list_requests(
        db, flow_status=flow_status, request_type=request_type
    )
    return {
        "status": "success",
        "message": "Reprint requests retrieved successfully.",
        "data": records,
    }


@router.post(
    "",
    response_model=schemas.ReprintManageResponse,
    dependencies=[
        has_any_permission(
            "bhikku:update",
            "bhikku:approve",
            "bhikku_high:update",
            "bhikku_high:approve",
        )
    ],
)
def manage_reprint(
    request: schemas.ReprintManageRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Manage reprint requests via actions (single endpoint CRUD).
    Actions: CREATE, READ_ONE, READ_ALL, APPROVE, REJECT, MARK_PRINTED, DELETE
    """
    actor_id = current_user.ua_user_id if current_user else None
    action = request.action

    try:
        if action == schemas.ReprintAction.CREATE:
            if not request.create_payload:
                raise HTTPException(status_code=400, detail="create_payload is required for CREATE")
            record = reprint_service.create_request(
                db, payload=request.create_payload, actor_id=actor_id
            )
            return {
                "status": "success",
                "message": "Reprint request created (status = PENDING).",
                "data": record,
            }

        if action == schemas.ReprintAction.READ_ONE:
            if not request.request_id:
                raise HTTPException(status_code=400, detail="request_id is required for READ_ONE")
            record = reprint_service.get_by_identifier(db, identifier=request.request_id)
            if not record:
                raise HTTPException(status_code=404, detail="Reprint request not found")
            return {
                "status": "success",
                "message": "Reprint request retrieved.",
                "data": record,
            }

        if action == schemas.ReprintAction.READ_ALL:
            records = reprint_service.list_requests(
                db,
                flow_status=request.flow_status,
                request_type=request.request_type,
            )
            return {
                "status": "success",
                "message": "Reprint requests retrieved.",
                "data": records,
            }

        if action == schemas.ReprintAction.APPROVE:
            if not request.request_id:
                raise HTTPException(status_code=400, detail="request_id is required for APPROVE")
            try:
                req_id = int(request.request_id)
            except (TypeError, ValueError):
                raise HTTPException(status_code=400, detail="request_id must be numeric for APPROVE")
            record = reprint_service.approve(
                db, request_id=req_id, actor_id=actor_id
            )
            return {
                "status": "success",
                "message": "Reprint request approved.",
                "data": record,
            }

        if action == schemas.ReprintAction.REJECT:
            if not request.request_id:
                raise HTTPException(status_code=400, detail="request_id is required for REJECT")
            if not request.rejection_reason:
                raise HTTPException(status_code=400, detail="rejection_reason is required for REJECT")
            try:
                req_id = int(request.request_id)
            except (TypeError, ValueError):
                raise HTTPException(status_code=400, detail="request_id must be numeric for REJECT")
            record = reprint_service.reject(
                db,
                request_id=req_id,
                actor_id=actor_id,
                rejection_reason=request.rejection_reason,
            )
            return {
                "status": "success",
                "message": "Reprint request rejected.",
                "data": record,
            }

        if action == schemas.ReprintAction.MARK_PRINTED:
            if not request.request_id:
                raise HTTPException(status_code=400, detail="request_id is required for MARK_PRINTED")
            try:
                req_id = int(request.request_id)
            except (TypeError, ValueError):
                raise HTTPException(status_code=400, detail="request_id must be numeric for MARK_PRINTED")
            record = reprint_service.mark_printed(
                db, request_id=req_id, actor_id=actor_id
            )
            return {
                "status": "success",
                "message": "Reprint request marked as COMPLETED after printing.",
                "data": record,
            }

        if action == schemas.ReprintAction.DELETE:
            if not request.request_id:
                raise HTTPException(status_code=400, detail="request_id is required for DELETE")
            try:
                req_id = int(request.request_id)
            except (TypeError, ValueError):
                raise HTTPException(status_code=400, detail="request_id must be numeric for DELETE")
            reprint_service.delete(db, request_id=req_id)
            return {
                "status": "success",
                "message": "Reprint request deleted.",
                "data": None,
            }

        raise HTTPException(status_code=400, detail="Invalid action")

    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise HTTPException(status_code=status_code, detail=message) from exc
