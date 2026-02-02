from datetime import datetime
import re
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

PHONE_PATTERN = re.compile(r"^\+?[0-9\s\-()]{7,15}$")
STATUS_MAX_LENGTH = 20


class UserCreate(BaseModel):
    ua_user_id: Annotated[str, Field(min_length=1, max_length=10)]
    ua_username: Annotated[str, Field(min_length=3, max_length=50)]
    ua_email: EmailStr
    ua_password: Annotated[str, Field(min_length=8, max_length=255)]
    ua_first_name: Annotated[Optional[str], Field(default=None, max_length=50)]
    ua_last_name: Annotated[Optional[str], Field(default=None, max_length=50)]
    ua_phone: Annotated[Optional[str], Field(default=None, max_length=15)]
    ua_status: Annotated[str, Field(max_length=STATUS_MAX_LENGTH)] = "active"
    ua_last_login: Optional[datetime] = None
    ua_login_attempts: Annotated[int, Field(ge=0)] = 0
    ua_locked_until: Optional[datetime] = None
    ua_password_expires: Optional[datetime] = None
    ua_must_change_password: bool = False
    ua_two_factor_enabled: bool = False
    ua_two_factor_secret: Annotated[Optional[str], Field(default=None, max_length=100)]
    ua_is_deleted: bool = False
    ua_created_at: Optional[datetime] = None
    ua_updated_at: Optional[datetime] = None
    ua_created_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    ua_updated_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    ua_version_number: Annotated[int, Field(ge=1)] = 1
    ro_role_id: Annotated[str, Field(min_length=1, max_length=20)]

    @field_validator(
        "ua_user_id",
        "ua_username",
        "ua_status",
        "ua_created_by",
        "ua_updated_by",
        "ro_role_id",
        mode="before",
    )
    @classmethod
    def _strip_strings(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
        if value == "":
            raise ValueError("Field cannot be empty or whitespace.")
        return value

    @field_validator("ua_first_name", "ua_last_name", "ua_phone", mode="before")
    @classmethod
    def _clean_optional_strings(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value

    @field_validator("ua_phone")
    @classmethod
    def _validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not PHONE_PATTERN.fullmatch(value):
            raise ValueError("ua_phone must contain only digits, spaces, (), -, or + and be 7-15 characters.")
        return value

    @field_validator("ua_password")
    @classmethod
    def _validate_password_strength(cls, value: str) -> str:
        if not any(ch.islower() for ch in value):
            raise ValueError("ua_password must include at least one lowercase letter.")
        if not any(ch.isupper() for ch in value):
            raise ValueError("ua_password must include at least one uppercase letter.")
        if not any(ch.isdigit() for ch in value):
            raise ValueError("ua_password must include at least one digit.")
        if not any(ch in "!@#$%^&*()-_=+[]{}|;:,.<>?/" for ch in value):
            raise ValueError("ua_password must include at least one special character.")
        return value

    @field_validator("ua_status")
    @classmethod
    def _validate_status_length(cls, value: str) -> str:
        if len(value) > STATUS_MAX_LENGTH:
            raise ValueError(f"ua_status must be {STATUS_MAX_LENGTH} characters or fewer.")
        return value


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ua_user_id: str
    ua_username: str
    ua_email: EmailStr
    ua_first_name: Optional[str] = None
    ua_last_name: Optional[str] = None
    ua_phone: Optional[str] = None
    ua_status: Optional[str] = None
    ua_last_login: Optional[datetime] = None
    ua_login_attempts: Optional[int] = None
    ua_locked_until: Optional[datetime] = None
    ua_password_expires: Optional[datetime] = None
    ua_must_change_password: Optional[bool] = None
    ua_two_factor_enabled: Optional[bool] = None
    ua_two_factor_secret: Optional[str] = None
    ua_is_deleted: Optional[bool] = None
    ua_created_at: Optional[datetime] = None
    ua_updated_at: Optional[datetime] = None
    ua_created_by: Optional[str] = None
    ua_updated_by: Optional[str] = None
    ua_version_number: Optional[int] = None
    ro_role_id: Optional[str] = None
