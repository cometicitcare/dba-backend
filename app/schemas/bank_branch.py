# app/schemas/bank_branch.py
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


class BankBranchBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    bb_bcode: str = Field(min_length=1, max_length=10)
    bb_bbcode: str = Field(min_length=1, max_length=10)
    bb_brname: Optional[str] = Field(default=None, max_length=200)


class BankBranchCreate(BankBranchBase):
    pass


class BankBranchUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    bb_bcode: Optional[str] = Field(default=None, min_length=1, max_length=10)
    bb_bbcode: Optional[str] = Field(default=None, min_length=1, max_length=10)
    bb_brname: Optional[str] = Field(default=None, max_length=200)


class BankBranch(BankBranchBase):
    model_config = ConfigDict(
        from_attributes=True, str_strip_whitespace=True, populate_by_name=True
    )

    bb_id: int
    bb_version: datetime
    bb_is_deleted: bool
    bb_created_at: Optional[datetime] = None
    bb_updated_at: Optional[datetime] = None
    bb_version_number: Optional[int] = None
    bb_created_by: Optional[str] = None
    bb_updated_by: Optional[str] = None


class BankBranchRequestPayload(BaseModel):
    bb_id: Optional[int] = None
    bb_bbcode: Optional[str] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1, le=200)
    page: Optional[int] = Field(default=1, ge=1)
    search_key: Optional[str] = ""
    data: Optional[Union[BankBranchCreate, BankBranchUpdate]] = None


class BankBranchManagementRequest(BaseModel):
    action: CRUDAction
    payload: BankBranchRequestPayload


class BankBranchManagementResponse(BaseModel):
    status: str
    message: str
    data: Optional[Union[BankBranch, List[BankBranch]]] = None
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None
