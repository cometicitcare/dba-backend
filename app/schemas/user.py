# app/schemas/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class RoleBase(BaseModel):
    ro_role_id: str
    ro_role_name: str
    ro_description: Optional[str] = None


class Role(RoleBase):
    ro_is_system_role: bool
    ro_is_deleted: bool
    ro_created_at: datetime
    ro_updated_at: datetime
    ro_version_number: int

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    ua_username: str
    ua_password: str
    ua_email: EmailStr
    ua_first_name: Optional[str] = None
    ua_last_name: Optional[str] = None
    ua_phone: Optional[str] = None
    ro_role_id: str  # Role selection (must be one of the 5 roles)


class UserLogin(BaseModel):
    ua_username: str
    ua_password: str


class UserResponse(BaseModel):
    ua_user_id: str
    ua_username: str
    ua_email: str
    ua_first_name: Optional[str]
    ua_last_name: Optional[str]
    ua_phone: Optional[str]
    ua_status: str
    ro_role_id: str
    role: Optional[RoleBase] = None

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    session_id: str
    user: UserResponse


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None