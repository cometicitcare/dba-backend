# app/schemas/temporary_vihara.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Union
from enum import Enum


# --- Nested Response Classes for Foreign Key Resolution ---
class ProvinceResponse(BaseModel):
    """Nested response for province"""
    cp_code: str
    cp_name: str


class DistrictResponse(BaseModel):
    """Nested response for district"""
    dd_dcode: str
    dd_dname: str


class DivisionalSecretariatResponse(BaseModel):
    """Nested response for divisional secretariat"""
    dv_dvcode: str
    dv_dvname: str


class GNDivisionResponse(BaseModel):
    """Nested response for GN division"""
    gn_gnc: str
    gn_gnname: str


# --- Action Enum ---
class CRUDAction(str, Enum):
    CREATE = "CREATE"
    READ_ONE = "READ_ONE"
    READ_ALL = "READ_ALL"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


# --- Base Schema ---
class TemporaryViharaBase(BaseModel):
    """Base schema with common fields for Temporary Vihara"""
    tv_name: str = Field(..., max_length=200, description="Vihara/Temple name (required)")
    tv_address: Optional[str] = Field(None, max_length=500, description="Temple address")
    tv_contact_number: Optional[str] = Field(None, max_length=15, description="Contact/mobile number")
    tv_district: Optional[Union[DistrictResponse, str]] = Field(None, description="District (nested object or code)")
    tv_province: Optional[Union[ProvinceResponse, str]] = Field(None, description="Province (nested object or code)")
    tv_viharadhipathi_name: Optional[str] = Field(None, max_length=200, description="Viharadhipathi/Chief incumbent name")


# --- Create Schema ---
class TemporaryViharaCreate(TemporaryViharaBase):
    """Schema for creating a new temporary vihara record"""
    pass


# --- Update Schema ---
class TemporaryViharaUpdate(BaseModel):
    """Schema for updating an existing temporary vihara record - all fields optional"""
    tv_name: Optional[str] = Field(None, max_length=200, description="Vihara/Temple name")
    tv_address: Optional[str] = Field(None, max_length=500, description="Temple address")
    tv_contact_number: Optional[str] = Field(None, max_length=15, description="Contact/mobile number")
    tv_district: Optional[str] = Field(None, max_length=100, description="District code")
    tv_province: Optional[str] = Field(None, max_length=100, description="Province code")
    tv_viharadhipathi_name: Optional[str] = Field(None, max_length=200, description="Viharadhipathi/Chief incumbent name")


# --- Response Schema ---
class TemporaryViharaResponse(TemporaryViharaBase):
    """Schema for temporary vihara response with enriched foreign key objects"""
    tv_id: int
    tv_created_at: datetime
    tv_created_by: Optional[str]
    tv_updated_at: Optional[datetime]
    tv_updated_by: Optional[str]

    model_config = ConfigDict(from_attributes=True)


# --- Management Payload Schema ---
class TemporaryViharaPayload(BaseModel):
    """Payload for temporary vihara management operations"""
    tv_id: Optional[int] = Field(None, description="Temporary vihara ID (required for READ_ONE, UPDATE, DELETE)")
    data: Optional[TemporaryViharaCreate] = Field(None, description="Data for CREATE operation")
    updates: Optional[TemporaryViharaUpdate] = Field(None, description="Updates for UPDATE operation")
    
    # Pagination and filters for READ_ALL
    # Support both page-based and skip-based pagination for client flexibility
    page: Optional[int] = Field(None, ge=1, description="Page number (1-based) - alternative to skip")
    skip: Optional[int] = Field(None, ge=0, description="Number of records to skip (0-based) - alternative to page")
    limit: int = Field(100, ge=1, le=200, description="Maximum number of records to return")
    search: Optional[str] = Field(None, description="Search by name, address, or contact")


# --- Management Request Schema ---
class TemporaryViharaManagementRequest(BaseModel):
    """Request schema for temporary vihara management endpoint"""
    action: CRUDAction = Field(..., description="CRUD action to perform")
    payload: TemporaryViharaPayload = Field(..., description="Payload data based on action")


# --- Management Response Schema ---
class TemporaryViharaManagementResponse(BaseModel):
    """Response schema for temporary vihara management endpoint"""
    status: str = Field(..., description="Response status (success/error)")
    message: str = Field(..., description="Response message")
    data: Optional[TemporaryViharaResponse | list[TemporaryViharaResponse] | dict] = Field(
        None, description="Response data (single record, list, or metadata)"
    )

    model_config = ConfigDict(from_attributes=True)
