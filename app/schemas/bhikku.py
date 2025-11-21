# app/schemas/bhikku.py
from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator
from datetime import date, datetime
from typing import Annotated, Optional, List, Union, Any
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
    SCANNED = "SCANNED"
    COMPLETED = "COMPLETED"

# --- Approval Status Enum ---
class ApprovalStatus(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

# --- Bhikku Schemas with ALL Fields ---
class BhikkuBase(BaseModel):
    br_regn: Optional[str] = None  # Made optional - will be auto-generated
    br_reqstdate: date
    
    # Personal Information
    br_gihiname: Optional[str] = None
    br_dofb: Optional[date] = None
    br_fathrname: Optional[str] = None
    br_email: Optional[EmailStr] = None
    br_mobile: Optional[str] = Field(None, max_length=10)
    br_fathrsaddrs: Optional[str] = None
    br_fathrsmobile: Optional[str] = Field(None, max_length=10)
    
    # Geographic/Birth Information - All Optional
    br_birthpls: Optional[str] = None
    br_province: Optional[str] = None
    br_district: Optional[str] = None
    br_korale: Optional[str] = None  # Optional
    br_pattu: Optional[str] = None  # Optional
    br_division: Optional[str] = None  # Optional (Divisional Secretariat)
    br_vilage: Optional[str] = None  # Optional
    br_gndiv: Optional[str] = None  # Optional (GN Division)
    
    # Status Information
    br_currstat: str
    br_effctdate: Optional[date] = None
    
    # Temple/Religious Information
    br_viharadhipathi: Optional[str] = None
    br_nikaya: Optional[str] = None
    br_parshawaya: str
    br_mahanayaka_name: Optional[str] = None
    br_mahanayaka_address: Optional[str] = None
    br_cat: Optional[str] = None
    br_residence_at_declaration: Optional[str] = None
    br_declaration_date: Optional[date] = None
    br_remarks: Optional[str] = None
    br_mahanadate: Optional[date] = None
    br_mahananame: Optional[str] = None
    br_mahanaacharyacd: Optional[str] = None
    br_robing_tutor_residence: Optional[str] = None
    br_mahanatemple: Optional[str] = None
    br_robing_after_residence_temple: Optional[str] = None
    
    # Location tracking (location-based access control)
    br_created_by_district: Optional[str] = None
    
    @field_validator('br_email', mode='before')
    @classmethod
    def empty_string_to_none(cls, v):
        """Convert empty string to None for email validation"""
        if v == '' or (isinstance(v, str) and v.strip() == ''):
            return None
        return v

class BhikkuCreate(BhikkuBase):
    """Schema for creating a new Bhikku record - br_regn is auto-generated
    Only includes fields that should be provided during creation based on the payload structure"""
    # Workflow fields are set automatically - not included in create
    # Audit fields will be set from user context
    br_created_by: Optional[str] = None
    br_updated_by: Optional[str] = None
    pass

class BhikkuUpdate(BaseModel):
    """Schema for updating a Bhikku record - all fields optional"""
    br_regn: Optional[str] = None
    br_reqstdate: Optional[date] = None
    
    # Personal Information
    br_gihiname: Optional[str] = None
    br_dofb: Optional[date] = None
    br_fathrname: Optional[str] = None
    br_email: Optional[EmailStr] = None
    br_mobile: Optional[str] = Field(None, max_length=10)
    br_fathrsaddrs: Optional[str] = None
    br_fathrsmobile: Optional[str] = Field(None, max_length=10)
    
    # Geographic/Birth Information - All Optional
    br_birthpls: Optional[str] = None
    br_province: Optional[str] = None
    br_district: Optional[str] = None
    br_korale: Optional[str] = None
    br_pattu: Optional[str] = None
    br_division: Optional[str] = None
    br_vilage: Optional[str] = None
    br_gndiv: Optional[str] = None
    
    # Status Information
    br_currstat: Optional[str] = None
    br_effctdate: Optional[date] = None
    
    # Temple/Religious Information
    br_viharadhipathi: Optional[str] = None
    br_nikaya: Optional[str] = None
    br_parshawaya: Optional[str] = None
    br_mahanayaka_name: Optional[str] = None
    br_mahanayaka_address: Optional[str] = None
    br_cat: Optional[str] = None
    br_residence_at_declaration: Optional[str] = None
    br_declaration_date: Optional[date] = None
    br_remarks: Optional[str] = None
    br_mahanadate: Optional[date] = None
    br_mahananame: Optional[str] = None
    br_mahanaacharyacd: Optional[str] = None
    br_robing_tutor_residence: Optional[str] = None
    br_mahanatemple: Optional[str] = None
    br_robing_after_residence_temple: Optional[str] = None
    
    # Document Storage
    br_scanned_document_path: Optional[str] = None
    
    # Audit Fields (only for update)
    br_created_by: Optional[str] = None
    br_updated_by: Optional[str] = None

class BhikkuInternal(BhikkuBase):
    """Schema for internal use with ALL fields including workflow and audit fields"""
    model_config = ConfigDict(from_attributes=True)
    
    br_id: int
    br_regn: str  # Required in response
    br_is_deleted: bool
    br_version_number: int
    br_created_by: Optional[str] = None
    br_updated_by: Optional[str] = None
    
    # Additional fields from database model not in payload
    br_livtemple: Optional[str] = None  # Current residence temple
    br_multi_mahanaacharyacd: Optional[str] = None
    br_upasampada_serial_no: Optional[str] = None
    
    # Workflow Fields
    br_workflow_status: Optional[str] = "PENDING"
    br_approval_status: Optional[str] = None
    br_approved_by: Optional[str] = None
    br_approved_at: Optional[datetime] = None
    br_rejected_by: Optional[str] = None
    br_rejected_at: Optional[datetime] = None
    br_rejection_reason: Optional[str] = None
    br_printed_at: Optional[datetime] = None
    br_printed_by: Optional[str] = None
    br_scanned_at: Optional[datetime] = None
    br_scanned_by: Optional[str] = None
    
    # Reprint Workflow Fields
    br_reprint_status: Optional[str] = None
    br_reprint_requested_by: Optional[str] = None
    br_reprint_requested_at: Optional[datetime] = None
    br_reprint_request_reason: Optional[str] = None
    br_reprint_amount: Optional[float] = None
    br_reprint_remarks: Optional[str] = None
    br_reprint_approved_by: Optional[str] = None
    br_reprint_approved_at: Optional[datetime] = None
    br_reprint_rejected_by: Optional[str] = None
    br_reprint_rejected_at: Optional[datetime] = None
    br_reprint_rejection_reason: Optional[str] = None
    br_reprint_completed_by: Optional[str] = None
    br_reprint_completed_at: Optional[datetime] = None
    
    # Document Storage
    br_scanned_document_path: Optional[str] = None

# --- Nested Response Schemas for Foreign Key Fields ---
class ProvinceResponse(BaseModel):
    """Nested response for province"""
    cp_code: str
    cp_name: str

class DistrictResponse(BaseModel):
    """Nested response for district"""
    dd_dcode: str
    dd_dname: str

class DivisionResponse(BaseModel):
    """Nested response for divisional secretariat"""
    dv_dvcode: str
    dv_dvname: str

class GNDivisionResponse(BaseModel):
    """Nested response for GN division"""
    gn_gnc: str
    gn_gnname: str

class StatusResponse(BaseModel):
    """Nested response for status"""
    st_statcd: str
    st_descr: str

class NikayaResponse(BaseModel):
    """Nested response for nikaya"""
    code: str
    name: str

class ParshawaResponse(BaseModel):
    """Nested response for parshawa"""
    code: str
    name: str

class CategoryResponse(BaseModel):
    """Nested response for category"""
    cc_code: str
    cc_catogry: str

class ViharaResponse(BaseModel):
    """Nested response for vihara/temple"""
    vh_trn: str
    vh_vname: str

class BhikkuRefResponse(BaseModel):
    """Nested response for bhikku references (viharadhipathi, mahanaacharyacd, etc.)"""
    br_regn: str
    br_mahananame: str
    br_upasampadaname: Optional[str] = ""

class Bhikku(BhikkuBase):
    """Schema for returning a Bhikku record - PUBLIC API"""
    model_config = ConfigDict(from_attributes=True)
    
    br_regn: str  # Required in response
    
    # Override base fields to use nested response objects
    br_province: Optional[Union[ProvinceResponse, str]] = None
    br_district: Optional[Union[DistrictResponse, str]] = None
    br_division: Optional[Union[DivisionResponse, str]] = None  # Divisional Secretariat
    br_gndiv: Optional[Union[GNDivisionResponse, str]] = None  # GN Division
    br_currstat: Union[StatusResponse, str]
    br_parshawaya: Union[ParshawaResponse, str]
    br_mahanatemple: Optional[Union[ViharaResponse, str]] = None
    br_mahanaacharyacd: Optional[Union[BhikkuRefResponse, str]] = None
    br_cat: Optional[Union[CategoryResponse, str]] = None
    br_viharadhipathi: Optional[Union[BhikkuRefResponse, str]] = None
    br_nikaya: Optional[Union[NikayaResponse, str]] = None
    br_robing_tutor_residence: Optional[Union[ViharaResponse, str]] = None
    br_robing_after_residence_temple: Optional[Union[ViharaResponse, str]] = None
    
    # Workflow Fields - Include for client to track status
    br_workflow_status: Optional[str] = None
    br_approval_status: Optional[str] = None
    br_version_number: Optional[int] = None
    br_scanned_document_path: Optional[str] = None
    br_printed_at: Optional[datetime] = None
    br_scanned_at: Optional[datetime] = None
    br_approved_at: Optional[datetime] = None
    br_rejected_at: Optional[datetime] = None
    br_rejection_reason: Optional[str] = None
    
    # Location tracking field (for location-based access control)
    br_created_by_district: Optional[str] = None

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
    # Advanced filters for READ_ALL
    province: Optional[str] = Field(None, description="Province code filter")
    vh_trn: Optional[str] = Field(None, description="Vihara TRN filter")
    district: Optional[str] = Field(None, description="District code filter")
    divisional_secretariat: Optional[str] = Field(None, description="Divisional secretariat code filter")
    gn_division: Optional[str] = Field(None, description="GN division code filter")
    temple: Optional[str] = Field(None, description="Current residence temple TRN filter")
    child_temple: Optional[str] = Field(None, description="Mahana temple TRN filter")
    nikaya: Optional[str] = Field(None, description="Nikaya code filter")
    parshawaya: Optional[str] = Field(None, description="Parshawaya code filter")
    category: Optional[List[str]] = Field(None, description="List of category codes to filter by")
    status: Optional[List[str]] = Field(None, description="List of status codes to filter by")
    workflow_status: Optional[List[str]] = Field(None, description="List of workflow status codes to filter by")
    date_from: Optional[date] = Field(None, description="Start date for filtering by request date")
    date_to: Optional[date] = Field(None, description="End date for filtering by request date")
    # For CREATE, UPDATE
    data: Optional[Union[BhikkuCreate, BhikkuUpdate]] = None
    # For workflow actions (APPROVE, REJECT)
    rejection_reason: Optional[str] = Field(None, max_length=500)

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
    model_config = ConfigDict(from_attributes=True)
    
    status: str
    message: str
    data: Optional[Union[Bhikku, List[Bhikku], Any]] = None
    # Optional pagination fields (only for READ_ALL)
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None


class BhikkuMahanayakaListItem(BaseModel):
    regn: str
    mahananame: Optional[str] = None
    currstat: Optional[str] = None
    vname: Optional[str] = None
    addrs: Optional[str] = None


class BhikkuMahanayakaListResponse(BaseModel):
    status: str
    message: str
    data: List[BhikkuMahanayakaListItem]


class BhikkuNikayaListItem(BaseModel):
    nkn: Optional[str] = None
    nname: Optional[str] = None
    prn: Optional[str] = None
    pname: Optional[str] = None
    regn: str


class BhikkuNikayaListResponse(BaseModel):
    status: str
    message: str
    data: List[BhikkuNikayaListItem]


class BhikkuNikayaHierarchyBhikku(BaseModel):
    regn: str
    gihiname: Optional[str] = None
    mahananame: Optional[str] = None
    current_status: Optional[str] = None
    parshawaya: Optional[str] = None
    livtemple: Optional[str] = None
    mahanatemple: Optional[str] = None
    address: Optional[str] = None


class BhikkuNikayaParshawaItem(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    remarks: Optional[str] = None
    start_date: Optional[date] = None
    nayaka_regn: Optional[str] = None
    nayaka: Optional[BhikkuNikayaHierarchyBhikku] = None


class BhikkuNikayaHierarchyNikaya(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None


class BhikkuNikayaHierarchyItem(BaseModel):
    nikaya: BhikkuNikayaHierarchyNikaya
    main_bhikku: Optional[BhikkuNikayaHierarchyBhikku] = None
    parshawayas: List[BhikkuNikayaParshawaItem] = Field(default_factory=list)


class BhikkuNikayaHierarchyResponse(BaseModel):
    status: str
    message: str
    data: List[BhikkuNikayaHierarchyItem]


class BhikkuAcharyaListItem(BaseModel):
    currstated: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[EmailStr] = None
    mahanadate: Optional[date] = None
    reqstdate: Optional[date] = None
    regn: str


class BhikkuAcharyaListResponse(BaseModel):
    status: str
    message: str
    data: List[BhikkuAcharyaListItem]


class BhikkuDetailsListItem(BaseModel):
    regn: str
    birthpls: Optional[str] = None
    gihiname: Optional[str] = None
    dofb: Optional[date] = None
    fathrname: Optional[str] = None
    mahanadate: Optional[date] = None
    mahananame: Optional[str] = None
    teacher: Optional[str] = None
    teachadrs: Optional[str] = None
    mhanavh: Optional[str] = None
    livetemple: Optional[str] = None
    viharadipathi: Optional[str] = None
    pname: Optional[str] = None
    nname: Optional[str] = None
    nikayanayaka: Optional[str] = None
    effctdate: Optional[date] = None
    curstatus: Optional[str] = None
    catogry: Optional[str] = None
    vadescrdtls: Optional[str] = None


class BhikkuDetailsListResponse(BaseModel):
    status: str
    message: str
    data: List[BhikkuDetailsListItem]


class BhikkuCertificationListItem(BaseModel):
    regno: str
    mahananame: Optional[str] = None
    issuedate: Optional[date] = None
    reqstdate: Optional[date] = None
    adminautho: Optional[str] = None
    prtoptn: Optional[str] = None
    paydate: Optional[date] = None
    payamount: Optional[float] = None
    usname: Optional[str] = None
    adminusr: Optional[str] = None


class BhikkuCertificationListResponse(BaseModel):
    status: str
    message: str
    data: List[BhikkuCertificationListItem]


class BhikkuCertificationPrintListItem(BaseModel):
    regno: str
    mahananame: Optional[str] = None
    issuedate: Optional[date] = None
    reqstdate: Optional[date] = None
    adminautho: Optional[str] = None
    prtoptn: Optional[str] = None
    paydate: Optional[date] = None
    payamount: Optional[float] = None
    usname: Optional[str] = None
    adminusr: Optional[str] = None


class BhikkuCertificationPrintListResponse(BaseModel):
    status: str
    message: str
    data: List[BhikkuCertificationPrintListItem]


class BhikkuCurrentStatusListItem(BaseModel):
    statcd: str
    descr: Optional[str] = None
    regn: str


class BhikkuCurrentStatusListResponse(BaseModel):
    status: str
    message: str
    data: List[BhikkuCurrentStatusListItem]


class BhikkuDistrictListItem(BaseModel):
    dcode: str
    dname: Optional[str] = None
    regn: str


class BhikkuDistrictListResponse(BaseModel):
    status: str
    message: str
    data: List[BhikkuDistrictListItem]


class BhikkuDivisionSecListItem(BaseModel):
    dvcode: str
    dvname: Optional[str] = None
    regn: str


class BhikkuDivisionSecListResponse(BaseModel):
    status: str
    message: str
    data: List[BhikkuDivisionSecListItem]


class BhikkuGNListItem(BaseModel):
    gnc: str
    gnname: Optional[str] = None
    regn: str


class BhikkuGNListResponse(BaseModel):
    status: str
    message: str
    data: List[BhikkuGNListItem]


class BhikkuHistoryStatusListItem(BaseModel):
    descr: Optional[str] = None
    prvdate: Optional[date] = None
    chngdate: Optional[date] = None
    regno: str


class BhikkuHistoryStatusListResponse(BaseModel):
    status: str
    message: str
    data: List[BhikkuHistoryStatusListItem]


class BhikkuIDAllListItem(BaseModel):
    idn: str
    stat: Optional[str] = None
    reqstdate: Optional[date] = None
    printdate: Optional[date] = None
    issuedate: Optional[date] = None
    mahanaacharyacd: Optional[str] = None
    archadrs: Optional[str] = None
    achambl: Optional[str] = None
    achamhndate: Optional[date] = None
    acharegdt: Optional[date] = None
    mahananame: Optional[str] = None
    vname: Optional[str] = None
    addrs: Optional[str] = None
    regn: str
    dofb: Optional[date] = None
    mahanadate: Optional[date] = None
    gihiname: Optional[str] = None
    fathrdetails: Optional[str] = None


class BhikkuIDAllListResponse(BaseModel):
    status: str
    message: str
    data: List[BhikkuIDAllListItem]


class BhikkuIDDistrictListItem(BaseModel):
    dcode: str
    dname: Optional[str] = None
    idn: str


class BhikkuIDDistrictListResponse(BaseModel):
    status: str
    message: str
    data: List[BhikkuIDDistrictListItem]


class BhikkuIDDvSecListItem(BaseModel):
    dvcode: str
    dvname: Optional[str] = None
    idn: str


class BhikkuIDDvSecListResponse(BaseModel):
    status: str
    message: str
    data: List[BhikkuIDDvSecListItem]


class BhikkuIDGNListItem(BaseModel):
    gnname: Optional[str] = None
    idn: str


class BhikkuIDGNListResponse(BaseModel):
    status: str
    message: str
    data: List[BhikkuIDGNListItem]


class BhikkuNikayanayakaListItem(BaseModel):
    regn: str
    mahananame: Optional[str] = None
    currstat: Optional[str] = None
    vname: Optional[str] = None
    addrs: Optional[str] = None


class BhikkuNikayanayakaListResponse(BaseModel):
    status: str
    message: str
    data: List[BhikkuNikayanayakaListItem]


class BhikkuParshawaListItem(BaseModel):
    prn: str
    pname: Optional[str] = None
    regn: str


class BhikkuParshawaListResponse(BaseModel):
    status: str
    message: str
    data: List[BhikkuParshawaListItem]


class BhikkuStatusHistoryCompositeItem(BaseModel):
    regno: str
    vadescrdtls: Optional[str] = None


class BhikkuStatusHistoryCompositeResponse(BaseModel):
    status: str
    message: str
    data: List[BhikkuStatusHistoryCompositeItem]


class BhikkuStatusHistoryListItem(BaseModel):
    regno: str
    prvdate: Optional[date] = None
    chngdate: Optional[date] = None
    descr: Optional[str] = None


class BhikkuStatusHistoryListResponse(BaseModel):
    status: str
    message: str
    data: List[BhikkuStatusHistoryListItem]


class BhikkuStatusHistoryList2Item(BaseModel):
    regno: str
    statchgdescr: Optional[str] = None


class BhikkuStatusHistoryList2Response(BaseModel):
    status: str
    message: str
    data: List[BhikkuStatusHistoryList2Item]


class BhikkuViharadipathiListItem(BaseModel):
    regn: str
    mahananame: Optional[str] = None


class BhikkuViharadipathiListResponse(BaseModel):
    status: str
    message: str
    data: List[BhikkuViharadipathiListItem]


class BhikkuCurrentStatusSummaryItem(BaseModel):
    statcd: str
    descr: Optional[str] = None
    statcnt: int


class BhikkuCurrentStatusSummaryResponse(BaseModel):
    status: str
    message: str
    data: List[BhikkuCurrentStatusSummaryItem]


class BhikkuDistrictSummaryItem(BaseModel):
    dcode: str
    dname: Optional[str] = None
    totalbikku: int


class BhikkuDistrictSummaryResponse(BaseModel):
    status: str
    message: str
    data: List[BhikkuDistrictSummaryItem]


class BhikkuGNSummaryItem(BaseModel):
    gnc: str
    gnname: Optional[str] = None
    bikkucnt: int


class BhikkuGNSummaryResponse(BaseModel):
    status: str
    message: str
    data: List[BhikkuGNSummaryItem]


class BhikkuIDDistrictSummaryItem(BaseModel):
    dcode: str
    dname: Optional[str] = None
    idcnt: int


class BhikkuIDDistrictSummaryResponse(BaseModel):
    status: str
    message: str
    data: List[BhikkuIDDistrictSummaryItem]


class BhikkuIDGNSummaryItem(BaseModel):
    gnname: Optional[str] = None
    idcnt: int


class BhikkuIDGNSummaryResponse(BaseModel):
    status: str
    message: str
    data: List[BhikkuIDGNSummaryItem]


# --- Workflow Action Schemas ---
class WorkflowActionType(str, Enum):
    """Workflow actions available for bhikku records"""
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


class BhikkuWorkflowRequest(BaseModel):
    """Request to update workflow status of a bhikku record"""
    br_regn: str = Field(..., description="Bhikku registration number")
    action: WorkflowActionType
    rejection_reason: Optional[str] = Field(None, max_length=500, description="Required when action is REJECT or REJECT_REPRINT")
    reprint_reason: Optional[str] = Field(None, max_length=500, description="Required when action is REQUEST_REPRINT")
    reprint_amount: Optional[float] = Field(None, description="Reprint amount - required when action is REQUEST_REPRINT")
    reprint_remarks: Optional[str] = Field(None, max_length=500, description="Reprint remarks - optional when action is REQUEST_REPRINT")
    
    class Config:
        json_schema_extra = {
            "example": {
                "br_regn": "BH2025000001",
                "action": "APPROVE"
            }
        }


class BhikkuWorkflowResponse(BaseModel):
    """Response after workflow action"""
    model_config = ConfigDict(from_attributes=True)
    
    status: str
    message: str
    data: Optional[Bhikku] = None


class BhikkuRejectRequest(BaseModel):
    """Request to reject a bhikku registration"""
    rejection_reason: str = Field(..., min_length=1, max_length=500, description="Reason for rejection")
    
    class Config:
        json_schema_extra = {
            "example": {
                "rejection_reason": "Incomplete documentation"
            }
        }


# --- QR Search Schemas ---
class QRSearchRequest(BaseModel):
    """Request schema for QR search lookup"""
    id: str  # Can be br_regn, sil_regn, or bhr_regn
    record_type: Optional[str] = None  # Optional: "bhikku", "silmatha", or "bhikku_high"


class QRSearchDataItem(BaseModel):
    """Individual data item in QR search response"""
    titel: str
    text: Optional[str] = None


class QRSearchResponseWrapper(BaseModel):
    """Wrapper for QR search response"""
    status: str
    message: str
    data: List[QRSearchDataItem]
