# app/schemas/sasanarakshaka.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from enum import Enum


# --- Action Enum ---
class CRUDAction(str, Enum):
    CREATE = "CREATE"
    READ_ONE = "READ_ONE"
    READ_ALL = "READ_ALL"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


# --- Base Schema ---
class SasanarakshakaBalaMandalayaBase(BaseModel):
    """Base schema for Sasanarakshaka Bala Mandalaya with common fields"""
    sr_ssbmcode: str
    sr_dvcd: str
    sr_ssbname: Optional[str] = None
    sr_sbmnayakahimi: Optional[str] = None


# --- Create Schema ---
class SasanarakshakaBalaMandalayaCreate(SasanarakshakaBalaMandalayaBase):
    """Schema for creating a new Sasanarakshaka Bala Mandalaya record"""
    pass


# --- Update Schema ---
class SasanarakshakaBalaMandalayaUpdate(BaseModel):
    """Schema for updating a Sasanarakshaka Bala Mandalaya record - all fields optional"""
    sr_ssbmcode: Optional[str] = None
    sr_dvcd: Optional[str] = None
    sr_ssbname: Optional[str] = None
    sr_sbmnayakahimi: Optional[str] = None


# --- Response Schema ---
class SasanarakshakaBalaMandalayaResponse(SasanarakshakaBalaMandalayaBase):
    """Schema for Sasanarakshaka Bala Mandalaya responses"""
    sr_id: int
    sr_version: datetime
    sr_is_deleted: Optional[bool] = False
    sr_created_at: Optional[datetime] = None
    sr_updated_at: Optional[datetime] = None
    sr_created_by: Optional[str] = None
    sr_updated_by: Optional[str] = None
    sr_version_number: Optional[int] = 1

    model_config = ConfigDict(from_attributes=True)


# --- List Response Schema ---
class SasanarakshakaBalaMandalayaListResponse(BaseModel):
    """Response schema for list of Sasanarakshaka Bala Mandalaya records"""
    status: str
    message: str
    data: list[SasanarakshakaBalaMandalayaResponse]
    total: int
    page: int
    limit: int


# --- Single Response Schema ---
class SasanarakshakaBalaMandalayaSingleResponse(BaseModel):
    """Response schema for a single Sasanarakshaka Bala Mandalaya record"""
    status: str
    message: str
    data: SasanarakshakaBalaMandalayaResponse


# --- Delete Response Schema ---
class SasanarakshakaBalaMandalayaDeleteResponse(BaseModel):
    """Response schema for delete operation"""
    status: str
    message: str
    data: dict
