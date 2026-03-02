# app/schemas/dayakasaba_regist.py
from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


# ── Action Enum ────────────────────────────────────────────────────────────────
class DayakasabaAction(str, Enum):
    CREATE = "CREATE"
    READ_ONE = "READ_ONE"
    READ_ALL = "READ_ALL"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    APPROVE = "APPROVE"
    REJECT = "REJECT"


# ── Nested FK Response Schemas ─────────────────────────────────────────────────
class ViharaNestedResponse(BaseModel):
    vh_trn: str
    vh_vname: Optional[str] = None
    vh_addrs: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class NikayaNestedResponse(BaseModel):
    nk_nkn: str
    nk_nname: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class ParshawaNestedResponse(BaseModel):
    pr_prn: str
    pr_pname: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class DistrictNestedResponse(BaseModel):
    dd_dcode: str
    dd_dname: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class DsDivisionNestedResponse(BaseModel):
    dv_dvcode: str
    dv_dvname: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


# ── Base (shared fields) ───────────────────────────────────────────────────────
class DayakasabaRegistBase(BaseModel):
    temple_trn: str = Field(..., description="Vihara TRN (FK → vihaddata)")
    phone_number: Optional[str] = None
    nikaya: Optional[str] = None
    parshawa: Optional[str] = None
    district: Optional[str] = None
    ds_division: Optional[str] = None
    dayaka_sabha_name: Optional[str] = None
    meeting_date: Optional[date] = None
    devotee_family_count: Optional[int] = None

    president_name: Optional[str] = None
    is_signed_president: Optional[bool] = False
    vice_president_name: Optional[str] = None
    is_signed_vice_president: Optional[bool] = False
    secretary_name: Optional[str] = None
    is_signed_secretary: Optional[bool] = False
    asst_secretary_name: Optional[str] = None
    is_signed_asst_secretary: Optional[bool] = False
    treasurer_name: Optional[str] = None
    is_signed_treasurer: Optional[bool] = False

    committee_member_1: Optional[str] = None
    is_signed_member_1: Optional[bool] = False
    committee_member_2: Optional[str] = None
    is_signed_member_2: Optional[bool] = False
    committee_member_3: Optional[str] = None
    is_signed_member_3: Optional[bool] = False
    committee_member_4: Optional[str] = None
    is_signed_member_4: Optional[bool] = False
    committee_member_5: Optional[str] = None
    is_signed_member_5: Optional[bool] = False
    committee_member_6: Optional[str] = None
    is_signed_member_6: Optional[bool] = False
    committee_member_7: Optional[str] = None
    is_signed_member_7: Optional[bool] = False
    committee_member_8: Optional[str] = None
    is_signed_member_8: Optional[bool] = False
    committee_member_9: Optional[str] = None
    is_signed_member_9: Optional[bool] = False
    committee_member_10: Optional[str] = None
    is_signed_member_10: Optional[bool] = False

    bank_name: Optional[str] = None
    bank_branch: Optional[str] = None
    account_number: Optional[str] = None

    is_temple_registered: Optional[bool] = False
    is_signed_cert_secretary: Optional[bool] = False
    is_signed_cert_president: Optional[bool] = False
    is_signed_sasana_sec: Optional[bool] = False
    is_signed_ds: Optional[bool] = False
    is_signed_commissioner: Optional[bool] = False


# ── Create ─────────────────────────────────────────────────────────────────────
class DayakasabaRegistCreate(DayakasabaRegistBase):
    pass


# ── Update (all optional) ──────────────────────────────────────────────────────
class DayakasabaRegistUpdate(BaseModel):
    temple_trn: Optional[str] = None
    phone_number: Optional[str] = None
    nikaya: Optional[str] = None
    parshawa: Optional[str] = None
    district: Optional[str] = None
    ds_division: Optional[str] = None
    dayaka_sabha_name: Optional[str] = None
    meeting_date: Optional[date] = None
    devotee_family_count: Optional[int] = None

    president_name: Optional[str] = None
    is_signed_president: Optional[bool] = None
    vice_president_name: Optional[str] = None
    is_signed_vice_president: Optional[bool] = None
    secretary_name: Optional[str] = None
    is_signed_secretary: Optional[bool] = None
    asst_secretary_name: Optional[str] = None
    is_signed_asst_secretary: Optional[bool] = None
    treasurer_name: Optional[str] = None
    is_signed_treasurer: Optional[bool] = None

    committee_member_1: Optional[str] = None
    is_signed_member_1: Optional[bool] = None
    committee_member_2: Optional[str] = None
    is_signed_member_2: Optional[bool] = None
    committee_member_3: Optional[str] = None
    is_signed_member_3: Optional[bool] = None
    committee_member_4: Optional[str] = None
    is_signed_member_4: Optional[bool] = None
    committee_member_5: Optional[str] = None
    is_signed_member_5: Optional[bool] = None
    committee_member_6: Optional[str] = None
    is_signed_member_6: Optional[bool] = None
    committee_member_7: Optional[str] = None
    is_signed_member_7: Optional[bool] = None
    committee_member_8: Optional[str] = None
    is_signed_member_8: Optional[bool] = None
    committee_member_9: Optional[str] = None
    is_signed_member_9: Optional[bool] = None
    committee_member_10: Optional[str] = None
    is_signed_member_10: Optional[bool] = None

    bank_name: Optional[str] = None
    bank_branch: Optional[str] = None
    account_number: Optional[str] = None

    is_temple_registered: Optional[bool] = None
    is_signed_cert_secretary: Optional[bool] = None
    is_signed_cert_president: Optional[bool] = None
    is_signed_sasana_sec: Optional[bool] = None
    is_signed_ds: Optional[bool] = None
    is_signed_commissioner: Optional[bool] = None


