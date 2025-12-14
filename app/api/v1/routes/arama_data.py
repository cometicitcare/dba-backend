from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session
from typing import List

from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission, has_any_permission
from app.api.deps import get_db
from app.models.user import UserAccount
from app.models.silmatha_regist import SilmathaRegist
from app.schemas.arama import (
    CRUDAction,
    AramaCreate,
    AramaManagementRequest,
    AramaManagementResponse,
    AramaOut,
    AramaUpdate,
)
from app.services.arama_service import arama_service
from app.services.silmatha_regist_service import silmatha_regist_service
from app.repositories.silmatha_regist_repo import silmatha_regist_repo
from app.utils.http_exceptions import validation_error

router = APIRouter()  # Tags defined in router.py


@router.post("/manage", response_model=AramaManagementResponse, dependencies=[has_any_permission("arama:create", "arama:read", "arama:update", "arama:delete")])
def manage_arama_records(
    request: AramaManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Manage Arama records with role-based access control.
    
    Permission Requirements:
    - CREATE: arama:create
    - READ_ONE, READ_ALL: arama:read
    - UPDATE: arama:update
    - DELETE: arama:delete
    - APPROVE, REJECT, MARK_PRINTED, MARK_SCANNED: arama:update
    """
    from app.api.auth_dependencies import get_user_permissions, is_super_admin
    
    action = request.action
    payload = request.payload
    user_id = current_user.ua_user_id
    
    # Get user permissions
    user_perms = get_user_permissions(db, current_user)
    is_admin = is_super_admin(db, current_user)
    
    # Helper function to check permission
    def check_permission(required_perm: str):
        if not is_admin and required_perm not in user_perms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required permission: '{required_perm}'. Please contact your administrator if you need access to this resource."
            )

    if action == CRUDAction.CREATE:
        check_permission("arama:create")
        create_payload = _coerce_payload(
            payload.data,
            target=AramaCreate,
            prefix="payload.data",
        )
        try:
            created = arama_service.create_arama(
                db, payload=create_payload, actor_id=user_id
            )
            return AramaManagementResponse(
                status="success",
                message="Arama created successfully.",
                data=created,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    if action == CRUDAction.READ_ONE:
        check_permission("arama:read")
        identifier_id = payload.ar_id
        identifier_trn = payload.ar_trn
        if identifier_id is None and not identifier_trn:
            raise validation_error(
                [("payload.ar_id", "ar_id or ar_trn is required for READ_ONE action")]
            )

        entity: AramaOut | None = None
        if identifier_id is not None:
            entity = arama_service.get_arama(db, identifier_id)
        elif identifier_trn:
            entity = arama_service.get_arama_by_trn(db, identifier_trn)

        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Arama not found"
            )

        return AramaManagementResponse(
            status="success",
            message="Arama retrieved successfully.",
            data=entity,
        )

    if action == CRUDAction.READ_ALL:
        check_permission("arama:read")
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
            "ar_trn": payload.ar_trn,
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
            "ar_typ": payload.ar_typ,
            "date_from": payload.date_from,
            "date_to": payload.date_to,
            "current_user": current_user,
        }

        records = arama_service.list_aramas(db, **filters)
        total = arama_service.count_aramas(db, **{k: v for k, v in filters.items() if k not in ["skip", "limit", "current_user"]})
        
        return AramaManagementResponse(
            status="success",
            message="Arama records retrieved successfully.",
            data=records,
            totalRecords=total,
            page=page,
            limit=limit,
        )

    if action == CRUDAction.UPDATE:
        check_permission("arama:update")
        if payload.ar_id is None:
            raise validation_error(
                [("payload.ar_id", "ar_id is required for UPDATE action")]
            )
        update_payload = _coerce_payload(
            payload.data,
            target=AramaUpdate,
            prefix="payload.data",
        )

        try:
            updated = arama_service.update_arama(
                db,
                ar_id=payload.ar_id,
                payload=update_payload,
                actor_id=user_id,
            )
            return AramaManagementResponse(
                status="success",
                message="Arama updated successfully.",
                data=updated,
            )
        except ValueError as exc:
            if "not found" in str(exc).lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
                ) from exc
            raise validation_error([(None, str(exc))]) from exc

    if action == CRUDAction.DELETE:
        check_permission("arama:delete")
        if payload.ar_id is None:
            raise validation_error(
                [("payload.ar_id", "ar_id is required for DELETE action")]
            )
        try:
            arama_service.delete_arama(
                db,
                ar_id=payload.ar_id,
                actor_id=user_id,
            )
            return AramaManagementResponse(
                status="success",
                message="Arama deleted successfully.",
                data=None,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
            ) from exc

    if action == CRUDAction.APPROVE:
        check_permission("arama:update")
        if payload.ar_id is None:
            raise validation_error(
                [("payload.ar_id", "ar_id is required for APPROVE action")]
            )
        
        try:
            approved_arama = arama_service.approve_arama(
                db, ar_id=payload.ar_id, actor_id=user_id
            )
            return AramaManagementResponse(
                status="success",
                message="Arama approved successfully.",
                data=approved_arama,
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=message
                ) from exc
            raise validation_error([(None, message)]) from exc

    if action == CRUDAction.REJECT:
        check_permission("arama:update")
        if payload.ar_id is None:
            raise validation_error(
                [("payload.ar_id", "ar_id is required for REJECT action")]
            )
        if not payload.rejection_reason:
            raise validation_error(
                [("payload.rejection_reason", "Rejection reason is required for REJECT action")]
            )
        
        try:
            rejected_arama = arama_service.reject_arama(
                db,
                ar_id=payload.ar_id,
                actor_id=user_id,
                rejection_reason=payload.rejection_reason,
            )
            return AramaManagementResponse(
                status="success",
                message="Arama rejected successfully.",
                data=rejected_arama,
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=message
                ) from exc
            raise validation_error([(None, message)]) from exc

    if action == CRUDAction.MARK_PRINTED:
        check_permission("arama:update")
        if payload.ar_id is None:
            raise validation_error(
                [("payload.ar_id", "ar_id is required for MARK_PRINTED action")]
            )
        
        try:
            printed_arama = arama_service.mark_printed(
                db, ar_id=payload.ar_id, actor_id=user_id
            )
            return AramaManagementResponse(
                status="success",
                message="Arama certificate marked as printed successfully.",
                data=printed_arama,
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=message
                ) from exc
            raise validation_error([(None, message)]) from exc

    if action == CRUDAction.MARK_SCANNED:
        check_permission("arama:update")
        if payload.ar_id is None:
            raise validation_error(
                [("payload.ar_id", "ar_id is required for MARK_SCANNED action")]
            )
        
        try:
            scanned_arama = arama_service.mark_scanned(
                db, ar_id=payload.ar_id, actor_id=user_id
            )
            return AramaManagementResponse(
                status="success",
                message="Arama certificate marked as scanned successfully.",
                data=scanned_arama,
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
    "/{ar_id}/upload-scanned-document",
    response_model=AramaManagementResponse,
    dependencies=[has_any_permission("arama:update")],
)
async def upload_scanned_document(
    ar_id: int,
    file: UploadFile = File(..., description="Scanned document file (max 5MB, PDF, JPG, PNG)"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Upload a scanned document for an Arama record.
    
    **NEW BEHAVIOR**: Automatically changes workflow status from PRINTED → PEND-APPROVAL when document is uploaded.
    
    This endpoint allows uploading a scanned document (up to 5MB) for a specific arama.
    The file will be stored at: `app/storage/arama_data/<year>/<month>/<day>/<ar_trn>/scanned_document_*.ext`
    
    **Requirements:**
    - Maximum file size: 5MB
    - Allowed formats: PDF, JPG, JPEG, PNG
    - Current workflow status must be PRINTED
    - Requires: arama:update permission
    
    **Auto-Workflow Transition:**
    - Status automatically changes from PRINTED → PEND-APPROVAL
    - Sets ar_scanned_by and ar_scanned_at fields
    - Eliminates need for separate MARK_SCANNED action
    
    **Path Parameters:**
    - ar_id: Arama ID (e.g., 5)
    
    **Form Data:**
    - file: The scanned document file to upload
    
    **Response:**
    Returns the updated Arama record with:
    - ar_scanned_document_path: File path stored  
    - ar_workflow_status: "PEND-APPROVAL" (automatically set)
    - ar_scanned_by: User who uploaded
    - ar_scanned_at: Upload timestamp
    
    **Example Usage (Postman):**
    1. Method: POST
    2. URL: {{base_url}}/api/v1/arama-data/5/upload-scanned-document
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
        
        # Upload the file and update the arama record
        updated_arama = await arama_service.upload_scanned_document(
            db, ar_id=ar_id, file=file, actor_id=username
        )
        
        return AramaManagementResponse(
            status="success",
            message="Scanned document uploaded successfully. Status automatically changed to PEND-APPROVAL.",
            data=updated_arama,
        )
        
    except ValueError as exc:
        message = str(exc)
        if "not found" in message.lower():
            raise HTTPException(status_code=404, detail=message) from exc
        raise HTTPException(status_code=400, detail=message) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get(
    "/{ar_trn}/silmathas",
    dependencies=[has_any_permission("arama:read", "silmatha:read")],
)
def get_silmathas_by_arama(
    ar_trn: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Get all silmathas associated with a specific arama/temple by its TRN.
    
    This endpoint searches for silmatha records that are associated with the given
    arama/temple TRN through the following fields:
    - sil_robing_tutor_residence (robing tutor residence temple)
    - sil_mahanatemple (mahana temple)
    - sil_robing_after_residence_temple (robing after residence temple)
    
    **Path Parameters:**
    - ar_trn: Arama/Temple TRN (e.g., "TRN0000001" or "ARN0000001")
    
    **Query Parameters:**
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100, max: 200)
    
    **Response:**
    Returns a list of silmatha records enriched with nested foreign key data.
    
    **Example Usage:**
    ```
    GET /api/v1/arama-data/TRN0000001/silmathas?skip=0&limit=10
    ```
    """
    # Validate limit
    limit = max(1, min(limit, 200))
    skip = max(0, skip)
    
    # First, verify the arama exists
    arama = arama_service.get_arama_by_trn(db, ar_trn)
    if not arama:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Arama with TRN '{ar_trn}' not found"
        )
    
    # Search for silmathas associated with this arama/temple TRN
    # Since silmatha references vihara (vh_trn), we search using the ar_trn
    # as if it were a vh_trn (they may be the same or related in the system)
    silmathas_query = db.query(SilmathaRegist).filter(
        SilmathaRegist.sil_is_deleted.is_(False)
    ).filter(
        (SilmathaRegist.sil_robing_tutor_residence == ar_trn) |
        (SilmathaRegist.sil_mahanatemple == ar_trn) |
        (SilmathaRegist.sil_robing_after_residence_temple == ar_trn)
    )
    
    # Get total count
    total_count = silmathas_query.count()
    
    # Get paginated results
    silmathas = silmathas_query.offset(skip).limit(limit).all()
    
    # Enrich silmatha records with nested foreign key data
    enriched_silmathas = [
        silmatha_regist_service.enrich_silmatha_dict(silmatha, db)
        for silmatha in silmathas
    ]
    
    return {
        "status": "success",
        "message": f"Found {total_count} silmatha(s) associated with arama '{ar_trn}'",
        "data": enriched_silmathas,
        "totalRecords": total_count,
        "skip": skip,
        "limit": limit,
        "ar_trn": ar_trn,
        "arama_name": arama.ar_vname,
    }
