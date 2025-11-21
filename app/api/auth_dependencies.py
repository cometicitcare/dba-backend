"""
Authorization dependencies for FastAPI routes.
Provides permission checking, role checking, and group membership verification.
"""
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session, Query
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime

from app.api.deps import get_db
from app.api.auth_middleware import get_current_user
from app.models.user import UserAccount
from app.models.user_roles import UserRole
from app.models.user_group import UserGroup
from app.models.permissions import Permission
from app.models.role_permissions import RolePermission
from app.models.user_permission import UserPermission
from app.models.roles import Role
from app.models.district_branch import DistrictBranch


def get_user_permissions(db: Session, user: UserAccount) -> List[str]:
    """
    Get all effective permissions for a user.
    Combines:
    1. Permissions from active, non-expired roles
    2. User-specific permission overrides
    """
    current_time = datetime.utcnow()
    permissions_set = set()
    
    # Get permissions from user's roles
    user_roles = db.query(UserRole).filter(
        and_(
            UserRole.ur_user_id == user.ua_user_id,
            UserRole.ur_is_active == True,
            UserRole.ur_expires_date.is_(None) | (UserRole.ur_expires_date > current_time)
        )
    ).all()
    
    for user_role in user_roles:
        # Get permissions for this role
        role_permissions = db.query(Permission).join(
            RolePermission,
            RolePermission.rp_permission_id == Permission.pe_permission_id
        ).filter(
            and_(
                RolePermission.rp_role_id == user_role.ur_role_id,
                RolePermission.rp_granted == True
            )
        ).all()
        
        for perm in role_permissions:
            permissions_set.add(perm.pe_name)
    
    # Apply user-specific permission overrides
    user_permissions = db.query(UserPermission).join(
        Permission,
        Permission.pe_permission_id == UserPermission.up_permission_id
    ).filter(
        and_(
            UserPermission.up_user_id == user.ua_user_id,
            UserPermission.up_is_active == True,
            UserPermission.up_expires_date.is_(None) | (UserPermission.up_expires_date > current_time)
        )
    ).all()
    
    for user_perm in user_permissions:
        perm_name = db.query(Permission.pe_name).filter(
            Permission.pe_permission_id == user_perm.up_permission_id
        ).scalar()
        
        if user_perm.up_granted:
            # Grant permission (add it)
            permissions_set.add(perm_name)
        else:
            # Deny permission (remove it)
            permissions_set.discard(perm_name)
    
    return list(permissions_set)


def is_super_admin(db: Session, user: UserAccount) -> bool:
    """Check if user has SUPER_ADMIN role."""
    current_time = datetime.utcnow()
    
    super_admin_role = db.query(UserRole).join(
        Role,
        Role.ro_role_id == UserRole.ur_role_id
    ).filter(
        and_(
            UserRole.ur_user_id == user.ua_user_id,
            Role.ro_level == "SUPER_ADMIN",
            UserRole.ur_is_active == True,
            UserRole.ur_expires_date.is_(None) | (UserRole.ur_expires_date > current_time)
        )
    ).first()
    
    return super_admin_role is not None


def has_permission(permission: str):
    """
    Dependency to check if current user has a specific permission.
    Usage:
        @router.delete("/bhikku/{id}")
        def delete_bhikku(
            id: str,
            current_user: UserAccount = Depends(get_current_user),
            _: None = Depends(has_permission("bhikku:delete"))
        ):
            ...
    """
    def permission_checker(
        current_user: UserAccount = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        # Super admins bypass all permission checks
        if is_super_admin(db, current_user):
            return
        
        # Get user's permissions
        user_perms = get_user_permissions(db, current_user)
        
        if permission not in user_perms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required permission: '{permission}'. Please contact your administrator if you need access to this resource."
            )
    
    return Depends(permission_checker)


