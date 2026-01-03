# app/schemas/temporary_silmatha.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, date
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
class TemporarySilmathaBase(BaseModel):
    """Base schema with common fields for Temporary Silmatha"""
    ts_name: str = Field(..., max_length=200, description="Silmatha/Nun name (required)")
    ts_nic: Optional[str] = Field(None, max_length=15, description="NIC number")
    ts_contact_number: Optional[str] = Field(None, max_length=15, description="Contact/mobile number")
    ts_address: Optional[str] = Field(None, max_length=500, description="Address")
    ts_district: Optional[str] = Field(None, max_length=100, description="District name or code")
    ts_province: Optional[str] = Field(None, max_length=100, description="Province name or code")
    ts_arama_name: Optional[str] = Field(None, max_length=200, description="Arama/Hermitage name")
    ts_ordained_date: Optional[date] = Field(None, description="Date of ordination")


# --- Create Schema ---
class TemporarySilmathaCreate(TemporarySilmathaBase):
    """Schema for creating a new temporary silmatha record"""
    pass


# --- Update Schema ---
class TemporarySilmathaUpdate(BaseModel):
    """Schema for updating an existing temporary silmatha record - all fields optional"""
    ts_name: Optional[str] = Field(None, max_length=200, description="Silmatha/Nun name")
    ts_nic: Optional[str] = Field(None, max_length=15, description="NIC number")
    ts_contact_number: Optional[str] = Field(None, max_length=15, description="Contact/mobile number")
    ts_address: Optional[str] = Field(None, max_length=500, description="Address")
    ts_district: Optional[str] = Field(None, max_length=100, description="District name or code")
    ts_province: Optional[str] = Field(None, max_length=100, description="Province name or code")
    ts_arama_name: Optional[str] = Field(None, max_length=200, description="Arama/Hermitage name")
    ts_ordained_date: Optional[date] = Field(None, description="Date of ordination")


# --- Response Schema ---
class TemporarySilmathaResponse(TemporarySilmathaBase):
    """Schema for temporary silmatha response"""
    ts_id: int
    ts_created_at: datetime
    ts_created_by: Optional[str]
    ts_updated_at: Optional[datetime]
    ts_updated_by: Optional[str]

    model_config = ConfigDict(from_attributes=True)


# --- Management Payload Schema ---
class TemporarySilmathaPayload(BaseModel):
    """Payload for temporary silmatha management operations"""
    ts_id: Optional[int] = Field(None, description="Temporary silmatha ID (required for READ_ONE, UPDATE, DELETE)")
    data: Optional[TemporarySilmathaCreate] = Field(None, description="Data for CREATE operation")
    updates: Optional[TemporarySilmathaUpdate] = Field(None, description="Updates for UPDATE operation")
    
    # Pagination and filters for READ_ALL
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=200, description="Maximum number of records to return")
    search: Optional[str] = Field(None, description="Search by name, NIC, address, or contact")


# --- Management Request Schema ---
class TemporarySilmathaManagementRequest(BaseModel):
    """Request schema for temporary silmatha management endpoint"""
    action: CRUDAction = Field(..., description="CRUD action to perform")
    payload: TemporarySilmathaPayload = Field(..., description="Payload data based on action")


# --- Management Response Schema ---
class TemporarySilmathaManagementResponse(BaseModel):
    """Response schema for temporary silmatha management endpoint"""
    status: str = Field(..., description="Response status (success/error)")
    message: str = Field(..., description="Response message")
    data: Optional[TemporarySilmathaResponse | list[TemporarySilmathaResponse] | dict] = Field(
        None, description="Response data (single record, list, or metadata)"
    )

    model_config = ConfigDict(from_attributes=True)
