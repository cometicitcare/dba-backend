# app/schemas/bhikku_summary.py
from datetime import date, datetime
from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class CRUDAction(str, Enum):
    CREATE = "CREATE"
    READ_ONE = "READ_ONE"
    READ_ALL = "READ_ALL"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class BhikkuSummaryBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    bs_regn: str = Field(min_length=1, max_length=12)
    bs_mahananame: Optional[str] = Field(default=None, max_length=50)
    bs_birthpls: Optional[str] = Field(default=None, max_length=50)
    bs_gihiname: Optional[str] = Field(default=None, max_length=50)
    bs_dofb: Optional[date] = None
    bs_fathrname: Optional[str] = Field(default=None, max_length=50)
    bs_mahanadate: Optional[date] = None
    bs_teacher: Optional[str] = Field(default=None, max_length=50)
    bs_teachadrs: Optional[str] = Field(default=None, max_length=200)
    bs_mhanavh: Optional[str] = Field(default=None, max_length=30)
    bs_livetemple: Optional[str] = Field(default=None, max_length=30)
    bs_viharadipathi: Optional[str] = Field(default=None, max_length=50)
    bs_pname: Optional[str] = Field(default=None, max_length=25)
    bs_nname: Optional[str] = Field(default=None, max_length=25)
    bs_nikayanayaka: Optional[str] = Field(default=None, max_length=100)
    bs_effctdate: Optional[date] = None
    bs_curstatus: Optional[str] = Field(default=None, max_length=30)
    bs_catogry: Optional[str] = Field(default=None, max_length=30)
    bs_vadescrdtls: Optional[str] = None
    bs_qualifications: Optional[str] = None


class BhikkuSummaryCreate(BhikkuSummaryBase):
    pass


class BhikkuSummaryUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    bs_mahananame: Optional[str] = Field(default=None, max_length=50)
    bs_birthpls: Optional[str] = Field(default=None, max_length=50)
    bs_gihiname: Optional[str] = Field(default=None, max_length=50)
    bs_dofb: Optional[date] = None
    bs_fathrname: Optional[str] = Field(default=None, max_length=50)
    bs_mahanadate: Optional[date] = None
    bs_teacher: Optional[str] = Field(default=None, max_length=50)
    bs_teachadrs: Optional[str] = Field(default=None, max_length=200)
    bs_mhanavh: Optional[str] = Field(default=None, max_length=30)
    bs_livetemple: Optional[str] = Field(default=None, max_length=30)
    bs_viharadipathi: Optional[str] = Field(default=None, max_length=50)
    bs_pname: Optional[str] = Field(default=None, max_length=25)
    bs_nname: Optional[str] = Field(default=None, max_length=25)
    bs_nikayanayaka: Optional[str] = Field(default=None, max_length=100)
    bs_effctdate: Optional[date] = None
    bs_curstatus: Optional[str] = Field(default=None, max_length=30)
    bs_catogry: Optional[str] = Field(default=None, max_length=30)
    bs_vadescrdtls: Optional[str] = None
    bs_qualifications: Optional[str] = None


class BhikkuSummary(BhikkuSummaryBase):
    model_config = ConfigDict(
        from_attributes=True, str_strip_whitespace=True, populate_by_name=True
    )

    bs_version: datetime
    bs_is_deleted: bool
    bs_created_at: Optional[datetime] = None
    bs_updated_at: Optional[datetime] = None
    bs_created_by: Optional[str] = None
    bs_updated_by: Optional[str] = None
    bs_version_number: Optional[int] = None


class BhikkuSummaryRequestPayload(BaseModel):
    bs_regn: Optional[str] = None
    skip: int = 0
    limit: int = 10
    page: Optional[int] = 1
    search_key: Optional[str] = ""
    data: Optional[Union[BhikkuSummaryCreate, BhikkuSummaryUpdate]] = None


class BhikkuSummaryManagementRequest(BaseModel):
    action: CRUDAction
    payload: BhikkuSummaryRequestPayload


class BhikkuSummaryManagementResponse(BaseModel):
    status: str
    message: str
    data: Optional[Union[BhikkuSummary, List[BhikkuSummary]]] = None
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None

