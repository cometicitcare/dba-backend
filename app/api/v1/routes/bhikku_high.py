from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission, has_any_permission
from app.api.deps import get_db
from app.models.user import UserAccount
from app.models.user_roles import UserRole
from app.models.roles import Role
from app.schemas import bhikku_high as schemas
from app.services.bhikku_high_service import bhikku_high_service
from app.utils.http_exceptions import validation_error
from app.services.permission_service import permission_service  # New service for permission check
from pydantic import ValidationError

router = APIRouter()  # Tags defined in router.py

# Check if the user has permission to perform an action on Bhikku High
def check_permission(db: Session, user_id: str, permission_name: str):
    # Check if user is super admin - super admins bypass all permission checks
    user = db.query(UserAccount).filter(UserAccount.ua_user_id == user_id).first()
    if user:
        user_roles = db.query(UserRole).filter(UserRole.ur_user_id == user_id).all()
        for user_role in user_roles:
            role = db.query(Role).filter(Role.ro_role_id == user_role.ur_role_id).first()
            if role and role.ro_level == "SUPER_ADMIN":
                return  # Super admin has all permissions
    
    # For non-super admin users, check specific permissions
    permissions = permission_service.get_user_permissions(db, user_id)
    if permission_name not in permissions:
        raise HTTPException(status_code=403, detail="Permission denied")

