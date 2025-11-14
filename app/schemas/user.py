# app/schemas/user.py
from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


class RoleBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    model_config = ConfigDict(
        str_strip_whitespace=True,
        populate_by_name=True,
        extra="forbid",
    )

    ua_username: Annotated[str, Field(min_length=3, max_length=50)]
    ua_password: Annotated[str, Field(min_length=8, max_length=255)]
    confirm_password: Annotated[str, Field(min_length=8, max_length=255)] = Field(
        alias="confirmPassword"
    )
    ua_email: EmailStr
    ua_first_name: Annotated[Optional[str], Field(default=None, max_length=50)] = None
    ua_last_name: Annotated[Optional[str], Field(default=None, max_length=50)] = None
    ua_phone: Annotated[Optional[str], Field(default=None, max_length=15)] = None
    ro_role_id: Annotated[str, Field(min_length=1, max_length=20)]

    @field_validator("ua_username", "ro_role_id", mode="before")
    @classmethod
    def _validate_required_strings(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
        if not value:
            raise ValueError("Field is required.")
        return value

    @field_validator("ua_first_name", "ua_last_name", "ua_phone", mode="before")
    @classmethod
    def _normalize_optional_strings(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value

    @field_validator("ua_password")
    @classmethod
    def _validate_password_strength(cls, value: str) -> str:
        if not any(ch.islower() for ch in value):
            raise ValueError("Password must include at least one lowercase letter.")
        if not any(ch.isupper() for ch in value):
            raise ValueError("Password must include at least one uppercase letter.")
        if not any(ch.isdigit() for ch in value):
            raise ValueError("Password must include at least one digit.")
        if not any(ch in "!@#$%^&*()-_=+[]{}|;:,.<>?/" for ch in value):
            raise ValueError("Password must include at least one special character.")
        return value

    @model_validator(mode="after")
    def _check_password_confirmation(self):
        if self.ua_password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        return self


class UserLogin(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    ua_username: Annotated[str, Field(min_length=3, max_length=50)]
    ua_password: Annotated[str, Field(min_length=8, max_length=255)]

    @field_validator("ua_username", "ua_password", mode="before")
    @classmethod
    def _ensure_not_empty(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
        if not value:
            raise ValueError("Field is required.")
        return value


class UserResponse(BaseModel):
    ua_user_id: str
    ua_username: str
    ua_email: str
    ua_first_name: Optional[str]
    ua_last_name: Optional[str]
    ua_phone: Optional[str]
    ua_status: str
    ro_role_id: Optional[str] = None  # Made optional for RBAC - roles returned separately
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
