from datetime import datetime
from enum import Enum
from typing import Annotated, Optional, List, Union, Any
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ObjectionStatus(str, Enum):
    """Status of objection"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class ObjectionAction(str, Enum):
    """Actions for objection management"""
    CREATE = "CREATE"
    READ_ONE = "READ_ONE"
    READ_ALL = "READ_ALL"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    CANCEL = "CANCEL"


class ObjectionBase(BaseModel):
    """
    Base schema for objection.
    Provide EITHER id OR one of (vh_trn, ar_trn, dv_trn, bh_regn, sil_regn, dbh_regn).
    
    If id is provided, entity type is auto-detected from prefix:
    - TRN* → Vihara (populates vh_trn)
    - ARN* → Arama (populates ar_trn)
    - DVL* → Devala (populates dv_trn)
    - BH* → Bhikku (populates bh_regn)
    - SIL* → Silmatha (populates sil_regn)
    - DBH*/UPS* → High Bhikku (populates dbh_regn)
    """
    id: Optional[str] = Field(None, min_length=1, max_length=50, description="Entity ID (auto-detects type from prefix)")
    vh_trn: Optional[str] = Field(None, max_length=20, description="Vihara TRN")
    ar_trn: Optional[str] = Field(None, max_length=20, description="Arama TRN")
    dv_trn: Optional[str] = Field(None, max_length=20, description="Devala TRN")
    bh_regn: Optional[str] = Field(None, max_length=20, description="Bhikku registration number")
    sil_regn: Optional[str] = Field(None, max_length=20, description="Silmatha registration number")
    dbh_regn: Optional[str] = Field(None, max_length=20, description="High Bhikku registration number")
    ot_code: Annotated[str, Field(min_length=1, max_length=50, description="Objection type code (REPRINT_RESTRICTION or RESIDENCY_RESTRICTION)")]
    obj_reason: Annotated[str, Field(min_length=1, max_length=1000, description="Reason for objection")]
    form_id: Optional[str] = Field(None, max_length=50, description="Related form ID/number")
    obj_requester_name: Optional[str] = Field(None, max_length=200, description="Name of the person making the request")
    obj_requester_contact: Optional[str] = Field(None, max_length=20, description="Contact number of requester")
    obj_requester_id_num: Optional[str] = Field(None, max_length=20, description="ID number of requester (NIC/Passport)")
    obj_valid_from: Optional[datetime] = Field(None, description="Objection validity start date")
    obj_valid_until: Optional[datetime] = Field(None, description="Objection validity end date (null = indefinite)")
    
    @model_validator(mode='after')
    def validate_entity_provided(self):
        """Ensure either id or exactly one entity identifier is provided"""
        has_id = self.id is not None
        entity_ids = [self.vh_trn, self.ar_trn, self.dv_trn, self.bh_regn, self.sil_regn, self.dbh_regn]
        non_null_count = sum(1 for eid in entity_ids if eid is not None)
        
        # If ID provided, no entity identifiers should be provided
        if has_id and non_null_count > 0:
            raise ValueError("Provide either 'id' OR one of (vh_trn, ar_trn, dv_trn, bh_regn, sil_regn, dbh_regn), not both")
        
        # If ID not provided, exactly one entity identifier required
        if not has_id:
            if non_null_count == 0:
                raise ValueError("Either 'id' or exactly one of (vh_trn, ar_trn, dv_trn, bh_regn, sil_regn, dbh_regn) must be provided")
            if non_null_count > 1:
                raise ValueError("Only one of vh_trn, ar_trn, dv_trn, bh_regn, sil_regn, or dbh_regn can be provided")
        
        return self


class ObjectionCreate(ObjectionBase):
    """Schema for creating objection"""
    pass


class ObjectionUpdate(BaseModel):
    """Schema for updating objection status"""
    obj_rejection_reason: Optional[str] = Field(None, max_length=500)
    obj_cancellation_reason: Optional[str] = Field(None, max_length=500)


class ObjectionOut(BaseModel):
    """Schema for objection output"""
    model_config = ConfigDict(from_attributes=True, exclude={'objection_type'})
    
    obj_id: int
    vh_trn: Optional[str] = None
    ar_trn: Optional[str] = None
    dv_trn: Optional[str] = None
    bh_regn: Optional[str] = None
    sil_regn: Optional[str] = None
    dbh_regn: Optional[str] = None
    ot_code: str
    obj_reason: str
    form_id: Optional[str] = None
    obj_requester_name: Optional[str] = None
    obj_requester_contact: Optional[str] = None
    obj_requester_id_num: Optional[str] = None
    obj_valid_from: Optional[datetime] = None
    obj_valid_until: Optional[datetime] = None
    obj_status: ObjectionStatus
    obj_submitted_by: Optional[str] = None
    obj_submitted_at: datetime
    obj_approved_by: Optional[str] = None
    obj_approved_at: Optional[datetime] = None
    obj_rejected_by: Optional[str] = None
    obj_rejected_at: Optional[datetime] = None
    obj_rejection_reason: Optional[str] = None
    obj_cancelled_by: Optional[str] = None
    obj_cancelled_at: Optional[datetime] = None
    obj_cancellation_reason: Optional[str] = None
    obj_is_deleted: bool
    obj_created_at: datetime
    obj_updated_at: Optional[datetime] = None
    obj_updated_by: Optional[str] = None


class ObjectionRequestPayload(BaseModel):
    """Payload for objection requests"""
    obj_id: Optional[int] = Field(None, ge=1)
    vh_trn: Optional[str] = Field(None, max_length=20, description="Filter by vihara TRN")
    ar_trn: Optional[str] = Field(None, max_length=20, description="Filter by arama TRN")
    dv_trn: Optional[str] = Field(None, max_length=20, description="Filter by devala TRN")
    bh_regn: Optional[str] = Field(None, max_length=20, description="Filter by bhikku registration")
    sil_regn: Optional[str] = Field(None, max_length=20, description="Filter by silmatha registration")
    dbh_regn: Optional[str] = Field(None, max_length=20, description="Filter by high bhikku registration")
    obj_status: Optional[ObjectionStatus] = None
    
    # Pagination
    page: Optional[int] = Field(default=1, ge=1)
    limit: Optional[int] = Field(default=10, ge=1, le=100)
    
    # For rejection/cancellation
    rejection_reason: Optional[str] = Field(None, max_length=500)
    cancellation_reason: Optional[str] = Field(None, max_length=500)
    
    # Data for CREATE
    data: Optional[Union[ObjectionCreate, ObjectionUpdate]] = None


class ObjectionManagementRequest(BaseModel):
    """Request schema for objection management"""
    action: ObjectionAction
    payload: ObjectionRequestPayload


class ObjectionManagementResponse(BaseModel):
    """Response schema for objection management"""
    status: str
    message: str
    data: Optional[Union[ObjectionOut, List[ObjectionOut], Any]] = None
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None


class ObjectionCheckResponse(BaseModel):
    """Response for checking if entity has active objection by TRN"""
    has_active_objection: bool
    objection: Optional[ObjectionOut] = None
    message: str


# Helper function to determine entity type from ID
def get_entity_type_from_id(entity_id: str) -> str:
    """
    Determine entity type from ID prefix:
    - TRN* -> VIHARA
    - ARN* -> ARAMA  
    - DVL* -> DEVALA
    - BH* -> BHIKKU
    - SIL* -> SILMATHA
    - DBH* or UPS* -> HIGH_BHIKKU
    """
    id_upper = entity_id.upper().strip()
    if id_upper.startswith("TRN"):
        return "VIHARA"
    elif id_upper.startswith("ARN"):
        return "ARAMA"
    elif id_upper.startswith("DVL"):
        return "DEVALA"
    elif id_upper.startswith("BH"):
        return "BHIKKU"
    elif id_upper.startswith("SIL"):
        return "SILMATHA"
    elif id_upper.startswith("DBH") or id_upper.startswith("UPS"):
        return "HIGH_BHIKKU"
    else:
        raise ValueError(f"Invalid ID format: {entity_id}. Must start with TRN, ARN, DVL, BH, SIL, DBH, or UPS")
