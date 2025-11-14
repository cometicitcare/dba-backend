from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.api.auth_dependencies import has_permission, has_any_permission
from app.schemas.group import GroupCreate, GroupUpdate, GroupOut, GroupListResponse
from app.models.group import Group
from app.services.group_service import group_service
from app.utils.http_exceptions import validation_error

router = APIRouter(tags=["Groups"])

# Create a new group
@router.post("/create", response_model=GroupOut, dependencies=[has_permission("system:manage_roles")])
def create_group(
    group: GroupCreate,
    db: Session = Depends(get_db),
):
    try:
        created_group = group_service.create_group(db, group)
        return created_group
    except ValueError as exc:
        raise validation_error([(None, str(exc))]) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

# Update an existing group
@router.put("/update/{group_id}", response_model=GroupOut, dependencies=[has_permission("system:manage_roles")])
def update_group(
    group_id: int,
    group: GroupUpdate,
    db: Session = Depends(get_db),
):
    try:
        updated_group = group_service.update_group(db, group_id, group)
        return updated_group
    except ValueError as exc:
        raise validation_error([(None, str(exc))]) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

# Get a specific group by its ID
@router.get("/get/{group_id}", response_model=GroupOut, dependencies=[has_permission("system:manage_roles")])
def get_group(
    group_id: int,
    db: Session = Depends(get_db),
):
    group = group_service.get_group_by_id(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group

# Get a list of groups with pagination
@router.get("/list", response_model=GroupListResponse, dependencies=[has_permission("system:manage_roles")])
def list_groups(
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    groups = group_service.get_groups(db, page=page, limit=limit)
    total = group_service.count_groups(db)
    return GroupListResponse(
        status="success",
        message="Groups retrieved successfully.",
        data=groups,
        totalRecords=total,
        page=page,
        limit=limit,
    )

# Delete a group
@router.delete("/delete/{group_id}", response_model=GroupOut, dependencies=[has_permission("system:manage_roles")])
def delete_group(
    group_id: int,
    db: Session = Depends(get_db),
):
    try:
        deleted_group = group_service.delete_group(db, group_id)
        return deleted_group
    except ValueError as exc:
        raise validation_error([(None, str(exc))]) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc