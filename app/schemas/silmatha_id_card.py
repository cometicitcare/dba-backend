# app/schemas/silmatha_id_card.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional, List
from enum import Enum


# --- Action Enum for CRUD operations ---
class SilmathaIDCardAction(str, Enum):
    """Actions supported by the /manage endpoint"""
    CREATE = "CREATE"
    READ_ONE = "READ_ONE"
    READ_ALL = "READ_ALL"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    MARK_PRINTED = "MARK_PRINTED"


# --- Workflow Status Enum ---
class SilmathaIDCardWorkflowStatus(str, Enum):
    """Workflow statuses for Silmatha ID Card"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PRINTING_COMPLETE = "PRINTING_COMPLETE"
    COMPLETED = "COMPLETED"


# --- Stay History Item Schema ---
class StayHistoryItem(BaseModel):
    """Schema for individual stay history entry"""
    temple_name: str = Field(..., description="Name of the temple")
    temple_address: str = Field(..., description="Address of the temple")
    from_date: date = Field(..., description="Start date of stay (YYYY-MM-DD)")
    to_date: Optional[date] = Field(None, description="End date of stay (YYYY-MM-DD), can be null if still staying")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "temple_name": "Sri Maha Bodhi Viharaya",
                "temple_address": "Anuradhapura, Sri Lanka",
                "from_date": "2020-01-15",
                "to_date": "2022-03-20"
            }
        }
    )


# --- Base Schema ---
class SilmathaIDCardBase(BaseModel):
    """Base schema with all fields from the form"""
    
    # Top Section
    sic_divisional_secretariat: Optional[str] = Field(None, max_length=100, description="District")
    sic_district: Optional[str] = Field(None, max_length=100, description="District")
    
    # 01. Declaration Full Name
    sic_full_silmatha_name: str = Field(..., max_length=200, description="Full Silmatha Name")
    sic_title_post: Optional[str] = Field(None, max_length=100, description="Title/Post")
    
    # 02. As per birth certificate
    sic_lay_name_full: str = Field(..., max_length=200, description="Gihi/Lay Name in full")
    sic_dob: date = Field(..., description="Date of Birth (YYYY-MM-DD)")
    sic_birth_place: Optional[str] = Field(None, max_length=200, description="Place of Birth")
    
    # 03. Ordination details
    sic_robing_date: Optional[date] = Field(None, description="Date of Robing (YYYY-MM-DD)")
    sic_robing_place: Optional[str] = Field(None, max_length=200, description="Place of Robing")
    sic_robing_nikaya: Optional[str] = Field(None, max_length=100, description="Nikaya at robing")
    sic_robing_parshawaya: Optional[str] = Field(None, max_length=100, description="Parshawaya at robing")
    
    # 04. Registration numbers & higher ordination
    sic_samaneri_reg_no: Optional[str] = Field(None, max_length=50, description="Samaneri Registration Number")
    sic_dasa_sil_mata_reg_no: Optional[str] = Field(None, max_length=50, description="Dasa Sil Mata Registration Number")
    sic_higher_ord_date: Optional[date] = Field(None, description="Date of Higher Ordinance (YYYY-MM-DD)")
    
    # 05. Name at Higher Ordinance
    sic_higher_ord_name: Optional[str] = Field(None, max_length=200, description="Name taken at Higher Ordinance")
    
    # 06. Permanent residence
    sic_perm_residence: Optional[str] = Field(None, description="Permanent residence address")
    
    # 07. National ID
    sic_national_id: Optional[str] = Field(None, max_length=20, description="National ID Card Number")
    
    # 08. Places stayed so far
    sic_stay_history: Optional[List[StayHistoryItem]] = Field(
        None, 
        description="Array of stay history entries"
    )


# --- Create Schema ---
class SilmathaIDCardCreate(SilmathaIDCardBase):
    """
    Schema for creating a new Silmatha ID Card.
    
    - sic_sil_regn is REQUIRED (must be an existing Silmatha registration number)
    - sic_form_no is auto-generated, so NOT included here
    - Workflow status defaults to PENDING
    """
    sic_sil_regn: str = Field(..., max_length=20, description="Silmatha registration number (must exist in silmatha_regist)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sic_sil_regn": "SIL2025000001",
                "sic_divisional_secretariat": "Kandy",
                "sic_district": "Kandy",
                "sic_full_silmatha_name": "Sister Dharmapriya",
                "sic_title_post": "Chief Attendant",
                "sic_lay_name_full": "Karunaratne Mudiyanselage Nirmala",
                "sic_dob": "1988-08-22",
                "sic_birth_place": "Galle",
                "sic_robing_date": "2010-05-15",
                "sic_robing_place": "Dambulla Viharaya",
                "sic_robing_nikaya": "Siam",
                "sic_robing_parshawaya": "Dambulla",
                "sic_samaneri_reg_no": "SAM2010001",
                "sic_dasa_sil_mata_reg_no": "DSM2015001",
                "sic_higher_ord_date": "2015-10-10",
                "sic_higher_ord_name": "Dharmapriya",
                "sic_perm_residence": "Dambulla Viharaya, Matale",
                "sic_national_id": "888242345V",
                "sic_stay_history": [
                    {
                        "temple_name": "Dambulla Viharaya",
                        "temple_address": "Dambulla, Sri Lanka",
                        "from_date": "2010-05-15",
                        "to_date": None
                    }
                ]
            }
        }
    )


# --- Update Schema ---
class SilmathaIDCardUpdate(BaseModel):
    """
    Schema for updating an existing Silmatha ID Card.
    All fields are optional.
    """
    # Top Section
    sic_divisional_secretariat: Optional[str] = Field(None, max_length=100)
    sic_district: Optional[str] = Field(None, max_length=100)
    
    # 01. Declaration Full Name
    sic_full_silmatha_name: Optional[str] = Field(None, max_length=200)
    sic_title_post: Optional[str] = Field(None, max_length=100)
    
    # 02. As per birth certificate
    sic_lay_name_full: Optional[str] = Field(None, max_length=200)
    sic_dob: Optional[date] = Field(None, description="YYYY-MM-DD")
    sic_birth_place: Optional[str] = Field(None, max_length=200)
    
    # 03. Ordination details
    sic_robing_date: Optional[date] = Field(None)
    sic_robing_place: Optional[str] = Field(None, max_length=200)
    sic_robing_nikaya: Optional[str] = Field(None, max_length=100)
    sic_robing_parshawaya: Optional[str] = Field(None, max_length=100)
    
    # 04. Registration numbers & higher ordination
    sic_samaneri_reg_no: Optional[str] = Field(None, max_length=50)
    sic_dasa_sil_mata_reg_no: Optional[str] = Field(None, max_length=50)
    sic_higher_ord_date: Optional[date] = Field(None)
    
    # 05. Name at Higher Ordinance
    sic_higher_ord_name: Optional[str] = Field(None, max_length=200)
    
    # 06. Permanent residence
    sic_perm_residence: Optional[str] = Field(None)
    
    # 07. National ID
    sic_national_id: Optional[str] = Field(None, max_length=20)
    
    # 08. Places stayed so far
    sic_stay_history: Optional[List[StayHistoryItem]] = Field(None)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sic_district": "Matale",
                "sic_national_id": "888242345V"
            }
        }
    )


# --- Internal Schema (with all fields including auto-generated) ---
class SilmathaIDCardInternal(SilmathaIDCardBase):
    """
    Internal schema with ALL fields (including auto-generated ones).
    Used for database responses.
    """
    sic_id: int
    sic_form_no: str
    sic_sil_regn: str
    sic_left_thumbprint_url: Optional[str] = None
    sic_applicant_photo_url: Optional[str] = None
    sic_workflow_status: str
    sic_approved_by: Optional[str] = None
    sic_approved_at: Optional[datetime] = None
    sic_rejection_reason: Optional[str] = None
    sic_rejected_by: Optional[str] = None
    sic_rejected_at: Optional[datetime] = None
    sic_printed_by: Optional[str] = None
    sic_printed_at: Optional[datetime] = None
    sic_created_by: Optional[str] = None
    sic_created_at: datetime
    sic_updated_by: Optional[str] = None
    sic_updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# --- Response Schema (clean API response) ---
class SilmathaIDCardResponse(BaseModel):
    """Response schema for API endpoints"""
    sic_id: int
    sic_form_no: str
    sic_sil_regn: str
    sic_divisional_secretariat: Optional[str] = None
    sic_district: Optional[str] = None
    sic_full_silmatha_name: str
    sic_title_post: Optional[str] = None
    sic_lay_name_full: str
    sic_dob: date
    sic_birth_place: Optional[str] = None
    sic_robing_date: Optional[date] = None
    sic_robing_place: Optional[str] = None
    sic_robing_nikaya: Optional[str] = None
    sic_robing_parshawaya: Optional[str] = None
    sic_samaneri_reg_no: Optional[str] = None
    sic_dasa_sil_mata_reg_no: Optional[str] = None
    sic_higher_ord_date: Optional[date] = None
    sic_higher_ord_name: Optional[str] = None
    sic_perm_residence: Optional[str] = None
    sic_national_id: Optional[str] = None
    sic_stay_history: Optional[List[StayHistoryItem]] = None
    sic_left_thumbprint_url: Optional[str] = None
    sic_applicant_photo_url: Optional[str] = None
    sic_workflow_status: str
    sic_approved_by: Optional[str] = None
    sic_approved_at: Optional[datetime] = None
    sic_rejection_reason: Optional[str] = None
    sic_rejected_by: Optional[str] = None
    sic_rejected_at: Optional[datetime] = None
    sic_printed_by: Optional[str] = None
    sic_printed_at: Optional[datetime] = None
    sic_created_by: Optional[str] = None
    sic_created_at: datetime
    sic_updated_by: Optional[str] = None
    sic_updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# --- Manage Endpoint Response ---
class SilmathaIDCardManageResponse(BaseModel):
    """Unified response for /manage endpoint"""
    status: str = Field(..., description="success or error")
    message: str
    data: Optional[SilmathaIDCardResponse | List[SilmathaIDCardResponse]] = None
    total: Optional[int] = Field(None, description="Total count for READ_ALL")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "message": "Silmatha ID Card created successfully with form number SIC2025000001",
                "data": {
                    "sic_id": 1,
                    "sic_form_no": "SIC2025000001",
                    "sic_sil_regn": "SIL2025000001",
                    "sic_full_silmatha_name": "Sister Dharmapriya",
                    "sic_workflow_status": "PENDING"
                }
            }
        }
    )


# --- Workflow Action Types ---
class SilmathaIDCardWorkflowActionType(str, Enum):
    """Workflow actions for ID Card processing"""
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    MARK_PRINTED = "MARK_PRINTED"


# --- Workflow Request Schema ---
class SilmathaIDCardWorkflowRequest(BaseModel):
    """Request schema for workflow actions"""
    action: SilmathaIDCardWorkflowActionType
    sic_id: Optional[int] = Field(None, description="ID Card ID (use this OR sic_form_no)")
    sic_form_no: Optional[str] = Field(None, description="Form number (use this OR sic_id)")
    rejection_reason: Optional[str] = Field(None, description="Required for REJECT action")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "action": "APPROVE",
                "sic_form_no": "SIC2025000001"
            }
        }
    )


# --- Workflow Response Schema ---
class SilmathaIDCardWorkflowResponse(BaseModel):
    """Response schema for workflow actions"""
    status: str
    message: str
    data: Optional[SilmathaIDCardResponse] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "message": "ID Card SIC2025000001 approved successfully",
                "data": {
                    "sic_id": 1,
                    "sic_form_no": "SIC2025000001",
                    "sic_workflow_status": "APPROVED"
                }
            }
        }
    )
