# app/schemas/status.py
from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class CRUDAction(str, Enum):
    CREATE = "CREATE"
    READ_ONE = "READ_ONE"
    READ_ALL = "READ_ALL"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class StatusBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    st_statcd: str = Field(min_length=1, max_length=5)
    st_descr: Optional[str] = Field(default=None, max_length=200)


class StatusCreate(StatusBase):
    pass


class StatusUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    st_statcd: Optional[str] = Field(default=None, min_length=1, max_length=5)
    st_descr: Optional[str] = Field(default=None, max_length=200)


class StatusOut(StatusBase):
    model_config = ConfigDict(
        from_attributes=True, str_strip_whitespace=True, populate_by_name=True
    )

    st_id: int
    st_version: datetime
    st_is_deleted: bool
    st_created_at: Optional[datetime] = None
    st_updated_at: Optional[datetime] = None
    st_created_by: Optional[str] = None
    st_updated_by: Optional[str] = None
    st_version_number: Optional[int] = None


class StatusRequestPayload(BaseModel):
    st_id: Optional[int] = None
    st_statcd: Optional[str] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1, le=200)
    page: Optional[int] = Field(default=1, ge=1)
    search_key: Optional[str] = ""
    data: Optional[Union[StatusCreate, StatusUpdate]] = None


class StatusManagementRequest(BaseModel):
    action: CRUDAction
    payload: StatusRequestPayload


class StatusManagementResponse(BaseModel):
    status: str
    message: str
    data: Optional[Union[StatusOut, List[StatusOut]]] = None
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None
