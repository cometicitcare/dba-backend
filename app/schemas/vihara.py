from datetime import date, datetime
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


class ViharaBase(BaseModel):
    vh_trn: Annotated[str, Field(min_length=1, max_length=10)]
    vh_vname: Annotated[Optional[str], Field(default=None, max_length=200)]
    vh_addrs: Annotated[Optional[str], Field(default=None, max_length=200)]
    vh_mobile: Annotated[str, Field(min_length=10, max_length=10)]
    vh_whtapp: Annotated[str, Field(min_length=10, max_length=10)]
    vh_email: EmailStr
    vh_typ: Annotated[str, Field(min_length=1, max_length=10)]
    vh_gndiv: Annotated[str, Field(min_length=1, max_length=10)]
    vh_fmlycnt: Annotated[Optional[int], Field(default=None, ge=0)]
    vh_bgndate: Optional[date] = None
    vh_ownercd: Annotated[str, Field(min_length=1, max_length=12)]
    vh_parshawa: Annotated[str, Field(min_length=1, max_length=10)]
    vh_ssbmcode: Annotated[Optional[str], Field(default=None, max_length=10)]
    vh_syojakarmakrs: Annotated[Optional[str], Field(default=None, max_length=100)]
    vh_syojakarmdate: Optional[date] = None
    vh_landownrship: Annotated[Optional[str], Field(default=None, max_length=150)]
    vh_pralename: Annotated[Optional[str], Field(default=None, max_length=50)]
    vh_pralesigdate: Optional[date] = None
    vh_bacgrecmn: Annotated[Optional[str], Field(default=None, max_length=100)]
    vh_bacgrcmdate: Optional[date] = None
    vh_minissecrsigdate: Optional[date] = None
    vh_minissecrmrks: Annotated[Optional[str], Field(default=None, max_length=200)]
    vh_ssbmsigdate: Optional[date] = None
    vh_is_deleted: bool = False
    vh_created_at: Optional[datetime] = None
    vh_updated_at: Optional[datetime] = None
    vh_created_by: Annotated[Optional[str], Field(default=None, max_length=25)]
    vh_updated_by: Annotated[Optional[str], Field(default=None, max_length=25)]
    vh_version_number: Annotated[int, Field(ge=1)] = 1

    @field_validator(
        "vh_trn",
        "vh_vname",
        "vh_addrs",
        "vh_typ",
        "vh_gndiv",
        "vh_ownercd",
        "vh_parshawa",
        "vh_ssbmcode",
        "vh_syojakarmakrs",
        "vh_landownrship",
        "vh_pralename",
        "vh_bacgrecmn",
        "vh_minissecrmrks",
        "vh_created_by",
        "vh_updated_by",
        mode="before",
    )
    @classmethod
    def _strip_strings(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            if value == "":
                return None
        return value

    @field_validator("vh_mobile", "vh_whtapp")
    @classmethod
    def _validate_phone(cls, value: str) -> str:
        if not PHONE_PATTERN.fullmatch(value):
            raise ValueError("Phone numbers must be exactly 10 digits.")
        return value

    @field_validator("vh_email", mode="before")
    @classmethod
    def _normalize_email(cls, value: str) -> str:
        if isinstance(value, str):
            value = value.strip()
        return value


class ViharaCreate(ViharaBase):
    vh_trn: Annotated[Optional[str], Field(default=None, min_length=1, max_length=10)]
    vh_id: Annotated[Optional[int], Field(default=None, ge=1)] = None


class ViharaUpdate(BaseModel):
    vh_trn: Annotated[Optional[str], Field(default=None, min_length=1, max_length=10)]
    vh_vname: Annotated[Optional[str], Field(default=None, max_length=200)]
    vh_addrs: Annotated[Optional[str], Field(default=None, max_length=200)]
    vh_mobile: Annotated[Optional[str], Field(default=None, min_length=10, max_length=10)]
    vh_whtapp: Annotated[Optional[str], Field(default=None, min_length=10, max_length=10)]
    vh_email: Optional[EmailStr] = None
    vh_typ: Annotated[Optional[str], Field(default=None, min_length=1, max_length=10)]
    vh_gndiv: Annotated[Optional[str], Field(default=None, min_length=1, max_length=10)]
    vh_fmlycnt: Annotated[Optional[int], Field(default=None, ge=0)]
    vh_bgndate: Optional[date] = None
    vh_ownercd: Annotated[Optional[str], Field(default=None, min_length=1, max_length=12)]
    vh_parshawa: Annotated[Optional[str], Field(default=None, min_length=1, max_length=10)]
    vh_ssbmcode: Annotated[Optional[str], Field(default=None, max_length=10)]
    vh_syojakarmakrs: Annotated[Optional[str], Field(default=None, max_length=100)]
    vh_syojakarmdate: Optional[date] = None
    vh_landownrship: Annotated[Optional[str], Field(default=None, max_length=150)]
    vh_pralename: Annotated[Optional[str], Field(default=None, max_length=50)]
    vh_pralesigdate: Optional[date] = None
    vh_bacgrecmn: Annotated[Optional[str], Field(default=None, max_length=100)]
    vh_bacgrcmdate: Optional[date] = None
    vh_minissecrsigdate: Optional[date] = None
    vh_minissecrmrks: Annotated[Optional[str], Field(default=None, max_length=200)]
    vh_ssbmsigdate: Optional[date] = None
    vh_is_deleted: Optional[bool] = None
    vh_version_number: Annotated[Optional[int], Field(default=None, ge=1)] = None
    vh_updated_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    vh_updated_at: Optional[datetime] = None

    @field_validator(
        "vh_trn",
        "vh_vname",
        "vh_addrs",
        "vh_typ",
        "vh_gndiv",
        "vh_ownercd",
        "vh_parshawa",
        "vh_ssbmcode",
        "vh_syojakarmakrs",
        "vh_landownrship",
        "vh_pralename",
        "vh_bacgrecmn",
        "vh_minissecrmrks",
        "vh_updated_by",
        mode="before",
    )
    @classmethod
    def _strip_strings(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value

    @field_validator("vh_mobile", "vh_whtapp")
    @classmethod
    def _validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not PHONE_PATTERN.fullmatch(value):
            raise ValueError("Phone numbers must be exactly 10 digits.")
        return value

    @field_validator("vh_email", mode="before")
    @classmethod
    def _normalize_email(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class ViharaOut(ViharaBase):
    model_config = ConfigDict(from_attributes=True)

    vh_id: int


class ViharaRequestPayload(BaseModel):
    vh_id: Optional[int] = None
    vh_trn: Optional[str] = None
    skip: Annotated[int, Field(ge=0)] = 0
    limit: Annotated[int, Field(ge=1, le=200)] = 10
    page: Annotated[Optional[int], Field(default=1, ge=1)] = 1
    search_key: Annotated[Optional[str], Field(default=None, max_length=200)] = None
    data: Optional[Union[ViharaCreate, ViharaUpdate]] = None


class ViharaManagementRequest(BaseModel):
    action: CRUDAction
    payload: ViharaRequestPayload


class ViharaManagementResponse(BaseModel):
    status: str
    message: str
    data: Optional[Union[ViharaOut, List[ViharaOut], Any]] = None
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None
