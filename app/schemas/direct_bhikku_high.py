# app/schemas/direct_bhikku_high.py
"""
Schemas for Direct High Bhikku Registration
Combines bhikku registration and high bhikku registration fields
"""
from datetime import date, datetime
from enum import Enum
from typing import Optional, Union, List, Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CRUDAction(str, Enum):
    """CRUD and workflow actions for direct high bhikku registration"""
    CREATE = "CREATE"
    READ_ONE = "READ_ONE"
    READ_ALL = "READ_ALL"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    MARK_PRINTED = "MARK_PRINTED"
    MARK_SCANNED = "MARK_SCANNED"


class DirectBhikkuHighBase(BaseModel):
    """Base schema with all direct high bhikku fields"""
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True, use_enum_values=True)

    # Basic Information
    dbh_regn: Optional[str] = Field(default=None, max_length=20)
    dbh_reqstdate: Optional[date] = None
    
    # ==================== BHIKKU REGIST FIELDS ====================
    # Geographic/Birth Information
    dbh_birthpls: Optional[str] = Field(default=None, max_length=50)
    dbh_province: Optional[str] = Field(default=None, max_length=50)
    dbh_district: Optional[str] = Field(default=None, max_length=50)
    dbh_korale: Optional[str] = Field(default=None, max_length=50)
    dbh_pattu: Optional[str] = Field(default=None, max_length=50)
    dbh_division: Optional[str] = Field(default=None, max_length=50)
    dbh_vilage: Optional[str] = Field(default=None, max_length=50)
    dbh_gndiv: Optional[str] = Field(default=None, max_length=10)
    
    # Personal Information
    dbh_gihiname: Optional[str] = Field(default=None, max_length=50)
    dbh_dofb: Optional[date] = None
    dbh_fathrname: Optional[str] = Field(default=None, max_length=50)
    dbh_remarks: Optional[str] = Field(default=None, max_length=100)
    
    # Status Information
    dbh_currstat: Optional[str] = Field(default=None, max_length=5)
    dbh_effctdate: Optional[date] = None
    
    # Temple/Religious Information
    dbh_parshawaya: Optional[str] = Field(default=None, max_length=10)
    dbh_livtemple: Optional[str] = Field(default=None, max_length=10)
    dbh_mahanatemple: Optional[str] = Field(default=None, max_length=10)
    dbh_mahanaacharyacd: Optional[str] = Field(default=None, max_length=12)
    dbh_multi_mahanaacharyacd: Optional[str] = Field(default=None, max_length=200)
    dbh_mahananame: Optional[str] = Field(default=None, max_length=50)
    dbh_mahanadate: Optional[date] = None
    dbh_cat: Optional[str] = Field(default=None, max_length=5)
    
    # Additional Religious/Administrative Fields
    dbh_viharadhipathi: Optional[str] = Field(default=None, max_length=20)
    dbh_nikaya: Optional[str] = Field(default=None, max_length=10)
    dbh_mahanayaka_name: Optional[str] = Field(default=None, max_length=200)
    dbh_mahanayaka_address: Optional[str] = Field(default=None, max_length=500)
    dbh_residence_at_declaration: Optional[str] = Field(default=None, max_length=500)
    dbh_declaration_date: Optional[date] = Field(default=None, alias="dbh_u_date_declaration")
    dbh_robing_tutor_residence: Optional[str] = Field(default=None, max_length=20)
    dbh_robing_after_residence_temple: Optional[str] = Field(default=None, max_length=20)
    
    # Contact Information
    dbh_mobile: Optional[str] = Field(default=None, max_length=10)
    dbh_email: Optional[str] = Field(default=None, max_length=50)
    dbh_fathrsaddrs: Optional[str] = Field(default=None, max_length=200)
    dbh_fathrsmobile: Optional[str] = Field(default=None, max_length=10)
    
    # Serial Number
    dbh_upasampada_serial_no: Optional[str] = Field(default=None, max_length=20)
    
    # ==================== BHIKKU HIGH REGIST FIELDS ====================
    # High Bhikku Specific Fields
    dbh_samanera_serial_no: Optional[str] = Field(default=None, max_length=20)
    dbh_cc_code: Optional[str] = Field(default=None, max_length=5)
    dbh_higher_ordination_place: Optional[str] = Field(default=None, max_length=50)
    dbh_higher_ordination_date: Optional[date] = None
    dbh_karmacharya_name: Optional[str] = Field(default=None, max_length=100, alias="dbh_higher_ordination_karmaacharya")
    dbh_upaddhyaya_name: Optional[str] = Field(default=None, max_length=100, alias="dbh_higher_ordination_upaadhyaaya")
    dbh_assumed_name: Optional[str] = Field(default=None, max_length=50, alias="dbh_name_assumed_at_higher_ordination")
    dbh_residence_higher_ordination_trn: Optional[str] = Field(default=None, max_length=50, alias="dbh_residence_at_time_of_higher_ordination")
    dbh_residence_permanent_trn: Optional[str] = Field(default=None, max_length=50, alias="dbh_permanent_residence")
    dbh_declaration_residence_address: Optional[str] = Field(default=None, max_length=200, alias="dbh_residence_at_time_of_declaration_and_full_postal_address")
    dbh_tutors_tutor_regn: Optional[str] = Field(default=None, max_length=200)
    dbh_presiding_bhikshu_regn: Optional[str] = Field(default=None, max_length=200, alias="dbh_name_of_bhikshu_presiding_at_higher_ordination")
    
    # Additional Fields
    dbh_form_id: Optional[str] = Field(default=None, max_length=50)
    dbh_remarks_upasampada: Optional[str] = Field(default=None, max_length=500)


