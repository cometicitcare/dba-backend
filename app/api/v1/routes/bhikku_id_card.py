# app/api/v1/routes/bhikku_id_card.py
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import date
import json

from app.api.deps import get_db
from app.api.auth_middleware import get_current_user
from app.models.user import UserAccount
from app.schemas.bhikku_id_card import (
    BhikkuIDCardAction,
    BhikkuIDCardCreate,
    BhikkuIDCardUpdate,
    BhikkuIDCardResponse,
    BhikkuIDCardManageResponse,
    BhikkuIDCardWorkflowActionType,
    BhikkuIDCardWorkflowRequest,
    BhikkuIDCardWorkflowResponse,
    StayHistoryItem,
)
from app.services.bhikku_id_card_service import bhikku_id_card_service


router = APIRouter()


@router.post("/manage", response_model=BhikkuIDCardManageResponse)
async def manage_bhikku_id_card(
    # Action field
    action: str = Form(..., description="Action: CREATE, READ_ONE, READ_ALL, UPDATE, APPROVE, REJECT, MARK_PRINTED, DELETE"),
    
    # For READ_ONE, UPDATE, DELETE, APPROVE, REJECT, MARK_PRINTED
    bic_id: Optional[int] = Form(None, description="Bhikku ID Card ID"),
    bic_br_regn: Optional[str] = Form(None, description="Bhikku registration number (for READ_ONE or CREATE)"),
    
    # For CREATE - Required fields
    bic_full_bhikku_name: Optional[str] = Form(None, description="Full Bhikku Name"),
    bic_lay_name_full: Optional[str] = Form(None, description="Lay name in full"),
    bic_dob: Optional[str] = Form(None, description="Date of birth (YYYY-MM-DD)"),
    
    # For CREATE/UPDATE - Optional fields
    bic_divisional_secretariat: Optional[str] = Form(None),
    bic_district: Optional[str] = Form(None),
    bic_title_post: Optional[str] = Form(None),
    bic_birth_place: Optional[str] = Form(None),
    bic_robing_date: Optional[str] = Form(None, description="Date (YYYY-MM-DD)"),
    bic_robing_place: Optional[str] = Form(None),
    bic_robing_nikaya: Optional[str] = Form(None),
    bic_robing_parshawaya: Optional[str] = Form(None),
    bic_samanera_reg_no: Optional[str] = Form(None),
    bic_upasampada_reg_no: Optional[str] = Form(None),
    bic_higher_ord_date: Optional[str] = Form(None, description="Date (YYYY-MM-DD)"),
    bic_higher_ord_name: Optional[str] = Form(None),
    bic_perm_residence: Optional[str] = Form(None),
    bic_national_id: Optional[str] = Form(None),
    bic_stay_history: Optional[str] = Form(None, description="JSON array of stay history"),
    
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
    Unified endpoint for Bhikku ID Card management with multipart form-data support.
    
    This endpoint supports:
    - Creating ID cards with data + optional file uploads in a single request
    - Updating ID cards with data + optional file uploads in a single request
    - All other CRUD operations
    
    **For CREATE with Files in Postman:**
    
    1. Method: POST
    2. URL: {{base_url}}/api/v1/bhikku-id-card/manage
    3. Body: form-data
    4. Add fields:
       - action: CREATE
       - bic_br_regn: BH202500001
       - bic_full_bhikku_name: Ven. Mahanama Thero
       - bic_lay_name_full: K.M. Somapala
       - bic_dob: 1985-05-15
       - left_thumbprint: (file) - Select file
       - applicant_photo: (file) - Select file
       - bic_district: Kandy
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
            action_enum = BhikkuIDCardAction(action.upper())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid action: {action}. Must be one of: CREATE, READ_ONE, READ_ALL, UPDATE, DELETE, APPROVE, REJECT, MARK_PRINTED"
            )
        
        # --- CREATE ---
        if action_enum == BhikkuIDCardAction.CREATE:
            # Validate required fields
            if not bic_br_regn:
                raise HTTPException(status_code=400, detail="bic_br_regn is required for CREATE")
            if not bic_full_bhikku_name:
                raise HTTPException(status_code=400, detail="bic_full_bhikku_name is required for CREATE")
            if not bic_lay_name_full:
                raise HTTPException(status_code=400, detail="bic_lay_name_full is required for CREATE")
            if not bic_dob:
                raise HTTPException(status_code=400, detail="bic_dob is required for CREATE")
            
            # Parse stay_history JSON if provided
            stay_history_list = None
            if bic_stay_history:
                try:
                    stay_history_data = json.loads(bic_stay_history)
                    stay_history_list = [StayHistoryItem(**item) for item in stay_history_data]
                except json.JSONDecodeError:
                    raise HTTPException(status_code=400, detail="Invalid JSON format for stay_history")
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"Error parsing stay_history: {str(e)}")
            
            # Parse dates
            try:
                dob_date = date.fromisoformat(bic_dob)
                robing_date_parsed = date.fromisoformat(bic_robing_date) if bic_robing_date else None
                higher_ord_date_parsed = date.fromisoformat(bic_higher_ord_date) if bic_higher_ord_date else None
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
            
            # Create schema object
            create_data = BhikkuIDCardCreate(
                bic_br_regn=bic_br_regn,
                bic_divisional_secretariat=bic_divisional_secretariat,
                bic_district=bic_district,
                bic_full_bhikku_name=bic_full_bhikku_name,
                bic_title_post=bic_title_post,
                bic_lay_name_full=bic_lay_name_full,
                bic_dob=dob_date,
                bic_birth_place=bic_birth_place,
                bic_robing_date=robing_date_parsed,
                bic_robing_place=bic_robing_place,
                bic_robing_nikaya=bic_robing_nikaya,
                bic_robing_parshawaya=bic_robing_parshawaya,
                bic_samanera_reg_no=bic_samanera_reg_no,
                bic_upasampada_reg_no=bic_upasampada_reg_no,
                bic_higher_ord_date=higher_ord_date_parsed,
                bic_higher_ord_name=bic_higher_ord_name,
                bic_perm_residence=bic_perm_residence,
                bic_national_id=bic_national_id,
                bic_stay_history=stay_history_list,
            )
            
            # Create the record
            created_card = bhikku_id_card_service.create_bhikku_id_card(
                db,
                create_data,
                created_by=username
            )
            
            # Upload files if provided
            if left_thumbprint:
                created_card = await bhikku_id_card_service.upload_thumbprint(
                    db, created_card.bic_id, left_thumbprint
                )
            
            if applicant_photo:
                created_card = await bhikku_id_card_service.upload_applicant_photo(
                    db, created_card.bic_id, applicant_photo
                )
            
            return BhikkuIDCardManageResponse(
                status="success",
                message=f"Bhikku ID Card created successfully with form number {created_card.bic_form_no}",
                data=BhikkuIDCardResponse.from_orm(created_card)
            )
        
        # --- READ_ONE ---
        elif action_enum == BhikkuIDCardAction.READ_ONE:
            if bic_id:
                card = bhikku_id_card_service.get_bhikku_id_card_by_id(db, bic_id)
            elif bic_br_regn:
                card = bhikku_id_card_service.get_bhikku_id_card_by_br_regn(db, bic_br_regn)
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Either 'bic_id' or 'bic_br_regn' is required for READ_ONE"
                )
            
            return BhikkuIDCardManageResponse(
                status="success",
                message="Bhikku ID Card retrieved successfully",
                data=BhikkuIDCardResponse.from_orm(card)
            )
        
        # --- READ_ALL ---
        elif action_enum == BhikkuIDCardAction.READ_ALL:
            cards, total = bhikku_id_card_service.get_all_bhikku_id_cards(
                db,
                skip=skip or 0,
                limit=limit or 100,
                workflow_status=workflow_status,
                search_key=search_key
            )
            
            return BhikkuIDCardManageResponse(
                status="success",
                message=f"Retrieved {len(cards)} Bhikku ID Cards",
                data=[BhikkuIDCardResponse.from_orm(card) for card in cards],
                total=total
            )
        
        # --- UPDATE ---
        elif action_enum == BhikkuIDCardAction.UPDATE:
            if not bic_id:
                raise HTTPException(status_code=400, detail="bic_id is required for UPDATE")
            
            # Build update dict from provided fields
            update_dict = {}
            if bic_divisional_secretariat is not None:
                update_dict["bic_divisional_secretariat"] = bic_divisional_secretariat
            if bic_district is not None:
                update_dict["bic_district"] = bic_district
            if bic_full_bhikku_name is not None:
                update_dict["bic_full_bhikku_name"] = bic_full_bhikku_name
            if bic_title_post is not None:
                update_dict["bic_title_post"] = bic_title_post
            if bic_lay_name_full is not None:
                update_dict["bic_lay_name_full"] = bic_lay_name_full
            if bic_dob is not None:
                try:
                    update_dict["bic_dob"] = date.fromisoformat(bic_dob)
                except ValueError:
                    raise HTTPException(status_code=400, detail="Invalid date format for bic_dob")
            if bic_birth_place is not None:
                update_dict["bic_birth_place"] = bic_birth_place
            if bic_robing_date is not None:
                try:
                    update_dict["bic_robing_date"] = date.fromisoformat(bic_robing_date)
                except ValueError:
                    raise HTTPException(status_code=400, detail="Invalid date format for bic_robing_date")
            if bic_robing_place is not None:
                update_dict["bic_robing_place"] = bic_robing_place
            if bic_robing_nikaya is not None:
                update_dict["bic_robing_nikaya"] = bic_robing_nikaya
            if bic_robing_parshawaya is not None:
                update_dict["bic_robing_parshawaya"] = bic_robing_parshawaya
            if bic_samanera_reg_no is not None:
                update_dict["bic_samanera_reg_no"] = bic_samanera_reg_no
            if bic_upasampada_reg_no is not None:
                update_dict["bic_upasampada_reg_no"] = bic_upasampada_reg_no
            if bic_higher_ord_date is not None:
                try:
                    update_dict["bic_higher_ord_date"] = date.fromisoformat(bic_higher_ord_date)
                except ValueError:
                    raise HTTPException(status_code=400, detail="Invalid date format for bic_higher_ord_date")
            if bic_higher_ord_name is not None:
                update_dict["bic_higher_ord_name"] = bic_higher_ord_name
            if bic_perm_residence is not None:
                update_dict["bic_perm_residence"] = bic_perm_residence
            if bic_national_id is not None:
                update_dict["bic_national_id"] = bic_national_id
            if bic_stay_history is not None:
                try:
                    stay_history_data = json.loads(bic_stay_history)
                    update_dict["bic_stay_history"] = [StayHistoryItem(**item) for item in stay_history_data]
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"Error parsing stay_history: {str(e)}")
            
            # Create update schema
            update_data = BhikkuIDCardUpdate(**update_dict)
            
            # Update the record
            updated_card = bhikku_id_card_service.update_bhikku_id_card(
                db,
                bic_id,
                update_data,
                updated_by=username
            )
            
            # Upload files if provided
            if left_thumbprint:
                updated_card = await bhikku_id_card_service.upload_thumbprint(
                    db, bic_id, left_thumbprint
                )
            
            if applicant_photo:
                updated_card = await bhikku_id_card_service.upload_applicant_photo(
                    db, bic_id, applicant_photo
                )
            
            return BhikkuIDCardManageResponse(
                status="success",
                message="Bhikku ID Card updated successfully",
                data=BhikkuIDCardResponse.from_orm(updated_card)
            )
        
        # --- DELETE ---
        elif action_enum == BhikkuIDCardAction.DELETE:
            if not bic_id:
                raise HTTPException(status_code=400, detail="bic_id is required for DELETE")
            
            result = bhikku_id_card_service.delete_bhikku_id_card(db, bic_id)
            
            return BhikkuIDCardManageResponse(
                status="success",
                message=result["message"],
                data=None
            )
        
        # --- APPROVE ---
        elif action_enum == BhikkuIDCardAction.APPROVE:
            if not bic_id:
                raise HTTPException(status_code=400, detail="bic_id is required for APPROVE")
            
            approved_card = bhikku_id_card_service.approve_bhikku_id_card(
                db,
                bic_id,
                approved_by=username
            )
            
            return BhikkuIDCardManageResponse(
                status="success",
                message="Bhikku ID Card approved successfully",
                data=BhikkuIDCardResponse.from_orm(approved_card)
            )
        
        # --- REJECT ---
        elif action_enum == BhikkuIDCardAction.REJECT:
            if not bic_id:
                raise HTTPException(status_code=400, detail="bic_id is required for REJECT")
            if not rejection_reason:
                raise HTTPException(status_code=400, detail="rejection_reason is required for REJECT")
            
            rejected_card = bhikku_id_card_service.reject_bhikku_id_card(
                db,
                bic_id,
                rejected_by=username,
                rejection_reason=rejection_reason
            )
            
            return BhikkuIDCardManageResponse(
                status="success",
                message="Bhikku ID Card rejected successfully",
                data=BhikkuIDCardResponse.from_orm(rejected_card)
            )
        
        # --- MARK_PRINTED ---
        elif action_enum == BhikkuIDCardAction.MARK_PRINTED:
            if not bic_id:
                raise HTTPException(status_code=400, detail="bic_id is required for MARK_PRINTED")
            
            printed_card = bhikku_id_card_service.mark_bhikku_id_card_printed(
                db,
                bic_id,
                printed_by=username
            )
            
            return BhikkuIDCardManageResponse(
                status="success",
                message="Bhikku ID Card marked as printed and completed successfully",
                data=BhikkuIDCardResponse.from_orm(printed_card)
            )
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown action: {action}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/{bic_id}/upload-thumbprint", response_model=BhikkuIDCardManageResponse)
async def upload_thumbprint(
    bic_id: int,
    file: UploadFile = File(..., description="Left thumbprint image file (JPG, PNG, etc.)"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Upload left thumbprint image for a Bhikku ID Card.
    
    **NOTE**: You can also upload thumbprint during CREATE/UPDATE using the /manage endpoint.
    This endpoint is provided as an alternative for uploading files separately.
    
    The file will be stored at: `app/storage/<year>/<month>/<day>/<br_regn>/left_thumbprint_*.jpg`
    
    **Supported formats**: JPG, JPEG, PNG, GIF, BMP, WEBP  
    **Max file size**: 10 MB
    """
    try:
        updated_card = await bhikku_id_card_service.upload_thumbprint(db, bic_id, file)
        
        return BhikkuIDCardManageResponse(
            status="success",
            message="Left thumbprint uploaded successfully",
            data=BhikkuIDCardResponse.from_orm(updated_card)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload thumbprint: {str(e)}"
        )


@router.post("/{bic_id}/upload-photo", response_model=BhikkuIDCardManageResponse)
async def upload_applicant_photo(
    bic_id: int,
    file: UploadFile = File(..., description="Applicant photo (3cm x 2.5cm) - JPG, PNG, etc."),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Upload applicant photo for a Bhikku ID Card.
    
    **NOTE**: You can also upload photo during CREATE/UPDATE using the /manage endpoint.
    This endpoint is provided as an alternative for uploading files separately.
    
    The file will be stored at: `app/storage/<year>/<month>/<day>/<br_regn>/applicant_photo_*.jpg`
    
    **Recommended size**: 3cm x 2.5cm  
    **Supported formats**: JPG, JPEG, PNG, GIF, BMP, WEBP  
    **Max file size**: 10 MB
    """
    try:
        updated_card = await bhikku_id_card_service.upload_applicant_photo(db, bic_id, file)
        
        return BhikkuIDCardManageResponse(
            status="success",
            message="Applicant photo uploaded successfully",
            data=BhikkuIDCardResponse.from_orm(updated_card)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload photo: {str(e)}"
        )


@router.get("/{bic_id}", response_model=BhikkuIDCardManageResponse)
def get_bhikku_id_card_by_id(
    bic_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Get a single Bhikku ID Card by ID.
    
    Alternative to using `/manage` with READ_ONE action.
    """
    try:
        card = bhikku_id_card_service.get_bhikku_id_card_by_id(db, bic_id)
        
        return BhikkuIDCardManageResponse(
            status="success",
            message="Bhikku ID Card retrieved successfully",
            data=BhikkuIDCardResponse.from_orm(card)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/by-regn/{br_regn}", response_model=BhikkuIDCardManageResponse)
def get_bhikku_id_card_by_regn(
    br_regn: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Get a Bhikku ID Card by Bhikku registration number.
    
    Alternative to using `/manage` with READ_ONE action.
    """
    try:
        card = bhikku_id_card_service.get_bhikku_id_card_by_br_regn(db, br_regn)
        
        return BhikkuIDCardManageResponse(
            status="success",
            message="Bhikku ID Card retrieved successfully",
            data=BhikkuIDCardResponse.from_orm(card)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/workflow", response_model=BhikkuIDCardWorkflowResponse)
def update_bhikku_id_card_workflow(
    request: BhikkuIDCardWorkflowRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Update workflow status of a Bhikku ID Card record.
    
    Workflow Actions:
    - APPROVE: Approve pending ID card application (PENDING → APPROVED)
    - REJECT: Reject pending ID card application (PENDING → REJECTED, requires rejection_reason)
    - MARK_PRINTING_COMPLETE: Mark ID card as printed (APPROVED → PRINTING_COMPLETE)
    - MARK_COMPLETED: Mark workflow as completed (PRINTING_COMPLETE → COMPLETED)
    
    Workflow Flow:
    1. Create ID card → PENDING
    2. Approve/Reject → APPROVED or REJECTED
    3. Mark printing complete → PRINTING_COMPLETE
    4. Mark completed → COMPLETED
    
    Requires authentication.
    """
    username = current_user.ua_username if current_user else None
    action = request.action

    try:
        if action == BhikkuIDCardWorkflowActionType.APPROVE:
            updated_card = bhikku_id_card_service.approve_bhikku_id_card(
                db,
                bic_id=request.bic_id,
                bic_form_no=request.bic_form_no,
                actor_id=username
            )
            message = "Bhikku ID Card approved successfully."

        elif action == BhikkuIDCardWorkflowActionType.REJECT:
            if not request.rejection_reason:
                raise HTTPException(
                    status_code=400,
                    detail="Rejection reason is required when rejecting"
                )
            updated_card = bhikku_id_card_service.reject_bhikku_id_card(
                db,
                bic_id=request.bic_id,
                bic_form_no=request.bic_form_no,
                actor_id=username,
                rejection_reason=request.rejection_reason
            )
            message = "Bhikku ID Card rejected successfully."

        elif action == BhikkuIDCardWorkflowActionType.MARK_PRINTING_COMPLETE:
            updated_card = bhikku_id_card_service.mark_printing_complete(
                db,
                bic_id=request.bic_id,
                bic_form_no=request.bic_form_no,
                actor_id=username
            )
            message = "Bhikku ID Card marked as printing complete successfully."

        elif action == BhikkuIDCardWorkflowActionType.MARK_COMPLETED:
            updated_card = bhikku_id_card_service.mark_completed(
                db,
                bic_id=request.bic_id,
                bic_form_no=request.bic_form_no,
                actor_id=username
            )
            message = "Bhikku ID Card marked as completed successfully."

        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid workflow action"
            )

    except ValueError as exc:
        error_msg = str(exc)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg)
        raise HTTPException(status_code=400, detail=error_msg)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(exc)}")

    return BhikkuIDCardWorkflowResponse(
        status="success",
        message=message,
        data=BhikkuIDCardResponse.from_orm(updated_card)
    )
