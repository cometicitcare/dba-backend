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


class BhikkuCategoryBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    cc_code: str = Field(..., max_length=5)
    cc_catogry: Optional[str] = Field(default=None, max_length=200)


class BhikkuCategoryCreate(BhikkuCategoryBase):
    cc_created_by: Optional[str] = Field(default=None, max_length=25)
    cc_updated_by: Optional[str] = Field(default=None, max_length=25)


class BhikkuCategoryUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    cc_code: Optional[str] = Field(default=None, max_length=5)
    cc_catogry: Optional[str] = Field(default=None, max_length=200)
    cc_updated_by: Optional[str] = Field(default=None, max_length=25)


class BhikkuCategoryOut(BhikkuCategoryBase):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    cc_id: int
    cc_version: Optional[datetime] = None
    cc_is_deleted: bool
    cc_created_at: Optional[datetime] = None
    cc_updated_at: Optional[datetime] = None
    cc_created_by: Optional[str] = None
    cc_updated_by: Optional[str] = None
    cc_version_number: Optional[int] = None


class BhikkuCategoryRequestPayload(BaseModel):
    cc_id: Optional[int] = None
    cc_code: Optional[str] = Field(default=None, max_length=5)
    skip: Annotated[int, Field(ge=0)] = 0
    limit: Annotated[int, Field(ge=1, le=200)] = 10
    page: Annotated[Optional[int], Field(ge=1)] = 1
    search_key: Optional[str] = Field(default="", max_length=100)
    data: Optional[Union[BhikkuCategoryCreate, BhikkuCategoryUpdate]] = None


class BhikkuCategoryManagementRequest(BaseModel):
    action: CRUDAction
    payload: BhikkuCategoryRequestPayload


class BhikkuCategoryManagementResponse(BaseModel):
    status: str
    message: str
    data: Optional[Union[BhikkuCategoryOut, List[BhikkuCategoryOut]]] = None
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None
