from datetime import date, datetime
import re
from enum import Enum
from typing import Annotated, Optional, Union, List, Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from app.schemas.arama_land import AramaLandCreate, AramaLandInDB
from app.schemas.arama_resident_silmatha import AramaResidentSilmathaCreate, AramaResidentSilmathaInDB

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


# --- Nested Response Schemas for Foreign Key Fields ---
class ProvinceResponse(BaseModel):
    """Nested response for province"""
    cp_code: str
    cp_name: Optional[str] = None

class DistrictResponse(BaseModel):
    """Nested response for district"""
    dd_dcode: str
    dd_dname: Optional[str] = None

class DivisionalSecretariatResponse(BaseModel):
    """Nested response for divisional secretariat"""
    dv_dvcode: str
    dv_dvname: Optional[str] = None

class GNDivisionResponse(BaseModel):
    """Nested response for GN division"""
    gn_gnc: str
    gn_gnname: Optional[str] = None

class NikayaResponse(BaseModel):
    """Nested response for nikaya"""
    nk_nkn: str
    nk_nname: Optional[str] = None

class ParshawaResponse(BaseModel):
    """Nested response for parshawa"""
    pr_prn: str
    pr_pname: Optional[str] = None

class SilmathaResponse(BaseModel):
    """Nested response for owner silmatha"""
    sil_regn: str
    sil_gihiname: Optional[str] = None
    sil_mahananame: Optional[str] = None


