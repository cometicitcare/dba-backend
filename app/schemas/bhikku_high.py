# app/schemas/bhikku_high.py
from datetime import date, datetime
from enum import Enum
from typing import Optional, Union, List

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CRUDAction(str, Enum):
    CREATE = "CREATE"
    READ_ONE = "READ_ONE"
    READ_ALL = "READ_ALL"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class BhikkuHighBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    bhr_regn: str = Field(min_length=1, max_length=12)
    bhr_reqstdate: date
    bhr_currstat: str = Field(min_length=1, max_length=5)
    bhr_parshawaya: str = Field(min_length=1, max_length=10)
    bhr_livtemple: str = Field(min_length=1, max_length=10)

    bhr_samanera_serial_no: Optional[str] = Field(default=None, max_length=20)
    bhr_mahanaacharyacd: Optional[str] = Field(default=None, max_length=12)
    bhr_multi_mahanaacharyacd: Optional[str] = Field(default=None, max_length=200)
    bhr_karmacharya: Optional[str] = Field(default=None, max_length=12)
    bhr_multi_karmacharya: Optional[str] = Field(default=None, max_length=200)
    bhr_ordination_temple: Optional[str] = Field(default=None, max_length=10)
    bhr_mahanadate: Optional[date] = None
    bhr_effctdate: Optional[date] = None
    bhr_gndiv: Optional[str] = Field(default=None, max_length=10)
    bhr_remarks: Optional[str] = Field(default=None, max_length=100)
    bhr_mahananame: Optional[str] = Field(default=None, max_length=50)
    bhr_cat: Optional[str] = Field(default=None, max_length=5)
    bhr_mobile: Optional[str] = Field(default=None, max_length=10)
    bhr_email: Optional[EmailStr] = None

class BhikkuHighCreate(BhikkuHighBase):
    pass


class BhikkuHighUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    bhr_regn: Optional[str] = Field(default=None, max_length=12)
    bhr_reqstdate: Optional[date] = None
    bhr_currstat: Optional[str] = Field(default=None, max_length=5)
    bhr_parshawaya: Optional[str] = Field(default=None, max_length=10)
    bhr_livtemple: Optional[str] = Field(default=None, max_length=10)

    bhr_samanera_serial_no: Optional[str] = Field(default=None, max_length=20)
    bhr_mahanaacharyacd: Optional[str] = Field(default=None, max_length=12)
    bhr_multi_mahanaacharyacd: Optional[str] = Field(default=None, max_length=200)
    bhr_karmacharya: Optional[str] = Field(default=None, max_length=12)
    bhr_multi_karmacharya: Optional[str] = Field(default=None, max_length=200)
    bhr_ordination_temple: Optional[str] = Field(default=None, max_length=10)
    bhr_mahanadate: Optional[date] = None
    bhr_effctdate: Optional[date] = None
    bhr_gndiv: Optional[str] = Field(default=None, max_length=10)
    bhr_remarks: Optional[str] = Field(default=None, max_length=100)
    bhr_mahananame: Optional[str] = Field(default=None, max_length=50)
    bhr_cat: Optional[str] = Field(default=None, max_length=5)
    bhr_mobile: Optional[str] = Field(default=None, max_length=10)
    bhr_email: Optional[EmailStr] = None


class BhikkuHigh(BhikkuHighBase):
    model_config = ConfigDict(
        from_attributes=True, str_strip_whitespace=True, populate_by_name=True
    )

    bhr_id: int
    bhr_version: datetime
    bhr_is_deleted: bool
    bhr_created_at: Optional[datetime] = None
    bhr_updated_at: Optional[datetime] = None
    bhr_created_by: Optional[str] = None
    bhr_updated_by: Optional[str] = None
    bhr_version_number: Optional[int] = None


class BhikkuHighRequestPayload(BaseModel):
    bhr_id: Optional[int] = None
    bhr_regn: Optional[str] = None
    skip: int = 0
    limit: int = 10
    page: Optional[int] = 1
    search_key: Optional[str] = ""
    data: Optional[Union[BhikkuHighCreate, BhikkuHighUpdate]] = None


class BhikkuHighManagementRequest(BaseModel):
    action: CRUDAction
    payload: BhikkuHighRequestPayload


class BhikkuHighManagementResponse(BaseModel):
    status: str
    message: str
    data: Optional[Union[BhikkuHigh, List[BhikkuHigh]]] = None
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None
