# app/api/v1/routes/direct_bhikku_high.py
"""
API routes for Direct High Bhikku Registration
Combines bhikku registration and high bhikku registration in a single workflow
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission, has_any_permission
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas.direct_bhikku_high import (
    CRUDAction,
    DirectBhikkuHighCreate,
    DirectBhikkuHighManagementRequest,
    DirectBhikkuHighManagementResponse,
    DirectBhikkuHighUpdate,
)
from app.services.direct_bhikku_high_service import direct_bhikku_high_service
from app.utils.http_exceptions import validation_error

router = APIRouter()


@router.post(
    "/manage",
    response_model=DirectBhikkuHighManagementResponse,
    response_model_by_alias=True,
    dependencies=[has_any_permission("bhikku:create", "bhikku:read", "bhikku:update", "bhikku:delete")]
)
def manage_direct_bhikku_high_records(
    request: DirectBhikkuHighManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Manage direct high bhikku records with CRUD operations.
    
    This endpoint handles CREATE, READ_ONE, READ_ALL, UPDATE, DELETE, 
    APPROVE, REJECT, MARK_PRINTED, and MARK_SCANNED actions.
    
    Workflow:
    1. Create record → PENDING
    2. Mark as printed → PRINTED
    3. Upload scanned document → PEND-APPROVAL (auto-transition)
    4. Approve/Reject → COMPLETED or REJECTED
    """
    action = request.action
    payload = request.payload
    user_id = current_user.ua_user_id

    # ==================== CREATE ====================
    if action == CRUDAction.CREATE:
        if not payload.data:
            raise validation_error([("payload.data", "data is required for CREATE action")])

        # Coerce to DirectBhikkuHighCreate
        create_payload = _coerce_payload(
            payload.data,
            target=DirectBhikkuHighCreate,
            prefix="payload.data",
        )

        try:
            created = direct_bhikku_high_service.create_direct_bhikku_high(
                db, payload=create_payload, actor_id=user_id, current_user=current_user
            )
            return DirectBhikkuHighManagementResponse(
                status="success",
                message="Direct high bhikku record created successfully.",
                data=created,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    # ==================== READ_ONE ====================
    if action == CRUDAction.READ_ONE:
        if payload.dbh_id is None and not payload.dbh_regn:
            raise validation_error([
                ("payload.dbh_id", "dbh_id or dbh_regn is required for READ_ONE action")
            ])

        entity = None
        if payload.dbh_id:
            entity = direct_bhikku_high_service.get_direct_bhikku_high(db, payload.dbh_id)
        elif payload.dbh_regn:
            entity = direct_bhikku_high_service.get_direct_bhikku_high_by_regn(db, payload.dbh_regn)

        if not entity:
            raise HTTPException(status_code=404, detail="Direct high bhikku record not found")

        return DirectBhikkuHighManagementResponse(
            status="success",
            message="Direct high bhikku record retrieved successfully.",
            data=entity,
        )

    # ==================== READ_ALL ====================
    if action == CRUDAction.READ_ALL:
        page = payload.page or 1
        limit = payload.limit
        search = payload.search_key.strip() if payload.search_key else None
        if search == "":
            search = None
        skip = payload.skip if payload.page is None else (page - 1) * limit

        # Extract filters
        filters = {
            "skip": skip,
            "limit": limit,
            "search": search,
            "province": payload.province,
            "district": payload.district,
            "divisional_secretariat": payload.divisional_secretariat,
            "gn_division": payload.gn_division,
            "parshawaya": payload.parshawaya,
            "status": payload.status,
            "workflow_status": payload.workflow_status,
            "date_from": payload.date_from,
            "date_to": payload.date_to,
            "current_user": current_user,
        }

        records = direct_bhikku_high_service.list_direct_bhikku_highs(db, **filters)
        total = direct_bhikku_high_service.count_direct_bhikku_highs(
            db, **{k: v for k, v in filters.items() if k not in ["skip", "limit"]}
        )

        return DirectBhikkuHighManagementResponse(
            status="success",
            message="Direct high bhikku records retrieved successfully.",
            data=records,
            totalRecords=total,
            page=page,
            limit=limit,
        )

    # ==================== UPDATE ====================
    if action == CRUDAction.UPDATE:
        if payload.dbh_id is None:
            raise validation_error([("payload.dbh_id", "dbh_id is required for UPDATE action")])

        update_payload = _coerce_payload(
            payload.data,
            target=DirectBhikkuHighUpdate,
            prefix="payload.data",
        )

        try:
            updated = direct_bhikku_high_service.update_direct_bhikku_high(
                db, dbh_id=payload.dbh_id, payload=update_payload, actor_id=user_id
            )
            return DirectBhikkuHighManagementResponse(
                status="success",
                message="Direct high bhikku record updated successfully.",
                data=updated,
            )
        except ValueError as exc:
            if "not found" in str(exc).lower():
                raise HTTPException(status_code=404, detail=str(exc)) from exc
            raise validation_error([(None, str(exc))]) from exc

    # ==================== DELETE ====================
    if action == CRUDAction.DELETE:
        if payload.dbh_id is None:
            raise validation_error([("payload.dbh_id", "dbh_id is required for DELETE action")])

        try:
            direct_bhikku_high_service.delete_direct_bhikku_high(
                db, dbh_id=payload.dbh_id, actor_id=user_id
            )
            return DirectBhikkuHighManagementResponse(
                status="success",
                message="Direct high bhikku record deleted successfully.",
                data=None,
            )
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    # ==================== APPROVE ====================
    if action == CRUDAction.APPROVE:
        if payload.dbh_id is None:
            raise validation_error([("payload.dbh_id", "dbh_id is required for APPROVE action")])

        try:
            approved = direct_bhikku_high_service.approve_direct_bhikku_high(
                db, dbh_id=payload.dbh_id, actor_id=user_id
            )
            return DirectBhikkuHighManagementResponse(
                status="success",
                message="Direct high bhikku record approved successfully.",
                data=approved,
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message) from exc
            raise validation_error([(None, message)]) from exc

    # ==================== REJECT ====================
    if action == CRUDAction.REJECT:
        if payload.dbh_id is None:
            raise validation_error([("payload.dbh_id", "dbh_id is required for REJECT action")])
        if not payload.rejection_reason:
            raise validation_error([
                ("payload.rejection_reason", "Rejection reason is required for REJECT action")
            ])

        try:
            rejected = direct_bhikku_high_service.reject_direct_bhikku_high(
                db,
                dbh_id=payload.dbh_id,
                actor_id=user_id,
                rejection_reason=payload.rejection_reason,
            )
            return DirectBhikkuHighManagementResponse(
                status="success",
                message="Direct high bhikku record rejected successfully.",
                data=rejected,
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message) from exc
            raise validation_error([(None, message)]) from exc

    # ==================== MARK_PRINTED ====================
    if action == CRUDAction.MARK_PRINTED:
        if payload.dbh_id is None:
            raise validation_error([("payload.dbh_id", "dbh_id is required for MARK_PRINTED action")])

        try:
            printed = direct_bhikku_high_service.mark_printed(
                db, dbh_id=payload.dbh_id, actor_id=user_id
            )
            return DirectBhikkuHighManagementResponse(
                status="success",
                message="Certificate marked as printed successfully.",
                data=printed,
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message) from exc
            raise validation_error([(None, message)]) from exc

    # ==================== MARK_SCANNED ====================
    if action == CRUDAction.MARK_SCANNED:
        if payload.dbh_id is None:
            raise validation_error([("payload.dbh_id", "dbh_id is required for MARK_SCANNED action")])

        try:
            scanned = direct_bhikku_high_service.mark_scanned(
                db, dbh_id=payload.dbh_id, actor_id=user_id
            )
            return DirectBhikkuHighManagementResponse(
                status="success",
                message="Certificate marked as scanned successfully.",
                data=scanned,
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message) from exc
            raise validation_error([(None, message)]) from exc

    raise validation_error([("action", "Invalid action specified")])


@router.post(
    "/{dbh_id}/upload-scanned-document",
    response_model=DirectBhikkuHighManagementResponse,
    dependencies=[has_any_permission("bhikku:update")],
)
async def upload_scanned_document(
    dbh_id: int,
    file: UploadFile = File(..., description="Scanned document file (max 5MB, PDF, JPG, PNG)"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Upload a scanned document for a direct high bhikku record.
    
    **AUTO-TRANSITION**: Automatically changes workflow status from PRINTED → PEND-APPROVAL.
    
    This endpoint allows uploading a scanned document (up to 5MB) for a specific direct high bhikku record.
    The file will be stored at: `app/storage/direct_bhikku_high/<year>/<month>/<day>/<dbh_regn>/scanned_document_*.ext`
    
    **Requirements:**
    - Maximum file size: 5MB
    - Allowed formats: PDF, JPG, JPEG, PNG
    - Current workflow status must be PRINTED
    - Requires: bhikku:update permission
    
    **Auto-Workflow Transition:**
    - Status automatically changes from PRINTED → PEND-APPROVAL
    - Sets dbh_scanned_by and dbh_scanned_at fields
    - Eliminates need for separate MARK_SCANNED action
    
    **Path Parameters:**
    - dbh_id: Direct high bhikku ID (e.g., 5)
    
    **Form Data:**
    - file: The scanned document file to upload
    
    **Response:**
    Returns the updated record with:
    - dbh_scanned_document_path: File path stored  
    - dbh_workflow_status: "PEND-APPROVAL" (automatically set)
    - dbh_scanned_by: User who uploaded
    - dbh_scanned_at: Upload timestamp
    
    **Example Usage (curl):**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/direct-bhikku-high/5/upload-scanned-document" \\
      -H "Authorization: Bearer <token>" \\
      -F "file=@/path/to/document.pdf"
    ```
    """
    username = current_user.ua_user_id if current_user else None

    try:
        # Validate file size (5MB = 5 * 1024 * 1024 bytes)
        MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

        # Read file content to check size
        file_content = await file.read()
        file_size = len(file_content)

        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size ({file_size / 1024 / 1024:.2f}MB) exceeds maximum allowed size (5MB)"
            )

        # Reset file pointer for later processing
        await file.seek(0)

        # Upload the file and update the record
        updated_record = await direct_bhikku_high_service.upload_scanned_document(
            db, dbh_id=dbh_id, file=file, actor_id=username
        )

        return DirectBhikkuHighManagementResponse(
            status="success",
            message="Scanned document uploaded successfully. Status automatically changed to PEND-APPROVAL.",
            data=updated_record,
        )

    except ValueError as exc:
        message = str(exc)
        if "not found" in message.lower():
            raise HTTPException(status_code=404, detail=message) from exc
        raise HTTPException(status_code=400, detail=message) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ==================== HELPER FUNCTIONS ====================
def _build_pydantic_errors(
    exc: ValidationError,
    *,
    prefix: str | None = None,
) -> list[tuple[str | None, str]]:
    """Build formatted error list from Pydantic ValidationError"""
    errors: list[tuple[str | None, str]] = []
    for err in exc.errors():
        loc = err.get("loc") or ()
        msg = err.get("msg") or "Invalid value"
        field_parts = [str(part) for part in loc if part != "__root__"]
        field = ".".join(field_parts) if field_parts else None
        if prefix:
            field = f"{prefix}.{field}" if field else prefix
        errors.append((field, msg))
    return errors or [(prefix, "Invalid payload") if prefix else (None, "Invalid payload")]


def _coerce_payload(
    raw_payload: object,
    *,
    target: type,
    prefix: str,
):
    """Coerce raw payload to target Pydantic model"""
    if raw_payload is None:
        raise validation_error([(prefix, "Payload is required")])

    if isinstance(raw_payload, target):
        return raw_payload

    if hasattr(raw_payload, "model_dump"):
        raw_payload = raw_payload.model_dump(exclude_unset=True)

    if isinstance(raw_payload, dict):
        try:
            return target.model_validate(raw_payload)
        except ValidationError as exc:
            raise validation_error(_build_pydantic_errors(exc, prefix=prefix)) from exc

    raise validation_error(
        [(prefix, f"Expected object compatible with {target.__name__}")],
    )
