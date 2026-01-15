# app/api/v1/routes/sasanarakshaka.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.api.deps import get_db
from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission
from app.models.user import UserAccount
from app.schemas import sasanarakshaka as schemas
from app.services.sasanarakshaka_service import sasanarakshaka_service
from app.utils.http_exceptions import validation_error

router = APIRouter()


@router.post(
    "",
    response_model=schemas.SasanarakshakaBalaMandalayaSingleResponse,
    status_code=201,
    dependencies=[has_permission("sasanarakshaka:create")],
)
def create_sasanarakshaka(
    payload: schemas.SasanarakshakaBalaMandalayaCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Create a new Sasanarakshaka Bala Mandalaya record.
    Requires: sasanarakshaka:create permission
    """
    try:
        record = sasanarakshaka_service.create_sasanarakshaka(
            db, payload=payload, actor_id=current_user.ua_userid
        )
        return {
            "status": "success",
            "message": "Sasanarakshaka Bala Mandalaya created successfully.",
            "data": record,
        }
    except ValueError as e:
        raise validation_error(str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "",
    response_model=schemas.SasanarakshakaBalaMandalayaListResponse,
    dependencies=[has_permission("sasanarakshaka:read")],
)
def list_sasanarakshaka(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=1000, description="Items per page"),
    search_key: Optional[str] = Query(None, description="Search key for filtering"),
    sr_dvcd: Optional[str] = Query(None, description="Filter by divisional secretariat code"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Get paginated list of Sasanarakshaka Bala Mandalaya records with optional search and filters.
    Requires: sasanarakshaka:read permission
    """
    skip = (page - 1) * limit
    records, total = sasanarakshaka_service.get_all_sasanarakshaka(
        db, skip=skip, limit=limit, search_key=search_key, sr_dvcd=sr_dvcd
    )
    return {
        "status": "success",
        "message": "Sasanarakshaka Bala Mandalaya list retrieved successfully.",
        "data": records,
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.get(
    "/{sr_id}",
    response_model=schemas.SasanarakshakaBalaMandalayaSingleResponse,
    dependencies=[has_permission("sasanarakshaka:read")],
)
def get_sasanarakshaka_by_id(
    sr_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Get a single Sasanarakshaka Bala Mandalaya record by ID.
    Requires: sasanarakshaka:read permission
    """
    record = sasanarakshaka_service.get_sasanarakshaka_by_id(db, sr_id)
    if not record:
        raise HTTPException(
            status_code=404,
            detail=f"Sasanarakshaka Bala Mandalaya with ID {sr_id} not found",
        )
    return {
        "status": "success",
        "message": "Sasanarakshaka Bala Mandalaya retrieved successfully.",
        "data": record,
    }


@router.get(
    "/code/{sr_ssbmcode}",
    response_model=schemas.SasanarakshakaBalaMandalayaSingleResponse,
    dependencies=[has_permission("sasanarakshaka:read")],
)
def get_sasanarakshaka_by_code(
    sr_ssbmcode: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Get a single Sasanarakshaka Bala Mandalaya record by code.
    Requires: sasanarakshaka:read permission
    """
    record = sasanarakshaka_service.get_sasanarakshaka_by_code(db, sr_ssbmcode)
    if not record:
        raise HTTPException(
            status_code=404,
            detail=f"Sasanarakshaka Bala Mandalaya with code {sr_ssbmcode} not found",
        )
    return {
        "status": "success",
        "message": "Sasanarakshaka Bala Mandalaya retrieved successfully.",
        "data": record,
    }


@router.put(
    "/{sr_id}",
    response_model=schemas.SasanarakshakaBalaMandalayaSingleResponse,
    dependencies=[has_permission("sasanarakshaka:update")],
)
def update_sasanarakshaka(
    sr_id: int,
    payload: schemas.SasanarakshakaBalaMandalayaUpdate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Update an existing Sasanarakshaka Bala Mandalaya record.
    Requires: sasanarakshaka:update permission
    """
    try:
        record = sasanarakshaka_service.update_sasanarakshaka(
            db, sr_id=sr_id, payload=payload, actor_id=current_user.ua_userid
        )
        return {
            "status": "success",
            "message": "Sasanarakshaka Bala Mandalaya updated successfully.",
            "data": record,
        }
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise validation_error(str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete(
    "/{sr_id}",
    response_model=schemas.SasanarakshakaBalaMandalayaDeleteResponse,
    dependencies=[has_permission("sasanarakshaka:delete")],
)
def delete_sasanarakshaka(
    sr_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Soft delete a Sasanarakshaka Bala Mandalaya record.
    Requires: sasanarakshaka:delete permission
    """
    try:
        record = sasanarakshaka_service.delete_sasanarakshaka(
            db, sr_id=sr_id, actor_id=current_user.ua_userid
        )
        return {
            "status": "success",
            "message": "Sasanarakshaka Bala Mandalaya deleted successfully.",
            "data": {"sr_id": sr_id},
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
