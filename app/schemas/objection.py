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
    Provide EITHER trn OR one of (vh_id, ar_id, dv_id).
    
    If trn is provided, entity type is auto-detected:
    - TRN* → Vihara (populates vh_id)
    - ARN* → Arama (populates ar_id)
    - DVL* → Devala (populates dv_id)
    """
    trn: Optional[str] = Field(None, min_length=1, max_length=50, description="Entity TRN (auto-detects type from prefix)")
    vh_id: Optional[int] = Field(None, ge=1, description="Vihara ID (if objection is for vihara)")
    ar_id: Optional[int] = Field(None, ge=1, description="Arama ID (if objection is for arama)")
    dv_id: Optional[int] = Field(None, ge=1, description="Devala ID (if objection is for devala)")
    obj_type_id: Annotated[int, Field(ge=1, description="Objection type ID")]
    obj_reason: Annotated[str, Field(min_length=1, max_length=1000, description="Reason for objection")]
    
    @model_validator(mode='after')
    def validate_entity_provided(self):
        """Ensure either trn or exactly one entity FK is provided"""
        has_trn = self.trn is not None
        entity_ids = [self.vh_id, self.ar_id, self.dv_id]
        non_null_count = sum(1 for eid in entity_ids if eid is not None)
        
        # If TRN provided, no entity IDs should be provided
        if has_trn and non_null_count > 0:
            raise ValueError("Provide either 'trn' OR one of (vh_id, ar_id, dv_id), not both")
        
        # If TRN not provided, exactly one entity ID required
        if not has_trn:
            if non_null_count == 0:
                raise ValueError("Either 'trn' or exactly one of (vh_id, ar_id, dv_id) must be provided")
            if non_null_count > 1:
                raise ValueError("Only one of vh_id, ar_id, or dv_id can be provided")
        
        return self


class ObjectionCreate(ObjectionBase):
    """Schema for creating objection"""
    pass


class ObjectionUpdate(BaseModel):
    """Schema for updating objection status"""
    obj_rejection_reason: Optional[str] = Field(None, max_length=500)
    obj_cancellation_reason: Optional[str] = Field(None, max_length=500)


class ObjectionOut(ObjectionBase):
    """Schema for objection output"""
    model_config = ConfigDict(from_attributes=True, exclude={'objection_type', 'vihara', 'arama', 'devala'})
    
    obj_id: int
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
    vh_id: Optional[int] = Field(None, ge=1, description="Filter by vihara ID")
    ar_id: Optional[int] = Field(None, ge=1, description="Filter by arama ID")
    dv_id: Optional[int] = Field(None, ge=1, description="Filter by devala ID")
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


# Helper function to determine entity type from TRN
def get_entity_type_from_trn(trn: str) -> str:
    """
    Determine entity type from TRN prefix:
    - TRN* -> VIHARA
    - ARN* -> ARAMA  
    - DVL* -> DEVALA
    """
    trn_upper = trn.upper().strip()
    if trn_upper.startswith("TRN"):
        return "VIHARA"
    elif trn_upper.startswith("ARN"):
        return "ARAMA"
    elif trn_upper.startswith("DVL"):
        return "DEVALA"
    else:
        raise ValueError(f"Invalid TRN format: {trn}. Must start with TRN, ARN, or DVL")
