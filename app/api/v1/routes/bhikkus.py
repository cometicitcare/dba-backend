# app/api/v1/routes/bhikkus.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.auth_middleware import get_current_user
from app.models.user import UserAccount
from app.schemas import bhikku as schemas
from app.repositories import bhikku_repo

router = APIRouter()

@router.post("/manage", response_model=schemas.BhikkuManagementResponse)
def manage_bhikku_records(
    request: schemas.BhikkuManagementRequest, 
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """
    Unified endpoint for all Bhikku CRUD operations.
    Requires authentication via http-only cookies (access_token).
    """
    action = request.action
    payload = request.payload

    # Get user identifier for audit trail
    user_id = current_user.ua_user_id

    if action == schemas.CRUDAction.CREATE:
        if not payload.data or not isinstance(payload.data, schemas.BhikkuCreate):
            raise HTTPException(status_code=400, detail="Invalid data for CREATE action")
        
        # Check if br_regn was manually provided (optional check)
        if payload.data.br_regn:
            db_bhikku_existing = bhikku_repo.get_by_regn(db, br_regn=payload.data.br_regn)
            if db_bhikku_existing:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Registration number '{payload.data.br_regn}' already exists."
                )
        
        # Set the created_by field to current user ID (foreign key constraint)
        payload.data.br_created_by = user_id
        
        # br_regn will be auto-generated in repository if not provided
        created_bhikku = bhikku_repo.create(db=db, bhikku=payload.data)
        return {
            "status": "success", 
            "message": f"Bhikku created successfully with registration number: {created_bhikku.br_regn}", 
            "data": created_bhikku
        }

    elif action == schemas.CRUDAction.READ_ONE:
        if not payload.br_regn:
            raise HTTPException(status_code=400, detail="br_regn is required for READ_ONE action")
        
        db_bhikku = bhikku_repo.get_by_regn(db, br_regn=payload.br_regn)
        if db_bhikku is None:
            raise HTTPException(status_code=404, detail="Bhikku not found")
        return {"status": "success", "message": "Bhikku retrieved successfully.", "data": db_bhikku}

    elif action == schemas.CRUDAction.READ_ALL:
        # Calculate pagination parameters
        limit = payload.limit if payload.limit > 0 else 10
        
        # Prioritize page-based pagination, fall back to skip if page not provided
        if payload.page and payload.page > 0:
            # Page-based pagination
            page = payload.page
            skip = (page - 1) * limit
        else:
            # Direct skip-based pagination
            skip = payload.skip if payload.skip >= 0 else 0
            page = (skip // limit) + 1 if limit > 0 else 1
        
        # Get search key (empty string if not provided)
        search_key = payload.search_key if payload.search_key else ""
        
        # Get paginated data and total count with search filter
        bhikkus = bhikku_repo.get_all(db, skip=skip, limit=limit, search_key=search_key)
        total_records = bhikku_repo.get_total_count(db, search_key=search_key)
        
        return {
            "status": "success",
            "message": "Bhikkus retrieved successfully." if not search_key else f"Bhikkus matching '{search_key}' retrieved successfully.",
            "data": bhikkus,
            "totalRecords": total_records,
            "page": page,
            "limit": limit
        }

    elif action == schemas.CRUDAction.UPDATE:
        if not payload.br_regn or not payload.data or not isinstance(payload.data, schemas.BhikkuUpdate):
            raise HTTPException(status_code=400, detail="br_regn and data are required for UPDATE action")

        # Set the updated_by field to current user ID
        payload.data.br_updated_by = user_id
        updated_bhikku = bhikku_repo.update(db=db, br_regn=payload.br_regn, bhikku_update=payload.data)
        if updated_bhikku is None:
            raise HTTPException(status_code=404, detail="Bhikku not found")
        return {"status": "success", "message": "Bhikku updated successfully.", "data": updated_bhikku}

    elif action == schemas.CRUDAction.DELETE:
        if not payload.br_regn:
            raise HTTPException(status_code=400, detail="br_regn is required for DELETE action")
        
        deleted_bhikku = bhikku_repo.delete(db=db, br_regn=payload.br_regn)
        if deleted_bhikku is None:
            raise HTTPException(status_code=404, detail="Bhikku not found")
        return {"status": "success", "message": "Bhikku deleted successfully.", "data": None}

    else:
        raise HTTPException(status_code=400, detail="Invalid action specified")