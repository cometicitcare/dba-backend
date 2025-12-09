# app/schemas/silmatha_regist.py
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import date, datetime
from typing import Optional, List, Union, Any
from enum import Enum

# --- Action Enum ---
class CRUDAction(str, Enum):
    CREATE = "CREATE"
    READ_ONE = "READ_ONE"
    READ_ALL = "READ_ALL"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    MARK_PRINTED = "MARK_PRINTED"
    MARK_SCANNED = "MARK_SCANNED"

# --- Workflow Status Enum ---
class WorkflowStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PRINTING = "PRINTING"
    PRINTED = "PRINTED"
    PEND_APPROVAL = "PEND-APPROVAL"
    SCANNED = "SCANNED"
    COMPLETED = "COMPLETED"

# --- Approval Status Enum ---
class ApprovalStatus(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


# --- Nested Response Schemas (matching Bhikku format) ---
class ProvinceResponse(BaseModel):
    """Nested response for province"""
    pr_code: str
    pr_name: str


class DistrictResponse(BaseModel):
    """Nested response for district"""
    ds_code: str
    ds_name: str


class DivisionResponse(BaseModel):
    """Nested response for divisional secretariat"""
    dv_code: str
    dv_name: str


class GNDivisionResponse(BaseModel):
    """Nested response for GN division"""
    gn_code: str
    gn_name: str


class StatusResponse(BaseModel):
    """Nested response for status"""
    st_code: str
    st_description: str


class CategoryResponse(BaseModel):
    """Nested response for category"""
    cat_code: str
    cat_description: str


class ViharaResponse(BaseModel):
    """Nested response for vihara/temple"""
    vh_trn: str
    vh_vname: str


class SilmathaRefResponse(BaseModel):
    """Nested response for silmatha references (viharadhipathi, mahanaacharyacd, etc.)"""
    sil_regn: str
    sil_mahananame: str


# --- Silmatha Schemas ---
class SilmathaRegistBase(BaseModel):
    sil_regn: Optional[str] = None  # Auto-generated
    sil_reqstdate: date
    
    # Personal Information
    sil_gihiname: Optional[str] = None
    sil_dofb: Optional[date] = None
    sil_fathrname: Optional[str] = None
    sil_email: Optional[EmailStr] = None
    sil_mobile: Optional[str] = Field(None, max_length=10)
    sil_fathrsaddrs: Optional[str] = None
    sil_fathrsmobile: Optional[str] = Field(None, max_length=10)
    
    # Geographic/Birth Information
    sil_birthpls: Optional[str] = None
    sil_province: Optional[str] = None
    sil_district: Optional[str] = None
    sil_korale: Optional[str] = None
    sil_pattu: Optional[str] = None
    sil_division: Optional[str] = None
    sil_vilage: Optional[str] = None
    sil_gndiv: str
    sil_created_by_district: Optional[str] = None
    
    # Temple/Religious Information
    sil_viharadhipathi: Optional[str] = None
    sil_cat: Optional[str] = None
    sil_currstat: str
    sil_declaration_date: Optional[date] = None
    sil_remarks: Optional[str] = None
    sil_mahanadate: Optional[date] = None
    sil_mahananame: Optional[str] = None
    sil_mahanaacharyacd: Optional[str] = None
    sil_robing_tutor_residence: Optional[str] = None
    sil_mahanatemple: Optional[str] = None
    sil_robing_after_residence_temple: Optional[str] = None
    
    # Form ID
    sil_form_id: Optional[str] = None
    
    # Signature Fields (Boolean - true/false)
    sil_student_signature: Optional[bool] = None  # ශිෂ්‍ය මෑණියන් වහන්සේගේ අත්සන
    sil_acharya_signature: Optional[bool] = None  # ආචාර්ය මෑණියන් වහන්සේගේ අත්සන
    sil_aramadhipathi_signature: Optional[bool] = None  # ආරාමාධිපති මෑණියන් වහන්සේගේ අත්සන
    sil_district_secretary_signature: Optional[bool] = None  # දිස්ත්‍රික් සිල්මාතා සංගමයේ ලේකම් අත්සන


class SilmathaRegistCreate(SilmathaRegistBase):
    """Schema for creating a new Silmatha record"""
    sil_created_by: Optional[str] = None
    sil_updated_by: Optional[str] = None


class SilmathaRegistUpdate(BaseModel):
    """Schema for updating a Silmatha record - all fields optional"""
    sil_regn: Optional[str] = None
    sil_reqstdate: Optional[date] = None
    
    # Personal Information
    sil_gihiname: Optional[str] = None
    sil_dofb: Optional[date] = None
    sil_fathrname: Optional[str] = None
    sil_email: Optional[EmailStr] = None
    sil_mobile: Optional[str] = Field(None, max_length=10)
    sil_fathrsaddrs: Optional[str] = None
    sil_fathrsmobile: Optional[str] = Field(None, max_length=10)
    
    # Geographic/Birth Information
    sil_birthpls: Optional[str] = None
    sil_province: Optional[str] = None
    sil_district: Optional[str] = None
    sil_korale: Optional[str] = None
    sil_pattu: Optional[str] = None
    sil_division: Optional[str] = None
    sil_vilage: Optional[str] = None
    sil_gndiv: Optional[str] = None
    
    # Temple/Religious Information
    sil_viharadhipathi: Optional[str] = None
    sil_cat: Optional[str] = None
    sil_currstat: Optional[str] = None
    sil_declaration_date: Optional[date] = None
    sil_remarks: Optional[str] = None
    sil_mahanadate: Optional[date] = None
    sil_mahananame: Optional[str] = None
    sil_mahanaacharyacd: Optional[str] = None
    sil_robing_tutor_residence: Optional[str] = None
    sil_mahanatemple: Optional[str] = None
    sil_robing_after_residence_temple: Optional[str] = None
    
    # Signature Fields (Boolean - true/false)
    sil_student_signature: Optional[bool] = None
    sil_acharya_signature: Optional[bool] = None
    sil_aramadhipathi_signature: Optional[bool] = None
    sil_district_secretary_signature: Optional[bool] = None
    
    # Form ID
    sil_form_id: Optional[str] = None
    
    # Document Storage
    sil_scanned_document_path: Optional[str] = None
    
    # Audit Fields
    sil_created_by: Optional[str] = None
    sil_updated_by: Optional[str] = None


class Silmatha(SilmathaRegistBase):
    """Schema for returning a Silmatha record - PUBLIC API (with nested responses)"""
    model_config = ConfigDict(from_attributes=True)
    
    sil_regn: str  # Required in response
    
    # Override base fields to use nested response objects
    sil_province: Optional[Union[ProvinceResponse, str]] = None
    sil_district: Optional[Union[DistrictResponse, str]] = None
    sil_division: Optional[Union[DivisionResponse, str]] = None
    sil_gndiv: Union[GNDivisionResponse, str]
    sil_currstat: Union[StatusResponse, str]
    sil_cat: Optional[Union[CategoryResponse, str]] = None
    sil_viharadhipathi: Optional[Union[SilmathaRefResponse, str]] = None
    sil_mahanaacharyacd: Optional[Union[SilmathaRefResponse, str]] = None
    sil_robing_tutor_residence: Optional[Union[ViharaResponse, str]] = None
    sil_mahanatemple: Optional[Union[ViharaResponse, str]] = None
    sil_robing_after_residence_temple: Optional[Union[ViharaResponse, str]] = None
    
    # Workflow Fields - expose same set as Bhikku responses
    sil_workflow_status: Optional[str] = None
    sil_approval_status: Optional[str] = None
    sil_version_number: Optional[int] = None
    sil_scanned_document_path: Optional[str] = None
    sil_printed_at: Optional[datetime] = None
    sil_scanned_at: Optional[datetime] = None
    sil_approved_at: Optional[datetime] = None
    sil_rejected_at: Optional[datetime] = None
    sil_rejection_reason: Optional[str] = None
    sil_created_by_district: Optional[str] = None


class SilmathaRegistInternal(SilmathaRegistBase):
    """Schema for internal use with ALL fields including workflow and audit fields"""
    model_config = ConfigDict(from_attributes=True)
    
    sil_id: int
    sil_regn: str
    sil_is_deleted: bool
    sil_version_number: int
    sil_created_by: Optional[str] = None
    sil_updated_by: Optional[str] = None
    
    # Workflow Fields
    sil_workflow_status: Optional[str] = "PENDING"
    sil_approval_status: Optional[str] = None
    sil_approved_by: Optional[str] = None
    sil_approved_at: Optional[datetime] = None
    sil_rejected_by: Optional[str] = None
    sil_rejected_at: Optional[datetime] = None
    sil_rejection_reason: Optional[str] = None
    sil_printed_at: Optional[datetime] = None
    sil_printed_by: Optional[str] = None
    sil_scanned_at: Optional[datetime] = None
    sil_scanned_by: Optional[str] = None
    
    # Reprint Workflow Fields
    sil_reprint_status: Optional[str] = None
    sil_reprint_form_no: Optional[str] = None
    sil_reprint_requested_by: Optional[str] = None
    sil_reprint_requested_at: Optional[datetime] = None
    sil_reprint_request_reason: Optional[str] = None
    sil_reprint_amount: Optional[float] = None
    sil_reprint_remarks: Optional[str] = None
    sil_reprint_approved_by: Optional[str] = None
    sil_reprint_approved_at: Optional[datetime] = None
    sil_reprint_rejected_by: Optional[str] = None
    sil_reprint_rejected_at: Optional[datetime] = None
    sil_reprint_rejection_reason: Optional[str] = None
    sil_reprint_completed_by: Optional[str] = None
    sil_reprint_completed_at: Optional[datetime] = None
    
    # Document Storage
    sil_scanned_document_path: Optional[str] = None

# --- Request/Response Wrapper Schemas (matching Bhikku format) ---
class SilmathaRegistRequestPayload(BaseModel):
    """Request payload for all actions"""
    # For READ_ONE, UPDATE, DELETE
    sil_id: Optional[int] = None
    sil_regn: Optional[str] = None
    
    # For READ_ALL - Enhanced with page number and search
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1, le=200)
    page: Optional[int] = Field(default=1, ge=1)
    search_key: Optional[str] = Field(default="", max_length=100)
    
    # Advanced filters for READ_ALL
    vh_trn: Optional[str] = Field(None, description="Temple TRN filter (robing tutor residence)")
    province: Optional[str] = Field(None, description="Province code filter")
    district: Optional[str] = Field(None, description="District code filter")
    divisional_secretariat: Optional[str] = Field(None, description="Divisional secretariat code filter")
    gn_division: Optional[str] = Field(None, description="GN division code filter")
    temple: Optional[str] = Field(None, description="Temple filter (robing after residence temple)")
    child_temple: Optional[str] = Field(None, description="Child temple filter (mahana temple)")
    parshawaya: Optional[str] = Field(None, description="Parshawaya filter (not applicable to silmatha)")
    category: Optional[str] = Field(None, description="Category code filter")
    status: Optional[str] = Field(None, description="Status code filter")
    workflow_status: Optional[str] = Field(None, description="Workflow status filter")
    date_from: Optional[date] = Field(None, description="Start date for filtering by request date")
    date_to: Optional[date] = Field(None, description="End date for filtering by request date")
    
    # For CREATE, UPDATE
    data: Optional[Union[SilmathaRegistCreate, SilmathaRegistUpdate]] = None
    
    # For workflow actions (APPROVE, REJECT, MARK_SCANNED)
    rejection_reason: Optional[str] = Field(None, max_length=500)
    scanned_document_path: Optional[str] = Field(None, max_length=500, description="Path to scanned document (optional for MARK_SCANNED action)")


