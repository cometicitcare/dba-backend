# app/schemas/reprint.py
from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.bhikku import QRSearchDataItem

class ReprintType(str, Enum):
    BHIKKU = "BHIKKU"
    HIGH_BHIKKU = "HIGH_BHIKKU"
    UPASAMPADA = "UPASAMPADA"
    SILMATHA = "SILMATHA"


class ReprintFlowStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"


class ReprintAction(str, Enum):
    CREATE = "CREATE"
    READ_ONE = "READ_ONE"
    READ_ALL = "READ_ALL"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    MARK_PRINTED = "MARK_PRINTED"
    DELETE = "DELETE"


class ReprintRequestCreate(BaseModel):
    request_type: Optional[ReprintType] = Field(
        None,
        description="Optional. If omitted, detected from regn prefix: BH → BHIKKU, SI → SILMATHA, UP → HIGH_BHIKKU.",
    )
    regn: str = Field(..., description="Registration number for the target record")
    request_reason: str = Field(..., max_length=500)
    amount: float
    form_no: Optional[str] = Field(None, max_length=50)
    remarks: Optional[str] = Field(None, max_length=500)


class ReprintRequestReject(BaseModel):
    rejection_reason: str = Field(..., max_length=500)


class ReprintRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    request_type: ReprintType
    bhikku_regn: Optional[str] = None
    bhikku_high_regn: Optional[str] = None
    upasampada_regn: Optional[str] = None
    silmatha_regn: Optional[str] = None
    regn: Optional[str] = None
    form_no: Optional[str] = None
    request_reason: Optional[str] = None
    amount: Optional[float] = None
    remarks: Optional[str] = None
    flow_status: ReprintFlowStatus
    requested_by: Optional[str] = None
    requested_at: datetime
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejected_by: Optional[str] = None
    rejected_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    printed_by: Optional[str] = None
    printed_at: Optional[datetime] = None
    completed_by: Optional[str] = None
    completed_at: Optional[datetime] = None
    subject: Optional["ReprintSubject"] = None
    qr_details: Optional[List[QRSearchDataItem]] = None


class ReprintRequestResponse(BaseModel):
    status: str
    message: str
    data: ReprintRequest


class ReprintRequestListResponse(BaseModel):
    status: str
    message: str
    data: List[ReprintRequest]


class ReprintManageRequest(BaseModel):
    action: ReprintAction
    request_id: Optional[Union[int, str]] = None
    create_payload: Optional[ReprintRequestCreate] = None
    flow_status: Optional[ReprintFlowStatus] = None
    request_type: Optional[ReprintType] = None
    rejection_reason: Optional[str] = None


class ReprintManageResponse(BaseModel):
    status: str
    message: str
    # Can return a single request, list of requests, or QR-style items (for READ_ONE by regn/id)
    data: Optional[Union[ReprintRequest, List[ReprintRequest], List[QRSearchDataItem]]] = None


class ReprintSubject(BaseModel):
    name: Optional[str] = None
    gihi_name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    dob: Optional[datetime] = None
    regn: Optional[str] = None
    type: Optional[ReprintType] = None


ReprintRequest.model_rebuild()
