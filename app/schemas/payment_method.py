# app/schemas/payment_method.py
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


class PaymentMethodBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    pm_method_name: str = Field(min_length=1, max_length=30)
    pm_is_active: Optional[bool] = True


class PaymentMethodCreate(PaymentMethodBase):
    pass


class PaymentMethodUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    pm_method_name: Optional[str] = Field(default=None, min_length=1, max_length=30)
    pm_is_active: Optional[bool] = None


class PaymentMethod(PaymentMethodBase):
    model_config = ConfigDict(
        from_attributes=True, str_strip_whitespace=True, populate_by_name=True
    )

    pm_id: int
    pm_code: str
    pm_version: datetime
    pm_is_deleted: bool
    pm_created_at: Optional[datetime] = None
    pm_updated_at: Optional[datetime] = None
    pm_created_by: Optional[str] = None
    pm_updated_by: Optional[str] = None
    pm_version_number: Optional[int] = None


class PaymentMethodRequestPayload(BaseModel):
    pm_id: Optional[int] = None
    pm_code: Optional[str] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1, le=200)
    page: Optional[int] = Field(default=1, ge=1)
    search_key: Optional[str] = ""
    data: Optional[Union[PaymentMethodCreate, PaymentMethodUpdate]] = None


class PaymentMethodManagementRequest(BaseModel):
    action: CRUDAction
    payload: PaymentMethodRequestPayload


class PaymentMethodManagementResponse(BaseModel):
    status: str
    message: str
    data: Optional[Union[PaymentMethod, List[PaymentMethod]]] = None
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None
