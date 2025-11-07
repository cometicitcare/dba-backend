from datetime import datetime
from enum import Enum
from typing import Annotated, List, Optional, Union

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CRUDAction(str, Enum):
    CREATE = "CREATE"
    READ_ONE = "READ_ONE"
    READ_ALL = "READ_ALL"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class GramasewakaBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    gn_gnc: str = Field(..., max_length=10)
    gn_gnname: Optional[str] = Field(default=None, max_length=200)
    gn_mbile: Optional[str] = Field(default=None, max_length=10, min_length=10)
    gn_email: Optional[EmailStr] = Field(default=None, max_length=40)
    gn_dvcode: str = Field(..., max_length=10)


class GramasewakaCreate(GramasewakaBase):
    gn_created_by: Optional[str] = Field(default=None, max_length=25)
    gn_updated_by: Optional[str] = Field(default=None, max_length=25)


class GramasewakaUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    gn_gnc: Optional[str] = Field(default=None, max_length=10)
    gn_gnname: Optional[str] = Field(default=None, max_length=200)
    gn_mbile: Optional[str] = Field(default=None, max_length=10, min_length=10)
    gn_email: Optional[EmailStr] = Field(default=None, max_length=40)
    gn_dvcode: Optional[str] = Field(default=None, max_length=10)
    gn_updated_by: Optional[str] = Field(default=None, max_length=25)


class GramasewakaOut(GramasewakaBase):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    gn_id: int
    gn_version: Optional[datetime] = None
    gn_is_deleted: bool
    gn_created_at: Optional[datetime] = None
    gn_updated_at: Optional[datetime] = None
    gn_created_by: Optional[str] = None
    gn_updated_by: Optional[str] = None
    gn_version_number: Optional[int] = None


class GramasewakaRequestPayload(BaseModel):
    gn_id: Optional[int] = None
    gn_gnc: Optional[str] = Field(default=None, max_length=10)
    skip: Annotated[int, Field(ge=0)] = 0
    limit: Annotated[int, Field(ge=1, le=200)] = 10
    page: Annotated[Optional[int], Field(ge=1)] = 1
    search_key: Optional[str] = Field(default="", max_length=100)
    data: Optional[Union[GramasewakaCreate, GramasewakaUpdate]] = None


class GramasewakaManagementRequest(BaseModel):
    action: CRUDAction
    payload: GramasewakaRequestPayload


class GramasewakaManagementResponse(BaseModel):
    status: str
    message: str
    data: Optional[Union[GramasewakaOut, List[GramasewakaOut]]] = None
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None
