# app/api/v1/routes/bhikkus.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas import bhikku as schemas
from app.repositories import bhikku_repo

router = APIRouter()

@router.post("/manage", response_model=schemas.BhikkuManagementResponse)
def manage_bhikku_records(
    request: schemas.BhikkuManagementRequest, 
    db: Session = Depends(get_db)
):
    action = request.action
    payload = request.payload

    if action == schemas.CRUDAction.CREATE:
        if not payload.data or not isinstance(payload.data, schemas.BhikkuCreate):
            raise HTTPException(status_code=400, detail="Invalid data for CREATE action")
        
        db_bhikku_existing = bhikku_repo.get_by_regn(db, br_regn=payload.data.br_regn)
        if db_bhikku_existing:
            raise HTTPException(status_code=400, detail=f"Registration number '{payload.data.br_regn}' already exists.")
        
        created_bhikku = bhikku_repo.create(db=db, bhikku=payload.data)
        return {"status": "success", "message": "Bhikku created successfully.", "data": created_bhikku}

    elif action == schemas.CRUDAction.READ_ONE:
        if not payload.br_regn:
            raise HTTPException(status_code=400, detail="br_regn is required for READ_ONE action")
        
        db_bhikku = bhikku_repo.get_by_regn(db, br_regn=payload.br_regn)
        if db_bhikku is None:
            raise HTTPException(status_code=404, detail="Bhikku not found")
        return {"status": "success", "message": "Bhikku retrieved successfully.", "data": db_bhikku}

    elif action == schemas.CRUDAction.READ_ALL:
        bhikkus = bhikku_repo.get_all(db, skip=payload.skip, limit=payload.limit)
        return {"status": "success", "message": "Bhikkus retrieved successfully.", "data": bhikkus}

    elif action == schemas.CRUDAction.UPDATE:
        if not payload.br_regn or not payload.data or not isinstance(payload.data, schemas.BhikkuUpdate):
            raise HTTPException(status_code=400, detail="br_regn and data are required for UPDATE action")

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