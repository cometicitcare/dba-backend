# app/api/v1/routes/reprint.py
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.auth_dependencies import is_super_admin
from app.api.auth_middleware import get_current_user
from app.api.deps import get_db
from app.models.user import UserAccount
from app.models.user_roles import UserRole
from app.schemas import reprint as schemas
from app.services.reprint_service import reprint_service

router = APIRouter()

DIV_SEC_ADMIN_ROLE_IDS = {"DS_ADMIN"}
DIV_SEC_DATA_ENTRY_ROLE_IDS = {"DS_DE001"}
ALLOWED_REPRINT_ROLE_IDS = DIV_SEC_ADMIN_ROLE_IDS | DIV_SEC_DATA_ENTRY_ROLE_IDS


def _get_active_role_ids(db: Session, user_id: str) -> set[str]:
    """Return active (non-expired) role IDs for the user."""
    now = datetime.utcnow()
    roles = (
        db.query(UserRole.ur_role_id)
        .filter(
            UserRole.ur_user_id == user_id,
            UserRole.ur_is_active.is_(True),
            (UserRole.ur_expires_date.is_(None) | (UserRole.ur_expires_date > now)),
        )
        .all()
    )
    return {role.ur_role_id for role in roles}


def require_reprint_roles(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Ensure caller has Divisional Secretariat access for reprint operations.
    Allows Div. Secretariat Admin/Data Entry roles and super admins.
    """
    if is_super_admin(db, current_user):
        return {
            "role_ids": set(),
            "is_super_admin": True,
            "is_div_sec_admin": True,
            "is_div_sec_data_entry": False,
        }

    role_ids = _get_active_role_ids(db, current_user.ua_user_id)
    if not role_ids.intersection(ALLOWED_REPRINT_ROLE_IDS):
        raise HTTPException(
            status_code=403,
            detail="Access denied. Reprint operations are limited to Divisional Secretariat Admin/Data Entry roles.",
        )

    return {
        "role_ids": role_ids,
        "is_super_admin": False,
        "is_div_sec_admin": bool(role_ids.intersection(DIV_SEC_ADMIN_ROLE_IDS)),
        "is_div_sec_data_entry": bool(role_ids.intersection(DIV_SEC_DATA_ENTRY_ROLE_IDS)),
    }


@router.get(
    "",
    response_model=schemas.ReprintRequestListResponse,
)
def list_reprint_requests(
    flow_status: Optional[schemas.ReprintFlowStatus] = Query(None),
    request_type: Optional[schemas.ReprintType] = Query(None),
    page: Optional[int] = Query(1, ge=1),
    limit: Optional[int] = Query(50, ge=1, le=200),
    search_key: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
    _: dict = Depends(require_reprint_roles),
):
    """List reprint requests with optional status/type filters."""
    records, total = reprint_service.list_requests(
        db,
        flow_status=flow_status,
        request_type=request_type,
        page=page,
        limit=limit,
        search_key=search_key,
    )
    return {
        "status": "success",
        "message": "Reprint requests retrieved successfully.",
        "data": records,
        "totalRecords": total,
        "page": page,
        "limit": limit,
    }


@router.post(
    "/reprint_url",
    response_model=schemas.ReprintUrlResponse,
)
def get_reprint_scanned_document_path(
    request: schemas.ReprintUrlRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
    _: dict = Depends(require_reprint_roles),
):
    """
    Return scanned document path for a given regn (bhikku / high bhikku / silmatha).
    """
    try:
        result = reprint_service.get_scanned_document_path(db, regn=request.regn)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise HTTPException(status_code=status_code, detail=message) from exc

    return {
        "status": "success",
        "message": "Scanned document path retrieved.",
        "data": result,
    }


@router.post(
    "",
    response_model=schemas.ReprintManageResponse,
)
def manage_reprint(
    request: schemas.ReprintManageRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
    access: dict = Depends(require_reprint_roles),
):
    """
    Manage reprint requests via actions (single endpoint CRUD).
    Actions: CREATE, READ_ONE, READ_ALL, APPROVE, REJECT, MARK_PRINTED, DELETE
    """
    actor_id = current_user.ua_user_id if current_user else None
    action = request.action
    is_admin = access.get("is_div_sec_admin") or access.get("is_super_admin")

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
            if not request.request_id or (isinstance(request.request_id, str) and not request.request_id.strip()):
                raise HTTPException(status_code=400, detail="request_id is required for READ_ONE")
            identifier = request.request_id
            record = reprint_service.get_by_identifier(db, identifier=identifier)

            # Return QR-search style payload (titel/text list) to mirror /qr_search response.
            qr_data = reprint_service.resolve_qr_details(
                db,
                record=record,
                identifier=identifier,
            )
            if not qr_data:
                raise HTTPException(status_code=404, detail=f"No record found with ID: {identifier}")
            return {
                "status": "success",
                "message": "Record details retrieved successfully.",
                "data": qr_data,
            }

        if action == schemas.ReprintAction.READ_ALL:
            records, total = reprint_service.list_requests(
                db,
                flow_status=request.flow_status,
                request_type=request.request_type,
                regn=request.regn,
                page=request.page,
                limit=request.limit,
                search_key=request.search_key,
            )
            return {
                "status": "success",
                "message": "Reprint requests retrieved.",
                "data": records,
                "totalRecords": total,
                "page": request.page,
                "limit": request.limit,
            }

        if action == schemas.ReprintAction.APPROVE:
            if not is_admin:
                raise HTTPException(
                    status_code=403,
                    detail="Only Divisional Secretariat Admins can approve reprint requests.",
                )
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
            if not is_admin:
                raise HTTPException(
                    status_code=403,
                    detail="Only Divisional Secretariat Admins can reject reprint requests.",
                )
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
            if not is_admin:
                raise HTTPException(
                    status_code=403,
                    detail="Only Divisional Secretariat Admins can mark reprints as printed.",
                )
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
            if not is_admin:
                raise HTTPException(
                    status_code=403,
                    detail="Only Divisional Secretariat Admins can delete reprint requests.",
                )
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
