"""
RBAC Administration Endpoints
Manage user roles, groups, and permission overrides
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_any_permission
from app.api.deps import get_db
from app.models.user import UserAccount
from app.services.rbac_service import rbac_service
from app.schemas.rbac_admin import (
    UserRoleAssignRequest,
    UserRoleRevokeRequest,
    UserGroupAssignRequest,
    UserGroupRemoveRequest,
    UserPermissionOverrideRequest,
    UserPermissionRemoveRequest,
    RBACManagementResponse,
    UserListResponse,
)

router = APIRouter(prefix="/rbac")  # Tags defined in router.py


# ==================== User Role Management ====================

@router.post("/user/assign-role", response_model=RBACManagementResponse, dependencies=[has_any_permission("system:manage_users", "system:manage_roles")])
def assign_role_to_user(
    request: UserRoleAssignRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Assign a role to a user.
    Requires: system:manage_users OR system:manage_roles
    """
    is_new, data = rbac_service.assign_role_to_user(
        db=db,
        user_id=request.user_id,
        role_id=request.role_id,
        expires_days=request.expires_days,
        is_active=request.is_active,
        actor_id=current_user.ua_user_id
    )
    
    action = "assigned" if is_new else "updated"
    return RBACManagementResponse(
        success=True,
        message=f"Role '{request.role_id}' {action} to user '{data['username']}'",
        data=data
    )


@router.post("/user/revoke-role", response_model=RBACManagementResponse, dependencies=[has_any_permission("system:manage_users", "system:manage_roles")])
def revoke_role_from_user(
    request: UserRoleRevokeRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Revoke (deactivate) a role from a user.
    Requires: system:manage_users OR system:manage_roles
    """
    data = rbac_service.revoke_role_from_user(
        db=db,
        user_id=request.user_id,
        role_id=request.role_id,
        actor_id=current_user.ua_user_id
    )
    
    return RBACManagementResponse(
        success=True,
        message=f"Role '{request.role_id}' revoked from user '{data['username']}'",
        data=data
    )


# ==================== User Group Management ====================

@router.post("/user/assign-group", response_model=RBACManagementResponse, dependencies=[has_any_permission("system:manage_users", "system:manage_groups")])
def assign_group_to_user(
    request: UserGroupAssignRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Add a user to a group (department).
    Requires: system:manage_users OR system:manage_groups
    """
    is_new, data = rbac_service.assign_group_to_user(
        db=db,
        user_id=request.user_id,
        group_id=request.group_id,
        actor_id=current_user.ua_user_id
    )
    
    if data.get("already_member"):
        message = f"User '{data['username']}' already in group '{data['group_name']}'"
    elif data.get("reactivated"):
        message = f"User '{data['username']}' reactivated in group '{data['group_name']}'"
    else:
        message = f"User '{data['username']}' added to group '{data['group_name']}'"
    
    return RBACManagementResponse(success=True, message=message, data=data)


@router.post("/user/remove-group", response_model=RBACManagementResponse, dependencies=[has_any_permission("system:manage_users", "system:manage_groups")])
def remove_group_from_user(
    request: UserGroupRemoveRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Remove a user from a group.
    Requires: system:manage_users OR system:manage_groups
    """
    data = rbac_service.remove_group_from_user(
        db=db,
        user_id=request.user_id,
        group_id=request.group_id,
        actor_id=current_user.ua_user_id
    )
    
    return RBACManagementResponse(
        success=True,
        message=f"User '{data['username']}' removed from group '{data['group_name']}'",
        data=data
    )


# ==================== User Permission Overrides ====================

@router.post("/user/override-permission", response_model=RBACManagementResponse, dependencies=[has_any_permission("system:manage_users", "system:manage_permissions")])
def override_user_permission(
    request: UserPermissionOverrideRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Grant or deny a specific permission to a user (overrides role permissions).
    Requires: system:manage_users OR system:manage_permissions
    """
    is_new, data = rbac_service.override_user_permission(
        db=db,
        user_id=request.user_id,
        permission_id=request.permission_id,
        granted=request.granted,
        expires_days=request.expires_days,
        is_active=request.is_active,
        actor_id=current_user.ua_user_id
    )
    
    action = "granted to" if request.granted else "denied for"
    return RBACManagementResponse(
        success=True,
        message=f"Permission '{data['permission_name']}' {action} user '{data['username']}'",
        data=data
    )


@router.post("/user/remove-permission-override", response_model=RBACManagementResponse, dependencies=[has_any_permission("system:manage_users", "system:manage_permissions")])
def remove_permission_override(
    request: UserPermissionRemoveRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Remove a permission override (user will inherit permissions from roles again).
    Requires: system:manage_users OR system:manage_permissions
    """
    data = rbac_service.remove_permission_override(
        db=db,
        user_id=request.user_id,
        permission_id=request.permission_id,
        actor_id=current_user.ua_user_id
    )
    
    return RBACManagementResponse(
        success=True,
        message=f"Permission override removed for user '{data['username']}'",
        data=data
    )


# ==================== User RBAC Context Retrieval ====================

@router.get("/user/{user_id}/context", dependencies=[has_any_permission("system:manage_users", "system:view_users")])
def get_user_rbac_context(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Get complete RBAC context for a specific user (roles, groups, permissions, overrides).
    Requires: system:manage_users OR system:view_users
    """
    return rbac_service.get_user_rbac_context(db=db, user_id=user_id)


@router.get("/users/list", response_model=UserListResponse, dependencies=[has_any_permission("system:manage_users", "system:view_users")])
def list_all_users_with_rbac(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50,
):
    """
    List all users with their RBAC summary.
    Requires: system:manage_users OR system:view_users
    """
    total, user_list = rbac_service.list_users_with_rbac(db=db, skip=skip, limit=limit)
    
    return UserListResponse(
        success=True,
        total=total,
        page=(skip // limit) + 1,
        limit=limit,
        data=user_list
    )
