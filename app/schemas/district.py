from datetime import datetime
from enum import Enum
from typing import Annotated, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class CRUDAction(str, Enum):
    CREATE = "CREATE"
    READ_ONE = "READ_ONE"
    READ_ALL = "READ_ALL"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class DistrictBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    dd_dcode: str = Field(..., max_length=10)
    dd_dname: Optional[str] = Field(default=None, max_length=200)


class DistrictCreate(DistrictBase):
    dd_created_by: Optional[str] = Field(default=None, max_length=25)
    dd_updated_by: Optional[str] = Field(default=None, max_length=25)


class DistrictUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    dd_dcode: Optional[str] = Field(default=None, max_length=10)
    dd_dname: Optional[str] = Field(default=None, max_length=200)
    dd_updated_by: Optional[str] = Field(default=None, max_length=25)


class DistrictOut(DistrictBase):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    dd_id: int
    dd_version: Optional[datetime] = None
    dd_is_deleted: bool
    dd_created_at: Optional[datetime] = None
    dd_updated_at: Optional[datetime] = None
    dd_created_by: Optional[str] = None
    dd_updated_by: Optional[str] = None
    dd_version_number: Optional[int] = None


class DistrictRequestPayload(BaseModel):
    dd_id: Optional[int] = None
    dd_dcode: Optional[str] = Field(default=None, max_length=10)
    skip: Annotated[int, Field(ge=0)] = 0
    limit: Annotated[int, Field(ge=1, le=200)] = 10
    page: Annotated[Optional[int], Field(ge=1)] = 1
    search_key: Optional[str] = Field(default="", max_length=100)
    data: Optional[Union[DistrictCreate, DistrictUpdate]] = None


class DistrictManagementRequest(BaseModel):
    action: CRUDAction
    payload: DistrictRequestPayload


class DistrictManagementResponse(BaseModel):
    status: str
    message: str
    data: Optional[Union[DistrictOut, List[DistrictOut]]] = None
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None
