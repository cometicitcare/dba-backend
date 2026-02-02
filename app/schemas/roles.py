from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class CRUDAction(str, Enum):
    CREATE = "CREATE"
    READ_ONE = "READ_ONE"
    READ_ALL = "READ_ALL"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class RoleBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    ro_role_name: Annotated[str, Field(min_length=1, max_length=50)]
    ro_description: Annotated[Optional[str], Field(default=None, max_length=200)] = None
    ro_is_system_role: bool = False


class RoleCreate(RoleBase):
    ro_created_by: Annotated[Optional[str], Field(default=None, min_length=1, max_length=25)] = None
    ro_updated_by: Annotated[Optional[str], Field(default=None, min_length=1, max_length=25)] = None


class RoleUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    ro_role_name: Annotated[Optional[str], Field(default=None, min_length=1, max_length=50)] = None
    ro_description: Annotated[Optional[str], Field(default=None, max_length=200)] = None
    ro_is_system_role: Optional[bool] = None
    ro_updated_by: Annotated[Optional[str], Field(default=None, min_length=1, max_length=25)] = None


class RoleOut(RoleBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    ro_role_id: str
    ro_is_active: bool
    ro_created_at: Optional[datetime] = None
    ro_updated_at: Optional[datetime] = None
    ro_created_by: Optional[str] = None
    ro_updated_by: Optional[str] = None
    ro_version_number: Optional[int] = None


class RoleRequestPayload(BaseModel):
    ro_role_id: Optional[str] = None
    skip: Annotated[int, Field(ge=0)] = 0
    limit: Annotated[int, Field(ge=1, le=200)] = 50
    page: Annotated[Optional[int], Field(ge=1)] = 1
    search_key: Optional[str] = Field(default=None, max_length=50)
    include_deleted: bool = False
    data: Optional[Union[RoleCreate, RoleUpdate]] = None


class RoleManagementRequest(BaseModel):
    action: CRUDAction
    payload: RoleRequestPayload


class RoleManagementResponse(BaseModel):
    status: str
    message: str
    data: Optional[Union[RoleOut, list[RoleOut]]] = None
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None
