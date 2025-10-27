# app/schemas/nilame.py
from datetime import date, datetime
from enum import Enum
from typing import Annotated, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class CRUDAction(str, Enum):
    CREATE = "CREATE"
    READ_ONE = "READ_ONE"
    READ_ALL = "READ_ALL"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class NilameBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    kr_kname: Optional[str] = Field(default=None, max_length=20)
    kr_nic: Optional[str] = Field(default=None, max_length=20)
    kr_nic_issue_date: Optional[date] = None
    kr_dofb: Optional[date] = None
    kr_addrs: Optional[str] = Field(default=None, max_length=100)
    kr_grndiv: Optional[str] = Field(default=None, max_length=10)
    kr_trn: Optional[str] = Field(default=None, max_length=10)


class NilameCreate(NilameBase):
    kr_krn: Optional[str] = Field(default=None, max_length=20)


class NilameUpdate(NilameBase):
    pass


class Nilame(NilameBase):
    kr_krn: str
    model_config = ConfigDict(
        from_attributes=True, str_strip_whitespace=True, populate_by_name=True
    )

    kr_id: int
    kr_version: datetime
    kr_is_deleted: bool
    kr_created_at: Optional[datetime] = None
    kr_updated_at: Optional[datetime] = None
    kr_created_by: Optional[str] = None
    kr_updated_by: Optional[str] = None
    kr_version_number: Optional[int] = None


class NilameRequestPayload(BaseModel):
    kr_id: Optional[int] = None
    kr_krn: Optional[str] = None
    skip: Annotated[int, Field(ge=0)] = 0
    limit: Annotated[int, Field(ge=1, le=200)] = 10
    page: Annotated[Optional[int], Field(ge=1)] = 1
    search_key: Optional[str] = Field(default="", max_length=100)
    data: Optional[Union[NilameCreate, NilameUpdate]] = None


class NilameManagementRequest(BaseModel):
    action: CRUDAction
    payload: NilameRequestPayload


class NilameManagementResponse(BaseModel):
    status: str
    message: str
    data: Optional[Union[Nilame, List[Nilame]]] = None
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None
