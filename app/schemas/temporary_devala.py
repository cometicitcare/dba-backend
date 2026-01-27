# app/schemas/temporary_devala.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Union
from enum import Enum


# --- Action Enum ---
class CRUDAction(str, Enum):
    CREATE = "CREATE"
    READ_ONE = "READ_ONE"
    READ_ALL = "READ_ALL"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


# --- Foreign Key Response Classes ---
class ProvinceResponse(BaseModel):
    """Province reference for responses"""
    cp_code: str
    cp_name: str

    model_config = ConfigDict(from_attributes=True)


class DistrictResponse(BaseModel):
    """District reference for responses"""
    dd_dcode: str
    dd_dname: str

    model_config = ConfigDict(from_attributes=True)


# --- Base Schema ---
class TemporaryDevalaBase(BaseModel):
    """Base schema with common fields for Temporary Devala"""
    td_name: str = Field(..., max_length=200, description="Devala/Shrine name (required)")
    td_address: Optional[str] = Field(None, max_length=500, description="Devala address")
    td_contact_number: Optional[str] = Field(None, max_length=15, description="Contact/mobile number")
    td_district: Optional[Union["DistrictResponse", str]] = Field(None, description="District (nested object or code string)")
    td_province: Optional[Union["ProvinceResponse", str]] = Field(None, description="Province (nested object or code string)")
    td_basnayake_nilame_name: Optional[str] = Field(None, max_length=200, description="Basnayake Nilame name")


# --- Create Schema ---
class TemporaryDevalaCreate(TemporaryDevalaBase):
    """Schema for creating a new temporary devala record"""
    pass


# --- Update Schema ---
class TemporaryDevalaUpdate(BaseModel):
    """Schema for updating an existing temporary devala record - all fields optional"""
    td_name: Optional[str] = Field(None, max_length=200, description="Devala/Shrine name")
    td_address: Optional[str] = Field(None, max_length=500, description="Devala address")
    td_contact_number: Optional[str] = Field(None, max_length=15, description="Contact/mobile number")
    td_district: Optional[str] = Field(None, max_length=100, description="District name or code")
    td_province: Optional[str] = Field(None, max_length=100, description="Province name or code")
    td_basnayake_nilame_name: Optional[str] = Field(None, max_length=200, description="Basnayake Nilame name")


# --- Response Schema ---
class TemporaryDevalaResponse(TemporaryDevalaBase):
    """Schema for temporary devala response"""
    td_id: int
    td_created_at: datetime
    td_created_by: Optional[str]
    td_updated_at: Optional[datetime]
    td_updated_by: Optional[str]

    model_config = ConfigDict(from_attributes=True)


# --- Management Payload Schema ---
class TemporaryDevalaPayload(BaseModel):
    """Payload for temporary devala management operations"""
    td_id: Optional[int] = Field(None, description="Temporary devala ID (required for READ_ONE, UPDATE, DELETE)")
    data: Optional[TemporaryDevalaCreate] = Field(None, description="Data for CREATE operation")
    updates: Optional[TemporaryDevalaUpdate] = Field(None, description="Updates for UPDATE operation")
    
    # Pagination and filters for READ_ALL
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=200, description="Maximum number of records to return")
    search: Optional[str] = Field(None, description="Search by name, address, or contact")


# --- Management Request Schema ---
class TemporaryDevalaManagementRequest(BaseModel):
    """Request schema for temporary devala management endpoint"""
    action: CRUDAction = Field(..., description="CRUD action to perform")
    payload: TemporaryDevalaPayload = Field(..., description="Payload data based on action")


# --- Management Response Schema ---
class TemporaryDevalaManagementResponse(BaseModel):
    """Response schema for temporary devala management endpoint"""
    status: str = Field(..., description="Response status (success/error)")
    message: str = Field(..., description="Response message")
    data: Optional[TemporaryDevalaResponse | list[TemporaryDevalaResponse] | dict] = Field(
        None, description="Response data (single record, list, or metadata)"
    )

    model_config = ConfigDict(from_attributes=True)
