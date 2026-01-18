from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session
from datetime import date

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
from app.services.temporary_vihara_service import temporary_vihara_service
from app.utils.http_exceptions import validation_error

router = APIRouter()  # Tags defined in router.py


# =============================================================================
# MAIN MANAGE ENDPOINT
# =============================================================================

@router.post("/manage", response_model=ViharaManagementResponse, dependencies=[has_any_permission("vihara:create", "vihara:read", "vihara:update", "vihara:delete")])
def manage_vihara_records(
    request: ViharaManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Main endpoint for managing Vihara records with staged workflow.
    
    ## Staged Workflow Overview:
    
    ### Stage 1 Flow:
    1. **SAVE_STAGE_ONE** - Creates/updates basic profile → status: S1_PENDING
    2. **MARK_S1_PRINTED** - Mark form as printed → status: S1_PRINTING
    3. Upload document via `/upload-stage1-document` → status: S1_PEND_APPROVAL
    4. **APPROVE_STAGE_ONE** or **REJECT_STAGE_ONE** → status: S1_APPROVED or S1_REJECTED
    
    ### Stage 2 Flow (can work in parallel with Stage 1):
    1. **SAVE_STAGE_TWO** - Save assets & certification → status: S2_PENDING
    2. **MARK_S2_PRINTED** - Mark Stage 2 form as printed → status: S2_PRINTING (✨ NEW)
    3. Upload document via `/upload-stage2-document` → status: S2_PEND_APPROVAL
    4. **APPROVE_STAGE_TWO** or **REJECT_STAGE_TWO** → status: COMPLETED or REJECTED
    
    ## Supported Actions:
    - SAVE_STAGE_ONE, UPDATE_STAGE_ONE
    - MARK_S1_PRINTED
    - APPROVE_STAGE_ONE, REJECT_STAGE_ONE
    - SAVE_STAGE_TWO, UPDATE_STAGE_TWO
    - MARK_S2_PRINTED (✨ NEW - can be done even when Stage 1 is pending)
    - APPROVE_STAGE_TWO, REJECT_STAGE_TWO
    - CREATE, READ_ONE, READ_ALL, UPDATE, DELETE (legacy)
    """
    action = request.action
    payload = request.payload
    user_id = current_user.ua_user_id

    # =================================================================
    # STAGE ONE OPERATIONS
    # =================================================================
    
    if action == CRUDAction.SAVE_STAGE_ONE:
        vh_id = payload.vh_id
        raw_data = payload.data
        if isinstance(raw_data, BaseModel):
            raw_data = raw_data.model_dump()
        
        try:
            result = vihara_service.save_stage_one(
                db, payload_data=raw_data, actor_id=user_id, vh_id=vh_id
            )
            # Enrich with temporary entity data
            temp_data = vihara_service.enrich_with_temp_entities(db, result)
            result_dict = ViharaOut.model_validate(result).model_dump()
            result_dict.update(temp_data)
            
            return ViharaManagementResponse(
                status="success",
                message="Stage 1 (Basic Profile) saved. Status: S1_PENDING. Next: Mark as printed.",
                data=result_dict,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    if action == CRUDAction.UPDATE_STAGE_ONE:
        if payload.vh_id is None:
            raise validation_error(
                [("payload.vh_id", "vh_id is required for UPDATE_STAGE_ONE action")]
            )
        
        raw_data = payload.data
        if isinstance(raw_data, BaseModel):
            raw_data = raw_data.model_dump()
        
        try:
            result = vihara_service.save_stage_one(
                db, payload_data=raw_data, actor_id=user_id, vh_id=payload.vh_id
            )
            
            # Enrich with temporary entities if present
            temp_data = vihara_service.enrich_with_temp_entities(db, result)
            result_dict = ViharaOut.model_validate(result).model_dump()
            result_dict.update(temp_data)
            
            return ViharaManagementResponse(
                status="success",
                message="Stage 1 (Basic Profile) updated successfully.",
                data=result_dict,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    if action == CRUDAction.MARK_S1_PRINTED:
        if payload.vh_id is None:
            raise validation_error(
                [("payload.vh_id", "vh_id is required for MARK_S1_PRINTED action")]
            )
        
        try:
            result = vihara_service.mark_stage1_printed(
                db, vh_id=payload.vh_id, actor_id=user_id
            )
            return ViharaManagementResponse(
                status="success",
                message="Stage 1 form marked as printed. Status: S1_PRINTING. Next: Upload scanned document.",
                data=result,
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=message
                ) from exc
            raise validation_error([(None, message)]) from exc

    if action == CRUDAction.APPROVE_STAGE_ONE:
        if payload.vh_id is None:
            raise validation_error(
                [("payload.vh_id", "vh_id is required for APPROVE_STAGE_ONE action")]
            )
        
        try:
            result = vihara_service.approve_stage_one(
                db, vh_id=payload.vh_id, actor_id=user_id
            )
            
            # Enrich with temporary entities if present
            temp_data = vihara_service.enrich_with_temp_entities(db, result)
            result_dict = ViharaOut.model_validate(result).model_dump()
            result_dict.update(temp_data)
            
            return ViharaManagementResponse(
                status="success",
                message="Stage 1 approved. Status: S1_APPROVED. Ready for Stage 2 input.",
                data=result_dict,
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=message
                ) from exc
            raise validation_error([(None, message)]) from exc

    if action == CRUDAction.REJECT_STAGE_ONE:
        if payload.vh_id is None:
            raise validation_error(
                [("payload.vh_id", "vh_id is required for REJECT_STAGE_ONE action")]
            )
        if not payload.rejection_reason:
            raise validation_error(
                [("payload.rejection_reason", "Rejection reason is required for REJECT_STAGE_ONE action")]
            )
        
        try:
            result = vihara_service.reject_stage_one(
                db, vh_id=payload.vh_id, actor_id=user_id, rejection_reason=payload.rejection_reason
            )
            
            # Enrich with temporary entities if present
            temp_data = vihara_service.enrich_with_temp_entities(db, result)
            result_dict = ViharaOut.model_validate(result).model_dump()
            result_dict.update(temp_data)
            
            return ViharaManagementResponse(
                status="success",
                message="Stage 1 rejected. Status: S1_REJECTED.",
                data=result_dict,
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=message
                ) from exc
            raise validation_error([(None, message)]) from exc

    # =================================================================
    # STAGE TWO OPERATIONS
    # =================================================================
    
    if action == CRUDAction.SAVE_STAGE_TWO:
        if payload.vh_id is None:
            raise validation_error(
                [("payload.vh_id", "vh_id is required for SAVE_STAGE_TWO action. Please complete Stage 1 first.")]
            )
        
        raw_data = payload.data
        if isinstance(raw_data, BaseModel):
            raw_data = raw_data.model_dump()
        
        try:
            result = vihara_service.save_stage_two(
                db, vh_id=payload.vh_id, payload_data=raw_data, actor_id=user_id
            )
            
            # Enrich with temporary entities if present
            temp_data = vihara_service.enrich_with_temp_entities(db, result)
            result_dict = ViharaOut.model_validate(result).model_dump()
            result_dict.update(temp_data)
            
            return ViharaManagementResponse(
                status="success",
                message="Stage 2 (Assets & Certification) saved. Status: S2_PENDING. Next: Upload scanned document.",
                data=result_dict,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    if action == CRUDAction.UPDATE_STAGE_TWO:
        if payload.vh_id is None:
            raise validation_error(
                [("payload.vh_id", "vh_id is required for UPDATE_STAGE_TWO action")]
            )
        
        raw_data = payload.data
        if isinstance(raw_data, BaseModel):
            raw_data = raw_data.model_dump()
        
        try:
            result = vihara_service.save_stage_two(
                db, vh_id=payload.vh_id, payload_data=raw_data, actor_id=user_id
            )
            
            # Enrich with temporary entities if present
            temp_data = vihara_service.enrich_with_temp_entities(db, result)
            result_dict = ViharaOut.model_validate(result).model_dump()
            result_dict.update(temp_data)
            
            return ViharaManagementResponse(
                status="success",
                message="Stage 2 (Assets & Certification) updated successfully.",
                data=result_dict,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    if action == CRUDAction.MARK_S2_PRINTED:
        if payload.vh_id is None:
            raise validation_error(
                [("payload.vh_id", "vh_id is required for MARK_S2_PRINTED action")]
            )
        
        try:
            result = vihara_service.mark_stage2_printed(
                db, vh_id=payload.vh_id, actor_id=user_id
            )
            return ViharaManagementResponse(
                status="success",
                message="Stage 2 form marked as printed. Status: S2_PRINTING. Next: Upload scanned document.",
                data=result,
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=message
                ) from exc
            raise validation_error([(None, message)]) from exc

    if action == CRUDAction.APPROVE_STAGE_TWO:
        if payload.vh_id is None:
            raise validation_error(
                [("payload.vh_id", "vh_id is required for APPROVE_STAGE_TWO action")]
            )
        
        try:
            result = vihara_service.approve_stage_two(
                db, vh_id=payload.vh_id, actor_id=user_id
            )
            
            # Enrich with temporary entities if present
            temp_data = vihara_service.enrich_with_temp_entities(db, result)
            result_dict = ViharaOut.model_validate(result).model_dump()
            result_dict.update(temp_data)
            
            return ViharaManagementResponse(
                status="success",
                message="Stage 2 approved. Vihara registration COMPLETED!",
                data=result_dict,
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=message
                ) from exc
            raise validation_error([(None, message)]) from exc

    if action == CRUDAction.REJECT_STAGE_TWO:
        if payload.vh_id is None:
            raise validation_error(
                [("payload.vh_id", "vh_id is required for REJECT_STAGE_TWO action")]
            )
        if not payload.rejection_reason:
            raise validation_error(
                [("payload.rejection_reason", "Rejection reason is required for REJECT_STAGE_TWO action")]
            )
        
        try:
            result = vihara_service.reject_stage_two(
                db, vh_id=payload.vh_id, actor_id=user_id, rejection_reason=payload.rejection_reason
            )
            
            # Enrich with temporary entities if present
            temp_data = vihara_service.enrich_with_temp_entities(db, result)
            result_dict = ViharaOut.model_validate(result).model_dump()
            result_dict.update(temp_data)
            
            return ViharaManagementResponse(
                status="success",
                message="Stage 2 rejected. Status: REJECTED.",
                data=result_dict,
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=message
                ) from exc
            raise validation_error([(None, message)]) from exc

    # =================================================================
    # LEGACY / CRUD OPERATIONS
    # =================================================================

    if action == CRUDAction.CREATE:
        create_payload = None
        raw_data = payload.data
        if isinstance(raw_data, BaseModel):
            raw_data = raw_data.model_dump(exclude_unset=True)
        
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
            
            # Enrich with temporary entities if present
            temp_data = vihara_service.enrich_with_temp_entities(db, created)
            result_dict = ViharaOut.model_validate(created).model_dump()
            result_dict.update(temp_data)
            
            return ViharaManagementResponse(
                status="success",
                message="Vihara created successfully.",
                data=result_dict,
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

        entity = None
        if identifier_id is not None:
            entity = vihara_service.get_vihara(db, identifier_id)
        elif identifier_trn:
            entity = vihara_service.get_vihara_by_trn(db, identifier_trn)

        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Vihara not found"
            )

        # Enrich with temporary entities if present
        temp_data = vihara_service.enrich_with_temp_entities(db, entity)
        result_dict = ViharaOut.model_validate(entity).model_dump()
        result_dict.update(temp_data)

        # Return entity directly - FastAPI will serialize it using the response_model
        return ViharaManagementResponse(
            status="success",
            message="Vihara retrieved successfully.",
            data=result_dict,
        )

    if action == CRUDAction.READ_ALL:
        page = payload.page or 1
        limit = payload.limit
        search = payload.search_key.strip() if payload.search_key else None
        if search == "":
            search = None
        skip = payload.skip if payload.page is None else (page - 1) * limit

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
            "current_user": current_user,
        }

        records = vihara_service.list_viharas(db, **filters)
        total = vihara_service.count_viharas(db, **{k: v for k, v in filters.items() if k not in ["skip", "limit"]})
        
        # Convert records to list of dicts for modification (serialize SQLAlchemy models)
        records_list = []
        for record in records:
            # Enrich with temporary entities if present
            temp_data = vihara_service.enrich_with_temp_entities(db, record)
            record_dict = ViharaOut.model_validate(record).model_dump()
            record_dict.update(temp_data)
            records_list.append(record_dict)
        
        # Also fetch temporary viharas and include them in results
        # Only apply search filter for temporary viharas (other filters don't apply to them)
        temp_viharas = temporary_vihara_service.list_temporary_viharas(
            db,
            skip=0,  # Get all matching temp viharas
            limit=200,  # Max allowed
            search=search
        )
        
        # Convert temporary viharas to Vihara-compatible format
        for temp_vihara in temp_viharas:
            # Truncate mobile to 10 chars if needed
            mobile = temp_vihara.tv_contact_number[:10] if temp_vihara.tv_contact_number and len(temp_vihara.tv_contact_number) > 10 else (temp_vihara.tv_contact_number or "0000000000")
            if not mobile or len(mobile) < 10:
                mobile = "0000000000"  # Default placeholder for required field
            
            temp_vihara_dict = {
                "vh_id": -temp_vihara.tv_id,  # Negative ID to distinguish from real records
                "vh_trn": f"TEMP-{temp_vihara.tv_id}",  # Use TEMP prefix for identification
                "vh_vname": temp_vihara.tv_name,
                "vh_addrs": temp_vihara.tv_address,
                "vh_mobile": mobile,
                "vh_whtapp": mobile,
                "vh_email": f"temp{temp_vihara.tv_id}@temporary.local",  # Placeholder email
                "vh_typ": "TEMP",  # Mark as temporary type
                "vh_gndiv": "TEMP",  # Placeholder
                "vh_ownercd": "TEMP",  # Placeholder
                "vh_parshawa": "TEMP",  # Placeholder
                "vh_province": temp_vihara.tv_province,
                "vh_district": temp_vihara.tv_district,
                "vh_viharadhipathi_name": temp_vihara.tv_viharadhipathi_name,
                "vh_workflow_status": "TEMPORARY",  # Mark workflow as temporary
                "vh_created_at": temp_vihara.tv_created_at,
                "vh_created_by": temp_vihara.tv_created_by,
                "vh_updated_at": temp_vihara.tv_updated_at,
                "vh_updated_by": temp_vihara.tv_updated_by,
                "vh_is_deleted": False,
                "vh_version_number": 1,
                "temple_lands": [],
                "resident_bhikkhus": [],
            }
            records_list.append(temp_vihara_dict)
        
        # Update total count to include temporary viharas
        temp_count = temporary_vihara_service.count_temporary_viharas(db, search=search)
        total_with_temp = total + temp_count
        
        return ViharaManagementResponse(
            status="success",
            message="Vihara records retrieved successfully.",
            data=records_list,
            totalRecords=total_with_temp,
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
            
            # Enrich with temporary entities if present
            temp_data = vihara_service.enrich_with_temp_entities(db, updated)
            result_dict = ViharaOut.model_validate(updated).model_dump()
            result_dict.update(temp_data)
            
            return ViharaManagementResponse(
                status="success",
                message="Vihara updated successfully.",
                data=result_dict,
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

    # Legacy approval actions (for backward compatibility)
    if action == CRUDAction.APPROVE:
        if payload.vh_id is None:
            raise validation_error(
                [("payload.vh_id", "vh_id is required for APPROVE action")]
            )
        
        try:
            approved_vihara = vihara_service.approve_vihara(
                db, vh_id=payload.vh_id, actor_id=user_id
            )
            
            # Enrich with temporary entities if present
            temp_data = vihara_service.enrich_with_temp_entities(db, approved_vihara)
            result_dict = ViharaOut.model_validate(approved_vihara).model_dump()
            result_dict.update(temp_data)
            
            return ViharaManagementResponse(
                status="success",
                message="Vihara approved successfully.",
                data=result_dict,
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
            
            # Enrich with temporary entities if present
            temp_data = vihara_service.enrich_with_temp_entities(db, rejected_vihara)
            result_dict = ViharaOut.model_validate(rejected_vihara).model_dump()
            result_dict.update(temp_data)
            
            return ViharaManagementResponse(
                status="success",
                message="Vihara rejected successfully.",
                data=result_dict,
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
            
            # Enrich with temporary entities if present
            temp_data = vihara_service.enrich_with_temp_entities(db, printed_vihara)
            result_dict = ViharaOut.model_validate(printed_vihara).model_dump()
            result_dict.update(temp_data)
            
            return ViharaManagementResponse(
                status="success",
                message="Vihara certificate marked as printed successfully.",
                data=result_dict,
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
            
            # Enrich with temporary entities if present
            temp_data = vihara_service.enrich_with_temp_entities(db, scanned_vihara)
            result_dict = ViharaOut.model_validate(scanned_vihara).model_dump()
            result_dict.update(temp_data)
            
            return ViharaManagementResponse(
                status="success",
                message="Vihara certificate marked as scanned successfully.",
                data=result_dict,
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=message
                ) from exc
            raise validation_error([(None, message)]) from exc

    raise validation_error([("action", "Invalid action specified")])


# =============================================================================
# STAGE 1 DOCUMENT UPLOAD ENDPOINT
# =============================================================================

@router.post(
    "/{vh_id}/upload-stage1-document",
    response_model=ViharaManagementResponse,
    dependencies=[has_any_permission("vihara:update")],
)
async def upload_stage1_document(
    vh_id: int,
    file: UploadFile = File(..., description="Scanned Stage 1 document file (max 5MB, PDF, JPG, PNG)"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Upload a scanned document for Stage 1.
    
    **Workflow Transition:** S1_PRINTING → S1_PEND_APPROVAL
    
    This endpoint is used after the Stage 1 form has been printed and scanned.
    Upon successful upload, the workflow status automatically changes to S1_PEND_APPROVAL.
    
    **Requirements:**
    - Maximum file size: 5MB
    - Allowed formats: PDF, JPG, JPEG, PNG
    - Current workflow status must be S1_PRINTING
    
    **Example Usage:**
    ```
    POST /api/v1/vihara-data/{vh_id}/upload-stage1-document
    Content-Type: multipart/form-data
    Body: file=@scanned_document.pdf
    ```
    """
    username = current_user.ua_user_id if current_user else None
    
    try:
        MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size ({file_size / 1024 / 1024:.2f}MB) exceeds maximum allowed size (5MB)"
            )
        
        await file.seek(0)
        
        updated_vihara = await vihara_service.upload_stage1_document(
            db, vh_id=vh_id, file=file, actor_id=username
        )
        
        return ViharaManagementResponse(
            status="success",
            message="Stage 1 document uploaded. Status: S1_PEND_APPROVAL. Next: Approve or reject Stage 1.",
            data=updated_vihara,
        )
        
    except ValueError as exc:
        message = str(exc)
        if "not found" in message.lower():
            raise HTTPException(status_code=404, detail=message) from exc
        raise HTTPException(status_code=400, detail=message) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# =============================================================================
