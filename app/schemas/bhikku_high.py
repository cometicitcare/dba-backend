# app/schemas/bhikku_high.py
from datetime import date, datetime
from enum import Enum
from typing import Optional, Union, List, Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CRUDAction(str, Enum):
    CREATE = "CREATE"
    READ_ONE = "READ_ONE"
    READ_ALL = "READ_ALL"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


# --- Nested Response Schemas for Foreign Key Fields (from candidate bhikku) ---
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


class ParshawaResponse(BaseModel):
    """Nested response for parshawa"""
    code: str
    name: str


class ViharaResponse(BaseModel):
    """Nested response for vihara/temple"""
    vh_trn: str
    vh_vname: str


class BhikkuRefResponse(BaseModel):
    """Nested response for bhikku references"""
    br_regn: str
    br_mahananame: str
    br_upasampadaname: Optional[str] = ""


class BhikkuHighBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    bhr_regn: Optional[str] = Field(default=None, max_length=12)
    bhr_reqstdate: Optional[date] = None
    bhr_currstat: Optional[str] = Field(default=None, max_length=5)
    bhr_parshawaya: Optional[str] = Field(default=None, max_length=10)
    bhr_livtemple: Optional[str] = Field(default=None, max_length=10)

    bhr_samanera_serial_no: Optional[str] = Field(default=None, max_length=20)
    bhr_remarks: Optional[str] = Field(default=None, max_length=100)
    bhr_cc_code: Optional[str] = Field(default=None, max_length=5)
    bhr_candidate_regn: Optional[str] = Field(default=None, max_length=12)
    bhr_higher_ordination_place: Optional[str] = Field(default=None, max_length=50)
    bhr_higher_ordination_date: Optional[date] = None
    bhr_karmacharya_name: Optional[str] = Field(default=None, max_length=12)
    bhr_upaddhyaya_name: Optional[str] = Field(default=None, max_length=12)
    bhr_assumed_name: Optional[str] = Field(default=None, max_length=50)
    bhr_residence_higher_ordination_trn: Optional[str] = Field(default=None, max_length=50)
    bhr_residence_permanent_trn: Optional[str] = Field(default=None, max_length=50)
    bhr_declaration_residence_address: Optional[str] = Field(default=None, max_length=200)
    bhr_tutors_tutor_regn: Optional[str] = Field(default=None, max_length=200)
    bhr_presiding_bhikshu_regn: Optional[str] = Field(default=None, max_length=200)
    bhr_declaration_date: Optional[date] = None

class BhikkuHighCreate(BhikkuHighBase):
    pass


class BhikkuHighUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    bhr_regn: Optional[str] = Field(default=None, max_length=12)
    bhr_reqstdate: Optional[date] = None
    bhr_currstat: Optional[str] = Field(default=None, max_length=5)
    bhr_parshawaya: Optional[str] = Field(default=None, max_length=10)
    bhr_livtemple: Optional[str] = Field(default=None, max_length=10)

    bhr_samanera_serial_no: Optional[str] = Field(default=None, max_length=20)
    bhr_remarks: Optional[str] = Field(default=None, max_length=100)
    bhr_cc_code: Optional[str] = Field(default=None, max_length=5)
    bhr_candidate_regn: Optional[str] = Field(default=None, max_length=12)
    bhr_higher_ordination_place: Optional[str] = Field(default=None, max_length=50)
    bhr_higher_ordination_date: Optional[date] = None
    bhr_karmacharya_name: Optional[str] = Field(default=None, max_length=12)
    bhr_upaddhyaya_name: Optional[str] = Field(default=None, max_length=12)
    bhr_assumed_name: Optional[str] = Field(default=None, max_length=50)
    bhr_residence_higher_ordination_trn: Optional[str] = Field(default=None, max_length=50)
    bhr_residence_permanent_trn: Optional[str] = Field(default=None, max_length=50)
    bhr_declaration_residence_address: Optional[str] = Field(default=None, max_length=200)
    bhr_tutors_tutor_regn: Optional[str] = Field(default=None, max_length=200)
    bhr_presiding_bhikshu_regn: Optional[str] = Field(default=None, max_length=200)
    bhr_declaration_date: Optional[date] = None


class BhikkuHigh(BhikkuHighBase):
    model_config = ConfigDict(
        from_attributes=True, str_strip_whitespace=True, populate_by_name=True
    )

    bhr_regn: str
    bhr_id: int
    bhr_version: datetime
    bhr_is_deleted: bool
    bhr_created_at: Optional[datetime] = None
    bhr_updated_at: Optional[datetime] = None
    bhr_created_by: Optional[str] = None
    bhr_updated_by: Optional[str] = None
    bhr_version_number: Optional[int] = None


