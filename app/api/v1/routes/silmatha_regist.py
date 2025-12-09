# app/api/v1/routes/silmatha_regist.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission, has_any_permission, get_user_permissions
from app.models.user import UserAccount
from app.schemas import silmatha_regist as schemas
from app.services.silmatha_regist_service import silmatha_regist_service
from app.services.arama_service import arama_service
from app.repositories.silmatha_regist_repo import silmatha_regist_repo
from app.utils.http_exceptions import validation_error
from pydantic import ValidationError

router = APIRouter()

def check_silmatha_permission(db: Session, user: UserAccount, required_permission: str):
    """Ensure the current user has the required silmatha permission."""
    user_permissions = get_user_permissions(db, user)
    if required_permission not in user_permissions:
        raise HTTPException(
            status_code=403,
            detail=f"Permission denied. Required permission: {required_permission}"
        )


@router.post(
    "/manage",
    response_model=schemas.SilmathaRegistManagementResponse,
    dependencies=[has_any_permission("silmatha:create", "silmatha:update", "silmatha:delete", "silmatha:read")],
)
def manage_silmatha_records(
    request: schemas.SilmathaRegistManagementRequest, 
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Unified endpoint for all Silmatha CRUD operations.
    Requires authentication + at least one of: silmatha:create, silmatha:update, silmatha:delete, silmatha:read
    """
    action = request.action
    payload = request.payload

    # Get user identifier for audit trail
    user_id = current_user.ua_user_id

    if action == schemas.CRUDAction.CREATE:
        # Match Bhikku workflow by enforcing explicit create permission
        check_silmatha_permission(db, current_user, "silmatha:create")

        if not payload or not hasattr(payload, 'data'):
            raise validation_error(
                [("payload.data", "data is required for CREATE action")]
            )

        create_payload: schemas.SilmathaRegistCreate
        if isinstance(payload.data, schemas.SilmathaRegistCreate):
            create_payload = payload.data
        else:
            raw_data = (
                payload.data.model_dump()
                if hasattr(payload.data, "model_dump")
                else payload.data
            )
            try:
                create_payload = schemas.SilmathaRegistCreate(**raw_data)
            except ValidationError as exc:
                formatted_errors = []
                for error in exc.errors():
                    loc = ".".join(str(part) for part in error.get("loc", []))
                    formatted_errors.append(
                        (loc or None, error.get("msg", "Invalid data"))
                    )
                raise validation_error(formatted_errors) from exc

        try:
            created_silmatha = silmatha_regist_service.create_silmatha(
                db, payload=create_payload, actor_id=user_id, current_user=current_user
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        # Convert SQLAlchemy model to Pydantic schema with enriched nested data
        silmatha_enriched = silmatha_regist_service.enrich_silmatha_dict(created_silmatha, db)
        silmatha_schema = schemas.Silmatha.model_validate(silmatha_enriched)
        
        return schemas.SilmathaRegistManagementResponse(
            status="success",
            message="Silmatha record created successfully.",
            data=silmatha_schema,
        )

    elif action == schemas.CRUDAction.READ_ONE:
        if not payload or not hasattr(payload, 'sil_regn'):
            raise validation_error(
                [("payload.sil_regn", "sil_regn is required for READ_ONE action")]
            )
        
        db_silmatha = silmatha_regist_repo.get_by_regn(db, sil_regn=payload.sil_regn)
        if db_silmatha is None:
            raise HTTPException(status_code=404, detail="Silmatha record not found")
        
        # Enrich with nested FK objects
        silmatha_enriched = silmatha_regist_service.enrich_silmatha_dict(db_silmatha, db)
        silmatha_schema = schemas.Silmatha.model_validate(silmatha_enriched)
        
        return schemas.SilmathaRegistManagementResponse(
            status="success",
            message="Silmatha record retrieved successfully.",
            data=silmatha_schema,
        )

    elif action == schemas.CRUDAction.READ_ALL:
        # Handle pagination
        skip = payload.skip if payload and hasattr(payload, 'skip') else 0
        limit = payload.limit if payload and hasattr(payload, 'limit') else 100
        page = payload.page if payload and hasattr(payload, 'page') else 1
        search_key = payload.search_key.strip() if payload and hasattr(payload, 'search_key') and payload.search_key else None
        
        # Get paginated silmatha records with search and filters
        silmatha_records = silmatha_regist_repo.get_all(
            db, 
            skip=skip, 
            limit=limit, 
            search_key=search_key,
            vh_trn=payload.vh_trn if payload and hasattr(payload, 'vh_trn') else None,
            province=payload.province if payload and hasattr(payload, 'province') else None,
            district=payload.district if payload and hasattr(payload, 'district') else None,
            divisional_secretariat=payload.divisional_secretariat if payload and hasattr(payload, 'divisional_secretariat') else None,
            gn_division=payload.gn_division if payload and hasattr(payload, 'gn_division') else None,
            temple=payload.temple if payload and hasattr(payload, 'temple') else None,
            child_temple=payload.child_temple if payload and hasattr(payload, 'child_temple') else None,
            parshawaya=payload.parshawaya if payload and hasattr(payload, 'parshawaya') else None,
            category=payload.category if payload and hasattr(payload, 'category') else None,
            status=payload.status if payload and hasattr(payload, 'status') else None,
            workflow_status=payload.workflow_status if payload and hasattr(payload, 'workflow_status') else None,
            date_from=payload.date_from if payload and hasattr(payload, 'date_from') else None,
            date_to=payload.date_to if payload and hasattr(payload, 'date_to') else None,
            current_user=current_user
        )
        
        # Get total count for pagination
        total_count = silmatha_regist_repo.get_total_count(
            db, 
            search_key=search_key,
            vh_trn=payload.vh_trn if payload and hasattr(payload, 'vh_trn') else None,
            province=payload.province if payload and hasattr(payload, 'province') else None,
            district=payload.district if payload and hasattr(payload, 'district') else None,
            divisional_secretariat=payload.divisional_secretariat if payload and hasattr(payload, 'divisional_secretariat') else None,
            gn_division=payload.gn_division if payload and hasattr(payload, 'gn_division') else None,
            temple=payload.temple if payload and hasattr(payload, 'temple') else None,
            child_temple=payload.child_temple if payload and hasattr(payload, 'child_temple') else None,
            parshawaya=payload.parshawaya if payload and hasattr(payload, 'parshawaya') else None,
            category=payload.category if payload and hasattr(payload, 'category') else None,
            status=payload.status if payload and hasattr(payload, 'status') else None,
            workflow_status=payload.workflow_status if payload and hasattr(payload, 'workflow_status') else None,
            date_from=payload.date_from if payload and hasattr(payload, 'date_from') else None,
            date_to=payload.date_to if payload and hasattr(payload, 'date_to') else None,
            current_user=current_user
        )
        
        # Enrich each record with nested FK objects
        silmatha_enriched = [silmatha_regist_service.enrich_silmatha_dict(record, db) for record in silmatha_records]
        
        return schemas.SilmathaRegistManagementResponse(
            status="success",
            message="Silmatha records retrieved successfully.",
            data=silmatha_enriched,
            totalRecords=total_count,
            page=page,
            limit=limit,
        )

    elif action == schemas.CRUDAction.UPDATE:
        if not payload or not hasattr(payload, 'sil_regn'):
            raise validation_error(
                [("payload.sil_regn", "sil_regn is required for UPDATE action")]
            )
        if not hasattr(payload, 'data'):
            raise validation_error(
                [("payload.data", "data is required for UPDATE action")]
            )

        update_payload: schemas.SilmathaRegistUpdate
        if isinstance(payload.data, schemas.SilmathaRegistUpdate):
            update_payload = payload.data
        else:
            raw_data = (
                payload.data.model_dump()
                if hasattr(payload.data, "model_dump")
                else payload.data
            )
            try:
                update_payload = schemas.SilmathaRegistUpdate(**raw_data)
            except ValidationError as exc:
                formatted_errors = []
                for error in exc.errors():
                    loc = ".".join(str(part) for part in error.get("loc", []))
                    formatted_errors.append(
                        (loc or None, error.get("msg", "Invalid data"))
                    )
                raise validation_error(formatted_errors) from exc

        try:
            updated_silmatha = silmatha_regist_service.update_silmatha(
                db, sil_regn=payload.sil_regn, payload=update_payload, actor_id=user_id
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message) from exc
            raise validation_error([(None, message)]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        silmatha_enriched = silmatha_regist_service.enrich_silmatha_dict(updated_silmatha, db)
        silmatha_schema = schemas.Silmatha.model_validate(silmatha_enriched)
        return schemas.SilmathaRegistManagementResponse(
            status="success",
            message="Silmatha record updated successfully.",
            data=silmatha_schema,
        )

    elif action == schemas.CRUDAction.DELETE:
        if not payload or not hasattr(payload, 'sil_regn'):
            raise validation_error(
                [("payload.sil_regn", "sil_regn is required for DELETE action")]
            )
        
        try:
            silmatha_regist_service.delete_silmatha(
                db, sil_regn=payload.sil_regn, actor_id=user_id
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message) from exc
            raise validation_error([(None, message)]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        return schemas.SilmathaRegistManagementResponse(
            status="success",
            message="Silmatha record deleted successfully.",
            data=None,
        )

    elif action == schemas.CRUDAction.APPROVE:
        if not payload or not hasattr(payload, 'sil_regn'):
            raise validation_error(
                [("payload.sil_regn", "sil_regn is required for APPROVE action")]
            )
        
        try:
            approved_silmatha = silmatha_regist_service.approve_silmatha(
                db, sil_regn=payload.sil_regn, actor_id=user_id
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message) from exc
            raise validation_error([(None, message)]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        silmatha_enriched = silmatha_regist_service.enrich_silmatha_dict(approved_silmatha, db)
        silmatha_schema = schemas.Silmatha.model_validate(silmatha_enriched)
        return schemas.SilmathaRegistManagementResponse(
            status="success",
            message="Silmatha record approved successfully.",
            data=silmatha_schema,
        )

    elif action == schemas.CRUDAction.REJECT:
        if not payload or not hasattr(payload, 'sil_regn'):
            raise validation_error(
                [("payload.sil_regn", "sil_regn is required for REJECT action")]
            )
        if not hasattr(payload, 'rejection_reason'):
            raise validation_error(
                [("payload.rejection_reason", "rejection_reason is required for REJECT action")]
            )
        
        try:
            rejected_silmatha = silmatha_regist_service.reject_silmatha(
                db, 
                sil_regn=payload.sil_regn, 
                rejection_reason=payload.rejection_reason,
                actor_id=user_id
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message) from exc
            raise validation_error([(None, message)]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        silmatha_enriched = silmatha_regist_service.enrich_silmatha_dict(rejected_silmatha, db)
        silmatha_schema = schemas.Silmatha.model_validate(silmatha_enriched)
        return schemas.SilmathaRegistManagementResponse(
            status="success",
            message="Silmatha record rejected successfully.",
            data=silmatha_schema,
        )

    elif action == schemas.CRUDAction.MARK_PRINTED:
        if not payload or not hasattr(payload, 'sil_regn'):
            raise validation_error(
                [("payload.sil_regn", "sil_regn is required for MARK_PRINTED action")]
            )
        
        try:
            printed_silmatha = silmatha_regist_service.mark_printed(
                db, sil_regn=payload.sil_regn, actor_id=user_id
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message) from exc
            raise validation_error([(None, message)]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        silmatha_enriched = silmatha_regist_service.enrich_silmatha_dict(printed_silmatha, db)
        silmatha_schema = schemas.Silmatha.model_validate(silmatha_enriched)
        return schemas.SilmathaRegistManagementResponse(
            status="success",
            message="Silmatha record marked as printed successfully.",
            data=silmatha_schema,
        )

    elif action == schemas.CRUDAction.MARK_SCANNED:
        if not payload or not hasattr(payload, 'sil_regn'):
            raise validation_error(
                [("payload.sil_regn", "sil_regn is required for MARK_SCANNED action")]
            )
        
        # scanned_document_path is optional - can be empty string
        scanned_path = payload.scanned_document_path if hasattr(payload, 'scanned_document_path') else ""
        
        try:
            scanned_silmatha = silmatha_regist_service.mark_scanned(
                db, 
                sil_regn=payload.sil_regn, 
                scanned_document_path=scanned_path,
                actor_id=user_id
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message) from exc
            raise validation_error([(None, message)]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        silmatha_enriched = silmatha_regist_service.enrich_silmatha_dict(scanned_silmatha, db)
        silmatha_schema = schemas.Silmatha.model_validate(silmatha_enriched)
        return schemas.SilmathaRegistManagementResponse(
            status="success",
            message="Silmatha record marked as scanned successfully.",
            data=silmatha_schema,
        )

    else:
        raise HTTPException(status_code=400, detail=f"Invalid action: {action}")


@router.post(
    "/{sil_regn}/upload-scanned-document",
    response_model=schemas.SilmathaRegistManagementResponse,
    dependencies=[has_any_permission("silmatha:update")],
)
async def upload_scanned_document(
    sil_regn: str,
    file: UploadFile = File(..., description="Scanned document file (max 5MB, PDF, JPG, PNG)"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Upload a scanned document for a Silmatha record.
    
    This endpoint allows uploading a scanned document (up to 5MB) for a specific silmatha registration.
    The file will be stored at: `app/storage/silmatha_update/<year>/<month>/<day>/<sil_regn>/scanned_document_*.ext`
    When the current workflow status is PRINTED, a successful upload will automatically transition the record to PEND-APPROVAL.
    
    **Requirements:**
    - Maximum file size: 5MB
    - Allowed formats: PDF, JPG, JPEG, PNG
    - Requires: silmatha:update permission
    
    **Path Parameters:**
    - sil_regn: Silmatha registration number (e.g., SIL2025000001)
    
    **Form Data:**
    - file: The scanned document file to upload
    
    **Response:**
    Returns the updated Silmatha record with the file path stored in sil_scanned_document_path
    
    **Example Usage (Postman):**
    1. Method: POST
    2. URL: {{base_url}}/api/v1/silmatha-regist/SIL2025000001/upload-scanned-document
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
        
        # Upload the file and update the silmatha record
        updated_silmatha = await silmatha_regist_service.upload_scanned_document(
            db, sil_regn=sil_regn, file=file, actor_id=username
        )
        
        # Return enriched data (matches bhikku upload response)
        silmatha_enriched = silmatha_regist_service.enrich_silmatha_dict(updated_silmatha, db)
        silmatha_schema = schemas.Silmatha.model_validate(silmatha_enriched)
        
        return schemas.SilmathaRegistManagementResponse(
            status="success",
            message="Scanned document uploaded successfully. Status automatically changed to PEND-APPROVAL when applicable.",
            data=silmatha_schema,
        )
        
    except ValueError as exc:
        message = str(exc)
        if "not found" in message.lower():
            raise HTTPException(status_code=404, detail=message) from exc
        raise HTTPException(status_code=400, detail=message) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post(
    "/{sil_regn}/mark-printed",
    response_model=schemas.SilmathaRegistWorkflowResponse,
    dependencies=[has_any_permission("silmatha:update")],
)
def mark_silmatha_printed(
    sil_regn: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Mark silmatha certificate as printed.
    
    Transitions: PENDING → PRINTED
    
    Indicates that the certificate has been physically printed.
    This is the first action after creating a silmatha record.
    
    Requires: silmatha:update permission
    """
    user_id = current_user.ua_user_id
    
    try:
        updated_silmatha = silmatha_regist_service.mark_printed(
            db, sil_regn=sil_regn, actor_id=user_id
        )
    except ValueError as exc:
        error_msg = str(exc)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg) from exc
        raise validation_error([(None, error_msg)]) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    
    silmatha_schema = schemas.SilmathaRegistInternal.model_validate(updated_silmatha)
    return schemas.SilmathaRegistWorkflowResponse(
        success=True,
        message="Silmatha certificate marked as printed successfully.",
        data=silmatha_schema,
    )


