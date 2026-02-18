# app/schemas/sasanarakshana_regist.py
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, Any, List, Union
from enum import Enum


# --- Action Enum ---
class CRUDAction(str, Enum):
    CREATE = "CREATE"
    READ_ONE = "READ_ONE"
    READ_ALL = "READ_ALL"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


# --- Nested Vihara Schema (returned in response) ---
class ViharaNestedResponse(BaseModel):
    """Minimal vihara info nested inside the response"""
    vh_trn: str
    vh_vname: Optional[str] = None
    vh_addrs: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# --- Base Schema ---
class SasanarakshanaRegistBase(BaseModel):
    """Base schema for Sasanaarakshana Registration with common fields"""
    temple_trn: str  # FK: vihara TRN (vh_trn from vihaddata)
    temple_address: Optional[str] = None
    mandala_name: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    president_name: Optional[str] = None
    deputy_president_name: Optional[str] = None
    vice_president_1_name: Optional[str] = None
    vice_president_2_name: Optional[str] = None
    general_secretary_name: Optional[str] = None
    deputy_secretary_name: Optional[str] = None
    treasurer_name: Optional[str] = None
    committee_member_1: Optional[str] = None
    committee_member_2: Optional[str] = None
    committee_member_3: Optional[str] = None
    committee_member_4: Optional[str] = None
    committee_member_5: Optional[str] = None
    committee_member_6: Optional[str] = None
    committee_member_7: Optional[str] = None
    committee_member_8: Optional[str] = None
    chief_organizer_name: Optional[str] = None


# --- Create Schema ---
class SasanarakshanaRegistCreate(SasanarakshanaRegistBase):
    """Schema for creating a new Sasanaarakshana Registration record"""
    pass


# --- Update Schema ---
class SasanarakshanaRegistUpdate(BaseModel):
    """Schema for updating a Sasanaarakshana Registration record - all fields optional"""
    temple_trn: Optional[str] = None  # FK: vihara TRN
    temple_address: Optional[str] = None
    mandala_name: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    president_name: Optional[str] = None
    deputy_president_name: Optional[str] = None
    vice_president_1_name: Optional[str] = None
    vice_president_2_name: Optional[str] = None
    general_secretary_name: Optional[str] = None
    deputy_secretary_name: Optional[str] = None
    treasurer_name: Optional[str] = None
    committee_member_1: Optional[str] = None
    committee_member_2: Optional[str] = None
    committee_member_3: Optional[str] = None
    committee_member_4: Optional[str] = None
    committee_member_5: Optional[str] = None
    committee_member_6: Optional[str] = None
    committee_member_7: Optional[str] = None
    committee_member_8: Optional[str] = None
    chief_organizer_name: Optional[str] = None


# --- Response Schema ---
class SasanarakshanaRegistResponse(BaseModel):
    """Schema for Sasanaarakshana Registration responses"""
    sar_id: int
    temple_trn: str                             # raw FK stored
    temple: Optional[ViharaNestedResponse] = None  # nested vihara object
    temple_address: Optional[str] = None
    mandala_name: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    president_name: Optional[str] = None
    deputy_president_name: Optional[str] = None
    vice_president_1_name: Optional[str] = None
    vice_president_2_name: Optional[str] = None
    general_secretary_name: Optional[str] = None
    deputy_secretary_name: Optional[str] = None
    treasurer_name: Optional[str] = None
    committee_member_1: Optional[str] = None
    committee_member_2: Optional[str] = None
    committee_member_3: Optional[str] = None
    committee_member_4: Optional[str] = None
    committee_member_5: Optional[str] = None
    committee_member_6: Optional[str] = None
    committee_member_7: Optional[str] = None
    committee_member_8: Optional[str] = None
    chief_organizer_name: Optional[str] = None
    sar_is_deleted: Optional[bool] = False
    sar_created_at: Optional[datetime] = None
    sar_updated_at: Optional[datetime] = None
    sar_created_by: Optional[str] = None
    sar_updated_by: Optional[str] = None
    sar_version_number: Optional[int] = 1

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm_map(cls, obj) -> "SasanarakshanaRegistResponse":
        """Map DB model (sar_ prefixed) to flat response schema with nested vihara"""
        vihara = obj.temple  # loaded via relationship (lazy="joined")
        return cls(
            sar_id=obj.sar_id,
            temple_trn=obj.sar_temple_trn,
            temple=ViharaNestedResponse(
                vh_trn=vihara.vh_trn,
                vh_vname=vihara.vh_vname,
                vh_addrs=vihara.vh_addrs,
            ) if vihara else None,
            temple_address=obj.sar_temple_address,
            mandala_name=obj.sar_mandala_name,
            bank_name=obj.sar_bank_name,
            account_number=obj.sar_account_number,
            president_name=obj.sar_president_name,
            deputy_president_name=obj.sar_deputy_president_name,
            vice_president_1_name=obj.sar_vice_president_1_name,
            vice_president_2_name=obj.sar_vice_president_2_name,
            general_secretary_name=obj.sar_general_secretary_name,
            deputy_secretary_name=obj.sar_deputy_secretary_name,
            treasurer_name=obj.sar_treasurer_name,
            committee_member_1=obj.sar_committee_member_1,
            committee_member_2=obj.sar_committee_member_2,
            committee_member_3=obj.sar_committee_member_3,
            committee_member_4=obj.sar_committee_member_4,
            committee_member_5=obj.sar_committee_member_5,
            committee_member_6=obj.sar_committee_member_6,
            committee_member_7=obj.sar_committee_member_7,
            committee_member_8=obj.sar_committee_member_8,
            chief_organizer_name=obj.sar_chief_organizer_name,
            sar_is_deleted=obj.sar_is_deleted,
            sar_created_at=obj.sar_created_at,
            sar_updated_at=obj.sar_updated_at,
            sar_created_by=obj.sar_created_by,
            sar_updated_by=obj.sar_updated_by,
            sar_version_number=obj.sar_version_number,
        )



# --- List Response Schema ---
class SasanarakshanaRegistListResponse(BaseModel):
    """Response schema for list of Sasanaarakshana Registration records"""
    status: str
    message: str
    data: list[SasanarakshanaRegistResponse]
    total: int
    page: int
    limit: int


# --- Single Response Schema ---
class SasanarakshanaRegistSingleResponse(BaseModel):
    """Response schema for a single Sasanaarakshana Registration record"""
    status: str
    message: str
    data: SasanarakshanaRegistResponse


# --- Delete Response Schema ---
class SasanarakshanaRegistDeleteResponse(BaseModel):
    """Response schema for delete operation"""
    status: str
    message: str
    data: dict


# --- Management Request Payload ---
class SasanarakshanaRegistRequestPayload(BaseModel):
    """Payload wrapper used by the unified manage endpoint"""
    # For READ_ONE, UPDATE, DELETE
    sar_id: Optional[int] = None
    # For READ_ALL
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1, le=1000)
    page: Optional[int] = Field(default=1, ge=1)
    search_key: Optional[str] = Field(default="", max_length=200)
    # For CREATE / UPDATE
    data: Optional[Union[SasanarakshanaRegistCreate, SasanarakshanaRegistUpdate]] = None


# --- Unified Management Request ---
class SasanarakshanaRegistManagementRequest(BaseModel):
    action: CRUDAction
    payload: SasanarakshanaRegistRequestPayload


# --- Unified Management Response ---
class SasanarakshanaRegistManagementResponse(BaseModel):
    status: str
    message: str
    data: Optional[Any] = None
    total: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None
