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


class ParshawaBase(BaseModel):
    pr_prn: Annotated[Optional[str], Field(default=None, max_length=20)]
    pr_pname: Annotated[Optional[str], Field(default=None, max_length=200)]
    pr_nayakahimi: Annotated[Optional[str], Field(default=None, max_length=20)]
    pr_rmrks: Annotated[Optional[str], Field(default=None, max_length=200)]
    pr_startdate: Optional[date] = None
    pr_nikayacd: Annotated[Optional[str], Field(default=None, max_length=10)]
    pr_is_deleted: bool = False
    pr_created_at: Optional[datetime] = None
    pr_updated_at: Optional[datetime] = None
    pr_created_by: Annotated[Optional[str], Field(default=None, max_length=25)]
    pr_updated_by: Annotated[Optional[str], Field(default=None, max_length=25)]
    pr_version_number: Annotated[int, Field(ge=1)] = 1

    @field_validator(
        "pr_prn",
        "pr_pname",
        "pr_nayakahimi",
        "pr_rmrks",
        "pr_nikayacd",
        "pr_created_by",
        "pr_updated_by",
        mode="before",
    )
    @classmethod
    def _strip_strings(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            if value == "":
                return None
        return value


class ParshawaCreate(ParshawaBase):
    pr_prn: Annotated[str, Field(min_length=1, max_length=20)]
    pr_nayakahimi: Annotated[str, Field(min_length=1, max_length=20)]


class ParshawaUpdate(BaseModel):
    pr_prn: Annotated[Optional[str], Field(default=None, min_length=1, max_length=20)]
    pr_pname: Annotated[Optional[str], Field(default=None, max_length=200)]
    pr_nayakahimi: Annotated[Optional[str], Field(default=None, min_length=1, max_length=20)]
    pr_rmrks: Annotated[Optional[str], Field(default=None, max_length=200)]
    pr_startdate: Optional[date] = None
    pr_nikayacd: Annotated[Optional[str], Field(default=None, max_length=10)]
    pr_is_deleted: Optional[bool] = None
    pr_updated_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    pr_updated_at: Optional[datetime] = None

    @field_validator(
        "pr_prn",
        "pr_pname",
        "pr_nayakahimi",
        "pr_rmrks",
        "pr_nikayacd",
        "pr_updated_by",
        mode="before",
    )
    @classmethod
    def _strip_strings(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            if value == "":
                return None
        return value


class ParshawaOut(ParshawaBase):
    model_config = ConfigDict(from_attributes=True)

    pr_id: int
    pr_version: datetime


class ParshawaRequestPayload(BaseModel):
    pr_id: Optional[int] = None
    pr_prn: Optional[str] = None
    skip: Annotated[int, Field(ge=0)] = 0
    limit: Annotated[int, Field(ge=1, le=200)] = 10
    page: Annotated[Optional[int], Field(default=1, ge=1)] = 1
    search_key: Annotated[Optional[str], Field(default=None, max_length=200)] = None
    data: Optional[Union[ParshawaCreate, ParshawaUpdate]] = None


class ParshawaManagementRequest(BaseModel):
    action: CRUDAction
    payload: ParshawaRequestPayload


class ParshawaManagementResponse(BaseModel):
    status: str
    message: str
    data: Optional[Union[ParshawaOut, List[ParshawaOut], Any]] = None
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None