class AramaBase(BaseModel):
    ar_trn: Annotated[str, Field(min_length=1, max_length=10)]
    ar_vname: Annotated[Optional[str], Field(default=None, max_length=200)]
    ar_addrs: Annotated[Optional[str], Field(default=None, max_length=200)]
    ar_mobile: Annotated[str, Field(min_length=10, max_length=10)]
    ar_whtapp: Annotated[str, Field(min_length=10, max_length=10)]
    ar_email: EmailStr
    ar_typ: Annotated[str, Field(min_length=1, max_length=10)]
    ar_gndiv: Annotated[str, Field(min_length=1, max_length=10)]
    ar_fmlycnt: Annotated[Optional[int], Field(default=None, ge=0)]
    ar_bgndate: Optional[date] = None
    ar_ownercd: Annotated[str, Field(min_length=1, max_length=12)]
    ar_parshawa: Annotated[str, Field(min_length=1, max_length=10)]
    ar_ssbmcode: Annotated[Optional[str], Field(default=None, max_length=10)]
    ar_syojakarmakrs: Annotated[Optional[str], Field(default=None, max_length=100)]
    ar_syojakarmdate: Optional[date] = None
    ar_landownrship: Annotated[Optional[str], Field(default=None, max_length=150)]
    ar_pralename: Annotated[Optional[str], Field(default=None, max_length=50)]
    ar_pralesigdate: Optional[date] = None
    ar_bacgrecmn: Annotated[Optional[str], Field(default=None, max_length=100)]
    ar_bacgrcmdate: Optional[date] = None
    ar_minissecrsigdate: Optional[date] = None
    ar_minissecrmrks: Annotated[Optional[str], Field(default=None, max_length=200)]
    ar_ssbmsigdate: Optional[date] = None
    
    # Extended Fields
    ar_province: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    ar_district: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    ar_divisional_secretariat: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    ar_pradeshya_sabha: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    ar_nikaya: Annotated[Optional[str], Field(default=None, max_length=50)] = None
    ar_viharadhipathi_name: Annotated[Optional[str], Field(default=None, max_length=200)] = None
    ar_period_established: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    ar_buildings_description: Annotated[Optional[str], Field(default=None, max_length=1000)] = None
    ar_dayaka_families_count: Annotated[Optional[str], Field(default=None, max_length=50)] = None
    ar_kulangana_committee: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    ar_dayaka_sabha: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    ar_temple_working_committee: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    ar_other_associations: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    ar_land_info_certified: Optional[bool] = None
    ar_inspection_report: Annotated[Optional[str], Field(default=None, max_length=1000)] = None
    ar_inspection_code: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    ar_grama_niladhari_division_ownership: Annotated[Optional[str], Field(default=None, max_length=200)] = None
    ar_sanghika_donation_deed: Optional[bool] = None
    ar_government_donation_deed: Optional[bool] = None
    ar_government_donation_deed_in_progress: Optional[bool] = None
    ar_authority_consent_attached: Optional[bool] = None
    ar_recommend_new_center: Optional[bool] = None
    ar_recommend_registered_temple: Optional[bool] = None
    ar_annex2_recommend_construction: Optional[bool] = None
    ar_annex2_land_ownership_docs: Optional[bool] = None
    ar_annex2_chief_incumbent_letter: Optional[bool] = None
    ar_annex2_coordinator_recommendation: Optional[bool] = None
    ar_annex2_divisional_secretary_recommendation: Optional[bool] = None
    ar_annex2_approval_construction: Optional[bool] = None
    ar_annex2_referral_resubmission: Optional[bool] = None
    
    # Document Storage
    ar_scanned_document_path: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    ar_form_id: Annotated[Optional[str], Field(default=None, max_length=50)] = None
    
    # Workflow Fields
    ar_workflow_status: Annotated[Optional[str], Field(default="PENDING", max_length=20)] = "PENDING"
    ar_approval_status: Annotated[Optional[str], Field(default=None, max_length=20)] = None
    ar_approved_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    ar_approved_at: Optional[datetime] = None
    ar_rejected_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    ar_rejected_at: Optional[datetime] = None
    ar_rejection_reason: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    ar_printed_at: Optional[datetime] = None
    ar_printed_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    ar_scanned_at: Optional[datetime] = None
    ar_scanned_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    
    ar_is_deleted: bool = False
    ar_created_at: Optional[datetime] = None
    ar_updated_at: Optional[datetime] = None
    ar_created_by: Annotated[Optional[str], Field(default=None, max_length=25)]
    ar_updated_by: Annotated[Optional[str], Field(default=None, max_length=25)]
    ar_version_number: Annotated[int, Field(ge=1)] = 1

    @field_validator(
        "ar_trn",
        "ar_vname",
        "ar_addrs",
        "ar_typ",
        "ar_gndiv",
        "ar_ownercd",
        "ar_parshawa",
        "ar_ssbmcode",
        "ar_syojakarmakrs",
        "ar_landownrship",
        "ar_pralename",
        "ar_bacgrecmn",
        "ar_minissecrmrks",
        "ar_created_by",
        "ar_updated_by",
        mode="before",
    )
    @classmethod
    def _strip_strings(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            if value == "":
                return None
        return value

    @field_validator("ar_mobile", "ar_whtapp")
    @classmethod
    def _validate_phone(cls, value: str) -> str:
        if not PHONE_PATTERN.fullmatch(value):
            raise ValueError("Phone numbers must be exactly 10 digits.")
        return value

    @field_validator("ar_email", mode="before")
    @classmethod
    def _normalize_email(cls, value: str) -> str:
        if isinstance(value, str):
            value = value.strip()
        return value

    @field_validator("ar_ownercd", mode="before")
    @classmethod
    def _truncate_ownercd(cls, value: Optional[str]) -> Optional[str]:
        """Truncate ar_ownercd to max 12 characters if needed"""
        if isinstance(value, str) and len(value) > 12:
            return value[:12]
        return value


class AramaCreate(AramaBase):
    ar_trn: Annotated[Optional[str], Field(default=None, min_length=1, max_length=10)]
    ar_id: Annotated[Optional[int], Field(default=None, ge=1)] = None
    
    # Nested data - use AramaLandCreate for the new format with serial_number
    temple_owned_land: List[AramaLandCreate] = Field(default_factory=list)
    resident_silmathas: List[AramaResidentSilmathaCreate] = Field(default_factory=list)


class AramaCreatePayload(BaseModel):
    """Payload schema for creating Arama with camelCase field names"""
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
    
    temple_owned_land: List[AramaLandCreate] = Field(default_factory=list)
    
    land_info_certified: Optional[bool] = None
    resident_silmathas: List[AramaResidentSilmathaCreate] = Field(default_factory=list)
    resident_silmathas_certified: Optional[bool] = None
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


class AramaUpdate(BaseModel):
    ar_trn: Annotated[Optional[str], Field(default=None, min_length=1, max_length=10)]
    ar_vname: Annotated[Optional[str], Field(default=None, max_length=200)]
    ar_addrs: Annotated[Optional[str], Field(default=None, max_length=200)]
    ar_mobile: Annotated[Optional[str], Field(default=None, min_length=10, max_length=10)]
    ar_whtapp: Annotated[Optional[str], Field(default=None, min_length=10, max_length=10)]
    ar_email: Optional[EmailStr] = None
    ar_typ: Annotated[Optional[str], Field(default=None, min_length=1, max_length=10)]
    ar_gndiv: Annotated[Optional[str], Field(default=None, min_length=1, max_length=10)]
    ar_fmlycnt: Annotated[Optional[int], Field(default=None, ge=0)]
    ar_bgndate: Optional[date] = None
    ar_ownercd: Annotated[Optional[str], Field(default=None, min_length=1, max_length=12)]
    ar_parshawa: Annotated[Optional[str], Field(default=None, min_length=1, max_length=10)]
    ar_ssbmcode: Annotated[Optional[str], Field(default=None, max_length=10)]
    ar_syojakarmakrs: Annotated[Optional[str], Field(default=None, max_length=100)]
    ar_syojakarmdate: Optional[date] = None
    ar_landownrship: Annotated[Optional[str], Field(default=None, max_length=150)]
    ar_pralename: Annotated[Optional[str], Field(default=None, max_length=50)]
    ar_pralesigdate: Optional[date] = None
    ar_bacgrecmn: Annotated[Optional[str], Field(default=None, max_length=100)]
    ar_bacgrcmdate: Optional[date] = None
    ar_minissecrsigdate: Optional[date] = None
    ar_minissecrmrks: Annotated[Optional[str], Field(default=None, max_length=200)]
    ar_ssbmsigdate: Optional[date] = None
    
    # Extended Fields
    ar_province: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    ar_district: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    ar_divisional_secretariat: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    ar_pradeshya_sabha: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    ar_nikaya: Annotated[Optional[str], Field(default=None, max_length=50)] = None
    ar_viharadhipathi_name: Annotated[Optional[str], Field(default=None, max_length=200)] = None
    ar_period_established: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    ar_buildings_description: Annotated[Optional[str], Field(default=None, max_length=1000)] = None
    ar_dayaka_families_count: Annotated[Optional[str], Field(default=None, max_length=50)] = None
    ar_kulangana_committee: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    ar_dayaka_sabha: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    ar_temple_working_committee: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    ar_other_associations: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    ar_land_info_certified: Optional[bool] = None
    ar_inspection_report: Annotated[Optional[str], Field(default=None, max_length=1000)] = None
    ar_inspection_code: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    ar_grama_niladhari_division_ownership: Annotated[Optional[str], Field(default=None, max_length=200)] = None
    ar_sanghika_donation_deed: Optional[bool] = None
    ar_government_donation_deed: Optional[bool] = None
    ar_government_donation_deed_in_progress: Optional[bool] = None
    ar_authority_consent_attached: Optional[bool] = None
    ar_recommend_new_center: Optional[bool] = None
    ar_recommend_registered_temple: Optional[bool] = None
    ar_annex2_recommend_construction: Optional[bool] = None
    ar_annex2_land_ownership_docs: Optional[bool] = None
    ar_annex2_chief_incumbent_letter: Optional[bool] = None
    ar_annex2_coordinator_recommendation: Optional[bool] = None
    ar_annex2_divisional_secretary_recommendation: Optional[bool] = None
    ar_annex2_approval_construction: Optional[bool] = None
    ar_annex2_referral_resubmission: Optional[bool] = None
    
    # Document Storage
    ar_scanned_document_path: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    ar_form_id: Annotated[Optional[str], Field(default=None, max_length=50)] = None
    
    # Workflow Fields
    ar_workflow_status: Annotated[Optional[str], Field(default=None, max_length=20)] = None
    ar_approval_status: Annotated[Optional[str], Field(default=None, max_length=20)] = None
    ar_approved_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    ar_approved_at: Optional[datetime] = None
    ar_rejected_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    ar_rejected_at: Optional[datetime] = None
    ar_rejection_reason: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    ar_printed_at: Optional[datetime] = None
    ar_printed_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    ar_scanned_at: Optional[datetime] = None
    ar_scanned_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    
    ar_is_deleted: Optional[bool] = None
    ar_version_number: Annotated[Optional[int], Field(default=None, ge=1)] = None
    ar_updated_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    ar_updated_at: Optional[datetime] = None

    @field_validator(
        "ar_trn",
        "ar_vname",
        "ar_addrs",
        "ar_typ",
        "ar_gndiv",
        "ar_ownercd",
        "ar_parshawa",
        "ar_ssbmcode",
        "ar_syojakarmakrs",
        "ar_landownrship",
        "ar_pralename",
        "ar_bacgrecmn",
        "ar_minissecrmrks",
        "ar_updated_by",
        mode="before",
    )
    @classmethod
    def _strip_strings(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value

    @field_validator("ar_mobile", "ar_whtapp")
    @classmethod
    def _validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not PHONE_PATTERN.fullmatch(value):
            raise ValueError("Phone numbers must be exactly 10 digits.")
        return value

    @field_validator("ar_email", mode="before")
    @classmethod
    def _normalize_email(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value

    @field_validator("ar_ownercd", mode="before")
    @classmethod
    def _truncate_ownercd(cls, value: Optional[str]) -> Optional[str]:
        """Truncate ar_ownercd to max 12 characters if needed"""
        if isinstance(value, str) and len(value) > 12:
            return value[:12]
        return value


class AramaOut(AramaBase):
    model_config = ConfigDict(from_attributes=True)

    ar_id: int
    arama_lands: List[AramaLandInDB] = Field(default_factory=list)
    resident_silmathas: List[AramaResidentSilmathaInDB] = Field(default_factory=list)
    
    # Override base fields to use nested response objects
    ar_province: Optional[Union[ProvinceResponse, str]] = None
    ar_district: Optional[Union[DistrictResponse, str]] = None
    ar_divisional_secretariat: Optional[Union[DivisionalSecretariatResponse, str]] = None
    ar_gndiv: Union[GNDivisionResponse, str]
    ar_nikaya: Optional[Union[NikayaResponse, str]] = None
    ar_parshawa: Union[ParshawaResponse, str]
    ar_ownercd: Union[SilmathaResponse, str]


class AramaRequestPayload(BaseModel):
    # Identifiers
    ar_id: Optional[int] = None
    ar_trn: Optional[str] = None
    
    # Pagination
    skip: Annotated[int, Field(ge=0)] = 0
    limit: Annotated[int, Field(ge=1, le=200)] = 10
    page_size: Annotated[Optional[int], Field(default=None, ge=1, le=200)] = None  # Alias for limit
    page: Annotated[Optional[int], Field(default=1, ge=1)] = 1
    
    # Search and filters
    search_key: Annotated[Optional[str], Field(default=None, max_length=200)] = None
    province: Annotated[Optional[str], Field(default=None, max_length=10)] = None
    district: Annotated[Optional[str], Field(default=None, max_length=10)] = None
    divisional_secretariat: Annotated[Optional[str], Field(default=None, max_length=10)] = None
    gn_division: Annotated[Optional[str], Field(default=None, max_length=10)] = None
    temple: Annotated[Optional[str], Field(default=None, max_length=12)] = None  # ar_ownercd
    child_temple: Annotated[Optional[str], Field(default=None, max_length=12)] = None
    nikaya: Annotated[Optional[str], Field(default=None, max_length=10)] = None
    parshawaya: Annotated[Optional[str], Field(default=None, max_length=10)] = None  # ar_parshawa
    category: Annotated[Optional[str], Field(default=None, max_length=10)] = None
    status: Annotated[Optional[str], Field(default=None, max_length=10)] = None
    ar_typ: Annotated[Optional[str], Field(default=None, max_length=10)] = None  # arama type
    
    # Date range filters
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    
    # Workflow action fields
    rejection_reason: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    
    # Data payload for CREATE/UPDATE - order matters: snake_case first, then camelCase
    data: Optional[Union[AramaCreate, AramaUpdate, AramaCreatePayload]] = None


class AramaManagementRequest(BaseModel):
    action: CRUDAction
    payload: AramaRequestPayload


class AramaManagementResponse(BaseModel):
    status: str
    message: str
    data: Optional[Union[AramaOut, List[AramaOut], Any]] = None
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None


# Simple Arama List Schema for Bhikku endpoints
class BhikkuAramaListItem(BaseModel):
    ar_trn: str
    ar_vname: Optional[str] = None


class BhikkuAramaListResponse(BaseModel):
    status: str
    message: str
    data: List[BhikkuAramaListItem]
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None


# New schema for POST arama-list endpoint
class BhikkuAramaReadOnePayload(BaseModel):
    ar_id: int = Field(..., ge=1, description="Arama ID to retrieve")


class BhikkuAramaReadAllPayload(BaseModel):
    skip: Annotated[int, Field(ge=0)] = 0
    limit: Annotated[int, Field(ge=1, le=200)] = 10
    page: Annotated[Optional[int], Field(ge=1)] = 1
    search_key: Annotated[Optional[str], Field(default=None, max_length=200)] = None


class BhikkuAramaManagementRequest(BaseModel):
    action: str = Field(..., description="Action to perform: 'READ_ONE' or 'READ_ALL'")
    payload: Union[BhikkuAramaReadOnePayload, BhikkuAramaReadAllPayload]