@router.post(
    "/{sil_regn}/mark-scanned",
    response_model=schemas.SilmathaRegistWorkflowResponse,
    dependencies=[has_any_permission("silmatha:update")],
)
def mark_silmatha_scanned(
    sil_regn: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Mark silmatha certificate as scanned.
    
    Transitions: PRINTED → PEND-APPROVAL
    
    Indicates that the printed certificate has been scanned back into the system.
    After this step, the record can be approved or rejected.
    
    Requires: silmatha:update permission
    """
    user_id = current_user.ua_user_id
    
    try:
        # Note: mark_scanned expects a document path, but this endpoint doesn't handle file upload
        # Use the upload-scanned-document endpoint instead for auto-transition
        updated_silmatha = silmatha_regist_service.mark_scanned(
            db, 
            sil_regn=sil_regn, 
            scanned_document_path="",  # Empty path for manual marking
            actor_id=user_id
        )
    except ValueError as exc:
        error_msg = str(exc)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg) from exc
        raise validation_error([(None, error_msg)]) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    
    silmatha_schema = schemas.SilmathaRegistInternal.model_validate(updated_silmatha)
    return schemas.SilmathaRegistWorkflowResponse(
        success=True,
        message="Silmatha certificate marked as scanned successfully.",
        data=silmatha_schema,
    )


@router.post(
    "/{sil_regn}/approve",
    response_model=schemas.SilmathaRegistWorkflowResponse,
    dependencies=[has_any_permission("silmatha:approve")],
)
def approve_silmatha_record(
    sil_regn: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Approve silmatha registration.
    
    Transitions: PEND-APPROVAL → COMPLETED (with approval_status = APPROVED)
    
    Once approved, the workflow is completed. This is the final step for successful registrations.
    
    Requires: silmatha:approve permission
    """
    user_id = current_user.ua_user_id
    
    try:
        updated_silmatha = silmatha_regist_service.approve_silmatha(
            db, sil_regn=sil_regn, actor_id=user_id
        )
    except ValueError as exc:
        error_msg = str(exc)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg) from exc
        raise validation_error([(None, error_msg)]) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    
    silmatha_schema = schemas.SilmathaRegistInternal.model_validate(updated_silmatha)
    return schemas.SilmathaRegistWorkflowResponse(
        success=True,
        message="Silmatha registration approved and completed successfully.",
        data=silmatha_schema,
    )


