from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission, has_any_permission
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas.devala import (
    CRUDAction,
    DevalaCreate,
    DevalaManagementRequest,
    DevalaManagementResponse,
    DevalaOut,
    DevalaUpdate,
)
from app.services.devala_service import devala_service
from app.utils.http_exceptions import validation_error

router = APIRouter()  # Tags defined in router.py


@router.post("/manage", response_model=DevalaManagementResponse, dependencies=[has_any_permission("devala:create", "devala:read", "devala:update", "devala:delete")])
def manage_devala_records(
    request: DevalaManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    action = request.action
    payload = request.payload
    user_id = current_user.ua_user_id

    if action == CRUDAction.CREATE:
        create_payload = _coerce_payload(
            payload.data,
            target=DevalaCreate,
            prefix="payload.data",
        )
        try:
            created = devala_service.create_devala(
                db, payload=create_payload, actor_id=user_id
            )
            return DevalaManagementResponse(
                status="success",
                message="Devala created successfully.",
                data=created,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    if action == CRUDAction.READ_ONE:
        identifier_id = payload.dv_id
        identifier_trn = payload.dv_trn
        if identifier_id is None and not identifier_trn:
            raise validation_error(
                [("payload.dv_id", "dv_id or dv_trn is required for READ_ONE action")]
            )

        entity: DevalaOut | None = None
        if identifier_id is not None:
            entity = devala_service.get_devala(db, identifier_id)
        elif identifier_trn:
            entity = devala_service.get_devala_by_trn(db, identifier_trn)

        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Devala not found"
            )

        return DevalaManagementResponse(
            status="success",
            message="Devala retrieved successfully.",
            data=entity,
        )

    if action == CRUDAction.READ_ALL:
        page = payload.page or 1
        limit = payload.limit
        search = payload.search_key.strip() if payload.search_key else None
        if search == "":
            search = None
        skip = payload.skip if payload.page is None else (page - 1) * limit

        # Extract all filter parameters from payload
        filters = {
            "skip": skip,
            "limit": limit,
            "search": search,
            "dv_trn": payload.dv_trn,
            "province": payload.province,
            "district": payload.district,
            "divisional_secretariat": payload.divisional_secretariat,
            "gn_division": payload.gn_division,
            "temple": payload.temple,
            "child_temple": payload.child_temple,
            "nikaya": payload.nikaya,
            "parshawaya": payload.parshawaya,
            "category": payload.category,
            "status": payload.status,
            "dv_typ": payload.dv_typ,
            "date_from": payload.date_from,
            "date_to": payload.date_to,
            "current_user": current_user,
        }

        records = devala_service.list_devalas(db, **filters)
        total = devala_service.count_devalas(db, **{k: v for k, v in filters.items() if k not in ["skip", "limit", "current_user"]})
        
        return DevalaManagementResponse(
            status="success",
            message="Devala records retrieved successfully.",
            data=records,
            totalRecords=total,
            page=page,
            limit=limit,
        )

    if action == CRUDAction.UPDATE:
        if payload.dv_id is None:
            raise validation_error(
                [("payload.dv_id", "dv_id is required for UPDATE action")]
            )
        update_payload = _coerce_payload(
            payload.data,
            target=DevalaUpdate,
            prefix="payload.data",
        )

        try:
            updated = devala_service.update_devala(
                db,
                dv_id=payload.dv_id,
                payload=update_payload,
                actor_id=user_id,
            )
            return DevalaManagementResponse(
                status="success",
                message="Devala updated successfully.",
                data=updated,
            )
        except ValueError as exc:
            if "not found" in str(exc).lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
                ) from exc
            raise validation_error([(None, str(exc))]) from exc

    if action == CRUDAction.DELETE:
        if payload.dv_id is None:
            raise validation_error(
                [("payload.dv_id", "dv_id is required for DELETE action")]
            )
        try:
            devala_service.delete_devala(
                db,
                dv_id=payload.dv_id,
                actor_id=user_id,
            )
            return DevalaManagementResponse(
                status="success",
                message="Devala deleted successfully.",
                data=None,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
            ) from exc

    if action == CRUDAction.APPROVE:
        if payload.dv_id is None:
            raise validation_error(
                [("payload.dv_id", "dv_id is required for APPROVE action")]
            )
        
        try:
            approved_devala = devala_service.approve_devala(
                db, dv_id=payload.dv_id, actor_id=user_id
            )
            return DevalaManagementResponse(
                status="success",
                message="Devala approved successfully.",
                data=approved_devala,
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=message
                ) from exc
            raise validation_error([(None, message)]) from exc

    if action == CRUDAction.REJECT:
        if payload.dv_id is None:
            raise validation_error(
                [("payload.dv_id", "dv_id is required for REJECT action")]
            )
        if not payload.rejection_reason:
            raise validation_error(
                [("payload.rejection_reason", "Rejection reason is required for REJECT action")]
            )
        
        try:
            rejected_devala = devala_service.reject_devala(
                db,
                dv_id=payload.dv_id,
                actor_id=user_id,
                rejection_reason=payload.rejection_reason,
            )
            return DevalaManagementResponse(
                status="success",
                message="Devala rejected successfully.",
                data=rejected_devala,
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=message
                ) from exc
            raise validation_error([(None, message)]) from exc

    if action == CRUDAction.MARK_PRINTED:
        if payload.dv_id is None:
            raise validation_error(
                [("payload.dv_id", "dv_id is required for MARK_PRINTED action")]
            )
        
        try:
            printed_devala = devala_service.mark_printed(
                db, dv_id=payload.dv_id, actor_id=user_id
            )
            return DevalaManagementResponse(
                status="success",
                message="Devala certificate marked as printed successfully.",
                data=printed_devala,
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=message
                ) from exc
            raise validation_error([(None, message)]) from exc

    if action == CRUDAction.MARK_SCANNED:
        if payload.dv_id is None:
            raise validation_error(
                [("payload.dv_id", "dv_id is required for MARK_SCANNED action")]
            )
        
        try:
            scanned_devala = devala_service.mark_scanned(
                db, dv_id=payload.dv_id, actor_id=user_id
            )
            return DevalaManagementResponse(
                status="success",
                message="Devala certificate marked as scanned successfully.",
                data=scanned_devala,
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=message
                ) from exc
            raise validation_error([(None, message)]) from exc

    raise validation_error([("action", "Invalid action specified")])


