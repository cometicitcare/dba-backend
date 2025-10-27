# app/schemas/bhikku_certification.py
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CRUDAction(str, Enum):
    CREATE = "CREATE"
    READ_ONE = "READ_ONE"
    READ_ALL = "READ_ALL"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class BhikkuCertificationBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    bc_issuedate: date
    bc_paydate: date
    bc_payamount: Decimal = Field(gt=0, max_digits=6, decimal_places=2)

    bc_reqstdate: Optional[date] = None
    bc_adminautho: Optional[str] = Field(default=None, max_length=200)
    bc_prtoptn: Optional[str] = Field(default=None, max_length=5)
    bc_usr: Optional[str] = Field(default=None, max_length=10)
    bc_admnusr: Optional[str] = Field(default=None, max_length=10)

    @model_validator(mode="after")
    def validate_chronology(self) -> "BhikkuCertificationBase":
        if self.bc_reqstdate and self.bc_issuedate and self.bc_reqstdate > self.bc_issuedate:
            raise ValueError("bc_reqstdate cannot be after bc_issuedate.")
        if self.bc_paydate and self.bc_issuedate and self.bc_paydate < self.bc_issuedate:
            raise ValueError("bc_paydate cannot be before bc_issuedate.")
        if (
            self.bc_reqstdate
            and self.bc_paydate
            and self.bc_paydate < self.bc_reqstdate
        ):
            raise ValueError("bc_paydate cannot be before bc_reqstdate.")
        return self


class BhikkuCertificationCreate(BhikkuCertificationBase):
    bc_regno: Optional[str] = Field(
        default=None, min_length=12, max_length=12
    )


class BhikkuCertificationUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    bc_regno: Optional[str] = Field(default=None, max_length=12)
    bc_issuedate: Optional[date] = None
    bc_paydate: Optional[date] = None
    bc_payamount: Optional[Decimal] = Field(default=None, gt=0, max_digits=6, decimal_places=2)

    bc_reqstdate: Optional[date] = None
    bc_adminautho: Optional[str] = Field(default=None, max_length=200)
    bc_prtoptn: Optional[str] = Field(default=None, max_length=5)
    bc_usr: Optional[str] = Field(default=None, max_length=10)
    bc_admnusr: Optional[str] = Field(default=None, max_length=10)
    bc_updated_by: Optional[str] = Field(default=None, max_length=25)

    @model_validator(mode="after")
    def validate_chronology(self) -> "BhikkuCertificationUpdate":
        if (
            self.bc_reqstdate
            and self.bc_issuedate
            and self.bc_reqstdate > self.bc_issuedate
        ):
            raise ValueError("bc_reqstdate cannot be after bc_issuedate.")
        if (
            self.bc_paydate
            and self.bc_issuedate
            and self.bc_paydate < self.bc_issuedate
        ):
            raise ValueError("bc_paydate cannot be before bc_issuedate.")
        if (
            self.bc_reqstdate
            and self.bc_paydate
            and self.bc_paydate < self.bc_reqstdate
        ):
            raise ValueError("bc_paydate cannot be before bc_reqstdate.")
        return self


class BhikkuCertification(BhikkuCertificationBase):
    model_config = ConfigDict(
        from_attributes=True, str_strip_whitespace=True, populate_by_name=True
    )

    bc_id: int
    bc_regno: str
    bc_version: datetime
    bc_is_deleted: bool
    bc_created_at: Optional[datetime] = None
    bc_updated_at: Optional[datetime] = None
    bc_created_by: Optional[str] = None
    bc_updated_by: Optional[str] = None
    bc_version_number: Optional[int] = None


class BhikkuCertificationRequestPayload(BaseModel):
    bc_id: Optional[int] = None
    bc_regno: Optional[str] = None
    skip: int = 0
    limit: int = 10
    page: Optional[int] = 1
    search_key: Optional[str] = ""
    data: Optional[Union[BhikkuCertificationCreate, BhikkuCertificationUpdate]] = None


class BhikkuCertificationManagementRequest(BaseModel):
    action: CRUDAction
    payload: BhikkuCertificationRequestPayload


class BhikkuCertificationManagementResponse(BaseModel):
    status: str
    message: str
    data: Optional[Union[BhikkuCertification, List[BhikkuCertification]]] = None
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None
