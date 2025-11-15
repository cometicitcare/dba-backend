from pydantic import BaseModel
from typing import List, Dict, Optional, Any


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginIn(BaseModel):
    username: str
    password: str


class RoleListResponse(BaseModel):
    """Response model for listing roles"""
    roles: List[Dict[str, Any]]


class LogoutResponse(BaseModel):
    """Response model for logout"""
    message: str


class RefreshResponse(BaseModel):
    """Response model for token refresh"""
    message: str


class UserContextResponse(BaseModel):
    """Response model for user RBAC context"""
    user: Dict[str, Any]
    roles: List[Dict[str, Any]]
    groups: List[Dict[str, Any]]
    permissions: List[str]
    permission_map: Dict[str, List[str]]
    is_super_admin: bool
    is_admin: bool
    can_manage_users: bool
    departments: List[str]


class UserPermissionsResponse(BaseModel):
    """Response model for user permissions"""
    permissions: List[str]
    is_super_admin: bool
