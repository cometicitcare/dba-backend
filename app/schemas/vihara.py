from datetime import date, datetime
import re
from enum import Enum
from typing import Annotated, ClassVar, Optional, Union, List, Any, Dict

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from app.schemas.temple_land import TempleLandCreate, TempleLandInDB
from app.schemas.resident_bhikkhu import ResidentBhikkhuCreate, ResidentBhikkhuInDB
from app.schemas.vihara_land import ViharaLandCreate, ViharaLandInDB

PHONE_PATTERN = re.compile(r"^[0-9]{10}$")


# Nested response schemas for foreign key relationships
class ProvinceNested(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    cp_code: Optional[str] = None
    cp_name: Optional[str] = None


class DistrictNested(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    dd_dcode: Optional[str] = None
    dd_dname: Optional[str] = None
    dd_prcode: Optional[str] = None


class DivisionalSecretariatNested(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    dv_dvcode: Optional[str] = None
    dv_dvname: Optional[str] = None
    dv_ddcode: Optional[str] = None


class GNDivisionNested(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    gn_gnc: Optional[str] = None
    gn_gnname: Optional[str] = None
    gn_dvcode: Optional[str] = None


class NikayaMainBhikkuNested(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    br_regn: Optional[str] = None
    br_mahananame: Optional[str] = None
    br_fathrsaddrs: Optional[str] = None
    br_mobile: Optional[str] = None


class ViharangaNested(BaseModel):
    """Nested response schema for viharanga"""
    model_config = ConfigDict(from_attributes=True)
    vg_id: Optional[int] = None
    vg_code: Optional[str] = None
    vg_item: Optional[str] = None


class NikayaNested(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    nk_nkn: Optional[str] = None
    nk_nname: Optional[str] = None
    nk_nahimicd: Optional[str] = None
    main_bhikku_info: Optional[NikayaMainBhikkuNested] = None


class ParshawaNested(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    pr_prn: Optional[str] = None
    pr_pname: Optional[str] = None
    pr_nikayacd: Optional[str] = None


class SsbmNested(BaseModel):
    """Nested response schema for Sasanarakshaka Bala Mandalaya"""
    model_config = ConfigDict(from_attributes=True)
    sr_ssbmcode: Optional[str] = None
    sr_ssbname: Optional[str] = None


class OwnerBhikkuNested(BaseModel):
    """Nested response schema for owner bhikku"""
    model_config = ConfigDict(from_attributes=True)
    br_regn: Optional[str] = None
    br_gihiname: Optional[str] = None
    br_nikaya: Optional[str] = None


class TemporaryViharaNested(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    tv_id: Optional[int] = None
    tv_name: Optional[str] = None
    tv_address: Optional[str] = None
    tv_contact_number: Optional[str] = None
    tv_district: Optional[str] = None
    tv_province: Optional[str] = None


class TemporaryBhikkuNested(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    tb_id: Optional[int] = None
    tb_name: Optional[str] = None
    tb_id_number: Optional[str] = None
    tb_contact_number: Optional[str] = None
    tb_samanera_name: Optional[str] = None
    tb_address: Optional[str] = None
    tb_living_temple: Optional[str] = None


class CRUDAction(str, Enum):
    CREATE = "CREATE"
    READ_ONE = "READ_ONE"
    READ_ALL = "READ_ALL"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    # Stage One Actions
    SAVE_STAGE_ONE = "SAVE_STAGE_ONE"
    UPDATE_STAGE_ONE = "UPDATE_STAGE_ONE"
    MARK_S1_PRINTED = "MARK_S1_PRINTED"
    APPROVE_STAGE_ONE = "APPROVE_STAGE_ONE"
    REJECT_STAGE_ONE = "REJECT_STAGE_ONE"
    # Stage Two Actions
    SAVE_STAGE_TWO = "SAVE_STAGE_TWO"
    UPDATE_STAGE_TWO = "UPDATE_STAGE_TWO"
    MARK_S2_PRINTED = "MARK_S2_PRINTED"
    APPROVE_STAGE_TWO = "APPROVE_STAGE_TWO"
    REJECT_STAGE_TWO = "REJECT_STAGE_TWO"
    # Legacy actions (kept for backward compatibility)
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    MARK_PRINTED = "MARK_PRINTED"
    MARK_SCANNED = "MARK_SCANNED"


class ViharaBase(BaseModel):
    vh_trn: Annotated[str, Field(min_length=1, max_length=10)]
    vh_vname: Annotated[Optional[str], Field(default=None, max_length=200)]
    vh_addrs: Annotated[Optional[str], Field(default=None, max_length=200)]
    vh_mobile: Annotated[Optional[str], Field(default=None, min_length=10, max_length=10)] = None
    vh_whtapp: Annotated[Optional[str], Field(default=None, min_length=10, max_length=10)] = None
    vh_email: Optional[EmailStr] = None
    vh_typ: Annotated[Optional[str], Field(default=None, min_length=1, max_length=10)] = None
    vh_gndiv: Annotated[Optional[str], Field(default=None, min_length=1, max_length=10)] = None
    vh_fmlycnt: Annotated[Optional[int], Field(default=None, ge=0)]
    vh_bgndate: Optional[date] = None
    vh_ownercd: Annotated[Optional[str], Field(default=None, min_length=1, max_length=12)] = None
    vh_parshawa: Annotated[Optional[str], Field(default=None, min_length=1, max_length=10)] = None
    vh_ssbmcode: Annotated[Optional[str], Field(default=None, max_length=10)]
    vh_syojakarmakrs: Annotated[Optional[str], Field(default=None, max_length=100)]
    vh_syojakarmdate: Optional[date] = None
    vh_landownrship: Annotated[Optional[str], Field(default=None, max_length=150)]
    vh_pralename: Annotated[Optional[str], Field(default=None, max_length=50)]
    vh_pralesigdate: Optional[date] = None
    vh_bacgrecmn: Annotated[Optional[str], Field(default=None, max_length=100)]
    vh_bacgrcmdate: Optional[date] = None
    vh_minissecrsigdate: Optional[date] = None
    vh_minissecrmrks: Annotated[Optional[str], Field(default=None, max_length=200)]
    vh_ssbmsigdate: Optional[date] = None
    vh_mahanayake_date: Optional[date] = None
    vh_mahanayake_letter_nu: Annotated[Optional[str], Field(default=None, max_length=50)] = None
    vh_mahanayake_remarks: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    
    # File / Code fields
    vh_file_number: Annotated[Optional[str], Field(default=None, max_length=50)] = None
    vh_vihara_code: Annotated[Optional[str], Field(default=None, max_length=50)] = None
    
    # Extended Fields
    vh_province: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    vh_district: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    vh_divisional_secretariat: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    vh_pradeshya_sabha: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    vh_nikaya: Annotated[Optional[str], Field(default=None, max_length=50)] = None
    vh_viharadhipathi_name: Annotated[Optional[str], Field(default=None, max_length=200)] = None
    vh_viharadhipathi_regn: Annotated[Optional[str], Field(default=None, max_length=50)] = None
    vh_period_established: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    vh_buildings_description: Annotated[Optional[str], Field(default=None, max_length=1000)] = None
    vh_dayaka_families_count: Annotated[Optional[str], Field(default=None, max_length=50)] = None
    vh_kulangana_committee: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    vh_dayaka_sabha: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    vh_temple_working_committee: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    vh_other_associations: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    vh_land_info_certified: Optional[bool] = None
    vh_resident_bhikkhus_certified: Optional[bool] = None
    vh_inspection_report: Annotated[Optional[str], Field(default=None, max_length=1000)] = None
    vh_inspection_code: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    vh_grama_niladhari_division_ownership: Annotated[Optional[str], Field(default=None, max_length=200)] = None
    vh_sanghika_donation_deed: Optional[bool] = None
    vh_government_donation_deed: Optional[bool] = None
    vh_government_donation_deed_in_progress: Optional[bool] = None
    vh_authority_consent_attached: Optional[bool] = None
    vh_recommend_new_center: Optional[bool] = None
    vh_recommend_registered_temple: Optional[bool] = None
    vh_annex2_recommend_construction: Optional[bool] = None
    vh_annex2_land_ownership_docs: Optional[bool] = None
    vh_annex2_chief_incumbent_letter: Optional[bool] = None
    vh_annex2_coordinator_recommendation: Optional[bool] = None
    vh_annex2_divisional_secretary_recommendation: Optional[bool] = None
    vh_annex2_approval_construction: Optional[bool] = None
    vh_annex2_referral_resubmission: Optional[bool] = None
    
    # Document Storage
    vh_scanned_document_path: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    vh_stage2_document_path: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    vh_form_id: Annotated[Optional[str], Field(default=None, max_length=50)] = None
    
    # Workflow Fields - Staged workflow
    vh_workflow_status: Annotated[Optional[str], Field(default="S1_PENDING", max_length=25)] = "S1_PENDING"
    vh_approval_status: Annotated[Optional[str], Field(default=None, max_length=20)] = None
    
    # Stage 1 workflow fields
    vh_s1_printed_at: Optional[datetime] = None
    vh_s1_printed_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    vh_s1_scanned_at: Optional[datetime] = None
    vh_s1_scanned_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    vh_s1_approved_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    vh_s1_approved_at: Optional[datetime] = None
    vh_s1_rejected_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    vh_s1_rejected_at: Optional[datetime] = None
    vh_s1_rejection_reason: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    
    # Stage 2 workflow fields
    vh_s2_scanned_at: Optional[datetime] = None
    vh_s2_scanned_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    vh_s2_approved_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    vh_s2_approved_at: Optional[datetime] = None
    vh_s2_rejected_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    vh_s2_rejected_at: Optional[datetime] = None
    vh_s2_rejection_reason: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    
    # Legacy fields (kept for backward compatibility)
    vh_approved_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    vh_approved_at: Optional[datetime] = None
    vh_rejected_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    vh_rejected_at: Optional[datetime] = None
    vh_rejection_reason: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    vh_printed_at: Optional[datetime] = None
    vh_printed_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    vh_scanned_at: Optional[datetime] = None
    vh_scanned_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    
    vh_is_deleted: bool = False
    vh_created_at: Optional[datetime] = None
    vh_updated_at: Optional[datetime] = None
    vh_created_by: Annotated[Optional[str], Field(default=None, max_length=25)]
    vh_updated_by: Annotated[Optional[str], Field(default=None, max_length=25)]
    vh_version_number: Annotated[int, Field(ge=1)] = 1

    @field_validator(
        "vh_trn",
        "vh_vname",
        "vh_addrs",
        "vh_typ",
        "vh_gndiv",
        "vh_ownercd",
        "vh_parshawa",
        "vh_ssbmcode",
        "vh_syojakarmakrs",
        "vh_landownrship",
        "vh_pralename",
        "vh_bacgrecmn",
        "vh_minissecrmrks",
        "vh_mahanayake_letter_nu",
        "vh_mahanayake_remarks",
        "vh_created_by",
        "vh_updated_by",
        mode="before",
    )
    @classmethod
    def _strip_strings(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            if value == "":
                return None
        return value

    @field_validator("vh_mobile", "vh_whtapp", mode="before")
    @classmethod
    def _validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            if not value:  # Empty string becomes None
                return None
        if value is None:
            return None
        if not PHONE_PATTERN.fullmatch(value):
            raise ValueError("Phone numbers must be exactly 10 digits.")
        return value

    @field_validator("vh_email", mode="before")
    @classmethod
    def _normalize_email(cls, value: str) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            if value == "":
                return None
        return value

    @field_validator("vh_ownercd", mode="before")
    @classmethod
    def _truncate_ownercd(cls, value: Optional[str]) -> Optional[str]:
        """Truncate vh_ownercd to max 12 characters if needed"""
        if isinstance(value, str) and len(value) > 12:
            return value[:12]
        return value


class ViharaCreate(ViharaBase):
    vh_trn: Annotated[Optional[str], Field(default=None, min_length=1, max_length=10)]
    vh_id: Annotated[Optional[int], Field(default=None, ge=1)] = None
    
    # Nested data - use ViharaLandCreate for the new format with serial_number
    temple_owned_land: List[ViharaLandCreate] = Field(default_factory=list)
    resident_bhikkhus: List[ResidentBhikkhuCreate] = Field(default_factory=list)


class ViharaCreatePayload(BaseModel):
    """Payload schema for creating Vihara with camelCase field names"""
    temple_name: Optional[str] = Field(default=None, max_length=200)
    temple_address: Optional[str] = Field(default=None, max_length=200)
    telephone_number: str = Field(min_length=10, max_length=10)
    whatsapp_number: str = Field(min_length=10, max_length=10)
    email_address: Optional[EmailStr] = None
    temple_type: str = Field(min_length=1, max_length=10)  # Required: VIHARA, ARAMA, etc.
    province: Optional[str] = Field(default=None, max_length=100)
    district: Optional[str] = Field(default=None, max_length=100)
    divisional_secretariat: Optional[str] = Field(default=None, max_length=100)
    pradeshya_sabha: Optional[str] = Field(default=None, max_length=100)
    grama_niladhari_division: str = Field(min_length=1, max_length=10)
    nikaya: Optional[str] = Field(default=None, max_length=50)
    parshawaya: str = Field(min_length=1, max_length=10)
    owner_code: str = Field(min_length=1, max_length=12)  # Required: Bhikku registration number
    viharadhipathi_name: Optional[str] = Field(default=None, max_length=200)
    viharadhipathi_regn: Optional[str] = Field(default=None, max_length=50)
    period_established: Optional[str] = Field(default=None, max_length=100)
    buildings_description: Optional[str] = Field(default=None, max_length=1000)
    dayaka_families_count: Optional[str] = Field(default=None, max_length=50)
    kulangana_committee: Optional[str] = Field(default=None, max_length=500)
    dayaka_sabha: Optional[str] = Field(default=None, max_length=500)
    temple_working_committee: Optional[str] = Field(default=None, max_length=500)
    other_associations: Optional[str] = Field(default=None, max_length=500)
    
    temple_owned_land: List[TempleLandCreate] = Field(default_factory=list)
    
    land_info_certified: Optional[bool] = None
    
    resident_bhikkhus: List[ResidentBhikkhuCreate] = Field(default_factory=list)
    
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
    
    form_id: Optional[str] = Field(default=None, max_length=50)

    @field_validator("email_address", mode="before")
    @classmethod
    def _normalize_email(cls, value: str) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            if value == "":
                return None
        return value

    @field_validator("telephone_number", "whatsapp_number")
    @classmethod
    def _validate_phone(cls, value: str) -> str:
        if not PHONE_PATTERN.fullmatch(value):
            raise ValueError("Phone numbers must be exactly 10 digits.")
        return value


class ViharaUpdate(BaseModel):
    vh_trn: Annotated[Optional[str], Field(default=None, min_length=1, max_length=10)]
    vh_vname: Annotated[Optional[str], Field(default=None, max_length=200)]
    vh_addrs: Annotated[Optional[str], Field(default=None, max_length=200)]
    vh_mobile: Annotated[Optional[str], Field(default=None, min_length=10, max_length=10)]
    vh_whtapp: Annotated[Optional[str], Field(default=None, min_length=10, max_length=10)]
    vh_email: Optional[EmailStr] = None
    vh_typ: Annotated[Optional[str], Field(default=None, min_length=1, max_length=10)]
    vh_gndiv: Annotated[Optional[str], Field(default=None, min_length=1, max_length=10)]
    vh_fmlycnt: Annotated[Optional[int], Field(default=None, ge=0)]
    vh_bgndate: Optional[date] = None
    vh_ownercd: Annotated[Optional[str], Field(default=None, min_length=1, max_length=12)]
    vh_parshawa: Annotated[Optional[str], Field(default=None, min_length=1, max_length=10)]
    vh_ssbmcode: Annotated[Optional[str], Field(default=None, max_length=10)]
    vh_syojakarmakrs: Annotated[Optional[str], Field(default=None, max_length=100)]
    vh_syojakarmdate: Optional[date] = None
    vh_landownrship: Annotated[Optional[str], Field(default=None, max_length=150)]
    vh_pralename: Annotated[Optional[str], Field(default=None, max_length=50)]
    vh_pralesigdate: Optional[date] = None
    vh_bacgrecmn: Annotated[Optional[str], Field(default=None, max_length=100)]
    vh_bacgrcmdate: Optional[date] = None
    vh_minissecrsigdate: Optional[date] = None
    vh_minissecrmrks: Annotated[Optional[str], Field(default=None, max_length=200)]
    vh_ssbmsigdate: Optional[date] = None
    vh_mahanayake_date: Optional[date] = None
    vh_mahanayake_letter_nu: Annotated[Optional[str], Field(default=None, max_length=50)] = None
    vh_mahanayake_remarks: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    
    # File / Code fields
    vh_file_number: Annotated[Optional[str], Field(default=None, max_length=50)] = None
    vh_vihara_code: Annotated[Optional[str], Field(default=None, max_length=50)] = None
    
    # Extended Fields
    vh_province: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    vh_district: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    vh_divisional_secretariat: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    vh_pradeshya_sabha: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    vh_nikaya: Annotated[Optional[str], Field(default=None, max_length=50)] = None
    vh_viharadhipathi_name: Annotated[Optional[str], Field(default=None, max_length=200)] = None
    vh_period_established: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    vh_buildings_description: Annotated[Optional[str], Field(default=None, max_length=1000)] = None
    vh_dayaka_families_count: Annotated[Optional[str], Field(default=None, max_length=50)] = None
    vh_kulangana_committee: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    vh_dayaka_sabha: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    vh_temple_working_committee: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    vh_other_associations: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    vh_land_info_certified: Optional[bool] = None
    vh_resident_bhikkhus_certified: Optional[bool] = None
    vh_inspection_report: Annotated[Optional[str], Field(default=None, max_length=1000)] = None
    vh_inspection_code: Annotated[Optional[str], Field(default=None, max_length=100)] = None
    vh_grama_niladhari_division_ownership: Annotated[Optional[str], Field(default=None, max_length=200)] = None
    vh_sanghika_donation_deed: Optional[bool] = None
    vh_government_donation_deed: Optional[bool] = None
    vh_government_donation_deed_in_progress: Optional[bool] = None
    vh_authority_consent_attached: Optional[bool] = None
    vh_recommend_new_center: Optional[bool] = None
    vh_recommend_registered_temple: Optional[bool] = None
    vh_annex2_recommend_construction: Optional[bool] = None
    vh_annex2_land_ownership_docs: Optional[bool] = None
    vh_annex2_chief_incumbent_letter: Optional[bool] = None
    vh_annex2_coordinator_recommendation: Optional[bool] = None
    vh_annex2_divisional_secretary_recommendation: Optional[bool] = None
    vh_annex2_approval_construction: Optional[bool] = None
    vh_annex2_referral_resubmission: Optional[bool] = None
    
    # Document Storage
    vh_scanned_document_path: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    vh_stage2_document_path: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    
    # Workflow Fields - Staged workflow
    vh_workflow_status: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    vh_approval_status: Annotated[Optional[str], Field(default=None, max_length=20)] = None
    
    # Stage 1 workflow fields
    vh_s1_printed_at: Optional[datetime] = None
    vh_s1_printed_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    vh_s1_scanned_at: Optional[datetime] = None
    vh_s1_scanned_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    vh_s1_approved_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    vh_s1_approved_at: Optional[datetime] = None
    vh_s1_rejected_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    vh_s1_rejected_at: Optional[datetime] = None
    vh_s1_rejection_reason: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    
    # Stage 2 workflow fields
    vh_s2_scanned_at: Optional[datetime] = None
    vh_s2_scanned_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    vh_s2_approved_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    vh_s2_approved_at: Optional[datetime] = None
    vh_s2_rejected_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    vh_s2_rejected_at: Optional[datetime] = None
    vh_s2_rejection_reason: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    
    # Legacy fields (kept for backward compatibility)
    vh_approved_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    vh_approved_at: Optional[datetime] = None
    vh_rejected_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    vh_rejected_at: Optional[datetime] = None
    vh_rejection_reason: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    vh_printed_at: Optional[datetime] = None
    vh_printed_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    vh_scanned_at: Optional[datetime] = None
    vh_scanned_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    
    vh_is_deleted: Optional[bool] = None
    vh_version_number: Annotated[Optional[int], Field(default=None, ge=1)] = None
    vh_updated_by: Annotated[Optional[str], Field(default=None, max_length=25)] = None
    vh_updated_at: Optional[datetime] = None

    @field_validator(
        "vh_trn",
        "vh_vname",
        "vh_addrs",
        "vh_typ",
        "vh_gndiv",
        "vh_ownercd",
        "vh_parshawa",
        "vh_ssbmcode",
        "vh_syojakarmakrs",
        "vh_landownrship",
        "vh_pralename",
        "vh_bacgrecmn",
        "vh_minissecrmrks",
        "vh_updated_by",
        mode="before",
    )
    @classmethod
    def _strip_strings(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value

    @field_validator("vh_mobile", "vh_whtapp", mode="before")
    @classmethod
    def _validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            if not value:  # Empty string becomes None
                return None
        if value is None:
            return value
        if not PHONE_PATTERN.fullmatch(value):
            raise ValueError("Phone numbers must be exactly 10 digits.")
        return value

    @field_validator("vh_email", mode="before")
    @classmethod
    def _normalize_email(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value

    @field_validator("vh_ownercd", mode="before")
    @classmethod
    def _truncate_ownercd(cls, value: Optional[str]) -> Optional[str]:
        """Truncate vh_ownercd to max 12 characters if needed"""
        if isinstance(value, str) and len(value) > 12:
            return value[:12]
        return value


# Stage-specific schemas for multi-stage vihara data entry
class ViharaStageOneData(BaseModel):
    """Data for Stage 1: Basic Profile (steps 1–4)"""
    vh_typ: Optional[str] = Field(default=None, min_length=1, max_length=10)
    vh_ownercd: Optional[str] = Field(default=None, min_length=1, max_length=12)
    vh_vname: Optional[str] = Field(default=None, max_length=200)
    vh_addrs: Optional[str] = Field(default=None, max_length=200)
    vh_mobile: Optional[str] = Field(default=None, min_length=10, max_length=10)
    vh_whtapp: Optional[str] = Field(default=None, min_length=10, max_length=10)
    vh_email: Optional[EmailStr] = None
    vh_file_number: Optional[str] = Field(default=None, max_length=50)
    vh_vihara_code: Optional[str] = Field(default=None, max_length=50)
    vh_province: Optional[str] = Field(default=None, max_length=100)
    vh_district: Optional[str] = Field(default=None, max_length=100)
    vh_divisional_secretariat: Optional[str] = Field(default=None, max_length=100)
    vh_pradeshya_sabha: Optional[str] = Field(default=None, max_length=100)
    vh_gndiv: Optional[str] = Field(default=None, min_length=1, max_length=10)
    vh_nikaya: Optional[str] = Field(default=None, max_length=50)
    vh_parshawa: Optional[str] = Field(default=None, min_length=1, max_length=10)
    vh_viharadhipathi_name: Optional[str] = Field(default=None, max_length=200)
    vh_viharadhipathi_regn: Optional[str] = Field(default=None, max_length=50)
    vh_period_established: Optional[str] = Field(default=None, max_length=100)
    vh_bgndate: Optional[date] = None
    vh_mahanayake_date: Optional[date] = None
    vh_mahanayake_letter_nu: Optional[str] = Field(default=None, max_length=50)
    vh_mahanayake_remarks: Optional[str] = Field(default=None, max_length=500)

    @field_validator(
        "vh_typ", "vh_ownercd", "vh_vname", "vh_addrs", "vh_file_number",
        "vh_vihara_code", "vh_province", 
        "vh_district", "vh_divisional_secretariat", "vh_pradeshya_sabha", 
        "vh_gndiv", "vh_nikaya", "vh_parshawa", "vh_viharadhipathi_name", 
        "vh_viharadhipathi_regn", "vh_period_established", "vh_mahanayake_letter_nu", 
        "vh_mahanayake_remarks",
        mode="before",
    )
    @classmethod
    def _strip_strings(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            if value == "":
                return None
        return value

    @field_validator("vh_mobile", "vh_whtapp", mode="before")
    @classmethod
    def _validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, str):
            value = value.strip()
            if value == "":
                return None
        if not PHONE_PATTERN.fullmatch(value):
            raise ValueError("Phone numbers must be exactly 10 digits.")
        return value
    
    @field_validator("vh_email", mode="before")
    @classmethod
    def _validate_email(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            if value == "":
                return None
        return value


class ViharaStageTwoData(BaseModel):
    """Data for Stage 2: Assets, Certification & Annex (steps 5–10)"""
    vh_buildings_description: Optional[str] = Field(default=None, max_length=1000)
    vh_dayaka_families_count: Optional[str] = Field(default=None, max_length=50)
    vh_fmlycnt: Optional[int] = Field(default=None, ge=0)
    vh_kulangana_committee: Optional[str] = Field(default=None, max_length=500)
    vh_dayaka_sabha: Optional[str] = Field(default=None, max_length=500)
    vh_temple_working_committee: Optional[str] = Field(default=None, max_length=500)
    vh_other_associations: Optional[str] = Field(default=None, max_length=500)
    
    temple_owned_land: List[ViharaLandCreate] = Field(default_factory=list)
    vh_land_info_certified: Optional[bool] = None
    
    resident_bhikkhus: List[ResidentBhikkhuCreate] = Field(default_factory=list)
    vh_resident_bhikkhus_certified: Optional[bool] = None
    
    vh_inspection_report: Optional[str] = Field(default=None, max_length=1000)
    vh_inspection_code: Optional[str] = Field(default=None, max_length=100)
    
    vh_grama_niladhari_division_ownership: Optional[str] = Field(default=None, max_length=200)
    vh_sanghika_donation_deed: Optional[bool] = None
    vh_government_donation_deed: Optional[bool] = None
    vh_government_donation_deed_in_progress: Optional[bool] = None
    vh_authority_consent_attached: Optional[bool] = None
    vh_recommend_new_center: Optional[bool] = None
    vh_recommend_registered_temple: Optional[bool] = None
    
    vh_annex2_recommend_construction: Optional[bool] = None
    vh_annex2_land_ownership_docs: Optional[bool] = None
    vh_annex2_chief_incumbent_letter: Optional[bool] = None
    vh_annex2_coordinator_recommendation: Optional[bool] = None
    vh_annex2_divisional_secretary_recommendation: Optional[bool] = None
    vh_annex2_approval_construction: Optional[bool] = None
    vh_annex2_referral_resubmission: Optional[bool] = None


class ViharaOut(ViharaBase):
    """Output schema for Vihara data - more lenient validation for reading existing data."""
    model_config = ConfigDict(from_attributes=True, validate_assignment=False)

    vh_id: int
    
    # Override required fields from ViharaBase to make them optional for output
    # (existing data may have empty/null values)
    vh_trn: Optional[str] = None
    vh_mobile: Optional[str] = None
    vh_whtapp: Optional[str] = None
    vh_email: Optional[str] = None
    vh_typ: Optional[str] = None
    
    # FK fields: Always return simple string codes, not nested objects
    # The frontend uses these codes to look up in STATIC_PROVINCES and expects simple string codes
    vh_province: Optional[str] = None  # Province code like "CP01"
    vh_district: Optional[str] = None  # District code like "DD01"
    vh_divisional_secretariat: Optional[str] = None  # Divisional Secretariat code like "DV01"
    vh_gndiv: Optional[str] = None  # GN Division code like "GN01"
    vh_nikaya: Optional[Union[NikayaNested, str]] = None
    vh_parshawa: Optional[Union[ParshawaNested, str]] = None
    vh_ssbmcode: Optional[Union[SsbmNested, str]] = None
    vh_ownercd: Optional[Union[OwnerBhikkuNested, str]] = None
    
    temple_lands: List[TempleLandInDB] = Field(default_factory=list)
    resident_bhikkhus: List[ResidentBhikkhuInDB] = Field(default_factory=list)
    
    # Viharanga nested objects (parsed from buildings_description)
    viharanga_list: List[ViharangaNested] = Field(default_factory=list)
    
    # Temporary entity nested objects (for TEMP- references)
    owner_temp_vihara_info: Optional[TemporaryViharaNested] = None
    viharadhipathi_temp_bhikku_info: Optional[TemporaryBhikkuNested] = None
    
    # ---------- FK nesting validator ----------
    _FK_INFO_MAP: ClassVar[Dict[str, str]] = {
        "vh_province": "province_info",
        "vh_district": "district_info",
        "vh_divisional_secretariat": "divisional_secretariat_info",
        "vh_gndiv": "gn_division_info",
        "vh_nikaya": "nikaya_info",
        "vh_parshawa": "parshawa_info",
        "vh_ssbmcode": "ssbm_info",
        "vh_ownercd": "owner_bhikku_info",
    }

    @model_validator(mode="before")
    @classmethod
    def _nest_fk_into_fields(cls, data):
        """Replace raw FK string values with their nested relationship objects.
        
        NOTE: We exclude administrative division fields (vh_province, vh_district, 
        vh_divisional_secretariat, vh_gndiv) and religious affiliation fields 
        (vh_nikaya, vh_parshawa) because the frontend expects simple string codes 
        for these fields, not nested objects.
        """
        # Fields that should NOT be nested - these should remain as simple string codes
        # for the frontend components which use them for lookup in static data
        EXCLUDE_FROM_NESTING = {
            "vh_province",
            "vh_district", 
            "vh_divisional_secretariat",
            "vh_gndiv",
            "vh_nikaya",
            "vh_parshawa",
        }
        
        fk_map = cls._FK_INFO_MAP
        if isinstance(data, dict):
            for fk_field, info_key in fk_map.items():
                # Skip nesting for administrative division fields
                if fk_field in EXCLUDE_FROM_NESTING:
                    data.pop(info_key, None)  # Remove the relationship data key
                    continue
                info_val = data.pop(info_key, None)
                if info_val is not None:
                    data[fk_field] = info_val
            return data
        # SQLAlchemy model: build a dict, overriding FK fields with relationship data
        obj = {}
        for field_name, field_info in cls.model_fields.items():
            val = getattr(data, field_name, None)
            if val is not None:
                obj[field_name] = val
            # skip None so Pydantic uses the field default (e.g. [] for lists)
        for fk_field, info_attr in fk_map.items():
            # Skip nesting for administrative division fields
            if fk_field in EXCLUDE_FROM_NESTING:
                continue
            info_val = getattr(data, info_attr, None)
            if info_val is not None:
                obj[fk_field] = info_val
        return obj
    
    # Override validators to allow None/empty for output - these run AFTER parent validators
    # Use wrap validator to intercept validation errors
    @field_validator("vh_mobile", "vh_whtapp", mode="wrap")
    @classmethod
    def _allow_empty_phone(cls, value, handler, info):
        """Skip validation for empty phone numbers in output schema."""
        if value is None or value == "":
            return None
        try:
            return handler(value)
        except ValueError:
            # If parent validator fails, return the value as-is (for legacy data)
            return value
    
    @field_validator("vh_email", mode="wrap")
    @classmethod
    def _allow_empty_email(cls, value, handler, info):
        """Skip validation for empty email in output schema."""
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return None
        try:
            return handler(value)
        except ValueError:
            # If parent validator fails, return the value as-is (for legacy data)
            return value


class ViharaRequestPayload(BaseModel):
    # Identifiers
    vh_id: Optional[int] = None
    vh_trn: Optional[str] = None
    
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
    temple: Annotated[Optional[str], Field(default=None, max_length=12)] = None  # vh_ownercd
    child_temple: Annotated[Optional[str], Field(default=None, max_length=12)] = None
    nikaya: Annotated[Optional[str], Field(default=None, max_length=10)] = None
    parshawaya: Annotated[Optional[str], Field(default=None, max_length=10)] = None  # vh_parshawa
    category: Annotated[Optional[str], Field(default=None, max_length=10)] = None
    status: Annotated[Optional[str], Field(default=None, max_length=10)] = None
    vh_typ: Annotated[Optional[str], Field(default=None, max_length=10)] = None  # vihara type
    
    # Date range filters
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    
    # Workflow action fields
    rejection_reason: Annotated[Optional[str], Field(default=None, max_length=500)] = None
    
    # Data payload for CREATE/UPDATE (supports both snake_case and camelCase, and staged operations)
    data: Optional[Union[ViharaCreate, ViharaCreatePayload, ViharaUpdate, ViharaStageOneData, ViharaStageTwoData, dict]] = None


class ViharaManagementRequest(BaseModel):
    action: CRUDAction
    payload: ViharaRequestPayload


class ViharaManagementResponse(BaseModel):
    status: str
    message: str
    data: Optional[Union[ViharaOut, List[ViharaOut], Any]] = None
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None


# Simple Vihara List Schema for Bhikku endpoints
class BhikkuViharaListItem(BaseModel):
    vh_trn: str
    vh_vname: Optional[str] = None
    vh_addrs: Optional[str] = None


class BhikkuViharaListResponse(BaseModel):
    status: str
    message: str
    data: List[BhikkuViharaListItem]
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None


# New schema for POST vihara-list endpoint
class BhikkuViharaReadOnePayload(BaseModel):
    vh_id: int = Field(..., ge=1, description="Vihara ID to retrieve")


class BhikkuViharaReadAllPayload(BaseModel):
    skip: Annotated[int, Field(ge=0)] = 0
    limit: Annotated[int, Field(ge=1, le=200)] = 10
    page: Annotated[Optional[int], Field(ge=1)] = 1
    search_key: Annotated[Optional[str], Field(default=None, max_length=200)] = None


class BhikkuViharaManagementRequest(BaseModel):
    action: str = Field(..., description="Action to perform: 'READ_ONE' or 'READ_ALL'")
    payload: Union[BhikkuViharaReadOnePayload, BhikkuViharaReadAllPayload]
