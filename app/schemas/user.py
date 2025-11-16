# app/schemas/user.py
from datetime import datetime
from typing import Annotated, Optional
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


class UserLocationType(str, Enum):
    """Enum for user location types/levels"""
    MAIN_BRANCH = "MAIN_BRANCH"
    PROVINCE_BRANCH = "PROVINCE_BRANCH"
    DISTRICT_BRANCH = "DISTRICT_BRANCH"


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
    
    # Location-based access control fields
    ua_location_type: Optional[UserLocationType] = None
    ua_main_branch_id: Optional[int] = None
    ua_province_branch_id: Optional[int] = None
    ua_district_branch_id: Optional[int] = None

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
    
    @model_validator(mode="after")
    def _validate_location_fields(self):
        """Validate that location fields are consistent with location type"""
        if self.ua_location_type:
            if self.ua_location_type == UserLocationType.MAIN_BRANCH:
                if not self.ua_main_branch_id:
                    raise ValueError("Main branch ID is required for MAIN_BRANCH type users")
                if self.ua_province_branch_id or self.ua_district_branch_id:
                    raise ValueError("MAIN_BRANCH type users should not have province or district branch IDs")
            elif self.ua_location_type == UserLocationType.PROVINCE_BRANCH:
                if not self.ua_province_branch_id:
                    raise ValueError("Province branch ID is required for PROVINCE_BRANCH type users")
                if self.ua_district_branch_id:
                    raise ValueError("PROVINCE_BRANCH type users should not have district branch ID")
            elif self.ua_location_type == UserLocationType.DISTRICT_BRANCH:
                if not self.ua_district_branch_id:
                    raise ValueError("District branch ID is required for DISTRICT_BRANCH type users")
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
    
    # Location-based access control fields
    ua_location_type: Optional[UserLocationType] = None
    ua_main_branch_id: Optional[int] = None
    ua_province_branch_id: Optional[int] = None
    ua_district_branch_id: Optional[int] = None

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