def _build_pydantic_errors(
    exc: ValidationError,
    *,
    prefix: str | None = None,
) -> list[tuple[str | None, str]]:
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
    target: type[BaseModel],
    prefix: str,
) -> BaseModel:
    if raw_payload is None:
        raise validation_error([(prefix, "Payload is required")])

    if isinstance(raw_payload, target):
        return raw_payload

    if isinstance(raw_payload, BaseModel):
        raw_payload = raw_payload.model_dump(exclude_unset=True)

    if isinstance(raw_payload, dict):
        try:
            return target.model_validate(raw_payload)
        except ValidationError as exc:
            raise validation_error(_build_pydantic_errors(exc, prefix=prefix)) from exc

    raise validation_error(
        [(prefix, f"Expected object compatible with {target.__name__}")],
    )


@router.post(
    "/{dv_id}/upload-scanned-document",
    response_model=DevalaManagementResponse,
    dependencies=[has_any_permission("devala:update")],
)
async def upload_scanned_document(
    dv_id: int,
    file: UploadFile = File(..., description="Scanned document file (max 5MB, PDF, JPG, PNG)"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Upload a scanned document for an Devala record.
    
    **NEW BEHAVIOR**: Automatically changes workflow status from PRINTED → PEND-APPROVAL when document is uploaded.
    
    This endpoint allows uploading a scanned document (up to 5MB) for a specific devala.
    The file will be stored at: `app/storage/devala_data/<year>/<month>/<day>/<dv_trn>/scanned_document_*.ext`
    
    **Requirements:**
    - Maximum file size: 5MB
    - Allowed formats: PDF, JPG, JPEG, PNG
    - Current workflow status must be PRINTED
    - Requires: devala:update permission
    
    **Auto-Workflow Transition:**
    - Status automatically changes from PRINTED → PEND-APPROVAL
    - Sets dv_scanned_by and dv_scanned_at fields
    - Eliminates need for separate MARK_SCANNED action
    
    **Path Parameters:**
    - dv_id: Devala ID (e.g., 5)
    
    **Form Data:**
    - file: The scanned document file to upload
    
    **Response:**
    Returns the updated Devala record with:
    - dv_scanned_document_path: File path stored  
    - dv_workflow_status: "PEND-APPROVAL" (automatically set)
    - dv_scanned_by: User who uploaded
    - dv_scanned_at: Upload timestamp
    
    **Example Usage (Postman):**
    1. Method: POST
    2. URL: {{base_url}}/api/v1/devala-data/5/upload-scanned-document
    3. Headers: Authorization: Bearer <token>
    4. Body: form-data
       - file: (select file)
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
        
        # Upload the file and update the devala record
        updated_devala = await devala_service.upload_scanned_document(
            db, dv_id=dv_id, file=file, actor_id=username
        )
        
        return DevalaManagementResponse(
            status="success",
            message="Scanned document uploaded successfully. Status automatically changed to PEND-APPROVAL.",
            data=updated_devala,
        )
        
    except ValueError as exc:
        message = str(exc)
        if "not found" in message.lower():
            raise HTTPException(status_code=404, detail=message) from exc
        raise HTTPException(status_code=400, detail=message) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
