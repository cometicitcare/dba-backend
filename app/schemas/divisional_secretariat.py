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


class DivisionalSecretariatBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    dv_dvcode: str = Field(..., max_length=10)
    dv_distrcd: str = Field(..., max_length=10)
    dv_dvname: Optional[str] = Field(default=None, max_length=200)


class DivisionalSecretariatCreate(DivisionalSecretariatBase):
    dv_created_by: Optional[str] = Field(default=None, max_length=25)
    dv_updated_by: Optional[str] = Field(default=None, max_length=25)


class DivisionalSecretariatUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    dv_dvcode: Optional[str] = Field(default=None, max_length=10)
    dv_distrcd: Optional[str] = Field(default=None, max_length=10)
    dv_dvname: Optional[str] = Field(default=None, max_length=200)
    dv_updated_by: Optional[str] = Field(default=None, max_length=25)


class DivisionalSecretariatOut(DivisionalSecretariatBase):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    dv_id: int
    dv_version: Optional[datetime] = None
    dv_is_deleted: bool
    dv_created_at: Optional[datetime] = None
    dv_updated_at: Optional[datetime] = None
    dv_created_by: Optional[str] = None
    dv_updated_by: Optional[str] = None
    dv_version_number: Optional[int] = None


class DivisionalSecretariatRequestPayload(BaseModel):
    dv_id: Optional[int] = None
    dv_dvcode: Optional[str] = Field(default=None, max_length=10)
    dv_distrcd: Optional[str] = Field(default=None, max_length=10)
    skip: Annotated[int, Field(ge=0)] = 0
    limit: Annotated[int, Field(ge=1, le=200)] = 10
    page: Annotated[Optional[int], Field(ge=1)] = 1
    search_key: Optional[str] = Field(default="", max_length=100)
    data: Optional[Union[DivisionalSecretariatCreate, DivisionalSecretariatUpdate]] = None


class DivisionalSecretariatManagementRequest(BaseModel):
    action: CRUDAction
    payload: DivisionalSecretariatRequestPayload


class DivisionalSecretariatManagementResponse(BaseModel):
    status: str
    message: str
    data: Optional[
        Union[DivisionalSecretariatOut, List[DivisionalSecretariatOut]]
    ] = None
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None
