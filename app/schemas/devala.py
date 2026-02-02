from datetime import date, datetime
import re
from enum import Enum
from typing import Annotated, Optional, Union, List, Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.devala_land import DevalaLandCreate, DevalaLandInDB

PHONE_PATTERN = re.compile(r"^[0-9]{10}$")


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


class DevalaBase(BaseModel):
    dv_trn: Annotated[str, Field(min_length=1, max_length=10)]
    dv_vname: Annotated[Optional[str], Field(default=None, max_length=200)]
    dv_addrs: Annotated[Optional[str], Field(default=None, max_length=200)]
    dv_mobile: Annotated[str, Field(min_length=10, max_length=10)]
    dv_whtapp: Annotated[str, Field(min_length=10, max_length=10)]
    dv_email: EmailStr
    dv_typ: Annotated[str, Field(min_length=1, max_length=10)]
    dv_gndiv: Annotated[str, Field(min_length=1, max_length=10)]
    dv_fmlycnt: Annotated[Optional[int], Field(default=None, ge=0)]
    dv_bgndate: Optional[date] = None
    dv_ownercd: Annotated[str, Field(min_length=1, max_length=12)]
    dv_parshawa: Annotated[str, Field(min_length=1, max_length=10)]
    dv_ssbmcode: Annotated[Optional[str], Field(default=None, max_length=10)]
    dv_syojakarmakrs: Annotated[Optional[str], Field(default=None, max_length=100)]
    dv_syojakarmdate: Optional[date] = None
    dv_landownrship: Annotated[Optional[str], Field(default=None, max_length=150)]
    dv_pralename: Annotated[Optional[str], Field(default=None, max_length=50)]
    dv_pralesigdate: Optional[date] = None
    dv_bacgrecmn: Annotated[Optional[str], Field(default=None, max_length=100)]
    dv_bacgrcmdate: Optional[date] = None
    dv_minissecrsigdate: Optional[date] = None
    dv_minissecrmrks: Annotated[Optional[str], Field(default=None, max_length=200)]
    dv_ssbmsigdate: Optional[date] = None
    
    # Extended Fields
    dv_province: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    dv_district: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    dv_divisional_secretariat: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    dv_pradeshya_sabha: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    dv_nikaya: Annotated[Optional[str], Field(default=None, max_length=50)] = None
    dv_viharadhipathi_name: Annotated[Optional[str], Field(default=None, max_length=200)] = None
    dv_period_established: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    dv_buildings_description: Annotated[Optional[str], Field(default=None, max_length=1000)] = None
    dv_dayaka_families_count: Annotated[Optional[str], Field(default=None, max_length=50)] = None
    dv_kulangana_committee: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    dv_dayaka_sabha: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    dv_temple_working_committee: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    dv_other_associations: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    dv_temple_owned_land: Annotated[Optional[str], Field(default=None, max_length=2000)] = None
    dv_land_info_certified: Optional[bool] = None
    dv_resident_bhikkhus: Annotated[Optional[str], Field(default=None, max_length=2000)] = None
    dv_resident_bhikkhus_certified: Optional[bool] = None
    dv_inspection_report: Annotated[Optional[str], Field(default=None, max_length=1000)] = None
    dv_inspection_code: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    dv_grama_niladhari_division_ownership: Annotated[Optional[str], Field(default=None, max_length=200)] = None
    dv_sanghika_donation_deed: Optional[bool] = None
    dv_government_donation_deed: Optional[bool] = None
    dv_government_donation_deed_in_progress: Optional[bool] = None
    dv_authority_consent_attached: Optional[bool] = None
    dv_recommend_new_center: Optional[bool] = None
    dv_recommend_registered_temple: Optional[bool] = None
    dv_annex2_recommend_construction: Optional[bool] = None
    dv_annex2_land_ownership_docs: Optional[bool] = None
    dv_annex2_chief_incumbent_letter: Optional[bool] = None
    dv_annex2_coordinator_recommendation: Optional[bool] = None
    dv_annex2_divisional_secretary_recommendation: Optional[bool] = None
    dv_annex2_approval_construction: Optional[bool] = None
    dv_annex2_referral_resubmission: Optional[bool] = None
    
    # Document Storage
    dv_scanned_document_path: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    dv_form_id: Annotated[Optional[str], Field(default=None, max_length=50)] = None
    
    # Workflow Fields
    dv_workflow_status: Annotated[Optional[str], Field(default="PENDING", max_length=20)] = "PENDING"
    dv_approval_status: Annotated[Optional[str], Field(default=None, max_length=20)] = None
    dv_approved_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    dv_approved_at: Optional[datetime] = None
    dv_rejected_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    dv_rejected_at: Optional[datetime] = None
    dv_rejection_reason: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    dv_printed_at: Optional[datetime] = None
    dv_printed_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    dv_scanned_at: Optional[datetime] = None
    dv_scanned_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    
    dv_is_deleted: bool = False
    dv_created_at: Optional[datetime] = None
    dv_updated_at: Optional[datetime] = None
    dv_created_by: Annotated[Optional[str], Field(default=None, max_length=25)]
    dv_updated_by: Annotated[Optional[str], Field(default=None, max_length=25)]
    dv_version_number: Annotated[int, Field(ge=1)] = 1

    @field_validator(
        "dv_trn",
        "dv_vname",
        "dv_addrs",
        "dv_typ",
        "dv_gndiv",
        "dv_ownercd",
        "dv_parshawa",
        "dv_ssbmcode",
        "dv_syojakarmakrs",
        "dv_landownrship",
        "dv_pralename",
        "dv_bacgrecmn",
        "dv_minissecrmrks",
        "dv_created_by",
        "dv_updated_by",
        mode="before",
    )
    @classmethod
    def _strip_strings(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            if value == "":
                return None
        return value

    @field_validator("dv_mobile", "dv_whtapp")
    @classmethod
    def _validate_phone(cls, value: str) -> str:
        if not PHONE_PATTERN.fullmatch(value):
            raise ValueError("Phone numbers must be exactly 10 digits.")
        return value

    @field_validator("dv_email", mode="before")
    @classmethod
    def _normalize_email(cls, value: str) -> str:
        if isinstance(value, str):
            value = value.strip()
        return value

    @field_validator("dv_ownercd", mode="before")
    @classmethod
    def _truncate_ownercd(cls, value: Optional[str]) -> Optional[str]:
        """Truncate dv_ownercd to max 12 characters if needed"""
        if isinstance(value, str) and len(value) > 12:
            return value[:12]
        return value


class DevalaCreate(DevalaBase):
    dv_trn: Annotated[Optional[str], Field(default=None, min_length=1, max_length=10)]
    dv_id: Annotated[Optional[int], Field(default=None, ge=1)] = None


class DevalaCreatePayload(BaseModel):
    """Payload schema for creating Devala with camelCase field names"""
    temple_name: Optional[str] = Field(default=None, max_length=200)
    temple_address: Optional[str] = Field(default=None, max_length=200)
    telephone_number: str = Field(min_length=10, max_length=10)
    whatsapp_number: str = Field(min_length=10, max_length=10)
    email_address: EmailStr
    province: Optional[str] = Field(default=None, max_length=100)
    district: Optional[str] = Field(default=None, max_length=100)
    divisional_secretariat: Optional[str] = Field(default=None, max_length=100)
    pradeshya_sabha: Optional[str] = Field(default=None, max_length=100)
    grama_niladhari_division: str = Field(min_length=1, max_length=10)
    nikaya: Optional[str] = Field(default=None, max_length=50)
    parshawaya: str = Field(min_length=1, max_length=10)
    viharadhipathi_name: Optional[str] = Field(default=None, max_length=200)
    period_established: Optional[str] = Field(default=None, max_length=100)
    buildings_description: Optional[str] = Field(default=None, max_length=1000)
    dayaka_families_count: Optional[str] = Field(default=None, max_length=50)
    kulangana_committee: Optional[str] = Field(default=None, max_length=500)
    dayaka_sabha: Optional[str] = Field(default=None, max_length=500)
    temple_working_committee: Optional[str] = Field(default=None, max_length=500)
    other_associations: Optional[str] = Field(default=None, max_length=500)
    
    temple_owned_land: List[DevalaLandCreate] = Field(default_factory=list)
    
    land_info_certified: Optional[bool] = None
    resident_bhikkhus: Optional[str] = Field(default=None, max_length=2000)
    resident_bhikkhus_certified: Optional[bool] = None
    inspection_report: Optional[str] = Field(default=None, max_length=1000)
    inspection_code: Optional[str] = Field(default=None, max_length=100)
    grama_niladhari_division_ownership: Optional[str] = Field(default=None, max_length=200)
    
    sanghika_donation_deed: Optional[bool] = None
    government_donation_deed: Optional[bool] = None
    government_donation_deed_in_progress: Optional[bool] = None
    authority_consent_attached: Optional[bool] = None
    recommend_new_center: Optional[bool] = None
    recommend_registered_temple: Optional[bool] = None
    
    annex2_recommend_construction: Optional[bool] = None
    annex2_land_ownership_docs: Optional[bool] = None
    annex2_chief_incumbent_letter: Optional[bool] = None
    annex2_coordinator_recommendation: Optional[bool] = None
    annex2_divisional_secretary_recommendation: Optional[bool] = None
    annex2_approval_construction: Optional[bool] = None
    annex2_referral_resubmission: Optional[bool] = None

    @field_validator("telephone_number", "whatsapp_number")
    @classmethod
    def _validate_phone(cls, value: str) -> str:
        if not PHONE_PATTERN.fullmatch(value):
            raise ValueError("Phone numbers must be exactly 10 digits.")
        return value


class DevalaUpdate(BaseModel):
    dv_trn: Annotated[Optional[str], Field(default=None, min_length=1, max_length=10)]
    dv_vname: Annotated[Optional[str], Field(default=None, max_length=200)]
    dv_addrs: Annotated[Optional[str], Field(default=None, max_length=200)]
    dv_mobile: Annotated[Optional[str], Field(default=None, min_length=10, max_length=10)]
    dv_whtapp: Annotated[Optional[str], Field(default=None, min_length=10, max_length=10)]
    dv_email: Optional[EmailStr] = None
    dv_typ: Annotated[Optional[str], Field(default=None, min_length=1, max_length=10)]
    dv_gndiv: Annotated[Optional[str], Field(default=None, min_length=1, max_length=10)]
    dv_fmlycnt: Annotated[Optional[int], Field(default=None, ge=0)]
    dv_bgndate: Optional[date] = None
    dv_ownercd: Annotated[Optional[str], Field(default=None, min_length=1, max_length=12)]
    dv_parshawa: Annotated[Optional[str], Field(default=None, min_length=1, max_length=10)]
    dv_ssbmcode: Annotated[Optional[str], Field(default=None, max_length=10)]
    dv_syojakarmakrs: Annotated[Optional[str], Field(default=None, max_length=100)]
    dv_syojakarmdate: Optional[date] = None
    dv_landownrship: Annotated[Optional[str], Field(default=None, max_length=150)]
    dv_pralename: Annotated[Optional[str], Field(default=None, max_length=50)]
    dv_pralesigdate: Optional[date] = None
    dv_bacgrecmn: Annotated[Optional[str], Field(default=None, max_length=100)]
    dv_bacgrcmdate: Optional[date] = None
    dv_minissecrsigdate: Optional[date] = None
    dv_minissecrmrks: Annotated[Optional[str], Field(default=None, max_length=200)]
    dv_ssbmsigdate: Optional[date] = None
    
    # Extended Fields
    dv_province: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    dv_district: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    dv_divisional_secretariat: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    dv_pradeshya_sabha: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    dv_nikaya: Annotated[Optional[str], Field(default=None, max_length=50)] = None
    dv_viharadhipathi_name: Annotated[Optional[str], Field(default=None, max_length=200)] = None
    dv_period_established: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    dv_buildings_description: Annotated[Optional[str], Field(default=None, max_length=1000)] = None
    dv_dayaka_families_count: Annotated[Optional[str], Field(default=None, max_length=50)] = None
    dv_kulangana_committee: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    dv_dayaka_sabha: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    dv_temple_working_committee: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    dv_other_associations: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    dv_temple_owned_land: Annotated[Optional[str], Field(default=None, max_length=2000)] = None
    dv_land_info_certified: Optional[bool] = None
    dv_resident_bhikkhus: Annotated[Optional[str], Field(default=None, max_length=2000)] = None
    dv_resident_bhikkhus_certified: Optional[bool] = None
    dv_inspection_report: Annotated[Optional[str], Field(default=None, max_length=1000)] = None
    dv_inspection_code: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    dv_grama_niladhari_division_ownership: Annotated[Optional[str], Field(default=None, max_length=200)] = None
    dv_sanghika_donation_deed: Optional[bool] = None
    dv_government_donation_deed: Optional[bool] = None
    dv_government_donation_deed_in_progress: Optional[bool] = None
    dv_authority_consent_attached: Optional[bool] = None
    dv_recommend_new_center: Optional[bool] = None
    dv_recommend_registered_temple: Optional[bool] = None
    dv_annex2_recommend_construction: Optional[bool] = None
    dv_annex2_land_ownership_docs: Optional[bool] = None
    dv_annex2_chief_incumbent_letter: Optional[bool] = None
    dv_annex2_coordinator_recommendation: Optional[bool] = None
    dv_annex2_divisional_secretary_recommendation: Optional[bool] = None
    dv_annex2_approval_construction: Optional[bool] = None
    dv_annex2_referral_resubmission: Optional[bool] = None
    
    # Document Storage
    dv_scanned_document_path: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    dv_form_id: Annotated[Optional[str], Field(default=None, max_length=50)] = None
    
    # Workflow Fields
    dv_workflow_status: Annotated[Optional[str], Field(default=None, max_length=20)] = None
    dv_approval_status: Annotated[Optional[str], Field(default=None, max_length=20)] = None
    dv_approved_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    dv_approved_at: Optional[datetime] = None
    dv_rejected_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    dv_rejected_at: Optional[datetime] = None
    dv_rejection_reason: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    dv_printed_at: Optional[datetime] = None
    dv_printed_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    dv_scanned_at: Optional[datetime] = None
    dv_scanned_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    
    dv_is_deleted: Optional[bool] = None
    dv_version_number: Annotated[Optional[int], Field(default=None, ge=1)] = None
    dv_updated_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    dv_updated_at: Optional[datetime] = None

    @field_validator(
        "dv_trn",
        "dv_vname",
        "dv_addrs",
        "dv_typ",
        "dv_gndiv",
        "dv_ownercd",
        "dv_parshawa",
        "dv_ssbmcode",
        "dv_syojakarmakrs",
        "dv_landownrship",
        "dv_pralename",
        "dv_bacgrecmn",
        "dv_minissecrmrks",
        "dv_updated_by",
        mode="before",
    )
    @classmethod
    def _strip_strings(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value

    @field_validator("dv_mobile", "dv_whtapp")
    @classmethod
    def _validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not PHONE_PATTERN.fullmatch(value):
            raise ValueError("Phone numbers must be exactly 10 digits.")
        return value

    @field_validator("dv_email", mode="before")
    @classmethod
    def _normalize_email(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value

    @field_validator("dv_ownercd", mode="before")
    @classmethod
    def _truncate_ownercd(cls, value: Optional[str]) -> Optional[str]:
        """Truncate dv_ownercd to max 12 characters if needed"""
        if isinstance(value, str) and len(value) > 12:
            return value[:12]
        return value


class DevalaOut(DevalaBase):
    model_config = ConfigDict(from_attributes=True)

    dv_id: int


class DevalaRequestPayload(BaseModel):
    # Identifiers
    dv_id: Optional[int] = None
    dv_trn: Optional[str] = None
    
    # Pagination
    skip: Annotated[int, Field(ge=0)] = 0
    limit: Annotated[int, Field(ge=1, le=200)] = 10
    page: Annotated[Optional[int], Field(default=1, ge=1)] = 1
    
    # Search and filters
    search_key: Annotated[Optional[str], Field(default=None, max_length=200)] = None
    province: Annotated[Optional[str], Field(default=None, max_length=10)] = None
    district: Annotated[Optional[str], Field(default=None, max_length=10)] = None
    divisional_secretariat: Annotated[Optional[str], Field(default=None, max_length=10)] = None
    gn_division: Annotated[Optional[str], Field(default=None, max_length=10)] = None
    temple: Annotated[Optional[str], Field(default=None, max_length=12)] = None  # dv_ownercd
    child_temple: Annotated[Optional[str], Field(default=None, max_length=12)] = None
    nikaya: Annotated[Optional[str], Field(default=None, max_length=10)] = None
    parshawaya: Annotated[Optional[str], Field(default=None, max_length=10)] = None  # dv_parshawa
    category: Annotated[Optional[str], Field(default=None, max_length=10)] = None
    status: Annotated[Optional[str], Field(default=None, max_length=10)] = None
    dv_typ: Annotated[Optional[str], Field(default=None, max_length=10)] = None  # devala type
    
    # Date range filters
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    
    # Workflow action fields
    rejection_reason: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    
    # Data payload for CREATE/UPDATE
    data: Optional[Union[DevalaCreate, DevalaUpdate]] = None


class DevalaManagementRequest(BaseModel):
    action: CRUDAction
    payload: DevalaRequestPayload


class DevalaManagementResponse(BaseModel):
    status: str
    message: str
    data: Optional[Union[DevalaOut, List[DevalaOut], Any]] = None
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None


# Simple Devala List Schema for Bhikku endpoints
class BhikkuDevalaListItem(BaseModel):
    dv_trn: str
    dv_vname: Optional[str] = None


class BhikkuDevalaListResponse(BaseModel):
    status: str
    message: str
    data: List[BhikkuDevalaListItem]
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None


# New schema for POST devala-list endpoint
class BhikkuDevalaReadOnePayload(BaseModel):
    dv_id: int = Field(..., ge=1, description="Devala ID to retrieve")


class BhikkuDevalaReadAllPayload(BaseModel):
    skip: Annotated[int, Field(ge=0)] = 0
    limit: Annotated[int, Field(ge=1, le=200)] = 10
    page: Annotated[Optional[int], Field(ge=1)] = 1
    search_key: Annotated[Optional[str], Field(default=None, max_length=200)] = None


class BhikkuDevalaManagementRequest(BaseModel):
    action: str = Field(..., description="Action to perform: 'READ_ONE' or 'READ_ALL'")
    payload: Union[BhikkuDevalaReadOnePayload, BhikkuDevalaReadAllPayload]
