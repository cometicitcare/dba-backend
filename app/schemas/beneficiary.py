from datetime import datetime
import re
from enum import Enum
from typing import Annotated, Optional, Union, List, Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

PHONE_PATTERN = re.compile(r"^[0-9]{10}$")


class CRUDAction(str, Enum):
    CREATE = "CREATE"
    READ_ONE = "READ_ONE"
    READ_ALL = "READ_ALL"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class BeneficiaryBase(BaseModel):
    bf_bfname: Annotated[Optional[str], Field(default=None, max_length=200)]
    bf_bfaddrs: Annotated[Optional[str], Field(default=None, max_length=200)]
    bf_whatapp: Annotated[Optional[str], Field(default=None, min_length=10, max_length=10)]
    bf_mobile: Annotated[Optional[str], Field(default=None, min_length=10, max_length=10)]
    bf_email: Annotated[Optional[EmailStr], Field(default=None, max_length=40)]
    bf_is_deleted: bool = False
    bf_created_at: Optional[datetime] = None
    bf_updated_at: Optional[datetime] = None
    bf_created_by: Annotated[Optional[str], Field(default=None, max_length=25)]
    bf_updated_by: Annotated[Optional[str], Field(default=None, max_length=25)]
    bf_version_number: Annotated[int, Field(ge=1)] = 1

    @field_validator(
        "bf_bfname",
        "bf_bfaddrs",
        "bf_created_by",
        "bf_updated_by",
        mode="before",
    )
    @classmethod
    def _strip_strings(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            if value == "":
                return None
        return value

    @field_validator("bf_mobile", "bf_whatapp")
    @classmethod
    def _validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not PHONE_PATTERN.fullmatch(value):
            raise ValueError("Phone numbers must be exactly 10 digits.")
        return value

    @field_validator("bf_email", mode="before")
    @classmethod
    def _normalize_email(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class BeneficiaryCreate(BeneficiaryBase):
    bf_bnn: Annotated[Optional[str], Field(default=None, min_length=1, max_length=10)] = None

    @field_validator("bf_bnn", mode="before")
    @classmethod
    def _strip_bnn(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class BeneficiaryUpdate(BaseModel):
    bf_bnn: Annotated[Optional[str], Field(default=None, min_length=1, max_length=10)]
    bf_bfname: Annotated[Optional[str], Field(default=None, max_length=200)]
    bf_bfaddrs: Annotated[Optional[str], Field(default=None, max_length=200)]
    bf_whatapp: Annotated[Optional[str], Field(default=None, min_length=10, max_length=10)]
    bf_mobile: Annotated[Optional[str], Field(default=None, min_length=10, max_length=10)]
    bf_email: Annotated[Optional[EmailStr], Field(default=None, max_length=40)]
    bf_is_deleted: Optional[bool] = None
    bf_version_number: Annotated[Optional[int], Field(default=None, ge=1)] = None
    bf_updated_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    bf_updated_at: Optional[datetime] = None

    @field_validator(
        "bf_bfname",
        "bf_bfaddrs",
        "bf_updated_by",
        mode="before",
    )
    @classmethod
    def _strip_strings(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value

    @field_validator("bf_bnn", mode="before")
    @classmethod
    def _strip_bnn(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value

    @field_validator("bf_mobile", "bf_whatapp")
    @classmethod
    def _validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not PHONE_PATTERN.fullmatch(value):
            raise ValueError("Phone numbers must be exactly 10 digits.")
        return value

    @field_validator("bf_email", mode="before")
    @classmethod
    def _normalize_email(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class BeneficiaryOut(BeneficiaryBase):
    model_config = ConfigDict(from_attributes=True)

    bf_bnn: str
    bf_id: int


class BeneficiaryRequestPayload(BaseModel):
    bf_id: Optional[int] = None
    bf_bnn: Optional[str] = None
    skip: Annotated[int, Field(ge=0)] = 0
    limit: Annotated[int, Field(ge=1, le=200)] = 10
    page: Annotated[Optional[int], Field(default=1, ge=1)] = 1
    search_key: Annotated[Optional[str], Field(default=None, max_length=200)] = None
    data: Optional[Union[BeneficiaryCreate, BeneficiaryUpdate]] = None


class BeneficiaryManagementRequest(BaseModel):
    action: CRUDAction
    payload: BeneficiaryRequestPayload


class BeneficiaryManagementResponse(BaseModel):
    status: str
    message: str
    data: Optional[Union[BeneficiaryOut, List[BeneficiaryOut], Any]] = None
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None
