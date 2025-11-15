from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.api.auth_dependencies import has_permission, has_any_permission
from app.schemas.user_group import UserGroupCreate, UserGroupUpdate, UserGroupOut
from app.models.user_group import UserGroup
from app.services.user_group_service import user_group_service
from app.utils.http_exceptions import validation_error

router = APIRouter()  # Tags defined in router.py

# Add a user to a group
@router.post("/add", response_model=UserGroupOut, dependencies=[has_permission("system:manage_users")])
def add_user_to_group(
    user_group: UserGroupCreate,
    db: Session = Depends(get_db),
):
    try:
        added_user_group = user_group_service.add_user_to_group(db, user_group)
        return added_user_group
    except ValueError as exc:
        raise validation_error([(None, str(exc))]) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

# Update user-group relationship (e.g., change the group)
@router.put("/update/{user_id}/{group_id}", response_model=UserGroupOut, dependencies=[has_permission("system:manage_users")])
def update_user_group(
    user_id: str,
    group_id: int,
    user_group: UserGroupUpdate,
    db: Session = Depends(get_db),
):
    try:
        updated_user_group = user_group_service.update_user_group(db, user_id, group_id, user_group)
        return updated_user_group
    except ValueError as exc:
        raise validation_error([(None, str(exc))]) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

# Remove a user from a group
@router.delete("/remove/{user_id}/{group_id}", response_model=UserGroupOut, dependencies=[has_permission("system:manage_users")])
def remove_user_from_group(
    user_id: str,
    group_id: int,
    db: Session = Depends(get_db),
):
    try:
        removed_user_group = user_group_service.remove_user_from_group(db, user_id, group_id)
        return removed_user_group
    except ValueError as exc:
        raise validation_error([(None, str(exc))]) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc