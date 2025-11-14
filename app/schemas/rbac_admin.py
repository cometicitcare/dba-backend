# app/schemas/rbac_admin.py
"""
Schemas for RBAC Administration
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# ==================== Request Schemas ====================

class UserRoleAssignRequest(BaseModel):
    user_id: str = Field(..., description="User ID to assign role to")
    role_id: str = Field(..., description="Role ID to assign")
    expires_days: Optional[int] = Field(None, description="Days until expiration (null = never expires)")
    is_active: bool = Field(True, description="Whether the role assignment is active")


class UserRoleRevokeRequest(BaseModel):
    user_id: str
    role_id: str


class UserGroupAssignRequest(BaseModel):
    user_id: str
    group_id: str


class UserGroupRemoveRequest(BaseModel):
    user_id: str
    group_id: str


class UserPermissionOverrideRequest(BaseModel):
    user_id: str
    permission_id: str
    granted: bool = Field(..., description="True to grant, False to deny")
    expires_days: Optional[int] = Field(None, description="Days until expiration")
    is_active: bool = Field(True)


class UserPermissionRemoveRequest(BaseModel):
    user_id: str
    permission_id: str


# ==================== Response Schemas ====================

class RBACManagementResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


class RoleAssignmentInfo(BaseModel):
    role_id: str
    role_name: str
    department: Optional[str] = None
    level: str
    assigned_date: Optional[str] = None
    expires_date: Optional[str] = None
    is_active: bool


class GroupMembershipInfo(BaseModel):
    group_id: str
    group_name: str
    group_type: str


class PermissionOverrideInfo(BaseModel):
    permission_id: str
    permission_name: str
    granted: bool
    expires_date: Optional[str] = None


class UserRBACContext(BaseModel):
    user_id: str
    username: str
    full_name: str
    email: str
    is_active: bool
    roles: List[RoleAssignmentInfo]
    groups: List[GroupMembershipInfo]
    permissions: List[str]
    permission_overrides: List[PermissionOverrideInfo]
    is_super_admin: bool
    is_admin: bool
    can_manage_users: bool


class UserListItem(BaseModel):
    user_id: str
    username: str
    full_name: str
    email: str
    is_active: bool
    roles: List[str]
    groups: List[str]
    is_super_admin: bool
    is_admin: bool


class UserListResponse(BaseModel):
    success: bool
    total: int
    page: int
    limit: int
    data: List[UserListItem]
