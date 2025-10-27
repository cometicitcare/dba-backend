# app/schemas/bhikku.py
from pydantic import BaseModel, Field, EmailStr
from datetime import date
from typing import Annotated, Optional, List, Union, Any
from enum import Enum

# --- Action Enum ---
class CRUDAction(str, Enum):
    CREATE = "CREATE"
    READ_ONE = "READ_ONE"
    READ_ALL = "READ_ALL"
    UPDATE = "UPDATE"
    DELETE = "DELETE"

# --- Bhikku Schemas with ALL Fields ---
class BhikkuBase(BaseModel):
    br_regn: Optional[str] = None  # Made optional - will be auto-generated
    br_reqstdate: date
    
    # Geographic/Birth Information
    br_birthpls: Optional[str] = None
    br_province: Optional[str] = None
    br_district: Optional[str] = None
    br_korale: Optional[str] = None
    br_pattu: Optional[str] = None
    br_division: Optional[str] = None
    br_vilage: Optional[str] = None
    br_gndiv: str
    
    # Personal Information
    br_gihiname: Optional[str] = None
    br_dofb: Optional[date] = None
    br_fathrname: Optional[str] = None
    br_remarks: Optional[str] = None
    
    # Status Information
    br_currstat: str
    br_effctdate: Optional[date] = None
    
    # Temple/Religious Information
    br_parshawaya: str
    br_livtemple: str
    br_mahanatemple: str
    br_mahanaacharyacd: str
    br_multi_mahanaacharyacd: Optional[str] = None
    br_mahananame: Optional[str] = None
    br_mahanadate: Optional[date] = None
    br_cat: Optional[str] = None
    
    # Contact Information
    br_mobile: Optional[str] = Field(None, max_length=10)
    br_email: Optional[EmailStr] = None
    br_fathrsaddrs: Optional[str] = None
    br_fathrsmobile: Optional[str] = Field(None, max_length=10)
    
    # Serial Number
    br_upasampada_serial_no: Optional[str] = None
    
    # Audit Fields
    br_created_by: Optional[str] = None
    br_updated_by: Optional[str] = None

class BhikkuCreate(BhikkuBase):
    """Schema for creating a new Bhikku record - br_regn is auto-generated"""
    pass

class BhikkuUpdate(BaseModel):
    """Schema for updating a Bhikku record - all fields optional"""
    br_regn: Optional[str] = None
    br_reqstdate: Optional[date] = None
    
    # Geographic/Birth Information
    br_birthpls: Optional[str] = None
    br_province: Optional[str] = None
    br_district: Optional[str] = None
    br_korale: Optional[str] = None
    br_pattu: Optional[str] = None
    br_division: Optional[str] = None
    br_vilage: Optional[str] = None
    br_gndiv: Optional[str] = None
    
    # Personal Information
    br_gihiname: Optional[str] = None
    br_dofb: Optional[date] = None
    br_fathrname: Optional[str] = None
    br_remarks: Optional[str] = None
    
    # Status Information
    br_currstat: Optional[str] = None
    br_effctdate: Optional[date] = None
    
    # Temple/Religious Information
    br_parshawaya: Optional[str] = None
    br_livtemple: Optional[str] = None
    br_mahanatemple: Optional[str] = None
    br_mahanaacharyacd: Optional[str] = None
    br_multi_mahanaacharyacd: Optional[str] = None
    br_mahananame: Optional[str] = None
    br_mahanadate: Optional[date] = None
    br_cat: Optional[str] = None
    
    # Contact Information
    br_mobile: Optional[str] = Field(None, max_length=10)
    br_email: Optional[EmailStr] = None
    br_fathrsaddrs: Optional[str] = None
    br_fathrsmobile: Optional[str] = Field(None, max_length=10)
    
    # Serial Number
    br_upasampada_serial_no: Optional[str] = None
    
    # Audit Fields
    br_created_by: Optional[str] = None
    br_updated_by: Optional[str] = None

class Bhikku(BhikkuBase):
    """Schema for returning a Bhikku record"""
    br_id: int
    br_regn: str  # Required in response
    br_is_deleted: bool
    br_version_number: int

    class Config:
        from_attributes = True

# --- Schemas for the Single Endpoint ---
class BhikkuRequestPayload(BaseModel):
    # For READ_ONE, UPDATE, DELETE
    br_id: Optional[int] = None
    br_regn: Optional[str] = None 
    # For READ_ALL - Enhanced with page number and search
    skip: Annotated[int, Field(ge=0)] = 0
    limit: Annotated[int, Field(ge=1, le=200)] = 10
    page: Annotated[Optional[int], Field(ge=1)] = 1
    search_key: Optional[str] = Field(default="", max_length=100)
    # For CREATE, UPDATE
    data: Optional[Union[BhikkuCreate, BhikkuUpdate]] = None

class BhikkuPaginatedResponse(BaseModel):
    status: str
    message: str
    data: List[Bhikku]
    totalRecords: int
    page: int
    limit: int

class BhikkuManagementRequest(BaseModel):
    action: CRUDAction
    payload: BhikkuRequestPayload

class BhikkuManagementResponse(BaseModel):
    status: str
    message: str
    data: Optional[Union[Bhikku, List[Bhikku], Any]] = None
    # Optional pagination fields (only for READ_ALL)
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None