# STAGE 2 DOCUMENT UPLOAD ENDPOINT
# =============================================================================

@router.post(
    "/{vh_id}/upload-stage2-document",
    response_model=ViharaManagementResponse,
    dependencies=[has_any_permission("vihara:update")],
)
async def upload_stage2_document(
    vh_id: int,
    file: UploadFile = File(..., description="Scanned Stage 2 document file (max 5MB, PDF, JPG, PNG)"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Upload a scanned document for Stage 2.
    
    **Workflow Transition:** S2_PENDING → S2_PEND_APPROVAL
    
    This endpoint is used after Stage 2 data has been saved and the document scanned.
    Upon successful upload, the workflow status automatically changes to S2_PEND_APPROVAL.
    
    **Requirements:**
    - Maximum file size: 5MB
    - Allowed formats: PDF, JPG, JPEG, PNG
    - Current workflow status must be S2_PENDING
    
    **Example Usage:**
    ```
    POST /api/v1/vihara-data/{vh_id}/upload-stage2-document
    Content-Type: multipart/form-data
    Body: file=@scanned_document.pdf
    ```
    """
    username = current_user.ua_user_id if current_user else None
    
    try:
        MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size ({file_size / 1024 / 1024:.2f}MB) exceeds maximum allowed size (5MB)"
            )
        
        await file.seek(0)
        
        updated_vihara = await vihara_service.upload_stage2_document(
            db, vh_id=vh_id, file=file, actor_id=username
        )
        
        return ViharaManagementResponse(
            status="success",
            message="Stage 2 document uploaded. Status: S2_PEND_APPROVAL. Next: Approve or reject Stage 2.",
            data=updated_vihara,
        )
        
    except ValueError as exc:
        message = str(exc)
        if "not found" in message.lower():
            raise HTTPException(status_code=404, detail=message) from exc
        raise HTTPException(status_code=400, detail=message) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# =============================================================================
# LEGACY DOCUMENT UPLOAD ENDPOINT (kept for backward compatibility)
# =============================================================================

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
    Legacy endpoint for uploading scanned documents.
    
    **DEPRECATED:** Use `/upload-stage1-document` or `/upload-stage2-document` instead.
    
    This endpoint is kept for backward compatibility and will route to the appropriate
    stage upload based on the current workflow status.
    """
    username = current_user.ua_user_id if current_user else None
    
    try:
        MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size ({file_size / 1024 / 1024:.2f}MB) exceeds maximum allowed size (5MB)"
            )
        
        await file.seek(0)
        
        updated_vihara = await vihara_service.upload_scanned_document(
            db, vh_id=vh_id, file=file, actor_id=username
        )
        
        return ViharaManagementResponse(
            status="success",
            message="Scanned document uploaded successfully.",
            data=updated_vihara,
        )
        
    except ValueError as exc:
        message = str(exc)
        if "not found" in message.lower():
            raise HTTPException(status_code=404, detail=message) from exc
        raise HTTPException(status_code=400, detail=message) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# =============================================================================
# STANDALONE APPROVAL ENDPOINTS
# =============================================================================

@router.post(
    "/{vh_id}/approve-stage1",
    response_model=ViharaManagementResponse,
    dependencies=[has_any_permission("vihara:update", "vihara:approve")],
)
def approve_stage1(
    vh_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Approve Stage 1 of vihara registration.
    
    **Workflow Transition:** S1_PEND_APPROVAL → S1_APPROVED
    
    After approval, Stage 2 input becomes available.
    """
    try:
        result = vihara_service.approve_stage_one(
            db, vh_id=vh_id, actor_id=current_user.ua_user_id
        )
        return ViharaManagementResponse(
            status="success",
            message="Stage 1 approved. Ready for Stage 2 input.",
            data=result,
        )
    except ValueError as exc:
        message = str(exc)
        if "not found" in message.lower():
            raise HTTPException(status_code=404, detail=message) from exc
        raise HTTPException(status_code=400, detail=message) from exc


@router.post(
    "/{vh_id}/reject-stage1",
    response_model=ViharaManagementResponse,
    dependencies=[has_any_permission("vihara:update", "vihara:approve")],
)
def reject_stage1(
    vh_id: int,
    rejection_reason: str = Query(..., description="Reason for rejection"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Reject Stage 1 of vihara registration.
    
    **Workflow Transition:** S1_PEND_APPROVAL → S1_REJECTED
    """
    try:
        result = vihara_service.reject_stage_one(
            db, vh_id=vh_id, actor_id=current_user.ua_user_id, rejection_reason=rejection_reason
        )
        return ViharaManagementResponse(
            status="success",
            message="Stage 1 rejected.",
            data=result,
        )
    except ValueError as exc:
        message = str(exc)
        if "not found" in message.lower():
            raise HTTPException(status_code=404, detail=message) from exc
        raise HTTPException(status_code=400, detail=message) from exc


@router.post(
    "/{vh_id}/approve-stage2",
    response_model=ViharaManagementResponse,
    dependencies=[has_any_permission("vihara:update", "vihara:approve")],
)
def approve_stage2(
    vh_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Approve Stage 2 of vihara registration.
    
    **Workflow Transition:** S2_PEND_APPROVAL → COMPLETED
    
    This is the final approval step. Vihara registration is now complete.
    """
    try:
        result = vihara_service.approve_stage_two(
            db, vh_id=vh_id, actor_id=current_user.ua_user_id
        )
        return ViharaManagementResponse(
            status="success",
            message="Vihara registration completed!",
            data=result,
        )
    except ValueError as exc:
        message = str(exc)
        if "not found" in message.lower():
            raise HTTPException(status_code=404, detail=message) from exc
        raise HTTPException(status_code=400, detail=message) from exc


@router.post(
    "/{vh_id}/reject-stage2",
    response_model=ViharaManagementResponse,
    dependencies=[has_any_permission("vihara:update", "vihara:approve")],
)
def reject_stage2(
    vh_id: int,
    rejection_reason: str = Query(..., description="Reason for rejection"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Reject Stage 2 of vihara registration.
    
    **Workflow Transition:** S2_PEND_APPROVAL → REJECTED
    """
    try:
        result = vihara_service.reject_stage_two(
            db, vh_id=vh_id, actor_id=current_user.ua_user_id, rejection_reason=rejection_reason
        )
        return ViharaManagementResponse(
            status="success",
            message="Stage 2 rejected.",
            data=result,
        )
    except ValueError as exc:
        message = str(exc)
        if "not found" in message.lower():
            raise HTTPException(status_code=404, detail=message) from exc
        raise HTTPException(status_code=400, detail=message) from exc


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

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