class BhikkuHighFrontendCreate(BaseModel):
    """Schema for frontend payload with human-readable field names"""
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)
    
    # Required fields
    cc_code: Optional[str] = Field(default=None, max_length=5)
    candidate_regn: str = Field(min_length=1, max_length=12)
    higher_ordination_place: Optional[str] = Field(default=None, max_length=10)
    higher_ordination_date: Optional[date] = None
    karmacharya_name: Optional[str] = Field(default=None, max_length=12)
    upaddhyaya_name: Optional[str] = Field(default=None, max_length=12)
    assumed_name: Optional[str] = Field(default=None, max_length=50)
    residence_higher_ordination_trn: str = Field(min_length=1, max_length=10)
    residence_permanent_trn: str = Field(min_length=1, max_length=10)
    declaration_residence_address: Optional[str] = Field(default=None, max_length=10)
    tutors_tutor_regn: Optional[str] = Field(default=None, max_length=200)
    presiding_bhikshu_regn: Optional[str] = Field(default=None, max_length=200)
    samanera_serial: Optional[str] = Field(default=None, max_length=20)
    declaration_date: date
    remarks: Optional[str] = Field(default=None, max_length=100)
    
    def to_bhikku_high_create(self) -> BhikkuHighCreate:
        """Convert frontend payload to internal BhikkuHighCreate schema"""
        return BhikkuHighCreate(
            bhr_regn=self.candidate_regn,
            bhr_reqstdate=self.declaration_date,
            bhr_currstat="PNDNG",  # Default status for new records
            bhr_parshawaya=self.residence_permanent_trn,
            bhr_livtemple=self.residence_higher_ordination_trn,
            bhr_samanera_serial_no=self.samanera_serial,
            bhr_remarks=self.remarks,
            bhr_cc_code=self.cc_code,
            bhr_candidate_regn=self.candidate_regn,
            bhr_higher_ordination_place=self.higher_ordination_place,
            bhr_higher_ordination_date=self.higher_ordination_date,
            bhr_karmacharya_name=self.karmacharya_name,
            bhr_upaddhyaya_name=self.upaddhyaya_name,
            bhr_assumed_name=self.assumed_name,
            bhr_residence_higher_ordination_trn=self.residence_higher_ordination_trn,
            bhr_residence_permanent_trn=self.residence_permanent_trn,
            bhr_declaration_residence_address=self.declaration_residence_address,
            bhr_tutors_tutor_regn=self.tutors_tutor_regn,
            bhr_presiding_bhikshu_regn=self.presiding_bhikshu_regn,
            bhr_declaration_date=self.declaration_date,
        )


class BhikkuHighFrontendUpdate(BaseModel):
    """Schema for frontend update payload with human-readable field names"""
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)
    
    # All fields are optional for updates
    cc_code: Optional[str] = Field(default=None, max_length=5)
    candidate_regn: Optional[str] = Field(default=None, max_length=12)
    higher_ordination_place: Optional[str] = Field(default=None, max_length=10)
    higher_ordination_date: Optional[date] = None
    karmacharya_name: Optional[str] = Field(default=None, max_length=12)
    upaddhyaya_name: Optional[str] = Field(default=None, max_length=12)
    assumed_name: Optional[str] = Field(default=None, max_length=50)
    residence_higher_ordination_trn: Optional[str] = Field(default=None, max_length=10)
    residence_permanent_trn: Optional[str] = Field(default=None, max_length=10)
    declaration_residence_address: Optional[str] = Field(default=None, max_length=10)
    tutors_tutor_regn: Optional[str] = Field(default=None, max_length=200)
    presiding_bhikshu_regn: Optional[str] = Field(default=None, max_length=200)
    samanera_serial: Optional[str] = Field(default=None, max_length=20)
    declaration_date: Optional[date] = None
    remarks: Optional[str] = Field(default=None, max_length=100)
    
    def to_bhikku_high_update(self) -> BhikkuHighUpdate:
        """Convert frontend payload to internal BhikkuHighUpdate schema"""
        return BhikkuHighUpdate(
            bhr_regn=self.candidate_regn,
            bhr_reqstdate=self.declaration_date,
            bhr_parshawaya=self.residence_permanent_trn,
            bhr_livtemple=self.residence_higher_ordination_trn,
            bhr_samanera_serial_no=self.samanera_serial,
            bhr_remarks=self.remarks,
            bhr_cc_code=self.cc_code,
            bhr_candidate_regn=self.candidate_regn,
            bhr_higher_ordination_place=self.higher_ordination_place,
            bhr_higher_ordination_date=self.higher_ordination_date,
            bhr_karmacharya_name=self.karmacharya_name,
            bhr_upaddhyaya_name=self.upaddhyaya_name,
            bhr_assumed_name=self.assumed_name,
            bhr_residence_higher_ordination_trn=self.residence_higher_ordination_trn,
            bhr_residence_permanent_trn=self.residence_permanent_trn,
            bhr_declaration_residence_address=self.declaration_residence_address,
            bhr_tutors_tutor_regn=self.tutors_tutor_regn,
            bhr_presiding_bhikshu_regn=self.presiding_bhikshu_regn,
            bhr_declaration_date=self.declaration_date,
        )


class BhikkuHighRequestPayload(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    bhr_id: Optional[int] = None
    bhr_regn: Optional[str] = None
    skip: int = 0
    limit: int = 10
    page: Optional[int] = 1
    search_key: Optional[str] = ""
    data: Optional[Any] = None  # Accept any type, will be parsed in the route


class BhikkuHighManagementRequest(BaseModel):
    action: CRUDAction
    payload: BhikkuHighRequestPayload


class BhikkuHighManagementResponse(BaseModel):
    status: str
    message: str
    data: Optional[Union[BhikkuHigh, List[BhikkuHigh], dict, List[dict]]] = None
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None


# --- Workflow Action Schemas ---
class BhikkuHighWorkflowActionType(str, Enum):
    """Workflow actions available for bhikku high records"""
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    MARK_PRINTED = "MARK_PRINTED"
    MARK_SCANNED = "MARK_SCANNED"


class BhikkuHighWorkflowRequest(BaseModel):
    """Request to update workflow status of a bhikku high record"""
    bhr_id: int = Field(..., description="Bhikku high registration ID")
    action: BhikkuHighWorkflowActionType
    rejection_reason: Optional[str] = Field(None, max_length=500, description="Required when action is REJECT")
    
    class Config:
        json_schema_extra = {
            "example": {
                "bhr_id": 1,
                "action": "APPROVE"
            }
        }


class BhikkuHighWorkflowResponse(BaseModel):
    """Response after workflow action"""
    model_config = ConfigDict(from_attributes=True)
    
    status: str
    message: str
    data: Optional[Union[BhikkuHigh, dict]] = None