# ── Response ───────────────────────────────────────────────────────────────────
class DayakasabaRegistResponse(BaseModel):
    ds_id: int

    # raw FK codes
    temple_trn: str
    nikaya_code: Optional[str] = None
    parshawa_code: Optional[str] = None
    district_code: Optional[str] = None
    ds_division_code: Optional[str] = None

    # nested FK objects
    temple: Optional[ViharaNestedResponse] = None
    nikaya: Optional[NikayaNestedResponse] = None
    parshawa: Optional[ParshawaNestedResponse] = None
    district: Optional[DistrictNestedResponse] = None
    ds_division: Optional[DsDivisionNestedResponse] = None

    phone_number: Optional[str] = None
    dayaka_sabha_name: Optional[str] = None
    meeting_date: Optional[date] = None
    devotee_family_count: Optional[int] = None

    president_name: Optional[str] = None
    is_signed_president: Optional[bool] = None
    vice_president_name: Optional[str] = None
    is_signed_vice_president: Optional[bool] = None
    secretary_name: Optional[str] = None
    is_signed_secretary: Optional[bool] = None
    asst_secretary_name: Optional[str] = None
    is_signed_asst_secretary: Optional[bool] = None
    treasurer_name: Optional[str] = None
    is_signed_treasurer: Optional[bool] = None

    committee_member_1: Optional[str] = None
    is_signed_member_1: Optional[bool] = None
    committee_member_2: Optional[str] = None
    is_signed_member_2: Optional[bool] = None
    committee_member_3: Optional[str] = None
    is_signed_member_3: Optional[bool] = None
    committee_member_4: Optional[str] = None
    is_signed_member_4: Optional[bool] = None
    committee_member_5: Optional[str] = None
    is_signed_member_5: Optional[bool] = None
    committee_member_6: Optional[str] = None
    is_signed_member_6: Optional[bool] = None
    committee_member_7: Optional[str] = None
    is_signed_member_7: Optional[bool] = None
    committee_member_8: Optional[str] = None
    is_signed_member_8: Optional[bool] = None
    committee_member_9: Optional[str] = None
    is_signed_member_9: Optional[bool] = None
    committee_member_10: Optional[str] = None
    is_signed_member_10: Optional[bool] = None

    bank_name: Optional[str] = None
    bank_branch: Optional[str] = None
    account_number: Optional[str] = None

    is_temple_registered: Optional[bool] = None
    is_signed_cert_secretary: Optional[bool] = None
    is_signed_cert_president: Optional[bool] = None
    is_signed_sasana_sec: Optional[bool] = None
    is_signed_ds: Optional[bool] = None
    is_signed_commissioner: Optional[bool] = None

    # workflow
    ds_workflow_status: Optional[str] = None
    ds_scanned_document_path: Optional[str] = None
    ds_approved_by: Optional[str] = None
    ds_approved_at: Optional[datetime] = None
    ds_rejected_by: Optional[str] = None
    ds_rejected_at: Optional[datetime] = None
    ds_rejection_reason: Optional[str] = None

    # audit
    ds_is_deleted: Optional[bool] = False
    ds_created_at: Optional[datetime] = None
    ds_updated_at: Optional[datetime] = None
    ds_created_by: Optional[str] = None
    ds_updated_by: Optional[str] = None
    ds_version_number: Optional[int] = 1

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm_map(cls, obj) -> "DayakasabaRegistResponse":
        """Map DB model (ds_ prefixed columns) to the flat+nested response schema."""
        temple_obj = obj.temple
        nikaya_obj = obj.nikaya
        parshawa_obj = obj.parshawa
        district_obj = obj.district
        ds_div_obj = obj.ds_division

        return cls(
            ds_id=obj.ds_id,
            # raw FK codes
            temple_trn=obj.ds_temple_trn,
            nikaya_code=obj.ds_nikaya,
            parshawa_code=obj.ds_parshawa,
            district_code=obj.ds_district,
            ds_division_code=obj.ds_ds_division,
            # nested objects
            temple=ViharaNestedResponse(
                vh_trn=temple_obj.vh_trn,
                vh_vname=temple_obj.vh_vname,
                vh_addrs=temple_obj.vh_addrs,
            ) if temple_obj else None,
            nikaya=NikayaNestedResponse(
                nk_nkn=nikaya_obj.nk_nkn,
                nk_nname=nikaya_obj.nk_nname,
            ) if nikaya_obj else None,
            parshawa=ParshawaNestedResponse(
                pr_prn=parshawa_obj.pr_prn,
                pr_pname=parshawa_obj.pr_pname,
            ) if parshawa_obj else None,
            district=DistrictNestedResponse(
                dd_dcode=district_obj.dd_dcode,
                dd_dname=district_obj.dd_dname,
            ) if district_obj else None,
            ds_division=DsDivisionNestedResponse(
                dv_dvcode=ds_div_obj.dv_dvcode,
                dv_dvname=ds_div_obj.dv_dvname,
            ) if ds_div_obj else None,
            # simple fields
            phone_number=obj.ds_phone_number,
            dayaka_sabha_name=obj.ds_dayaka_sabha_name,
            meeting_date=obj.ds_meeting_date,
            devotee_family_count=obj.ds_devotee_family_count,
            president_name=obj.ds_president_name,
            is_signed_president=obj.ds_is_signed_president,
            vice_president_name=obj.ds_vice_president_name,
            is_signed_vice_president=obj.ds_is_signed_vice_president,
            secretary_name=obj.ds_secretary_name,
            is_signed_secretary=obj.ds_is_signed_secretary,
            asst_secretary_name=obj.ds_asst_secretary_name,
            is_signed_asst_secretary=obj.ds_is_signed_asst_secretary,
            treasurer_name=obj.ds_treasurer_name,
            is_signed_treasurer=obj.ds_is_signed_treasurer,
            committee_member_1=obj.ds_committee_member_1,
            is_signed_member_1=obj.ds_is_signed_member_1,
            committee_member_2=obj.ds_committee_member_2,
            is_signed_member_2=obj.ds_is_signed_member_2,
            committee_member_3=obj.ds_committee_member_3,
            is_signed_member_3=obj.ds_is_signed_member_3,
            committee_member_4=obj.ds_committee_member_4,
            is_signed_member_4=obj.ds_is_signed_member_4,
            committee_member_5=obj.ds_committee_member_5,
            is_signed_member_5=obj.ds_is_signed_member_5,
            committee_member_6=obj.ds_committee_member_6,
            is_signed_member_6=obj.ds_is_signed_member_6,
            committee_member_7=obj.ds_committee_member_7,
            is_signed_member_7=obj.ds_is_signed_member_7,
            committee_member_8=obj.ds_committee_member_8,
            is_signed_member_8=obj.ds_is_signed_member_8,
            committee_member_9=obj.ds_committee_member_9,
            is_signed_member_9=obj.ds_is_signed_member_9,
            committee_member_10=obj.ds_committee_member_10,
            is_signed_member_10=obj.ds_is_signed_member_10,
            bank_name=obj.ds_bank_name,
            bank_branch=obj.ds_bank_branch,
            account_number=obj.ds_account_number,
            is_temple_registered=obj.ds_is_temple_registered,
            is_signed_cert_secretary=obj.ds_is_signed_cert_secretary,
            is_signed_cert_president=obj.ds_is_signed_cert_president,
            is_signed_sasana_sec=obj.ds_is_signed_sasana_sec,
            is_signed_ds=obj.ds_is_signed_ds,
            is_signed_commissioner=obj.ds_is_signed_commissioner,
            ds_workflow_status=obj.ds_workflow_status,
            ds_scanned_document_path=obj.ds_scanned_document_path,
            ds_approved_by=obj.ds_approved_by,
            ds_approved_at=obj.ds_approved_at,
            ds_rejected_by=obj.ds_rejected_by,
            ds_rejected_at=obj.ds_rejected_at,
            ds_rejection_reason=obj.ds_rejection_reason,
            ds_is_deleted=obj.ds_is_deleted,
            ds_created_at=obj.ds_created_at,
            ds_updated_at=obj.ds_updated_at,
            ds_created_by=obj.ds_created_by,
            ds_updated_by=obj.ds_updated_by,
            ds_version_number=obj.ds_version_number,
        )


# ── Management request payload ─────────────────────────────────────────────────
class DayakasabaRegistRequestPayload(BaseModel):
    # READ_ONE / UPDATE / DELETE / APPROVE / REJECT
    ds_id: Optional[int] = None
    # READ_ALL pagination
    page: Optional[int] = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=1000)
    search_key: Optional[str] = Field(default="", max_length=200)
    # filter helpers
    workflow_status: Optional[str] = None
    temple_trn: Optional[str] = None
    # CREATE / UPDATE body
    data: Optional[Union[DayakasabaRegistCreate, DayakasabaRegistUpdate]] = None
    # REJECT
    rejection_reason: Optional[str] = None


# ── Management request ─────────────────────────────────────────────────────────
class DayakasabaRegistManagementRequest(BaseModel):
    action: DayakasabaAction
    payload: DayakasabaRegistRequestPayload


# ── Management response ────────────────────────────────────────────────────────
class DayakasabaRegistManagementResponse(BaseModel):
    status: str
    message: str
    data: Optional[Any] = None
    total: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None
