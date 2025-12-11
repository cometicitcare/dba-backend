from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission, has_any_permission
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas.vihara import (
    CRUDAction,
    ViharaCreate,
    ViharaCreatePayload,
    ViharaManagementRequest,
    ViharaManagementResponse,
    ViharaOut,
    ViharaUpdate,
)
from app.services.vihara_service import vihara_service
from app.utils.http_exceptions import validation_error

router = APIRouter()  # Tags defined in router.py


@router.post("/manage", response_model=ViharaManagementResponse, dependencies=[has_any_permission("vihara:create", "vihara:read", "vihara:update", "vihara:delete")])
def manage_vihara_records(
    request: ViharaManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    action = request.action
    payload = request.payload
    user_id = current_user.ua_user_id

    if action == CRUDAction.CREATE:
        # Try camelCase first, then fall back to snake_case
        create_payload = None
        
        # Convert to dict if it's a BaseModel
        raw_data = payload.data
        if isinstance(raw_data, BaseModel):
            raw_data = raw_data.model_dump(exclude_unset=True)
        
        # Check if payload has camelCase keys
        if isinstance(raw_data, dict):
            has_camelcase = any(key in raw_data for key in ["temple_name", "telephone_number", "whatsapp_number", "email_address", "temple_type", "owner_code"])
            
            if has_camelcase:
                try:
                    create_payload = _coerce_payload(
                        raw_data,
                        target=ViharaCreatePayload,
                        prefix="payload.data",
                    )
                except Exception:
                    # If camelCase validation fails, raise the error
                    raise
        
        if create_payload is None:
            create_payload = _coerce_payload(
                payload.data,
                target=ViharaCreate,
                prefix="payload.data",
            )
        
        try:
            created = vihara_service.create_vihara(
                db, payload=create_payload, actor_id=user_id
            )
            return ViharaManagementResponse(
                status="success",
                message="Vihara created successfully.",
                data=created,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    if action == CRUDAction.READ_ONE:
        identifier_id = payload.vh_id
        identifier_trn = payload.vh_trn
        if identifier_id is None and not identifier_trn:
            raise validation_error(
                [("payload.vh_id", "vh_id or vh_trn is required for READ_ONE action")]
            )

        entity: ViharaOut | None = None
        if identifier_id is not None:
            entity = vihara_service.get_vihara(db, identifier_id)
        elif identifier_trn:
            entity = vihara_service.get_vihara_by_trn(db, identifier_trn)

        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Vihara not found"
            )

        return ViharaManagementResponse(
            status="success",
            message="Vihara retrieved successfully.",
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
            "vh_trn": payload.vh_trn,
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
            "vh_typ": payload.vh_typ,
            "date_from": payload.date_from,
            "date_to": payload.date_to,
        }

        records = vihara_service.list_viharas(db, **filters)
        total = vihara_service.count_viharas(db, **{k: v for k, v in filters.items() if k not in ["skip", "limit"]})
        
        return ViharaManagementResponse(
            status="success",
            message="Vihara records retrieved successfully.",
            data=records,
            totalRecords=total,
            page=page,
            limit=limit,
        )

    if action == CRUDAction.UPDATE:
        if payload.vh_id is None:
            raise validation_error(
                [("payload.vh_id", "vh_id is required for UPDATE action")]
            )
        update_payload = _coerce_payload(
            payload.data,
            target=ViharaUpdate,
            prefix="payload.data",
        )

        try:
            updated = vihara_service.update_vihara(
                db,
                vh_id=payload.vh_id,
                payload=update_payload,
                actor_id=user_id,
            )
            return ViharaManagementResponse(
                status="success",
                message="Vihara updated successfully.",
                data=updated,
            )
        except ValueError as exc:
            if "not found" in str(exc).lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
                ) from exc
            raise validation_error([(None, str(exc))]) from exc

    if action == CRUDAction.DELETE:
        if payload.vh_id is None:
            raise validation_error(
                [("payload.vh_id", "vh_id is required for DELETE action")]
            )
        try:
            vihara_service.delete_vihara(
                db,
                vh_id=payload.vh_id,
                actor_id=user_id,
            )
            return ViharaManagementResponse(
                status="success",
                message="Vihara deleted successfully.",
                data=None,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
            ) from exc

    if action == CRUDAction.APPROVE:
        if payload.vh_id is None:
            raise validation_error(
                [("payload.vh_id", "vh_id is required for APPROVE action")]
            )
        
        try:
            approved_vihara = vihara_service.approve_vihara(
                db, vh_id=payload.vh_id, actor_id=user_id
            )
            return ViharaManagementResponse(
                status="success",
                message="Vihara approved successfully.",
                data=approved_vihara,
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=message
                ) from exc
            raise validation_error([(None, message)]) from exc

    if action == CRUDAction.REJECT:
        if payload.vh_id is None:
            raise validation_error(
                [("payload.vh_id", "vh_id is required for REJECT action")]
            )
        if not payload.rejection_reason:
            raise validation_error(
                [("payload.rejection_reason", "Rejection reason is required for REJECT action")]
            )
        
        try:
            rejected_vihara = vihara_service.reject_vihara(
                db,
                vh_id=payload.vh_id,
                actor_id=user_id,
                rejection_reason=payload.rejection_reason,
            )
            return ViharaManagementResponse(
                status="success",
                message="Vihara rejected successfully.",
                data=rejected_vihara,
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=message
                ) from exc
            raise validation_error([(None, message)]) from exc

    if action == CRUDAction.MARK_PRINTED:
        if payload.vh_id is None:
            raise validation_error(
                [("payload.vh_id", "vh_id is required for MARK_PRINTED action")]
            )
        
        try:
            printed_vihara = vihara_service.mark_printed(
                db, vh_id=payload.vh_id, actor_id=user_id
            )
            return ViharaManagementResponse(
                status="success",
                message="Vihara certificate marked as printed successfully.",
                data=printed_vihara,
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=message
                ) from exc
            raise validation_error([(None, message)]) from exc

    if action == CRUDAction.MARK_SCANNED:
        if payload.vh_id is None:
            raise validation_error(
                [("payload.vh_id", "vh_id is required for MARK_SCANNED action")]
            )
        
        try:
            scanned_vihara = vihara_service.mark_scanned(
                db, vh_id=payload.vh_id, actor_id=user_id
            )
            return ViharaManagementResponse(
                status="success",
                message="Vihara certificate marked as scanned successfully.",
                data=scanned_vihara,
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
    "/{vh_id}/upload-scanned-document",
    response_model=ViharaManagementResponse,
    dependencies=[has_any_permission("vihara:update")],
)
async def upload_scanned_document(
    vh_id: int,
    file: UploadFile = File(..., description="Scanned document file (max 5MB, PDF, JPG, PNG)"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Upload a scanned document for a Vihara record.
    
    **NEW BEHAVIOR**: Automatically changes workflow status from PRINTED → PEND-APPROVAL when document is uploaded.
    
    This endpoint allows uploading a scanned document (up to 5MB) for a specific vihara.
    The file will be stored at: `app/storage/vihara_data/<year>/<month>/<day>/<vh_trn>/scanned_document_*.ext`
    
    **Requirements:**
    - Maximum file size: 5MB
    - Allowed formats: PDF, JPG, JPEG, PNG
    - Current workflow status must be PRINTED
    - Requires: vihara:update permission
    
    **Auto-Workflow Transition:**
    - Status automatically changes from PRINTED → PEND-APPROVAL
    - Sets vh_scanned_by and vh_scanned_at fields
    - Eliminates need for separate MARK_SCANNED action
    
    **Path Parameters:**
    - vh_id: Vihara ID (e.g., 5)
    
    **Form Data:**
    - file: The scanned document file to upload
    
    **Response:**
    Returns the updated Vihara record with:
    - vh_scanned_document_path: File path stored  
    - vh_workflow_status: "PEND-APPROVAL" (automatically set)
    - vh_scanned_by: User who uploaded
    - vh_scanned_at: Upload timestamp
    
    **Example Usage (Postman):**
    1. Method: POST
    2. URL: {{base_url}}/api/v1/vihara-data/5/upload-scanned-document
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
        
        # Upload the file and update the vihara record
        updated_vihara = await vihara_service.upload_scanned_document(
            db, vh_id=vh_id, file=file, actor_id=username
        )
        
        return ViharaManagementResponse(
            status="success",
            message="Scanned document uploaded successfully. Status automatically changed to PEND-APPROVAL.",
            data=updated_vihara,
        )
        
    except ValueError as exc:
        message = str(exc)
        if "not found" in message.lower():
            raise HTTPException(status_code=404, detail=message) from exc
        raise HTTPException(status_code=400, detail=message) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
