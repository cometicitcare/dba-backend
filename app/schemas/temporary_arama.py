# app/schemas/temporary_arama.py
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
class TemporaryAramaBase(BaseModel):
    """Base schema with common fields for Temporary Arama"""
    ta_name: str = Field(..., max_length=200, description="Arama/Hermitage name (required)")
    ta_address: Optional[str] = Field(None, max_length=500, description="Arama address")
    ta_contact_number: Optional[str] = Field(None, max_length=15, description="Contact/mobile number")
    ta_district: Optional[Union[DistrictResponse, str]] = Field(None, description="District (nested object or code)")
    ta_province: Optional[Union[ProvinceResponse, str]] = Field(None, description="Province (nested object or code)")
    ta_aramadhipathi_name: Optional[str] = Field(None, max_length=200, description="Aramadhipathi/Chief incumbent name")


# --- Create Schema ---
class TemporaryAramaCreate(TemporaryAramaBase):
    """Schema for creating a new temporary arama record"""
    pass


# --- Update Schema ---
class TemporaryAramaUpdate(BaseModel):
    """Schema for updating an existing temporary arama record - all fields optional"""
    ta_name: Optional[str] = Field(None, max_length=200, description="Arama/Hermitage name")
    ta_address: Optional[str] = Field(None, max_length=500, description="Arama address")
    ta_contact_number: Optional[str] = Field(None, max_length=15, description="Contact/mobile number")
    ta_district: Optional[str] = Field(None, max_length=100, description="District code")
    ta_province: Optional[str] = Field(None, max_length=100, description="Province code")
    ta_aramadhipathi_name: Optional[str] = Field(None, max_length=200, description="Aramadhipathi/Chief incumbent name")


# --- Response Schema ---
class TemporaryAramaResponse(TemporaryAramaBase):
    """Schema for temporary arama response with enriched foreign key objects"""
    ta_id: int
    ta_created_at: datetime
    ta_created_by: Optional[str]
    ta_updated_at: Optional[datetime]
    ta_updated_by: Optional[str]

    model_config = ConfigDict(from_attributes=True)


# --- Management Payload Schema ---
class TemporaryAramaPayload(BaseModel):
    """Payload for temporary arama management operations"""
    ta_id: Optional[int] = Field(None, description="Temporary arama ID (required for READ_ONE, UPDATE, DELETE)")
    data: Optional[TemporaryAramaCreate] = Field(None, description="Data for CREATE operation")
    updates: Optional[TemporaryAramaUpdate] = Field(None, description="Updates for UPDATE operation")
    
    # Pagination and filters for READ_ALL
    # Support both page-based and skip-based pagination for client flexibility
    page: Optional[int] = Field(None, ge=1, description="Page number (1-based) - alternative to skip")
    skip: Optional[int] = Field(None, ge=0, description="Number of records to skip (0-based) - alternative to page")
    limit: int = Field(100, ge=1, le=200, description="Maximum number of records to return")
    search: Optional[str] = Field(None, description="Search by name, address, or contact")


# --- Management Request Schema ---
class TemporaryAramaManagementRequest(BaseModel):
    """Request schema for temporary arama management endpoint"""
    action: CRUDAction = Field(..., description="CRUD action to perform")
    payload: TemporaryAramaPayload = Field(..., description="Payload data based on action")


# --- Management Response Schema ---
class TemporaryAramaManagementResponse(BaseModel):
    """Response schema for temporary arama management endpoint"""
    status: str = Field(..., description="Response status (success/error)")
    message: str = Field(..., description="Response message")
    data: Optional[TemporaryAramaResponse | list[TemporaryAramaResponse] | dict] = Field(
        None, description="Response data (single record, list, or metadata)"
    )

    model_config = ConfigDict(from_attributes=True)