class DirectBhikkuHighCreate(DirectBhikkuHighBase):
    """Schema for creating a direct high bhikku record"""
    # Override required fields for creation
    dbh_reqstdate: date
    dbh_currstat: str = Field(max_length=5)
    dbh_parshawaya: str = Field(max_length=10)


class DirectBhikkuHighUpdate(DirectBhikkuHighBase):
    """Schema for updating a direct high bhikku record - all fields optional"""
    pass


class DirectBhikkuHighOut(DirectBhikkuHighBase):
    """Schema for direct high bhikku output with all fields"""
    dbh_id: int
    dbh_regn: str
    
    # Workflow fields
    dbh_scanned_document_path: Optional[str] = None
    dbh_workflow_status: str
    dbh_approval_status: Optional[str] = None
    dbh_approved_by: Optional[str] = None
    dbh_approved_at: Optional[datetime] = None
    dbh_rejected_by: Optional[str] = None
    dbh_rejected_at: Optional[datetime] = None
    dbh_rejection_reason: Optional[str] = None
    dbh_printed_at: Optional[datetime] = None
    dbh_printed_by: Optional[str] = None
    dbh_scanned_at: Optional[datetime] = None
    dbh_scanned_by: Optional[str] = None
    
    # Audit fields
    dbh_is_deleted: bool
    dbh_created_at: datetime
    dbh_updated_at: datetime
    dbh_created_by: Optional[str] = None
    dbh_updated_by: Optional[str] = None
    dbh_version_number: int
    dbh_created_by_district: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ==================== MANAGEMENT REQUEST/RESPONSE ====================
class DirectBhikkuHighManagementPayload(BaseModel):
    """Payload for management actions"""
    model_config = ConfigDict(str_strip_whitespace=True)

    dbh_id: Optional[int] = None
    dbh_regn: Optional[str] = None
    data: Optional[Union[DirectBhikkuHighCreate, DirectBhikkuHighUpdate, dict]] = None
    
    # Pagination
    page: Optional[int] = Field(default=1, ge=1)
    limit: Optional[int] = Field(default=10, ge=1, le=200)
    skip: Optional[int] = Field(default=0, ge=0)
    search_key: Optional[str] = None
    
    # Filters
    province: Optional[str] = None
    district: Optional[str] = None
    divisional_secretariat: Optional[str] = None
    gn_division: Optional[str] = None
    parshawaya: Optional[str] = None
    status: Optional[str] = None
    workflow_status: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    
    # Rejection reason
    rejection_reason: Optional[str] = None


class DirectBhikkuHighManagementRequest(BaseModel):
    """Request schema for management endpoint"""
    action: CRUDAction
    payload: DirectBhikkuHighManagementPayload


class DirectBhikkuHighManagementResponse(BaseModel):
    """Response schema for management endpoint"""
    status: str
    message: str
    data: Optional[Union[DirectBhikkuHighOut, List[DirectBhikkuHighOut], dict]] = None
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
