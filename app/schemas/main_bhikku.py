from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Annotated, Any, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ------------------------------------------------------------------
# Enums
# ------------------------------------------------------------------

class CRUDAction(str, Enum):
    CREATE = "CREATE"
    READ_ONE = "READ_ONE"
    READ_ALL = "READ_ALL"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class MainBhikkuType(str, Enum):
    NIKAYA_MAHANAYAKA = "NIKAYA_MAHANAYAKA"
    PARSHAWA_MAHANAYAKA = "PARSHAWA_MAHANAYAKA"


# ------------------------------------------------------------------
# Base / Create / Update
# ------------------------------------------------------------------

class MainBhikkuBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    mb_type: MainBhikkuType
    mb_nikaya_cd: Annotated[str, Field(min_length=1, max_length=10)]
    mb_parshawa_cd: Annotated[Optional[str], Field(default=None, max_length=20)] = None
    mb_bhikku_regn: Annotated[str, Field(min_length=1, max_length=20)]
    mb_start_date: Optional[date] = None
    mb_end_date: Optional[date] = None
    mb_remarks: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    mb_is_active: Optional[bool] = True

    @field_validator(
        "mb_nikaya_cd", "mb_parshawa_cd", "mb_bhikku_regn", "mb_remarks",
        mode="before",
    )
    @classmethod
    def _strip(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            return value.upper() if value else None
        return value


class MainBhikkuCreate(MainBhikkuBase):
    """Fields required when creating a main_bhikkus record."""

    @field_validator("mb_nikaya_cd", mode="before")
    @classmethod
    def _require_nikaya(cls, v: Optional[str]) -> str:
        if not v or not str(v).strip():
            raise ValueError("mb_nikaya_cd is required.")
        return str(v).strip().upper()

    @field_validator("mb_bhikku_regn", mode="before")
    @classmethod
    def _require_bhikku(cls, v: Optional[str]) -> str:
        if not v or not str(v).strip():
            raise ValueError("mb_bhikku_regn is required.")
        return str(v).strip().upper()


class MainBhikkuUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    mb_type: Optional[MainBhikkuType] = None
    mb_nikaya_cd: Annotated[Optional[str], Field(default=None, max_length=10)] = None
    mb_parshawa_cd: Annotated[Optional[str], Field(default=None, max_length=20)] = None
    mb_bhikku_regn: Annotated[Optional[str], Field(default=None, max_length=20)] = None
    mb_start_date: Optional[date] = None
    mb_end_date: Optional[date] = None
    mb_remarks: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    mb_is_active: Optional[bool] = None

    @field_validator(
        "mb_nikaya_cd", "mb_parshawa_cd", "mb_bhikku_regn", "mb_remarks",
        mode="before",
    )
    @classmethod
    def _strip(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            return value.upper() if value else None
        return value


# ------------------------------------------------------------------
# Output
# ------------------------------------------------------------------

class BhikkuBriefOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    br_regn: str
    br_mahananame: Optional[str] = None
    br_gihiname: Optional[str] = None


class NikayaBriefOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    nk_nkn: str
    nk_nname: Optional[str] = None


class ParshawaBriefOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    pr_prn: str
    pr_pname: Optional[str] = None


class MainBhikkuOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    mb_id: int
    mb_type: str
    mb_nikaya_cd: str
    mb_parshawa_cd: Optional[str] = None
    mb_bhikku_regn: str
    mb_start_date: Optional[date] = None
    mb_end_date: Optional[date] = None
    mb_remarks: Optional[str] = None
    mb_is_active: bool
    mb_is_deleted: bool
    mb_created_at: Optional[datetime] = None
    mb_updated_at: Optional[datetime] = None
    mb_created_by: Optional[str] = None
    mb_updated_by: Optional[str] = None
    mb_version_number: int

    # Nested detail (populated from relationships)
    nikaya: Optional[NikayaBriefOut] = None
    parshawa: Optional[ParshawaBriefOut] = None
    bhikku: Optional[BhikkuBriefOut] = None


# ------------------------------------------------------------------
# Request / Response wrappers (single-endpoint CRUD pattern)
# ------------------------------------------------------------------

class MainBhikkuRequestPayload(BaseModel):
    mb_id: Optional[int] = None
    skip: Annotated[int, Field(ge=0)] = 0
    limit: Annotated[int, Field(ge=1, le=200)] = 10
    page: Annotated[Optional[int], Field(default=1, ge=1)] = 1
    search_key: Annotated[Optional[str], Field(default=None, max_length=200)] = None
    # Filters
    mb_type: Optional[MainBhikkuType] = None
    mb_nikaya_cd: Optional[str] = None
    mb_parshawa_cd: Optional[str] = None
    data: Optional[Union[MainBhikkuCreate, MainBhikkuUpdate]] = None


class MainBhikkuManagementRequest(BaseModel):
    action: CRUDAction
    payload: MainBhikkuRequestPayload


class MainBhikkuManagementResponse(BaseModel):
    status: str
    message: str
    data: Optional[Union[MainBhikkuOut, List[MainBhikkuOut], Any]] = None
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None
