# app/schemas/certificate.py
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


class CertificateBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    cd_code: str = Field(min_length=1, max_length=12)
    cd_stat: str = Field(min_length=1, max_length=5)

    cd_remarks: Optional[str] = Field(default=None, max_length=50)
    cd_initdate: Optional[date] = None
    cd_currstatupddat: Optional[date] = None
    cd_url: Optional[str] = Field(default=None, max_length=50)
    cd_cat: Optional[str] = Field(default=None, max_length=5)


class CertificateCreate(CertificateBase):
    pass


class CertificateUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    cd_code: Optional[str] = Field(default=None, max_length=12)
    cd_stat: Optional[str] = Field(default=None, max_length=5)
    cd_remarks: Optional[str] = Field(default=None, max_length=50)
    cd_initdate: Optional[date] = None
    cd_currstatupddat: Optional[date] = None
    cd_url: Optional[str] = Field(default=None, max_length=50)
    cd_cat: Optional[str] = Field(default=None, max_length=5)


class Certificate(CertificateBase):
    model_config = ConfigDict(
        from_attributes=True, str_strip_whitespace=True, populate_by_name=True
    )

    cd_id: int
    cd_version: datetime
    cd_is_deleted: bool
    cd_created_at: Optional[datetime] = None
    cd_updated_at: Optional[datetime] = None
    cd_created_by: Optional[str] = None
    cd_updated_by: Optional[str] = None
    cd_version_number: Optional[int] = None


class CertificateRequestPayload(BaseModel):
    cd_id: Optional[int] = None
    cd_code: Optional[str] = None
    skip: int = 0
    limit: int = 10
    page: Optional[int] = 1
    search_key: Optional[str] = ""
    data: Optional[Union[CertificateCreate, CertificateUpdate]] = None


class CertificateManagementRequest(BaseModel):
    action: CRUDAction
    payload: CertificateRequestPayload


class CertificateManagementResponse(BaseModel):
    status: str
    message: str
    data: Optional[Union[Certificate, List[Certificate]]] = None
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None

