# app/api/v1/routes/silmatha_id_card.py
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import date
import json

from app.api.deps import get_db
from app.api.auth_middleware import get_current_user
from app.models.user import UserAccount
from app.schemas.silmatha_id_card import (
    SilmathaIDCardAction,
    SilmathaIDCardCreate,
    SilmathaIDCardUpdate,
    SilmathaIDCardResponse,
    SilmathaIDCardManageResponse,
    SilmathaIDCardWorkflowActionType,
    SilmathaIDCardWorkflowRequest,
    SilmathaIDCardWorkflowResponse,
    StayHistoryItem,
)
from app.services.silmatha_id_card_service import silmatha_id_card_service
from app.services.temporary_silmatha_service import temporary_silmatha_service


router = APIRouter()


@router.post("/manage", response_model=SilmathaIDCardManageResponse)
async def manage_silmatha_id_card(
    # Action field
    action: str = Form(..., description="Action: CREATE, READ_ONE, READ_ALL, UPDATE, APPROVE, REJECT, MARK_PRINTED, DELETE"),
    
    # For READ_ONE, UPDATE, DELETE, APPROVE, REJECT, MARK_PRINTED
    sic_id: Optional[int] = Form(None, description="Silmatha ID Card ID"),
    sic_sil_regn: Optional[str] = Form(None, description="Silmatha registration number (for READ_ONE or CREATE)"),
    
    # For CREATE - Required fields
    sic_full_silmatha_name: Optional[str] = Form(None, description="Full Silmatha Name"),
    sic_lay_name_full: Optional[str] = Form(None, description="Lay name in full"),
    sic_dob: Optional[str] = Form(None, description="Date of birth (YYYY-MM-DD)"),
    
    # For CREATE/UPDATE - Optional fields
    sic_divisional_secretariat: Optional[str] = Form(None),
    sic_district: Optional[str] = Form(None),
    sic_title_post: Optional[str] = Form(None),
    sic_birth_place: Optional[str] = Form(None),
    sic_robing_date: Optional[str] = Form(None, description="Date (YYYY-MM-DD)"),
    sic_robing_place: Optional[str] = Form(None),
    sic_robing_nikaya: Optional[str] = Form(None),
    sic_robing_parshawaya: Optional[str] = Form(None),
    sic_samaneri_reg_no: Optional[str] = Form(None),
    sic_dasa_sil_mata_reg_no: Optional[str] = Form(None),
    sic_higher_ord_date: Optional[str] = Form(None, description="Date (YYYY-MM-DD)"),
    sic_higher_ord_name: Optional[str] = Form(None),
    sic_perm_residence: Optional[str] = Form(None),
    sic_national_id: Optional[str] = Form(None),
    sic_stay_history: Optional[str] = Form(None, description="JSON array of stay history"),
    
    # File uploads (optional)
    left_thumbprint: Optional[UploadFile] = File(None, description="Left thumbprint image"),
    applicant_photo: Optional[UploadFile] = File(None, description="Applicant photo"),
    
    # For REJECT
    rejection_reason: Optional[str] = Form(None),
    
    # For READ_ALL
    skip: Optional[int] = Form(0),
    limit: Optional[int] = Form(100),
    workflow_status: Optional[str] = Form(None),
    search_key: Optional[str] = Form(None),
    
    # Dependencies
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Unified endpoint for Silmatha ID Card management with multipart form-data support.
    
    This endpoint supports:
    - Creating ID cards with data + optional file uploads in a single request
    - Updating ID cards with data + optional file uploads in a single request
    - All other CRUD operations
    
    **For CREATE with Files in Postman:**
    
    1. Method: POST
    2. URL: {{base_url}}/api/v1/silmatha-id-card/manage
    3. Body: form-data
    4. Add fields:
       - action: CREATE
       - sic_sil_regn: SIL2025000001
       - sic_full_silmatha_name: Sister Dharmapriya
       - sic_lay_name_full: K.M. Nirmala
       - sic_dob: 1988-08-22
       - left_thumbprint: (file) - Select file
       - applicant_photo: (file) - Select file
       - sic_district: Kandy
       - ... (other optional fields)
    
    **For READ_ALL:**
    
    1. Body: form-data
    2. Fields:
       - action: READ_ALL
       - skip: 0
       - limit: 50
       - workflow_status: PENDING
    """
    username = current_user.ua_username if current_user else None
    
    try:
        # Convert action string to enum
        try:
            action_enum = SilmathaIDCardAction(action.upper())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid action: {action}. Must be one of: CREATE, READ_ONE, READ_ALL, UPDATE, DELETE, APPROVE, REJECT, MARK_PRINTED"
            )
        
        # --- CREATE ---
        if action_enum == SilmathaIDCardAction.CREATE:
            # Validate required fields
            if not sic_sil_regn:
                raise HTTPException(status_code=400, detail="sic_sil_regn is required for CREATE")
            if not sic_full_silmatha_name:
                raise HTTPException(status_code=400, detail="sic_full_silmatha_name is required for CREATE")
            if not sic_lay_name_full:
                raise HTTPException(status_code=400, detail="sic_lay_name_full is required for CREATE")
            if not sic_dob:
                raise HTTPException(status_code=400, detail="sic_dob is required for CREATE")
            
            # Parse stay_history JSON if provided
            stay_history_list = None
            if sic_stay_history:
                try:
                    stay_history_data = json.loads(sic_stay_history)
                    stay_history_list = [StayHistoryItem(**item) for item in stay_history_data]
                except json.JSONDecodeError:
                    raise HTTPException(status_code=400, detail="Invalid JSON format for stay_history")
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"Error parsing stay_history: {str(e)}")
            
            # Parse dates
            try:
                dob_date = date.fromisoformat(sic_dob)
                robing_date_parsed = date.fromisoformat(sic_robing_date) if sic_robing_date else None
                higher_ord_date_parsed = date.fromisoformat(sic_higher_ord_date) if sic_higher_ord_date else None
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
            
            # Create schema object
            create_data = SilmathaIDCardCreate(
                sic_sil_regn=sic_sil_regn,
                sic_divisional_secretariat=sic_divisional_secretariat,
                sic_district=sic_district,
                sic_full_silmatha_name=sic_full_silmatha_name,
                sic_title_post=sic_title_post,
                sic_lay_name_full=sic_lay_name_full,
                sic_dob=dob_date,
                sic_birth_place=sic_birth_place,
                sic_robing_date=robing_date_parsed,
                sic_robing_place=sic_robing_place,
                sic_robing_nikaya=sic_robing_nikaya,
                sic_robing_parshawaya=sic_robing_parshawaya,
                sic_samaneri_reg_no=sic_samaneri_reg_no,
                sic_dasa_sil_mata_reg_no=sic_dasa_sil_mata_reg_no,
                sic_higher_ord_date=higher_ord_date_parsed,
                sic_higher_ord_name=sic_higher_ord_name,
                sic_perm_residence=sic_perm_residence,
                sic_national_id=sic_national_id,
                sic_stay_history=stay_history_list,
            )
            
            # Create the record
            created_card = silmatha_id_card_service.create_silmatha_id_card(
                db,
                create_data,
                created_by=username
            )
            
            # Upload files if provided
            if left_thumbprint:
                created_card = await silmatha_id_card_service.upload_thumbprint(
                    db, created_card.sic_id, left_thumbprint
                )
            
            if applicant_photo:
                created_card = await silmatha_id_card_service.upload_applicant_photo(
                    db, created_card.sic_id, applicant_photo
                )
            
            return SilmathaIDCardManageResponse(
                status="success",
                message=f"Silmatha ID Card created successfully with form number {created_card.sic_form_no}",
                data=SilmathaIDCardResponse.model_validate(created_card)
            )
        
        # --- READ_ONE ---
        elif action_enum == SilmathaIDCardAction.READ_ONE:
            if sic_id:
                card = silmatha_id_card_service.get_silmatha_id_card_by_id(db, sic_id)
            elif sic_sil_regn:
                card = silmatha_id_card_service.get_silmatha_id_card_by_sil_regn(db, sic_sil_regn)
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Either 'sic_id' or 'sic_sil_regn' is required for READ_ONE"
                )
            
            return SilmathaIDCardManageResponse(
                status="success",
                message="Silmatha ID Card retrieved successfully",
                data=SilmathaIDCardResponse.model_validate(card)
            )
        
        # --- READ_ALL ---
        elif action_enum == SilmathaIDCardAction.READ_ALL:
            cards, total = silmatha_id_card_service.get_all_silmatha_id_cards(
                db,
                skip=skip or 0,
                limit=limit or 100,
                workflow_status=workflow_status,
                search_key=search_key
            )
            
            # Convert cards to response format
            card_responses = [SilmathaIDCardResponse.model_validate(card) for card in cards]
            
            # Also fetch temporary silmathas and include them in results
            # Only apply search filter for temporary silmathas (other filters don't apply to them)
            temp_silmathas = temporary_silmatha_service.list_temporary_silmathas(
                db,
                skip=0,  # Get all matching temp silmathas
                limit=200,  # Max allowed
                search=search_key
            )
            
            # Convert temporary silmathas to SilmathaIDCard-compatible format with temp_details
            for temp_silmatha in temp_silmathas:
                # Try to resolve province as nested object
                province_value = temp_silmatha.ts_province
                if temp_silmatha.ts_province:
                    from app.models.province import Province
                    province_obj = db.query(Province).filter(
                        Province.cp_code == temp_silmatha.ts_province
                    ).first()
                    if province_obj:
                        province_value = {
                            "pr_code": province_obj.cp_code,
                            "pr_name": province_obj.cp_name
                        }
                
                # Try to resolve district as nested object
                district_value = temp_silmatha.ts_district
                if temp_silmatha.ts_district:
                    from app.models.district import District
                    district_obj = db.query(District).filter(
                        District.dd_dcode == temp_silmatha.ts_district
                    ).first()
                    if district_obj:
                        district_value = {
                            "ds_code": district_obj.dd_dcode,
                            "ds_name": district_obj.dd_dname
                        }
                
                # Create a temporary ID card response format
                temp_card_dict = {
                    "sic_id": -temp_silmatha.ts_id,  # Negative ID to distinguish from real records
                    "sic_sil_regn": f"TEMP-{temp_silmatha.ts_id}",  # Use TEMP prefix for identification
                    "sic_form_no": f"TEMP-SIC-{temp_silmatha.ts_id}",
                    "sic_divisional_secretariat": None,
                    "sic_district": district_value.get("ds_name") if isinstance(district_value, dict) else district_value,
                    "sic_full_silmatha_name": temp_silmatha.ts_name,
                    "sic_title_post": None,
                    "sic_lay_name_full": None,
                    "sic_dob": None,
                    "sic_birth_place": None,
                    "sic_robing_date": temp_silmatha.ts_ordained_date,
                    "sic_robing_place": None,
                    "sic_robing_nikaya": None,
                    "sic_robing_parshawaya": None,
                    "sic_samaneri_reg_no": None,
                    "sic_dasa_sil_mata_reg_no": None,
                    "sic_higher_ord_date": None,
                    "sic_higher_ord_name": None,
                    "sic_perm_residence": temp_silmatha.ts_address,
                    "sic_national_id": temp_silmatha.ts_nic,
                    "sic_stay_history": None,
                    "sic_left_thumbprint_url": None,
                    "sic_applicant_photo_url": None,
                    "sic_workflow_status": "TEMPORARY",  # Mark workflow as temporary
                    "sic_submitted_by": temp_silmatha.ts_created_by,
                    "sic_submitted_at": temp_silmatha.ts_created_at,
                    "sic_approved_by": None,
                    "sic_approved_at": None,
                    "sic_rejected_by": None,
                    "sic_rejected_at": None,
                    "sic_rejection_reason": None,
                    "sic_printed_by": None,
                    "sic_printed_at": None,
                    "sic_created_at": temp_silmatha.ts_created_at,
                    "sic_created_by": temp_silmatha.ts_created_by,
                    "sic_updated_at": temp_silmatha.ts_updated_at,
                    "sic_updated_by": temp_silmatha.ts_updated_by,
                    # Nest all temporary silmatha data as a nested object
                    "temp_details": {
                        "ts_id": temp_silmatha.ts_id,
                        "ts_name": temp_silmatha.ts_name,
                        "ts_nic": temp_silmatha.ts_nic,
                        "ts_contact_number": temp_silmatha.ts_contact_number,
                        "ts_address": temp_silmatha.ts_address,
                        "ts_district": temp_silmatha.ts_district,
                        "ts_province": temp_silmatha.ts_province,
                        "ts_arama_name": temp_silmatha.ts_arama_name,
                        "ts_ordained_date": temp_silmatha.ts_ordained_date,
                        "ts_created_at": temp_silmatha.ts_created_at,
                        "ts_created_by": temp_silmatha.ts_created_by,
                        "ts_updated_at": temp_silmatha.ts_updated_at,
                        "ts_updated_by": temp_silmatha.ts_updated_by,
                    }
                }
                card_responses.append(temp_card_dict)
            
            # Update total count to include temporary silmathas
            temp_count = temporary_silmatha_service.count_temporary_silmathas(db, search=search_key)
            total_with_temp = total + temp_count
            
            return SilmathaIDCardManageResponse(
                status="success",
                message=f"Retrieved {len(card_responses)} Silmatha ID Cards (including temporary)",
                data=card_responses,
                total=total_with_temp
            )
        
        # --- UPDATE ---
        elif action_enum == SilmathaIDCardAction.UPDATE:
            if not sic_id:
                raise HTTPException(status_code=400, detail="sic_id is required for UPDATE")
            
            # Build update dict from provided fields
            update_dict = {}
            if sic_divisional_secretariat is not None:
                update_dict["sic_divisional_secretariat"] = sic_divisional_secretariat
            if sic_district is not None:
                update_dict["sic_district"] = sic_district
            if sic_full_silmatha_name is not None:
                update_dict["sic_full_silmatha_name"] = sic_full_silmatha_name
            if sic_title_post is not None:
                update_dict["sic_title_post"] = sic_title_post
            if sic_lay_name_full is not None:
                update_dict["sic_lay_name_full"] = sic_lay_name_full
            if sic_dob is not None:
                try:
                    update_dict["sic_dob"] = date.fromisoformat(sic_dob)
                except ValueError:
                    raise HTTPException(status_code=400, detail="Invalid date format for sic_dob")
            if sic_birth_place is not None:
                update_dict["sic_birth_place"] = sic_birth_place
            if sic_robing_date is not None:
                try:
                    update_dict["sic_robing_date"] = date.fromisoformat(sic_robing_date)
                except ValueError:
                    raise HTTPException(status_code=400, detail="Invalid date format for sic_robing_date")
            if sic_robing_place is not None:
                update_dict["sic_robing_place"] = sic_robing_place
            if sic_robing_nikaya is not None:
                update_dict["sic_robing_nikaya"] = sic_robing_nikaya
            if sic_robing_parshawaya is not None:
                update_dict["sic_robing_parshawaya"] = sic_robing_parshawaya
            if sic_samaneri_reg_no is not None:
                update_dict["sic_samaneri_reg_no"] = sic_samaneri_reg_no
            if sic_dasa_sil_mata_reg_no is not None:
                update_dict["sic_dasa_sil_mata_reg_no"] = sic_dasa_sil_mata_reg_no
            if sic_higher_ord_date is not None:
                try:
                    update_dict["sic_higher_ord_date"] = date.fromisoformat(sic_higher_ord_date)
                except ValueError:
                    raise HTTPException(status_code=400, detail="Invalid date format for sic_higher_ord_date")
            if sic_higher_ord_name is not None:
                update_dict["sic_higher_ord_name"] = sic_higher_ord_name
            if sic_perm_residence is not None:
                update_dict["sic_perm_residence"] = sic_perm_residence
            if sic_national_id is not None:
                update_dict["sic_national_id"] = sic_national_id
            if sic_stay_history is not None:
                try:
                    stay_history_data = json.loads(sic_stay_history)
                    update_dict["sic_stay_history"] = [StayHistoryItem(**item) for item in stay_history_data]
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"Error parsing stay_history: {str(e)}")
            
            # Create update schema
            update_data = SilmathaIDCardUpdate(**update_dict)
            
            # Update the record
            updated_card = silmatha_id_card_service.update_silmatha_id_card(
                db,
                sic_id,
                update_data,
                updated_by=username
            )
            
            # Upload files if provided
            if left_thumbprint:
                updated_card = await silmatha_id_card_service.upload_thumbprint(
                    db, updated_card.sic_id, left_thumbprint
                )
            
            if applicant_photo:
                updated_card = await silmatha_id_card_service.upload_applicant_photo(
                    db, updated_card.sic_id, applicant_photo
                )
            
            return SilmathaIDCardManageResponse(
                status="success",
                message=f"Silmatha ID Card {updated_card.sic_form_no} updated successfully",
                data=SilmathaIDCardResponse.model_validate(updated_card)
            )
        
        # --- DELETE ---
        elif action_enum == SilmathaIDCardAction.DELETE:
            if not sic_id:
                raise HTTPException(status_code=400, detail="sic_id is required for DELETE")
            
            silmatha_id_card_service.delete_silmatha_id_card(db, sic_id)
            
            return SilmathaIDCardManageResponse(
                status="success",
                message=f"Silmatha ID Card with ID {sic_id} deleted successfully",
                data=None
            )
        
        # --- APPROVE ---
        elif action_enum == SilmathaIDCardAction.APPROVE:
            if not sic_id:
                raise HTTPException(status_code=400, detail="sic_id is required for APPROVE")
            
            approved_card = silmatha_id_card_service.approve_silmatha_id_card(
                db, sic_id, approved_by=username
            )
            
            return SilmathaIDCardManageResponse(
                status="success",
                message=f"Silmatha ID Card {approved_card.sic_form_no} approved successfully",
                data=SilmathaIDCardResponse.model_validate(approved_card)
            )
        
        # --- REJECT ---
        elif action_enum == SilmathaIDCardAction.REJECT:
            if not sic_id:
                raise HTTPException(status_code=400, detail="sic_id is required for REJECT")
            if not rejection_reason:
                raise HTTPException(status_code=400, detail="rejection_reason is required for REJECT")
            
            rejected_card = silmatha_id_card_service.reject_silmatha_id_card(
                db, sic_id, rejected_by=username, rejection_reason=rejection_reason
            )
            
            return SilmathaIDCardManageResponse(
                status="success",
                message=f"Silmatha ID Card {rejected_card.sic_form_no} rejected",
                data=SilmathaIDCardResponse.model_validate(rejected_card)
            )
        
        # --- MARK_PRINTED ---
        elif action_enum == SilmathaIDCardAction.MARK_PRINTED:
            if not sic_id:
                raise HTTPException(status_code=400, detail="sic_id is required for MARK_PRINTED")
            
            printed_card = silmatha_id_card_service.mark_silmatha_id_card_printed(
                db, sic_id, printed_by=username
            )
            
            return SilmathaIDCardManageResponse(
                status="success",
                message=f"Silmatha ID Card {printed_card.sic_form_no} marked as printed",
                data=SilmathaIDCardResponse.model_validate(printed_card)
            )
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported action: {action}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/{sic_id}/upload-thumbprint", response_model=SilmathaIDCardManageResponse)
async def upload_thumbprint(
    sic_id: int,
    file: UploadFile = File(..., description="Left thumbprint image file"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Upload left thumbprint image for a Silmatha ID Card.
    
    Separate endpoint for file upload if needed.
    """
    try:
        updated_card = await silmatha_id_card_service.upload_thumbprint(db, sic_id, file)
        
        return SilmathaIDCardManageResponse(
            status="success",
            message=f"Thumbprint uploaded successfully for ID Card {updated_card.sic_form_no}",
            data=SilmathaIDCardResponse.model_validate(updated_card)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )


@router.post("/{sic_id}/upload-photo", response_model=SilmathaIDCardManageResponse)
async def upload_photo(
    sic_id: int,
    file: UploadFile = File(..., description="Applicant photo file"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Upload applicant photo for a Silmatha ID Card.
    
    Separate endpoint for file upload if needed.
    """
    try:
        updated_card = await silmatha_id_card_service.upload_applicant_photo(db, sic_id, file)
        
        return SilmathaIDCardManageResponse(
            status="success",
            message=f"Photo uploaded successfully for ID Card {updated_card.sic_form_no}",
            data=SilmathaIDCardResponse.model_validate(updated_card)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("/{sic_id}", response_model=SilmathaIDCardManageResponse)
async def get_silmatha_id_card_by_id(
    sic_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Get a Silmatha ID Card by ID.
    
    Alternative to /manage with READ_ONE action.
    """
    try:
        card = silmatha_id_card_service.get_silmatha_id_card_by_id(db, sic_id)
        
        return SilmathaIDCardManageResponse(
            status="success",
            message="Silmatha ID Card retrieved successfully",
            data=SilmathaIDCardResponse.model_validate(card)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Retrieval failed: {str(e)}"
        )


@router.get("/by-regn/{sil_regn}", response_model=SilmathaIDCardManageResponse)
async def get_silmatha_id_card_by_regn(
    sil_regn: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Get a Silmatha ID Card by Silmatha registration number.
    
    Alternative to /manage with READ_ONE action.
    """
    try:
        card = silmatha_id_card_service.get_silmatha_id_card_by_sil_regn(db, sil_regn)
        
        return SilmathaIDCardManageResponse(
            status="success",
            message="Silmatha ID Card retrieved successfully",
            data=SilmathaIDCardResponse.model_validate(card)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Retrieval failed: {str(e)}"
        )


@router.post("/workflow", response_model=SilmathaIDCardWorkflowResponse)
async def silmatha_id_card_workflow(
    request: SilmathaIDCardWorkflowRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Handle workflow actions for Silmatha ID Cards.
    
    Supported actions:
    - APPROVE: Approve an ID card
    - REJECT: Reject an ID card (requires rejection_reason)
    - MARK_PRINTED: Mark as printing complete
    
    Identify card by either sic_id or sic_form_no.
    """
    username = current_user.ua_username if current_user else None
    
    try:
        # Determine sic_id
        if request.sic_id:
            sic_id = request.sic_id
        elif request.sic_form_no:
            # Look up by form number
            card = silmatha_id_card_service.repository.get_by_form_no(db, request.sic_form_no)
            if not card:
                raise HTTPException(
                    status_code=404,
                    detail=f"Silmatha ID Card with form number '{request.sic_form_no}' not found"
                )
            sic_id = card.sic_id
        else:
            raise HTTPException(
                status_code=400,
                detail="Either 'sic_id' or 'sic_form_no' is required"
            )
        
        # Execute workflow action
        if request.action == SilmathaIDCardWorkflowActionType.APPROVE:
            updated_card = silmatha_id_card_service.approve_silmatha_id_card(
                db, sic_id, approved_by=username
            )
            message = f"ID Card {updated_card.sic_form_no} approved successfully"
        
        elif request.action == SilmathaIDCardWorkflowActionType.REJECT:
            if not request.rejection_reason:
                raise HTTPException(
                    status_code=400,
                    detail="rejection_reason is required for REJECT action"
                )
            updated_card = silmatha_id_card_service.reject_silmatha_id_card(
                db, sic_id, rejected_by=username, rejection_reason=request.rejection_reason
            )
            message = f"ID Card {updated_card.sic_form_no} rejected"
        
        elif request.action == SilmathaIDCardWorkflowActionType.MARK_PRINTED:
            updated_card = silmatha_id_card_service.mark_silmatha_id_card_printed(
                db, sic_id, printed_by=username
            )
            message = f"ID Card {updated_card.sic_form_no} marked as printed"
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported workflow action: {request.action}"
            )
        
        return SilmathaIDCardWorkflowResponse(
            status="success",
            message=message,
            data=SilmathaIDCardResponse.model_validate(updated_card)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Workflow action failed: {str(e)}"
        )
