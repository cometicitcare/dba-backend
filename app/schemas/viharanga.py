# app/schemas/viharanga.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List, Union, Any
from enum import Enum


# --- Action Enum ---
class CRUDAction(str, Enum):
    CREATE = "CREATE"
    READ_ONE = "READ_ONE"
    READ_ALL = "READ_ALL"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


# --- Viharanga Schemas ---
class ViharangaBase(BaseModel):
    """Base schema for Viharanga"""
    vg_code: str = Field(..., max_length=10, description="Viharanga code")
    vg_item: Optional[str] = Field(None, max_length=200, description="Viharanga description/name")


class ViharangaCreate(ViharangaBase):
    """Schema for creating a new Viharanga record"""
    pass


class ViharangaUpdate(BaseModel):
    """Schema for updating a Viharanga record - all fields optional"""
    vg_code: Optional[str] = Field(None, max_length=10, description="Viharanga code")
    vg_item: Optional[str] = Field(None, max_length=200, description="Viharanga description/name")


class ViharangaOut(ViharangaBase):
    """Schema for returning a Viharanga record"""
    model_config = ConfigDict(from_attributes=True)
    
    vg_id: int
    vg_version: Optional[datetime] = None
    vg_is_deleted: Optional[bool] = None
    vg_created_at: Optional[datetime] = None
    vg_updated_at: Optional[datetime] = None
    vg_created_by: Optional[str] = None
    vg_updated_by: Optional[str] = None
    vg_version_number: Optional[int] = None


class ViharangaInternal(ViharangaOut):
    """Schema for internal use with all fields"""
    pass


# --- Request/Response Wrapper Schemas ---
class ViharangaRequestPayload(BaseModel):
    """Payload for Viharanga management requests"""
    vg_id: Optional[int] = Field(None, description="Viharanga ID (for READ_ONE, UPDATE, DELETE)")
    vg_code: Optional[str] = Field(None, max_length=10, description="Viharanga code (alternative identifier)")
    data: Optional[Union[ViharangaCreate, ViharangaUpdate, Any]] = None
    search_key: Optional[str] = Field(None, description="Search keyword")
    page: Optional[int] = Field(None, ge=1, description="Page number for pagination")
    skip: Optional[int] = Field(0, ge=0, description="Number of records to skip")
    limit: Optional[int] = Field(10, ge=1, le=100, description="Number of records to fetch")


class ViharangaManagementRequest(BaseModel):
    """Complete request for Viharanga management operations"""
    action: CRUDAction
    payload: ViharangaRequestPayload


class ViharangaManagementResponse(BaseModel):
    """Response for Viharanga management operations"""
    model_config = ConfigDict(from_attributes=True)
    
    status: str = Field(..., description="Response status: 'success' or 'error'")
    message: str = Field(..., description="Response message")
    data: Optional[Union[ViharangaOut, List[ViharangaOut], Any]] = None
    # Optional pagination fields (only for READ_ALL)
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None