@router.post("/manage", response_model=schemas.BhikkuHighManagementResponse, dependencies=[has_any_permission("bhikku:create", "bhikku:read", "bhikku:update", "bhikku:delete")])
def manage_bhikku_high_records(
    request: schemas.BhikkuHighManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),  # UserAccount object from JWT
):
    action = request.action
    payload = request.payload
    user_id = current_user.ua_user_id  # Access user ID from the UserAccount object

    # Permission checks before CRUD actions
    if action == schemas.CRUDAction.CREATE:
        check_permission(db, user_id, 'CREATE_BHIKKU_HIGH')
        if not payload.data:
            raise validation_error([("payload.data", "data is required for CREATE action")])

        create_payload: schemas.BhikkuHighCreate
        
        # Get raw data from payload
        if hasattr(payload.data, "model_dump"):
            raw_data = payload.data.model_dump()
        elif isinstance(payload.data, dict):
            raw_data = payload.data
        else:
            raw_data = dict(payload.data)
        
        # Try to create BhikkuHighCreate from raw data
        try:
            create_payload = schemas.BhikkuHighCreate(**raw_data)
        except ValidationError as exc:
            formatted_errors = []
            for error in exc.errors():
                loc = ".".join(str(part) for part in error.get("loc", []))
                formatted_errors.append((loc or None, error.get("msg", "Invalid data")))
            raise validation_error(formatted_errors) from exc

        try:
            created = bhikku_high_service.create_bhikku_high(db, payload=create_payload, actor_id=user_id, current_user=current_user)
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        # Enrich the entity with nested objects
        enriched_data = bhikku_high_service.enrich_bhikku_high_dict(created)
        
        return schemas.BhikkuHighManagementResponse(status="success", message="Higher bhikku registration created successfully.", data=enriched_data)

    if action == schemas.CRUDAction.READ_ONE:
        check_permission(db, user_id, 'READ_BHIKKU_HIGH')
        if payload.bhr_id is None and not payload.bhr_regn:
            raise validation_error([("payload.bhr_id", "bhr_id or bhr_regn is required for READ_ONE action")])

        entity = None
        enriched_data = None
        
        # First, try to find in bhikku_high_regist table
        if payload.bhr_id:
            entity = bhikku_high_service.get_bhikku_high(db, bhr_id=payload.bhr_id)
        elif payload.bhr_regn:
            entity = bhikku_high_service.get_bhikku_high_by_regn(db, bhr_regn=payload.bhr_regn)

        if entity:
            # Enrich the entity with nested objects from candidate
            enriched_data = bhikku_high_service.enrich_bhikku_high_dict(entity)
        else:
            # If not found, try to find in direct_bhikku_high table
            from app.services.direct_bhikku_high_service import direct_bhikku_high_service
            direct_entity = None
            
            if payload.bhr_regn:
                # Can only search by regn in direct_bhikku_high (no bhr_id mapping)
                direct_entity = direct_bhikku_high_service.get_direct_bhikku_high_by_regn(db, payload.bhr_regn)
            
            if direct_entity:
                # Convert direct_bhikku_high to bhikku_high format
                enriched_data = bhikku_high_service.convert_direct_to_bhikku_high_dict(direct_entity, db)
            else:
                raise HTTPException(status_code=404, detail="Higher bhikku registration not found")

        return schemas.BhikkuHighManagementResponse(status="success", message="Higher bhikku registration retrieved successfully.", data=enriched_data)

    if action == schemas.CRUDAction.READ_ALL:
        check_permission(db, user_id, 'READ_BHIKKU_HIGH')
        page = payload.page or 1
        limit = payload.limit
        search = payload.search_key.strip() if payload.search_key else None
        if search == "":
            search = None
        skip = payload.skip if payload.page is None else (page - 1) * limit
        limit = max(1, min(limit, 200))
        skip = max(0, skip)
        
        # Extract filter parameters
        vh_trn = payload.vh_trn
        province = payload.province
        district = payload.district
        divisional_secretariat = payload.divisional_secretariat
        gn_division = payload.gn_division
        temple = payload.temple
        child_temple = payload.child_temple
        nikaya = payload.nikaya
        parshawaya = payload.parshawaya
        status = payload.status
        date_from = payload.date_from
        date_to = payload.date_to

        # Get ALL records from both tables (we'll paginate after merging)
        # Fetch more records than needed to ensure we have enough after merging
        fetch_limit = limit * 2  # Fetch double to account for both sources
        
        # Get records from bhikku_high_regist table
        records = bhikku_high_service.list_bhikku_highs(
            db,
            skip=0,
            limit=fetch_limit,
            search=search,
            current_user=current_user,
            vh_trn=vh_trn,
            province=province,
            district=district,
            divisional_secretariat=divisional_secretariat,
            gn_division=gn_division,
            temple=temple,
            child_temple=child_temple,
            nikaya=nikaya,
            parshawaya=parshawaya,
            status=status,
            date_from=date_from,
            date_to=date_to,
        )
        total = bhikku_high_service.count_bhikku_highs(
            db,
            search=search,
            vh_trn=vh_trn,
            province=province,
            district=district,
            divisional_secretariat=divisional_secretariat,
            gn_division=gn_division,
            temple=temple,
            child_temple=child_temple,
            nikaya=nikaya,
            parshawaya=parshawaya,
            status=status,
            date_from=date_from,
            date_to=date_to,
        )

        # Get records from direct_bhikku_high table
        from app.services.direct_bhikku_high_service import direct_bhikku_high_service
        
        # Convert status list to single value for direct_bhikku_high (it doesn't support list yet)
        status_single = status[0] if status and isinstance(status, list) and len(status) > 0 else None
        
        direct_records = direct_bhikku_high_service.list_direct_bhikku_highs(
            db, 
            skip=0, 
            limit=fetch_limit, 
            search=search, 
            current_user=current_user,
            province=province,
            district=district,
            divisional_secretariat=divisional_secretariat,
            gn_division=gn_division,
            parshawaya=parshawaya,
            status=status_single,
            date_from=date_from,
            date_to=date_to,
        )
        direct_total = direct_bhikku_high_service.count_direct_bhikku_highs(
            db,
            search=search,
            current_user=current_user,
            province=province,
            district=district,
            divisional_secretariat=divisional_secretariat,
            gn_division=gn_division,
            parshawaya=parshawaya,
            status=status_single,
            date_from=date_from,
            date_to=date_to,
        )

        # Enrich all records with nested objects from candidates
        enriched_records = [bhikku_high_service.enrich_bhikku_high_dict(record) for record in records]
        
        # Convert and add direct_bhikku_high records
        enriched_direct_records = [bhikku_high_service.convert_direct_to_bhikku_high_dict(record, db) for record in direct_records]
        
        # Merge both lists
        all_enriched_records = enriched_records + enriched_direct_records
        
        # Apply pagination to the merged result
        paginated_records = all_enriched_records[skip:skip + limit]
        
        # Calculate total count
        total_count = total + direct_total

        return schemas.BhikkuHighManagementResponse(
            status="success",
            message="Higher bhikku registrations retrieved successfully.",
            data=paginated_records,
            totalRecords=total_count,
            page=page,
            limit=limit,
        )

    if action == schemas.CRUDAction.UPDATE:
        check_permission(db, user_id, 'UPDATE_BHIKKU_HIGH')
        if not payload.data:
            raise validation_error([("payload.data", "data is required for UPDATE action")])

        # Accept bhr_id either at payload.bhr_id or inside payload.data for flexibility
        raw_data = payload.data.model_dump() if hasattr(payload.data, "model_dump") else payload.data
        if not isinstance(raw_data, dict):
            raise validation_error([("payload.data", "data must be an object for UPDATE action")])

        bhr_id = payload.bhr_id or raw_data.get("bhr_id")
        if bhr_id is None:
            raise validation_error([("payload.bhr_id", "bhr_id is required for UPDATE action (provide payload.bhr_id or payload.data.bhr_id)")])

        # Remove bhr_id from the update payload to avoid silent ignores
        raw_data = {key: value for key, value in raw_data.items() if key != "bhr_id"}

        update_payload: schemas.BhikkuHighUpdate

        # Handle both frontend and internal payload formats
        if isinstance(payload.data, schemas.BhikkuHighFrontendUpdate):
            update_payload = payload.data.to_bhikku_high_update()
        elif isinstance(payload.data, schemas.BhikkuHighUpdate):
            update_payload = payload.data
        else:
            # Prefer internal format when bhr_* keys are present, otherwise try frontend first
            has_internal_keys = any(key.startswith("bhr_") for key in raw_data.keys())
            parse_order = ["internal", "frontend"] if has_internal_keys else ["frontend", "internal"]
            last_error = None

            for parse_target in parse_order:
                try:
                    if parse_target == "frontend":
                        frontend_payload = schemas.BhikkuHighFrontendUpdate(**raw_data)
                        update_payload = frontend_payload.to_bhikku_high_update()
                    else:
                        update_payload = schemas.BhikkuHighUpdate(**raw_data)
                    break
                except ValidationError as exc:
                    last_error = exc
                    update_payload = None

            if update_payload is None:
                formatted_errors = []
                if last_error:
                    for error in last_error.errors():
                        loc = ".".join(str(part) for part in error.get("loc", []))
                        formatted_errors.append((loc or None, error.get("msg", "Invalid data")))
                raise validation_error(formatted_errors or [(None, "Invalid data")])

        try:
            updated = bhikku_high_service.update_bhikku_high(db, bhr_id=bhr_id, payload=update_payload, actor_id=user_id)
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        return schemas.BhikkuHighManagementResponse(status="success", message="Higher bhikku registration updated successfully.", data=updated)

    if action == schemas.CRUDAction.DELETE:
        check_permission(db, user_id, 'DELETE_BHIKKU_HIGH')
        if payload.bhr_id is None:
            raise validation_error([("payload.bhr_id", "bhr_id is required for DELETE action")])

        try:
            bhikku_high_service.delete_bhikku_high(db, bhr_id=payload.bhr_id, actor_id=user_id)
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message) from exc
            raise validation_error([(None, message)]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        return schemas.BhikkuHighManagementResponse(status="success", message="Higher bhikku registration deleted successfully.", data=None)

    raise validation_error([("action", "Invalid action specified")])


@router.post("/workflow", response_model=schemas.BhikkuHighWorkflowResponse, dependencies=[has_any_permission("bhikku:approve", "bhikku:update")])
def update_bhikku_high_workflow(
    request: schemas.BhikkuHighWorkflowRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Update workflow status of a bhikku high record.
    
    Workflow Actions:
    - APPROVE: Approve scanned bhikku high record (PEND-APPROVAL → COMPLETED)
    - REJECT: Reject scanned bhikku high record (PEND-APPROVAL → REJECTED, requires rejection_reason)
    - MARK_PRINTED: Mark certificate as printed (PENDING → PRINTED)
    - MARK_SCANNED: Mark certificate as scanned (PRINTED → PEND-APPROVAL)
    
    Workflow Flow:
    1. Create bhikku high record → PENDING
    2. Mark as printed → PRINTED
    3. Upload/mark scanned → PEND-APPROVAL
    4. Approve/Reject → COMPLETED or REJECTED
    
    Requires: bhikku:approve OR bhikku:update permission
    """
    user_id = current_user.ua_user_id
    action = request.action
    bhr_id = request.bhr_id

    try:
        if action == schemas.BhikkuHighWorkflowActionType.APPROVE:
            updated_bhikku_high = bhikku_high_service.approve_bhikku_high(
                db, bhr_id=bhr_id, actor_id=user_id
            )
            message = "Higher bhikku registration approved successfully."

        elif action == schemas.BhikkuHighWorkflowActionType.REJECT:
            if not request.rejection_reason:
                raise validation_error(
                    [("rejection_reason", "Rejection reason is required when rejecting")]
                )
            updated_bhikku_high = bhikku_high_service.reject_bhikku_high(
                db, 
                bhr_id=bhr_id, 
                actor_id=user_id,
                rejection_reason=request.rejection_reason
            )
            message = "Higher bhikku registration rejected successfully."

        elif action == schemas.BhikkuHighWorkflowActionType.MARK_PRINTED:
            updated_bhikku_high = bhikku_high_service.mark_printed(
                db, bhr_id=bhr_id, actor_id=user_id
            )
            message = "Higher bhikku certificate marked as printed successfully."

        elif action == schemas.BhikkuHighWorkflowActionType.MARK_SCANNED:
            updated_bhikku_high = bhikku_high_service.mark_scanned(
                db, bhr_id=bhr_id, actor_id=user_id
            )
            message = "Higher bhikku certificate marked as scanned successfully."

        else:
            raise validation_error([("action", "Invalid workflow action")])

    except ValueError as exc:
        error_msg = str(exc)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg) from exc
        raise validation_error([(None, error_msg)]) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Enrich the response with nested objects
    enriched_data = bhikku_high_service.enrich_bhikku_high_dict(updated_bhikku_high)
    
    return schemas.BhikkuHighWorkflowResponse(
        status="success",
        message=message,
        data=enriched_data,
    )


@router.post(
    "/{bhr_regn}/upload-scanned-document",
    response_model=schemas.BhikkuHighManagementResponse,
    dependencies=[has_any_permission("bhikku:update")],
)
async def upload_scanned_document(
    bhr_regn: str,
    file: UploadFile = File(..., description="Scanned document file (max 5MB, PDF, JPG, PNG)"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Upload a scanned document for a Higher Bhikku registration record.
    
    This endpoint allows uploading a scanned document (up to 5MB) for a specific higher bhikku registration.
    The file will be stored at: `app/storage/bhikku_high_regist/<year>/<month>/<day>/<bhr_regn>/scanned_document_*.ext`
    When the current workflow status is PRINTED, a successful upload will move the record to PEND-APPROVAL automatically.
    
    **Requirements:**
    - Maximum file size: 5MB
    - Allowed formats: PDF, JPG, JPEG, PNG
    - Requires: bhikku:update permission
    
    **Path Parameters:**
    - bhr_regn: Higher Bhikku registration number (e.g., UPS2025001)
    
    **Form Data:**
    - file: The scanned document file to upload
    
    **Response:**
    Returns the updated Higher Bhikku record with the file path stored in bhr_scanned_document_path
    
    **Example Usage (Postman):**
    1. Method: POST
    2. URL: {{base_url}}/api/v1/bhikkus-high/UPS2025001/upload-scanned-document
    3. Headers: Cookie with access_token
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
        
        # Upload the file and update the bhikku high record
        updated_bhikku_high = await bhikku_high_service.upload_scanned_document(
            db, bhr_regn=bhr_regn, file=file, actor_id=username
        )
        
        # Return enriched data
        enriched_data = bhikku_high_service.enrich_bhikku_high_dict(updated_bhikku_high)
        
        return schemas.BhikkuHighManagementResponse(
            status="success",
            message="Scanned document uploaded successfully.",
            data=enriched_data,
        )
        
    except ValueError as exc:
        message = str(exc)
        if "not found" in message.lower():
            raise HTTPException(status_code=404, detail=message) from exc
        raise validation_error([(None, message)]) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(exc)}") from exc
