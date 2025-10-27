# app/schemas/certificate_change.py
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


class CertificateChangeBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    ch_dofchg: date
    ch_prt: str = Field(min_length=1, max_length=5)
    ch_regno: str = Field(min_length=1, max_length=200)
    ch_autho: str = Field(min_length=1, max_length=50)
    ch_admnusr: str = Field(min_length=1, max_length=50)
    ch_dptusr: str = Field(min_length=1, max_length=50)


class CertificateChangeCreate(CertificateChangeBase):
    pass


class CertificateChangeUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    ch_dofchg: Optional[date] = None
    ch_prt: Optional[str] = Field(default=None, min_length=1, max_length=5)
    ch_regno: Optional[str] = Field(default=None, min_length=1, max_length=200)
    ch_autho: Optional[str] = Field(default=None, min_length=1, max_length=50)
    ch_admnusr: Optional[str] = Field(default=None, min_length=1, max_length=50)
    ch_dptusr: Optional[str] = Field(default=None, min_length=1, max_length=50)


class CertificateChange(CertificateChangeBase):
    model_config = ConfigDict(
        from_attributes=True, str_strip_whitespace=True, populate_by_name=True
    )

    ch_id: int
    ch_version: datetime
    ch_is_deleted: bool
    ch_created_at: Optional[datetime] = None
    ch_updated_at: Optional[datetime] = None
    ch_created_by: Optional[str] = None
    ch_updated_by: Optional[str] = None
    ch_version_number: Optional[int] = None


class CertificateChangeRequestPayload(BaseModel):
    ch_id: Optional[int] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1, le=200)
    page: Optional[int] = Field(default=1, ge=1)
    search_key: Optional[str] = ""
    data: Optional[
        Union[CertificateChangeCreate, CertificateChangeUpdate]
    ] = None


class CertificateChangeManagementRequest(BaseModel):
    action: CRUDAction
    payload: CertificateChangeRequestPayload


class CertificateChangeManagementResponse(BaseModel):
    status: str
    message: str
    data: Optional[
        Union[CertificateChange, List[CertificateChange]]
    ] = None
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None
