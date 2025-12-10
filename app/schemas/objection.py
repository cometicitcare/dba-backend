from datetime import datetime
from enum import Enum
from typing import Annotated, Optional, List, Union, Any
from pydantic import BaseModel, ConfigDict, Field, field_validator


class EntityType(str, Enum):
    """Type of entity for objection"""
    VIHARA = "VIHARA"
    ARAMA = "ARAMA"
    DEVALA = "DEVALA"


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
    """Base schema for objection"""
    obj_entity_type: EntityType
    obj_entity_trn: Annotated[str, Field(min_length=1, max_length=50)]
    obj_entity_name: Optional[str] = Field(None, max_length=200)
    obj_reason: Annotated[str, Field(min_length=1, max_length=1000)]


class ObjectionCreate(ObjectionBase):
    """Schema for creating objection"""
    pass


class ObjectionUpdate(BaseModel):
    """Schema for updating objection status"""
    obj_rejection_reason: Optional[str] = Field(None, max_length=500)
    obj_cancellation_reason: Optional[str] = Field(None, max_length=500)


class ObjectionOut(ObjectionBase):
    """Schema for objection output"""
    model_config = ConfigDict(from_attributes=True)
    
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
    obj_entity_type: Optional[EntityType] = None
    obj_entity_trn: Optional[str] = Field(None, max_length=50)
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
    """Response for checking if entity has active objection"""
    has_active_objection: bool
    objection: Optional[ObjectionOut] = None
    message: str
