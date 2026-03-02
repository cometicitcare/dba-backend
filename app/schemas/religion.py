# app/schemas/religion.py
from datetime import datetime
from enum import Enum
from typing import Annotated, Any, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CRUDAction(str, Enum):
    CREATE = "CREATE"
    READ_ONE = "READ_ONE"
    READ_ALL = "READ_ALL"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class ReligionBase(BaseModel):
    rl_descr: Annotated[Optional[str], Field(default=None, max_length=30)] = None
    rl_is_deleted: bool = False
    rl_created_at: Optional[datetime] = None
    rl_updated_at: Optional[datetime] = None
    rl_created_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    rl_updated_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    rl_version_number: Annotated[int, Field(ge=1)] = 1

    @field_validator("rl_descr", "rl_created_by", "rl_updated_by", mode="before")
    @classmethod
    def _strip_strings(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            if value == "":
                return None
        return value


class ReligionCreate(BaseModel):
    rl_descr: Annotated[Optional[str], Field(default=None, max_length=30)] = None

    @field_validator("rl_descr", mode="before")
    @classmethod
    def _strip_descr(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class ReligionUpdate(BaseModel):
    rl_descr: Annotated[Optional[str], Field(default=None, max_length=30)] = None

    @field_validator("rl_descr", mode="before")
    @classmethod
    def _strip_descr(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class ReligionOut(ReligionBase):
    model_config = ConfigDict(from_attributes=True)

    rl_id: int
    rl_code: str


class ReligionRequestPayload(BaseModel):
    rl_id: Optional[int] = None
    rl_code: Annotated[Optional[str], Field(default=None, max_length=10)] = None
    skip: Annotated[int, Field(ge=0)] = 0
    limit: Annotated[int, Field(ge=1, le=200)] = 10
    page: Annotated[Optional[int], Field(default=1, ge=1)] = 1
    search_key: Annotated[Optional[str], Field(default=None, max_length=30)] = None
    data: Optional[Union[ReligionCreate, ReligionUpdate]] = None

    @field_validator("rl_code", "search_key", mode="before")
    @classmethod
    def _strip_strings(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class ReligionManagementRequest(BaseModel):
    action: CRUDAction
    payload: ReligionRequestPayload


class ReligionManagementResponse(BaseModel):
    status: str
    message: str
    data: Optional[Union[ReligionOut, List[ReligionOut], Any]] = None
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None