@router.post(
    "/workflow",
    response_model=schemas.SilmathaRegistWorkflowResponse,
    dependencies=[has_any_permission("silmatha:approve", "silmatha:update")],
)
def update_silmatha_workflow(
    request: schemas.SilmathaRegistWorkflowRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Update workflow status of a silmatha record.
    
    Main Workflow Actions:
    - APPROVE: Approve pending silmatha registration (PEND-APPROVAL → COMPLETED)
    - REJECT: Reject pending silmatha registration (PEND-APPROVAL → REJECTED, requires rejection_reason)
    - MARK_PRINTING: Mark as in printing process (PENDING → PRINTING)
    - MARK_PRINTED: Mark certificate as printed (PENDING → PRINTED)
    - MARK_SCANNED: Mark certificate as scanned (PRINTED → PEND-APPROVAL)
    - RESET_TO_PENDING: Reset workflow to pending state (for corrections)
    
    Reprint Workflow Actions:
    - REQUEST_REPRINT: Request a certificate reprint (requires reprint_reason, reprint_amount, optional reprint_remarks)
    - ACCEPT_REPRINT: Accept a reprint request
    - REJECT_REPRINT: Reject a reprint request (requires rejection_reason)
    - COMPLETE_REPRINT: Mark reprint as completed
    
    Requires: silmatha:approve OR silmatha:update permission
    """
    user_id = current_user.ua_user_id
    action = request.action
    sil_regn = request.sil_regn

    try:
        if action == schemas.WorkflowActionType.APPROVE:
            updated_silmatha = silmatha_regist_service.approve_silmatha(
                db, sil_regn=sil_regn, actor_id=user_id
            )
            message = "Silmatha approved successfully."

        elif action == schemas.WorkflowActionType.REJECT:
            if not request.rejection_reason:
                raise validation_error(
                    [("rejection_reason", "Rejection reason is required when rejecting")]
                )
            updated_silmatha = silmatha_regist_service.reject_silmatha(
                db, 
                sil_regn=sil_regn, 
                rejection_reason=request.rejection_reason,
                actor_id=user_id
            )
            message = "Silmatha rejected successfully."

        elif action == schemas.WorkflowActionType.MARK_PRINTING:
            updated_silmatha = silmatha_regist_service.mark_printing(
                db, sil_regn=sil_regn, actor_id=user_id
            )
            message = "Silmatha marked as printing successfully."

        elif action == schemas.WorkflowActionType.MARK_PRINTED:
            updated_silmatha = silmatha_regist_service.mark_printed(
                db, sil_regn=sil_regn, actor_id=user_id
            )
            message = "Silmatha certificate marked as printed successfully."

        elif action == schemas.WorkflowActionType.MARK_SCANNED:
            updated_silmatha = silmatha_regist_service.mark_scanned(
                db, sil_regn=sil_regn, scanned_document_path="", actor_id=user_id
            )
            message = "Silmatha certificate marked as scanned successfully."

        elif action == schemas.WorkflowActionType.RESET_TO_PENDING:
            updated_silmatha = silmatha_regist_service.reset_to_pending(
                db, sil_regn=sil_regn, actor_id=user_id
            )
            message = "Silmatha workflow reset to pending successfully."

        # Reprint workflow actions
        elif action == schemas.WorkflowActionType.REQUEST_REPRINT:
            if not request.reprint_reason:
                raise validation_error(
                    [("reprint_reason", "Reprint reason is required when requesting reprint")]
                )
            if not request.reprint_amount:
                raise validation_error(
                    [("reprint_amount", "Reprint amount is required when requesting reprint")]
                )
            updated_silmatha = silmatha_regist_service.request_reprint(
                db, 
                sil_regn=sil_regn, 
                actor_id=user_id,
                reprint_reason=request.reprint_reason,
                reprint_amount=request.reprint_amount,
                reprint_remarks=request.reprint_remarks
            )
            message = "Reprint request submitted successfully."

        elif action == schemas.WorkflowActionType.ACCEPT_REPRINT:
            updated_silmatha = silmatha_regist_service.accept_reprint(
                db, sil_regn=sil_regn, actor_id=user_id
            )
            message = "Reprint request accepted successfully."

        elif action == schemas.WorkflowActionType.REJECT_REPRINT:
            if not request.rejection_reason:
                raise validation_error(
                    [("rejection_reason", "Rejection reason is required when rejecting reprint")]
                )
            updated_silmatha = silmatha_regist_service.reject_reprint(
                db, 
                sil_regn=sil_regn, 
                actor_id=user_id,
                rejection_reason=request.rejection_reason
            )
            message = "Reprint request rejected successfully."

        elif action == schemas.WorkflowActionType.COMPLETE_REPRINT:
            updated_silmatha = silmatha_regist_service.complete_reprint(
                db, sil_regn=sil_regn, actor_id=user_id
            )
            message = "Reprint completed successfully."

        else:
            raise validation_error([("action", "Invalid workflow action")])

    except ValueError as exc:
        error_msg = str(exc)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg) from exc
        raise validation_error([(None, error_msg)]) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    silmatha_schema = schemas.SilmathaRegistInternal.model_validate(updated_silmatha)
    return schemas.SilmathaRegistWorkflowResponse(
        success=True,
        message=message,
        data=silmatha_schema,
    )


@router.post(
    "/arama-list",
    response_model=schemas.AramaListResponse,
    dependencies=[has_any_permission("silmatha:create", "silmatha:read", "silmatha:update")],
)
def get_arama_list_for_silmatha(
    request: schemas.AramaListRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Get a simplified list of aramas for silmatha users.
    Returns only ar_trn, ar_vname, and ar_addrs.
    
    Requires: silmatha:read or silmatha:create or silmatha:update permission
    """
    if request.action != "READ_ALL":
        raise validation_error([("action", "Only READ_ALL action is supported")])
    
    payload = request.payload
    page = payload.page
    limit = payload.limit
    search = payload.search_key.strip() if payload.search_key else None
    if search == "":
        search = None
    skip = payload.skip if payload.page == 1 else (page - 1) * limit
    
    # Get aramas using the arama service
    aramas = arama_service.list_aramas(
        db,
        skip=skip,
        limit=limit,
        search=search,
    )
    
    # Get total count
    total = arama_service.count_aramas(
        db,
        search=search,
    )
    
    # Map to simplified response
    simple_aramas = [
        schemas.AramaSimpleItem(
            ar_trn=arama.ar_trn,
            ar_vname=arama.ar_vname,
            ar_addrs=arama.ar_addrs,
        )
        for arama in aramas
    ]
    
    return schemas.AramaListResponse(
        status="success",
        message="Arama records retrieved successfully.",
        data=simple_aramas,
        totalRecords=total,
        page=page,
        limit=limit,
    )

