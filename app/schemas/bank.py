# app/schemas/bank.py
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


class BankBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    bk_bcode: str = Field(min_length=1, max_length=10)
    bk_bname: Optional[str] = Field(default=None, max_length=200)


class BankCreate(BankBase):
    pass


class BankUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    bk_bcode: Optional[str] = Field(default=None, min_length=1, max_length=10)
    bk_bname: Optional[str] = Field(default=None, max_length=200)


class Bank(BankBase):
    model_config = ConfigDict(
        from_attributes=True, str_strip_whitespace=True, populate_by_name=True
    )

    bk_id: int
    bk_version: datetime
    bk_is_deleted: bool
    bk_created_at: Optional[datetime] = None
    bk_updated_at: Optional[datetime] = None
    bk_version_number: Optional[int] = None
    bk_created_by: Optional[str] = None
    bk_updated_by: Optional[str] = None


class BankRequestPayload(BaseModel):
    bk_id: Optional[int] = None
    bk_bcode: Optional[str] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1, le=200)
    page: Optional[int] = Field(default=1, ge=1)
    search_key: Optional[str] = ""
    data: Optional[Union[BankCreate, BankUpdate]] = None


class BankManagementRequest(BaseModel):
    action: CRUDAction
    payload: BankRequestPayload


class BankManagementResponse(BaseModel):
    status: str
    message: str
    data: Optional[Union[Bank, List[Bank]]] = None
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None
