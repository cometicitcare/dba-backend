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


class ProvinceBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    cp_code: str = Field(..., max_length=10)
    cp_name: Optional[str] = Field(default=None, max_length=200)


class ProvinceCreate(ProvinceBase):
    cp_created_by: Optional[str] = Field(default=None, max_length=25)
    cp_updated_by: Optional[str] = Field(default=None, max_length=25)


class ProvinceUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    cp_code: Optional[str] = Field(default=None, max_length=10)
    cp_name: Optional[str] = Field(default=None, max_length=200)
    cp_updated_by: Optional[str] = Field(default=None, max_length=25)


class ProvinceOut(ProvinceBase):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    cp_id: int
    cp_version: Optional[datetime] = None
    cp_is_deleted: bool
    cp_created_at: Optional[datetime] = None
    cp_updated_at: Optional[datetime] = None
    cp_created_by: Optional[str] = None
    cp_updated_by: Optional[str] = None
    cp_version_number: Optional[int] = None


class ProvinceRequestPayload(BaseModel):
    cp_id: Optional[int] = None
    cp_code: Optional[str] = Field(default=None, max_length=10)
    skip: Annotated[int, Field(ge=0)] = 0
    limit: Annotated[int, Field(ge=1, le=200)] = 10
    page: Annotated[Optional[int], Field(ge=1)] = 1
    search_key: Optional[str] = Field(default="", max_length=100)
    data: Optional[Union[ProvinceCreate, ProvinceUpdate]] = None


class ProvinceManagementRequest(BaseModel):
    action: CRUDAction
    payload: ProvinceRequestPayload


class ProvinceManagementResponse(BaseModel):
    status: str
    message: str
    data: Optional[Union[ProvinceOut, List[ProvinceOut]]] = None
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None
