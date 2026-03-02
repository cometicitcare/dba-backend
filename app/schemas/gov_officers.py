# app/schemas/gov_officers.py
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, List, Optional, Union

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ── Action Enum ────────────────────────────────────────────────────────────────
class GovOfficerAction(str, Enum):
    CREATE = "CREATE"
    READ_ONE = "READ_ONE"
    READ_ALL = "READ_ALL"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


# ── Base ───────────────────────────────────────────────────────────────────────
class GovOfficerBase(BaseModel):
    go_title: str = Field(..., max_length=100, description="Title (e.g. Mr., Mrs., Dr.)")
    go_first_name: str = Field(..., max_length=100, description="First name")
    go_last_name: str = Field(..., max_length=100, description="Last name")
    go_contact_number: str = Field(..., max_length=20, description="Contact phone number")
    go_email: Optional[str] = Field(None, max_length=255, description="Email address (optional)")
    go_address: str = Field(..., max_length=500, description="Address")
    go_id_number: Optional[str] = Field(None, max_length=50, description="National ID / NIC (optional)")


# ── Create ─────────────────────────────────────────────────────────────────────
class GovOfficerCreate(GovOfficerBase):
    pass


# ── Update (all optional) ──────────────────────────────────────────────────────
class GovOfficerUpdate(BaseModel):
    go_title: Optional[str] = Field(None, max_length=100)
    go_first_name: Optional[str] = Field(None, max_length=100)
    go_last_name: Optional[str] = Field(None, max_length=100)
    go_contact_number: Optional[str] = Field(None, max_length=20)
    go_email: Optional[str] = Field(None, max_length=255)
    go_address: Optional[str] = Field(None, max_length=500)
    go_id_number: Optional[str] = Field(None, max_length=50)


# ── Response ───────────────────────────────────────────────────────────────────
class GovOfficerResponse(BaseModel):
    go_id: int
    go_title: str
    go_first_name: str
    go_last_name: str
    go_contact_number: str
    go_email: Optional[str] = None
    go_address: str
    go_id_number: Optional[str] = None

    # audit
    go_is_deleted: Optional[bool] = False
    go_created_at: Optional[datetime] = None
    go_updated_at: Optional[datetime] = None
    go_created_by: Optional[str] = None
    go_updated_by: Optional[str] = None
    go_version_number: Optional[int] = 1

    model_config = ConfigDict(from_attributes=True)


# ── Management request payload ─────────────────────────────────────────────────
class GovOfficerRequestPayload(BaseModel):
    # READ_ONE / UPDATE / DELETE
    go_id: Optional[int] = None
    # READ_ALL pagination & search
    page: Optional[int] = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=1000)
    search_key: Optional[str] = Field(default="", max_length=200)
    # CREATE / UPDATE body
    data: Optional[Union[GovOfficerCreate, GovOfficerUpdate]] = None


# ── Management request ─────────────────────────────────────────────────────────
class GovOfficerManagementRequest(BaseModel):
    action: GovOfficerAction
    payload: GovOfficerRequestPayload


# ── Management response ────────────────────────────────────────────────────────
class GovOfficerManagementResponse(BaseModel):
    status: str
    message: str
    data: Optional[Any] = None
    total: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None
