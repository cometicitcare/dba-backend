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


class CityBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    ct_code: str = Field(..., max_length=10)
    ct_gncode: str = Field(..., max_length=10)
    ct_descr_name: Optional[str] = Field(default=None, max_length=200)
    ct_dvcode: Optional[str] = Field(default=None, max_length=10)


class CityCreate(CityBase):
    ct_created_by: Optional[str] = Field(default=None, max_length=25)
    ct_updated_by: Optional[str] = Field(default=None, max_length=25)


class CityUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    ct_code: Optional[str] = Field(default=None, max_length=10)
    ct_gncode: Optional[str] = Field(default=None, max_length=10)
    ct_descr_name: Optional[str] = Field(default=None, max_length=200)
    ct_dvcode: Optional[str] = Field(default=None, max_length=10)
    ct_updated_by: Optional[str] = Field(default=None, max_length=25)


class CityOut(CityBase):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    ct_id: int
    ct_version: Optional[datetime] = None
    ct_is_deleted: bool
    ct_created_at: Optional[datetime] = None
    ct_updated_at: Optional[datetime] = None
    ct_created_by: Optional[str] = None
    ct_updated_by: Optional[str] = None
    ct_version_number: Optional[int] = None


class CityRequestPayload(BaseModel):
    ct_id: Optional[int] = None
    ct_code: Optional[str] = Field(default=None, max_length=10)
    skip: Annotated[int, Field(ge=0)] = 0
    limit: Annotated[int, Field(ge=1, le=200)] = 10
    page: Annotated[Optional[int], Field(ge=1)] = 1
    search_key: Optional[str] = Field(default="", max_length=100)
    data: Optional[Union[CityCreate, CityUpdate]] = None


class CityManagementRequest(BaseModel):
    action: CRUDAction
    payload: CityRequestPayload


class CityManagementResponse(BaseModel):
    status: str
    message: str
    data: Optional[Union[CityOut, List[CityOut]]] = None
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None