class SilmathaRegistPaginatedResponse(BaseModel):
    """Paginated response matching Bhikku format"""
    status: str
    message: str
    data: List[Silmatha]
    totalRecords: int
    page: int
    limit: int


class SilmathaRegistManagementRequest(BaseModel):
    """Main request schema matching Bhikku format"""
    action: CRUDAction
    payload: SilmathaRegistRequestPayload


class SilmathaRegistManagementResponse(BaseModel):
    """Response schema matching Bhikku format"""
    model_config = ConfigDict(from_attributes=True)
    
    status: str
    message: str
    data: Optional[Union[Silmatha, List[Silmatha], Any]] = None
    # Optional pagination fields (only for READ_ALL)
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None


# --- Legacy Response Schemas (kept for backward compatibility) ---
class SilmathaRegistResponse(BaseModel):
    """Response schema for single record operations"""
    success: bool
    message: str
    data: Optional[SilmathaRegistInternal] = None


class SilmathaRegistListResponse(BaseModel):
    """Response schema for list operations"""
    success: bool
    message: str
    data: Optional[list[SilmathaRegistInternal]] = None
    total: Optional[int] = None

# --- Workflow Action Schemas ---
class WorkflowActionType(str, Enum):
    """Workflow actions available for silmatha records"""
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    MARK_PRINTING = "MARK_PRINTING"
    MARK_PRINTED = "MARK_PRINTED"
    MARK_SCANNED = "MARK_SCANNED"
    RESET_TO_PENDING = "RESET_TO_PENDING"
    # Reprint workflow actions
    REQUEST_REPRINT = "REQUEST_REPRINT"
    ACCEPT_REPRINT = "ACCEPT_REPRINT"
    REJECT_REPRINT = "REJECT_REPRINT"
    COMPLETE_REPRINT = "COMPLETE_REPRINT"


