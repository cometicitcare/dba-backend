# app/schemas/temporary_bhikku.py
from pydantic import BaseModel, Field, ConfigDict
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
class TemporaryBhikkuBase(BaseModel):
    """Base schema with common fields for Temporary Bhikku"""
    tb_name: str = Field(..., max_length=100, description="Bhikku name (required)")
    tb_id_number: Optional[str] = Field(None, max_length=20, description="National ID or identification number")
    tb_contact_number: Optional[str] = Field(None, max_length=15, description="Contact/mobile number")
    tb_samanera_name: Optional[str] = Field(None, max_length=100, description="Samanera (novice) name")
    tb_address: Optional[str] = Field(None, max_length=500, description="Residential address")
    tb_living_temple: Optional[str] = Field(None, max_length=200, description="Current living temple/vihara")
    # Additional fields from actual payload
    tb_bname: Optional[str] = Field(None, max_length=100, description="Bhikku name (alternate field)")
    tb_district: Optional[str] = Field(None, max_length=50, description="District")
    tb_province: Optional[str] = Field(None, max_length=50, description="Province")
    tb_vihara_name: Optional[str] = Field(None, max_length=200, description="Vihara name (alternate field)")


# --- Create Schema ---
class TemporaryBhikkuCreate(TemporaryBhikkuBase):
    """Schema for creating a new temporary bhikku record"""
    pass


# --- Update Schema ---
class TemporaryBhikkuUpdate(BaseModel):
    """Schema for updating an existing temporary bhikku record - all fields optional"""
    tb_name: Optional[str] = Field(None, max_length=100, description="Bhikku name")
    tb_id_number: Optional[str] = Field(None, max_length=20, description="National ID or identification number")
    tb_contact_number: Optional[str] = Field(None, max_length=15, description="Contact/mobile number")
    tb_samanera_name: Optional[str] = Field(None, max_length=100, description="Samanera (novice) name")
    tb_address: Optional[str] = Field(None, max_length=500, description="Residential address")
    tb_living_temple: Optional[str] = Field(None, max_length=200, description="Current living temple/vihara")


# --- Response Schema ---
class TemporaryBhikkuResponse(TemporaryBhikkuBase):
    """Schema for temporary bhikku response"""
    tb_id: int
    tb_created_at: datetime
    tb_created_by: Optional[str]
    tb_updated_at: Optional[datetime]
    tb_updated_by: Optional[str]

    model_config = ConfigDict(from_attributes=True)


# --- Management Payload Schema ---
class TemporaryBhikkuPayload(BaseModel):
    """Payload for temporary bhikku management operations"""
    tb_id: Optional[int] = Field(None, description="Temporary bhikku ID (required for READ_ONE, UPDATE, DELETE)")
    data: Optional[TemporaryBhikkuCreate] = Field(None, description="Data for CREATE operation")
    updates: Optional[TemporaryBhikkuUpdate] = Field(None, description="Updates for UPDATE operation")
    
    # Pagination and filters for READ_ALL
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=200, description="Maximum number of records to return")
    search: Optional[str] = Field(None, description="Search by name, ID number, or contact")


# --- Management Request Schema ---
class TemporaryBhikkuManagementRequest(BaseModel):
    """Request schema for temporary bhikku management endpoint"""
    action: CRUDAction = Field(..., description="CRUD action to perform")
    payload: TemporaryBhikkuPayload = Field(..., description="Payload data based on action")


# --- Management Response Schema ---
class TemporaryBhikkuManagementResponse(BaseModel):
    """Response schema for temporary bhikku management endpoint"""
    status: str = Field(..., description="Response status (success/error)")
    message: str = Field(..., description="Response message")
    data: Optional[TemporaryBhikkuResponse | list[TemporaryBhikkuResponse] | dict] = Field(
        None, description="Response data (single record, list, or metadata)"
    )

    model_config = ConfigDict(from_attributes=True)
