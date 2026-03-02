from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.api.auth_dependencies import has_permission, has_any_permission
from app.schemas.permission import PermissionCreate, PermissionUpdate, PermissionOut
from app.models.permission import Permission
from app.services.permission_service import permission_service
from app.utils.http_exceptions import validation_error

router = APIRouter()  # Tags defined in router.py

# Create a new permission
@router.post("/create", response_model=PermissionOut, dependencies=[has_permission("system:manage_permissions")])
def create_permission(
    permission: PermissionCreate,
    db: Session = Depends(get_db),
):
    try:
        created_permission = permission_service.create_permission(db, permission)
        return created_permission
    except ValueError as exc:
        raise validation_error([(None, str(exc))]) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

# Update an existing permission
@router.put("/update/{permission_id}", response_model=PermissionOut, dependencies=[has_permission("system:manage_permissions")])
def update_permission(
    permission_id: str,
    permission: PermissionUpdate,
    db: Session = Depends(get_db),
):
    try:
        updated_permission = permission_service.update_permission(db, permission_id, permission)
        return updated_permission
    except ValueError as exc:
        raise validation_error([(None, str(exc))]) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

# Get a specific permission by ID
@router.get("/get/{permission_id}", response_model=PermissionOut, dependencies=[has_permission("system:manage_permissions")])
def get_permission(
    permission_id: str,
    db: Session = Depends(get_db),
):
    permission = permission_service.get_permission_by_id(db, permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return permission

# Delete a permission
@router.delete("/delete/{permission_id}", response_model=PermissionOut, dependencies=[has_permission("system:manage_permissions")])
def delete_permission(
    permission_id: str,
    db: Session = Depends(get_db),
):
    try:
        deleted_permission = permission_service.delete_permission(db, permission_id)
        return deleted_permission
    except ValueError as exc:
        raise validation_error([(None, str(exc))]) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc