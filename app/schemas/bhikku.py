# app/schemas/bhikku.py
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List, Union, Any
from enum import Enum

# --- Action Enum ---
class CRUDAction(str, Enum):
    CREATE = "CREATE"
    READ_ONE = "READ_ONE"
    READ_ALL = "READ_ALL"
    UPDATE = "UPDATE"
    DELETE = "DELETE"

# --- Original Bhikku Schemas ---
class BhikkuBase(BaseModel):
    br_regn: str
    br_reqstdate: date
    br_vilage: Optional[str] = None
    br_gndiv: str
    br_gihiname: Optional[str] = None
    br_dofb: Optional[date] = None
    br_fathrname: Optional[str] = None
    br_remarks: Optional[str] = None
    br_currstat: str
    br_effctdate: Optional[date] = None
    br_parshawaya: str
    br_livtemple: str
    br_mahanatemple: str
    br_mahanaacharyacd: str
    br_multi_mahanaacharyacd: Optional[str] = None
    br_mahananame: Optional[str] = None
    br_mahanadate: Optional[date] = None
    br_cat: Optional[str] = None
    br_mobile: Optional[str] = None
    br_email: Optional[str] = None
    br_fathrsaddrs: Optional[str] = None
    br_fathrsmobile: Optional[str] = None
    br_upasampada_serial_no: Optional[str] = None
    br_created_by: Optional[str] = None
    br_updated_by: Optional[str] = None

class BhikkuCreate(BhikkuBase):
    pass

class BhikkuUpdate(BaseModel):
    br_regn: Optional[str] = None
    br_reqstdate: Optional[date] = None
    br_vilage: Optional[str] = None
    br_gndiv: Optional[str] = None
    br_gihiname: Optional[str] = None
    br_dofb: Optional[date] = None
    br_fathrname: Optional[str] = None
    br_remarks: Optional[str] = None
    br_currstat: Optional[str] = None
    br_effctdate: Optional[date] = None
    br_parshawaya: Optional[str] = None
    br_livtemple: Optional[str] = None
    br_mahanatemple: Optional[str] = None
    br_mahanaacharyacd: Optional[str] = None
    br_multi_mahanaacharyacd: Optional[str] = None
    br_mahananame: Optional[str] = None
    br_mahanadate: Optional[date] = None
    br_cat: Optional[str] = None
    br_mobile: Optional[str] = None
    br_email: Optional[str] = None
    br_fathrsaddrs: Optional[str] = None
    br_fathrsmobile: Optional[str] = None
    br_upasampada_serial_no: Optional[str] = None
    br_created_by: Optional[str] = None
    br_updated_by: Optional[str] = None

class Bhikku(BhikkuBase):
    br_id: int
    br_is_deleted: bool
    br_version_number: int

    class Config:
        from_attributes = True

# --- Schemas for the Single Endpoint ---
class BhikkuRequestPayload(BaseModel):
    # For READ_ONE, UPDATE, DELETE
    br_regn: Optional[str] = None 
    # For READ_ALL - Enhanced with page number and search
    skip: int = 0
    limit: int = 10
    page: Optional[int] = 1
    search_key: Optional[str] = ""  # Added search_key field
    # For CREATE, UPDATE
    data: Optional[Union[BhikkuCreate, BhikkuUpdate]] = None

# NEW: Paginated response for READ_ALL
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