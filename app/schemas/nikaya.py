from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Annotated, Any, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CRUDAction(str, Enum):
    CREATE = "CREATE"
    READ_ONE = "READ_ONE"
    READ_ALL = "READ_ALL"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class NikayaBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    nk_nname: Annotated[Optional[str], Field(default=None, max_length=200)] = None
    nk_nahimicd: Annotated[Optional[str], Field(default=None, max_length=12)] = None
    nk_startdate: Optional[date] = None
    nk_rmakrs: Annotated[Optional[str], Field(default=None, max_length=200)] = None
    nk_created_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    nk_updated_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None

    @field_validator(
        "nk_nname",
        "nk_nahimicd",
        "nk_rmakrs",
        "nk_created_by",
        "nk_updated_by",
        mode="before",
    )
    @classmethod
    def _strip_strings(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class NikayaCreate(NikayaBase):
    nk_nkn: Annotated[str, Field(min_length=1, max_length=10)]

    @field_validator("nk_nkn", mode="before")
    @classmethod
    def _normalize_nkn(cls, value: Optional[str]) -> str:
        if value is None:
            raise ValueError("nk_nkn is required.")
        stripped = value.strip()
        if not stripped:
            raise ValueError("nk_nkn is required.")
        return stripped.upper()

    @field_validator("nk_nahimicd", mode="before")
    @classmethod
    def _normalize_bhikku_regn(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            return value.upper() if value else None
        return value


class NikayaUpdate(NikayaBase):
    nk_nkn: Annotated[Optional[str], Field(default=None, max_length=10)] = None

    @field_validator("nk_nkn", mode="before")
    @classmethod
    def _normalize_nkn(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        stripped = value.strip()
        if not stripped:
            raise ValueError("nk_nkn cannot be blank.")
        return stripped.upper()

    @field_validator("nk_nahimicd", mode="before")
    @classmethod
    def _normalize_bhikku_regn(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            return value.upper() if value else None
        return value


class NikayaOut(NikayaBase):
    model_config = ConfigDict(from_attributes=True)

    nk_id: int
    nk_nkn: str
    nk_version: datetime
    nk_is_deleted: bool
    nk_created_at: Optional[datetime] = None
    nk_updated_at: Optional[datetime] = None
    nk_version_number: Optional[int] = None


class NikayaRequestPayload(BaseModel):
    nk_id: Optional[int] = None
    nk_nkn: Optional[str] = None
    skip: Annotated[int, Field(ge=0)] = 0
    limit: Annotated[int, Field(ge=1, le=200)] = 10
    page: Annotated[Optional[int], Field(default=1, ge=1)] = 1
    search_key: Annotated[Optional[str], Field(default=None, max_length=200)] = None
    data: Optional[Union[NikayaCreate, NikayaUpdate]] = None


class NikayaManagementRequest(BaseModel):
    action: CRUDAction
    payload: NikayaRequestPayload


class NikayaManagementResponse(BaseModel):
    status: str
    message: str
    data: Optional[Union[NikayaOut, List[NikayaOut], Any]] = None
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None
