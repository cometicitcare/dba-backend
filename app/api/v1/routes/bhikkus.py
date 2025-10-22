# app/api/v1/routes/bhikkus.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.auth_middleware import get_current_user
from app.models.user import UserAccount
from app.schemas import bhikku as schemas
from app.repositories import bhikku_repo
from app.utils.http_exceptions import validation_error

router = APIRouter()

@router.post("/manage", response_model=schemas.BhikkuManagementResponse)
def manage_bhikku_records(
    request: schemas.BhikkuManagementRequest, 
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """
    Unified endpoint for all Bhikku CRUD operations.
    Requires authentication via session ID in Authorization header.
    """
    action = request.action
    payload = request.payload

    # Get user identifier for audit trail
    user_id = current_user.ua_user_id

    if action == schemas.CRUDAction.CREATE:
        if not payload.data or not isinstance(payload.data, schemas.BhikkuCreate):
            raise validation_error(
                [("payload.data", "Invalid data for CREATE action")]
            )
        
        db_bhikku_existing = bhikku_repo.get_by_regn(db, br_regn=payload.data.br_regn)
        if db_bhikku_existing:
            raise validation_error(
                [
                    (
                        "payload.data.br_regn",
                        f"Registration number '{payload.data.br_regn}' already exists.",
                    )
                ]
            )
        
        # Set the created_by field to current user ID (foreign key constraint)
        payload.data.br_created_by = user_id
        created_bhikku = bhikku_repo.create(db=db, bhikku=payload.data)
        return {"status": "success", "message": "Bhikku created successfully.", "data": created_bhikku}

    elif action == schemas.CRUDAction.READ_ONE:
        if not payload.br_regn:
            raise validation_error(
                [("payload.br_regn", "br_regn is required for READ_ONE action")]
            )
        
        db_bhikku = bhikku_repo.get_by_regn(db, br_regn=payload.br_regn)
        if db_bhikku is None:
            raise HTTPException(status_code=404, detail="Bhikku not found")
        return {"status": "success", "message": "Bhikku retrieved successfully.", "data": db_bhikku}

    elif action == schemas.CRUDAction.READ_ALL:
        # Handle pagination - use page-based or skip-based
        page = payload.page if payload.page is not None else 1
        limit = payload.limit
        search_key = payload.search_key.strip() if payload.search_key else None
        
        # If search_key is empty string, treat as None
        if search_key == "":
            search_key = None
        
        # Calculate skip based on page if page is provided, otherwise use skip directly
        skip = payload.skip if payload.page is None else (page - 1) * limit
        skip = max(0, skip)
        
        # Get paginated bhikku records with search
        bhikkus = bhikku_repo.get_all(db, skip=skip, limit=limit, search_key=search_key)
        
        # Get total count for pagination
        total_count = bhikku_repo.get_total_count(db, search_key=search_key)
        
        return {
            "status": "success",
            "message": "Bhikkus retrieved successfully.",
            "data": bhikkus,
            "totalRecords": total_count,
            "page": page,
            "limit": limit
        }

    elif action == schemas.CRUDAction.UPDATE:
        update_errors = []
        if not payload.br_regn:
            update_errors.append(
                ("payload.br_regn", "br_regn is required for UPDATE action")
            )
        if not payload.data:
            update_errors.append(("payload.data", "data is required for UPDATE action"))
        elif not isinstance(payload.data, schemas.BhikkuUpdate):
            update_errors.append(
                ("payload.data", "Invalid data payload for UPDATE action")
            )
        if update_errors:
            raise validation_error(update_errors)

        # Set the updated_by field to current user ID
        payload.data.br_updated_by = user_id
        updated_bhikku = bhikku_repo.update(db=db, br_regn=payload.br_regn, bhikku_update=payload.data)
        if updated_bhikku is None:
            raise HTTPException(status_code=404, detail="Bhikku not found")
        return {"status": "success", "message": "Bhikku updated successfully.", "data": updated_bhikku}

    elif action == schemas.CRUDAction.DELETE:
        if not payload.br_regn:
            raise validation_error(
                [("payload.br_regn", "br_regn is required for DELETE action")]
            )
        
        deleted_bhikku = bhikku_repo.delete(db=db, br_regn=payload.br_regn)
        if deleted_bhikku is None:
            raise HTTPException(status_code=404, detail="Bhikku not found")
        return {"status": "success", "message": "Bhikku deleted successfully.", "data": None}

    else:
        raise validation_error([("action", "Invalid action specified")])
