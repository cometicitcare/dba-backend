from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class CRUDAction(str, Enum):
    CREATE = "CREATE"
    READ_ONE = "READ_ONE"
    READ_ALL = "READ_ALL"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class AuditLogBase(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        populate_by_name=True,
    )

    al_table_name: str
    al_record_id: str
    al_operation: str
    al_old_values: Optional[dict[str, Any]] = None
    al_new_values: Optional[dict[str, Any]] = None
    al_changed_fields: Optional[list[str]] = None
    al_user_id: Optional[str] = None
    al_session_id: Optional[str] = None
    al_ip_address: Optional[str] = None
    al_user_agent: Optional[str] = None
    al_transaction_id: Optional[str] = None


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogUpdate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        populate_by_name=True,
    )

    al_old_values: Optional[dict[str, Any]] = None
    al_new_values: Optional[dict[str, Any]] = None
    al_changed_fields: Optional[list[str]] = None
    al_session_id: Optional[str] = None
    al_ip_address: Optional[str] = None
    al_user_agent: Optional[str] = None
    al_transaction_id: Optional[str] = None


class AuditLogOut(AuditLogBase):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    al_id: int
    al_timestamp: datetime


class AuditLogFilters(BaseModel):
    al_id: Optional[int] = None
    al_table_name: Optional[str] = Field(default=None, max_length=50)
    al_record_id: Optional[str] = Field(default=None, max_length=50)
    al_operation: Optional[str] = Field(default=None, max_length=10)
    al_user_id: Optional[str] = Field(default=None, max_length=10)
    al_transaction_id: Optional[str] = Field(default=None, max_length=100)
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None
    search: Optional[str] = Field(default=None, max_length=100)
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=200)
    page: Optional[int] = Field(default=1, ge=1)


class AuditLogRequestPayload(BaseModel):
    al_id: Optional[int] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=200)
    page: Optional[int] = Field(default=1, ge=1)
    search: Optional[str] = Field(default=None, max_length=100)
    al_table_name: Optional[str] = Field(default=None, max_length=50)
    al_record_id: Optional[str] = Field(default=None, max_length=50)
    al_operation: Optional[str] = Field(default=None, max_length=10)
    al_user_id: Optional[str] = Field(default=None, max_length=10)
    al_transaction_id: Optional[str] = Field(default=None, max_length=100)
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None
    data: Optional[Union[AuditLogCreate, AuditLogUpdate]] = None


class AuditLogManagementRequest(BaseModel):
    action: CRUDAction
    payload: AuditLogRequestPayload


class AuditLogManagementResponse(BaseModel):
    status: str
    message: str
    data: Optional[Union[AuditLogOut, list[AuditLogOut]]] = None
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None