class SilmathaRegistWorkflowRequest(BaseModel):
    """Request to update workflow status of a silmatha record"""
    sil_regn: str = Field(..., description="Silmatha registration number")
    action: WorkflowActionType
    rejection_reason: Optional[str] = Field(None, max_length=500, description="Required when action is REJECT or REJECT_REPRINT")
    reprint_reason: Optional[str] = Field(None, max_length=500, description="Required when action is REQUEST_REPRINT")
    reprint_amount: Optional[float] = Field(None, description="Reprint amount - required when action is REQUEST_REPRINT")
    reprint_remarks: Optional[str] = Field(None, max_length=500, description="Reprint remarks - optional when action is REQUEST_REPRINT")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sil_regn": "SIL2025000001",
                "action": "APPROVE"
            }
        }
    )


class SilmathaRegistWorkflowResponse(BaseModel):
    """Response after workflow action"""
    model_config = ConfigDict(from_attributes=True)
    
    success: bool
    message: str
    data: Optional[SilmathaRegistInternal] = None


# --- Arama List Schemas for Silmatha Users ---
class AramaSimpleItem(BaseModel):
    """Simplified arama item for silmatha users"""
    ar_trn: str
    ar_vname: Optional[str] = None
    ar_addrs: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class AramaListPayload(BaseModel):
    """Payload for listing aramas"""
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=200)
    skip: int = Field(default=0, ge=0)
    search_key: Optional[str] = Field(default=None, max_length=200)


class AramaListRequest(BaseModel):
    """Request for arama list endpoint"""
    action: str = Field(..., description="Action type: READ_ALL")
    payload: AramaListPayload


class AramaListResponse(BaseModel):
    """Response for arama list endpoint"""
    status: str
    message: str
    data: List[AramaSimpleItem]
    totalRecords: int
    page: int
    limit: int


# --- Limited Silmatha List Schemas ---
class SilmathaLimitedItem(BaseModel):
    """Limited silmatha item - only registration number and maha name"""
    sil_regn: str
    sil_mahananame: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class SilmathaLimitedListPayload(BaseModel):
    """Payload for listing silmathas with limited info"""
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=200)
    skip: int = Field(default=0, ge=0)
    search_key: Optional[str] = Field(default=None, max_length=200)


class SilmathaLimitedListRequest(BaseModel):
    """Request for silmatha limited list endpoint"""
    action: str = Field(..., description="Action type: READ_ALL")
    payload: SilmathaLimitedListPayload


class SilmathaLimitedListResponse(BaseModel):
    """Response for silmatha limited list endpoint"""
    status: str
    message: str
    data: List[SilmathaLimitedItem]
    totalRecords: int = Field(default=0)
    page: int
    limit: int