def has_any_permission(*permissions: str):
    """
    Dependency to check if current user has AT LEAST ONE of the specified permissions.
    Usage:
        @router.get("/bhikku")
        def list_bhikku(
            current_user: UserAccount = Depends(get_current_user),
            _: None = Depends(has_any_permission("bhikku:read", "bhikku:create"))
        ):
            ...
    """
    def permission_checker(
        current_user: UserAccount = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        # Super admins bypass all permission checks
        if is_super_admin(db, current_user):
            return
        
        # Get user's permissions
        user_perms = get_user_permissions(db, current_user)
        
        # Check if user has any of the required permissions
        if not any(perm in user_perms for perm in permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required at least one of: {', '.join(permissions)}. Please contact your administrator."
            )
    
    return Depends(permission_checker)


def has_role(role_id: str):
    """
    Dependency to check if current user has a specific role.
    Usage:
        @router.get("/admin/dashboard")
        def admin_dashboard(
            current_user: UserAccount = Depends(get_current_user),
            _: None = Depends(has_role("SUPER_ADMIN"))
        ):
            ...
    """
    def role_checker(
        current_user: UserAccount = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        current_time = datetime.utcnow()
        
        user_role = db.query(UserRole).filter(
            and_(
                UserRole.ur_user_id == current_user.ua_user_id,
                UserRole.ur_role_id == role_id,
                UserRole.ur_is_active == True,
                UserRole.ur_expires_date.is_(None) | (UserRole.ur_expires_date > current_time)
            )
        ).first()
        
        if not user_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: '{role_id}'. Please contact your administrator."
            )
    
    return Depends(role_checker)


def in_group(group_name: str):
    """
    Dependency to check if current user belongs to a specific group/department.
    Usage:
        @router.get("/bhikku/internal")
        def internal_bhikku_data(
            current_user: UserAccount = Depends(get_current_user),
            _: None = Depends(in_group("Bhikku Management"))
        ):
            ...
    """
    def group_checker(
        current_user: UserAccount = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        # Super admins bypass all checks
        if is_super_admin(db, current_user):
            return
        
        current_time = datetime.utcnow()
        
        from app.models.group import Group
        user_group = db.query(UserGroup).join(
            Group,
            Group.group_id == UserGroup.group_id
        ).filter(
            and_(
                UserGroup.user_id == current_user.ua_user_id,
                Group.group_name == group_name,
                UserGroup.is_active == True,
                UserGroup.expires_date.is_(None) | (UserGroup.expires_date > current_time)
            )
        ).first()
        
        if not user_group:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required department: '{group_name}'. Please contact your administrator."
            )
    
    return Depends(group_checker)


def get_user_access_context(db: Session, user: UserAccount) -> dict:
    """
    Get complete access context for a user.
    Used in login endpoint to return full user capabilities to frontend.
    """
    current_time = datetime.utcnow()
    
    # Get user's active roles
    user_roles = db.query(UserRole, Role).join(
        Role,
        Role.ro_role_id == UserRole.ur_role_id
    ).filter(
        and_(
            UserRole.ur_user_id == user.ua_user_id,
            UserRole.ur_is_active == True,
            UserRole.ur_expires_date.is_(None) | (UserRole.ur_expires_date > current_time)
        )
    ).all()
    
    roles_list = []
    for user_role, role in user_roles:
        # Get department info
        from app.models.group import Group
        department = None
        if role.ro_department_id:
            dept = db.query(Group).filter(Group.group_id == role.ro_department_id).first()
            if dept:
                department = dept.group_name
        
        # Calculate days until expiry
        days_until_expiry = None
        if user_role.ur_expires_date:
            delta = user_role.ur_expires_date - current_time
            days_until_expiry = delta.days
        
        roles_list.append({
            "ro_role_id": role.ro_role_id,
            "ro_role_name": role.ro_role_name,
            "ro_level": role.ro_level,
            "department": department,
            "assigned_date": user_role.ur_assigned_date.isoformat() if user_role.ur_assigned_date else None,
            "expires_date": user_role.ur_expires_date.isoformat() if user_role.ur_expires_date else None,
            "days_until_expiry": days_until_expiry
        })
    
    # Get user's active groups
    from app.models.group import Group
    user_groups = db.query(UserGroup, Group).join(
        Group,
        Group.group_id == UserGroup.group_id
    ).filter(
        and_(
            UserGroup.user_id == user.ua_user_id,
            UserGroup.is_active == True,
            UserGroup.expires_date.is_(None) | (UserGroup.expires_date > current_time)
        )
    ).all()
    
    groups_list = []
    for user_group, group in user_groups:
        groups_list.append({
            "group_id": group.group_id,
            "group_name": group.group_name,
            "group_type": group.group_type
        })
    
    # Get effective permissions
    permissions = get_user_permissions(db, user)
    
    # Build permission map (resource -> actions)
    permission_map = {}
    for perm in permissions:
        if ":" in perm:
            resource, action = perm.split(":", 1)
            if resource not in permission_map:
                permission_map[resource] = []
            permission_map[resource].append(action)
    
    # Check if super admin
    super_admin = is_super_admin(db, user)
    
    # Check if admin (any ADMIN level role)
    is_admin = any(role["ro_level"] == "ADMIN" for role in roles_list)
    
    # Check if can manage users (has system:manage_users permission)
    can_manage_users = "system:manage_users" in permissions or super_admin
    
    # Get list of departments user has access to
    departments = list(set(role["department"] for role in roles_list if role["department"]))
    
    return {
        "roles": roles_list,
        "groups": groups_list,
        "permissions": permissions,
        "permission_map": permission_map,
        "is_super_admin": super_admin,
        "is_admin": is_admin,
        "can_manage_users": can_manage_users,
        "departments": departments
    }


def get_user_location_district_code(db: Session, user: UserAccount) -> Optional[str]:
    """
    Get the district code associated with user's location.
    Returns district code if user is assigned to district branch, None for main branch or no assignment.
    """
    if user.ua_location_type == "DISTRICT_BRANCH" and user.ua_district_branch_id:
        district_branch = db.query(DistrictBranch).filter(
            DistrictBranch.db_id == user.ua_district_branch_id
        ).first()
        if district_branch:
            return district_branch.db_district_code
    return None


def apply_location_filter_for_workflow(
    query: Query, 
    user: UserAccount, 
    db: Session,
    location_field_name: str,
    workflow_status_field_name: str
) -> Query:
    """
    Apply location-based filtering to queries for ALL workflow statuses except COMPLETED.
    
    Args:
        query: The SQLAlchemy query to filter
        user: Current user account
        db: Database session
        location_field_name: Name of the column storing created_by_district (e.g., 'br_created_by_district')
        workflow_status_field_name: Name of the workflow status field (e.g., 'br_workflow_status')
    
    Returns:
        Filtered query
    
    Logic:
        - SUPER_ADMIN: sees ALL records regardless of status
        - MAIN_BRANCH users: see ALL records from all districts (all workflow stages)
        - DISTRICT_BRANCH users: see records from their district ONLY (all workflow stages)
        - ALL users: see COMPLETED records from all locations (no filter)
        
    Workflow stages filtered by location:
        - PENDING, APPROVED, REJECTED, PRINTING, PRINTED, SCANNED
        
    Workflow stages visible to everyone:
        - COMPLETED
    """
    # Check if user is super admin - they see everything
    if is_super_admin(db, user):
        return query
    
    # Get the model class from the query
    model_class = query.column_descriptions[0]['type']
    location_field = getattr(model_class, location_field_name)
    workflow_status_field = getattr(model_class, workflow_status_field_name)
    
    # For MAIN_BRANCH users, no additional filtering needed (they see all workflow stages)
    if user.ua_location_type == "MAIN_BRANCH":
        return query
    
    # For DISTRICT_BRANCH users, filter ALL workflow stages except COMPLETED by their district
    if user.ua_location_type == "DISTRICT_BRANCH" and user.ua_district_branch_id:
        user_district_code = get_user_location_district_code(db, user)
        if user_district_code:
            # Apply location filter to all statuses EXCEPT COMPLETED
            # COMPLETED records are visible to everyone
            query = query.filter(
                (workflow_status_field == 'COMPLETED') | 
                (location_field == user_district_code)
            )
    
    return query
