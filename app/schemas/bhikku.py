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
    br_residence_at_declaration: Optional[str] = None
    br_declaration_date: Optional[date] = None
    
    # Temple/Religious Information
    br_parshawaya: str
    br_nikaya: Optional[str] = None
    br_livtemple: Optional[str] = None
    br_mahanatemple: str
    br_mahanaacharyacd: str
    br_multi_mahanaacharyacd: Optional[str] = None
    br_mahananame: Optional[str] = None
    br_mahanadate: Optional[date] = None
    br_mahanayaka_name: Optional[str] = None
    br_mahanayaka_address: Optional[str] = None
    br_viharadhipathi: Optional[str] = None
    br_cat: Optional[str] = None

    # Contact Information
    br_mobile: Optional[str] = Field(None, max_length=10)
    br_email: Optional[EmailStr] = None
    br_fathrsaddrs: Optional[str] = None
    br_fathrsmobile: Optional[str] = Field(None, max_length=10)

    # Serial Number
    br_upasampada_serial_no: Optional[str] = None
    br_robing_tutor_residence: Optional[str] = None
    br_robing_after_residence_temple: Optional[str] = None

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
    br_residence_at_declaration: Optional[str] = None
    br_declaration_date: Optional[date] = None
    
    # Temple/Religious Information
    br_parshawaya: Optional[str] = None
    br_nikaya: Optional[str] = None
    br_livtemple: Optional[str] = None
    br_mahanatemple: Optional[str] = None
    br_mahanaacharyacd: Optional[str] = None
    br_multi_mahanaacharyacd: Optional[str] = None
    br_mahananame: Optional[str] = None
    br_mahanadate: Optional[date] = None
    br_mahanayaka_name: Optional[str] = None
    br_mahanayaka_address: Optional[str] = None
    br_viharadhipathi: Optional[str] = None
    br_cat: Optional[str] = None
    
    # Contact Information
    br_mobile: Optional[str] = Field(None, max_length=10)
    br_email: Optional[EmailStr] = None
    br_fathrsaddrs: Optional[str] = None
    br_fathrsmobile: Optional[str] = Field(None, max_length=10)

    # Serial Number
    br_upasampada_serial_no: Optional[str] = None

    br_robing_tutor_residence: Optional[str] = None
    br_robing_after_residence_temple: Optional[str] = None

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
    # For READ_ALL - Pagination and search
    skip: Annotated[int, Field(ge=0)] = 0
    limit: Annotated[int, Field(ge=1, le=200)] = 10
    page: Annotated[Optional[int], Field(ge=1)] = 1
    search_key: Optional[str] = Field(default="", max_length=100)
    # Filters for READ_ALL
    province: Optional[str] = Field(default=None)
    vh_trn: Optional[str] = Field(default=None)
    district: Optional[str] = Field(default=None)
    divisional_secretariat: Optional[str] = Field(default=None)
    gn_division: Optional[str] = Field(default=None)
    temple: Optional[str] = Field(default=None)
    child_temple: Optional[str] = Field(default=None)
    nikaya: Optional[str] = Field(default=None)
    parshawaya: Optional[str] = Field(default=None)
    category: List[str] = Field(default_factory=list)
    status: List[str] = Field(default_factory=list)
    date_from: Optional[date] = None
    date_to: Optional[date] = None
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
