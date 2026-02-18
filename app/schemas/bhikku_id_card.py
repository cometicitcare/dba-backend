# app/schemas/bhikku_id_card.py
from pydantic import BaseModel, Field, validator
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from enum import Enum


# --- Action Enum for CRUD operations ---
class BhikkuIDCardAction(str, Enum):
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
class BhikkuIDCardWorkflowStatus(str, Enum):
    """Workflow statuses for Bhikku ID Card"""
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
    
    class Config:
        json_schema_extra = {
            "example": {
                "temple_name": "Sri Dalada Maligawa",
                "temple_address": "Kandy, Sri Lanka",
                "from_date": "2020-01-15",
                "to_date": "2022-03-20"
            }
        }


# --- Base Schema ---
class BhikkuIDCardBase(BaseModel):
    """Base schema with all fields from the form"""
    
    # Category
    bic_category: Optional[str] = Field(None, max_length=100, description="Category of ID card")

    # Top Section
    bic_divisional_secretariat: Optional[str] = Field(None, max_length=100, description="Division (English / divisionE)")
    bic_division_s: Optional[str] = Field(None, max_length=100, description="Division (Sinhala / divisionS)")
    bic_district: Optional[str] = Field(None, max_length=100, description="District (English / districtE)")
    bic_district_s: Optional[str] = Field(None, max_length=100, description="District (Sinhala / districtS)")
    
    # 01. Declaration Full Name
    bic_full_bhikku_name: str = Field(..., max_length=200, description="Full Bhikku Name (English / nameE)")
    bic_name_s: Optional[str] = Field(None, max_length=200, description="Full Bhikku Name (Sinhala / nameS)")
    bic_title_post: Optional[str] = Field(None, max_length=100, description="Title/Post (English / padawiyaE)")
    bic_padawiya_s: Optional[str] = Field(None, max_length=100, description="Title/Post (Sinhala / padawiyaS)")
    
    # 02. As per birth certificate
    bic_lay_name_full: str = Field(..., max_length=200, description="Gihi/Lay Name in full")
    bic_dob: date = Field(..., description="Date of Birth (YYYY-MM-DD)")
    bic_birth_place: Optional[str] = Field(None, max_length=200, description="Place of Birth")
    
    # 03. Ordination details
    bic_robing_date: Optional[date] = Field(None, description="Date of Robing (YYYY-MM-DD)")
    bic_robing_place: Optional[str] = Field(None, max_length=200, description="Place of Robing")
    bic_robing_nikaya: Optional[str] = Field(None, max_length=100, description="Nikaya (English / nikayaE)")
    bic_nikaya_s: Optional[str] = Field(None, max_length=100, description="Nikaya (Sinhala / nikayaS)")
    bic_robing_parshawaya: Optional[str] = Field(None, max_length=100, description="Parshwaya (English / parshwayaE)")
    bic_parshwaya_s: Optional[str] = Field(None, max_length=100, description="Parshwaya (Sinhala / parshwayaS)")

    # Temple Name (current/main temple)
    bic_temple_name_e: Optional[str] = Field(None, max_length=200, description="Temple Name (English / templeE)")
    bic_temple_name_s: Optional[str] = Field(None, max_length=200, description="Temple Name (Sinhala / templeS)")
    
    # 04. Registration numbers & higher ordination
    bic_samanera_reg_no: Optional[str] = Field(None, max_length=50, description="Samanera Registration Number")
    bic_upasampada_reg_no: Optional[str] = Field(None, max_length=50, description="Upasampada Registration Number")
    bic_higher_ord_date: Optional[date] = Field(None, description="Date of Higher Ordinance (YYYY-MM-DD)")
    
    # 05. Name at Higher Ordinance
    bic_higher_ord_name: Optional[str] = Field(None, max_length=200, description="Name taken at Higher Ordinance")
    
    # 06. Permanent residence
    bic_perm_residence: Optional[str] = Field(None, description="Permanent residence address")
    
    # 07. National ID
    bic_national_id: Optional[str] = Field(None, max_length=20, description="National ID Card Number")
    
    # 08. Places stayed so far
    bic_stay_history: Optional[List[StayHistoryItem]] = Field(
        None, 
        description="Array of stay history entries"
    )

    # Issue Date
    bic_issue_date: Optional[date] = Field(None, description="ID Card issue date (YYYY-MM-DD)")


# --- Create Schema ---
class BhikkuIDCardCreate(BhikkuIDCardBase):
    """
    Schema for creating a new Bhikku ID Card.
    
    - bic_br_regn is REQUIRED (must be an existing Bhikku registration number)
    - bic_form_no is auto-generated, so NOT included here
    - Workflow status defaults to PENDING
    """
    bic_br_regn: str = Field(..., max_length=20, description="Bhikku registration number (must exist in bhikku_regist)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "bic_br_regn": "BH202500001",
                "bic_divisional_secretariat": "Kandy",
                "bic_district": "Kandy",
                "bic_full_bhikku_name": "Ven. Mahanama Thero",
                "bic_title_post": "Chief Incumbent",
                "bic_lay_name_full": "Karunaratne Mudiyanselage Somapala",
                "bic_dob": "1985-05-15",
                "bic_birth_place": "Colombo",
                "bic_robing_date": "2005-07-10",
                "bic_robing_place": "Malwatta Maha Viharaya",
                "bic_robing_nikaya": "Siam",
                "bic_robing_parshawaya": "Malwatta",
                "bic_samanera_reg_no": "SAM2005001",
                "bic_upasampada_reg_no": "UPA2010001",
                "bic_higher_ord_date": "2010-06-20",
                "bic_higher_ord_name": "Mahanama",
                "bic_perm_residence": "Malwatta Maha Viharaya, Kandy",
                "bic_national_id": "850152345V",
                "bic_stay_history": [
                    {
                        "temple_name": "Malwatta Maha Viharaya",
                        "temple_address": "Kandy, Sri Lanka",
                        "from_date": "2005-07-10",
                        "to_date": None
                    }
                ]
            }
        }


# --- Update Schema ---
class BhikkuIDCardUpdate(BaseModel):
    """
    Schema for updating an existing Bhikku ID Card.
    All fields are optional.
    """
    # Category
    bic_category: Optional[str] = Field(None, max_length=100)

    # Top Section
    bic_divisional_secretariat: Optional[str] = Field(None, max_length=100)
    bic_division_s: Optional[str] = Field(None, max_length=100)
    bic_district: Optional[str] = Field(None, max_length=100)
    bic_district_s: Optional[str] = Field(None, max_length=100)
    
    # 01. Name
    bic_full_bhikku_name: Optional[str] = Field(None, max_length=200)
    bic_name_s: Optional[str] = Field(None, max_length=200)
    bic_title_post: Optional[str] = Field(None, max_length=100)
    bic_padawiya_s: Optional[str] = Field(None, max_length=100)
    
    # 02. As per birth certificate
    bic_lay_name_full: Optional[str] = Field(None, max_length=200)
    bic_dob: Optional[date] = None
    bic_birth_place: Optional[str] = Field(None, max_length=200)
    
    # 03. Ordination details
    bic_robing_date: Optional[date] = None
    bic_robing_place: Optional[str] = Field(None, max_length=200)
    bic_robing_nikaya: Optional[str] = Field(None, max_length=100)
    bic_nikaya_s: Optional[str] = Field(None, max_length=100)
    bic_robing_parshawaya: Optional[str] = Field(None, max_length=100)
    bic_parshwaya_s: Optional[str] = Field(None, max_length=100)

    # Temple Name
    bic_temple_name_e: Optional[str] = Field(None, max_length=200)
    bic_temple_name_s: Optional[str] = Field(None, max_length=200)
    
    # 04. Registration numbers & higher ordination
    bic_samanera_reg_no: Optional[str] = Field(None, max_length=50)
    bic_upasampada_reg_no: Optional[str] = Field(None, max_length=50)
    bic_higher_ord_date: Optional[date] = None
    
    # 05. Name at Higher Ordinance
    bic_higher_ord_name: Optional[str] = Field(None, max_length=200)
    
    # 06. Permanent residence
    bic_perm_residence: Optional[str] = None
    
    # 07. National ID
    bic_national_id: Optional[str] = Field(None, max_length=20)
    
    # 08. Places stayed so far
    bic_stay_history: Optional[List[StayHistoryItem]] = None

    # Issue Date
    bic_issue_date: Optional[date] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "bic_title_post": "Deputy Chief Incumbent",
                "bic_perm_residence": "New Temple Address, Kandy",
                "bic_stay_history": [
                    {
                        "temple_name": "Malwatta Maha Viharaya",
                        "temple_address": "Kandy, Sri Lanka",
                        "from_date": "2005-07-10",
                        "to_date": "2020-12-31"
                    },
                    {
                        "temple_name": "Asgiriya Maha Viharaya",
                        "temple_address": "Kandy, Sri Lanka",
                        "from_date": "2021-01-01",
                        "to_date": None
                    }
                ]
            }
        }


# --- Response Schema ---
class BhikkuIDCardResponse(BhikkuIDCardBase):
    """
    Schema for returning Bhikku ID Card data.
    Includes all fields including auto-generated and audit fields.
    """
    bic_id: int
    bic_br_regn: str
    bic_form_no: str
    
    # File paths
    bic_left_thumbprint_url: Optional[str] = None
    bic_applicant_photo_url: Optional[str] = None
    bic_signature_url: Optional[bool] = None
    bic_authorized_signature_url: Optional[bool] = None
    
    # Workflow fields
    bic_workflow_status: str
    bic_approved_by: Optional[str] = None
    bic_approved_at: Optional[datetime] = None
    bic_rejected_by: Optional[str] = None
    bic_rejected_at: Optional[datetime] = None
    bic_rejection_reason: Optional[str] = None
    bic_printed_by: Optional[str] = None
    bic_printed_at: Optional[datetime] = None
    bic_completed_by: Optional[str] = None
    bic_completed_at: Optional[datetime] = None
    
    # Audit fields
    bic_is_deleted: bool
    bic_created_at: datetime
    bic_updated_at: datetime
    bic_created_by: Optional[str] = None
    bic_updated_by: Optional[str] = None
    bic_version_number: int
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "bic_id": 1,
                "bic_br_regn": "BH202500001",
                "bic_form_no": "FORM-2025-0001",
                "bic_divisional_secretariat": "Kandy",
                "bic_district": "Kandy",
                "bic_full_bhikku_name": "Ven. Mahanama Thero",
                "bic_title_post": "Chief Incumbent",
                "bic_lay_name_full": "Karunaratne Mudiyanselage Somapala",
                "bic_dob": "1985-05-15",
                "bic_birth_place": "Colombo",
                "bic_robing_date": "2005-07-10",
                "bic_robing_place": "Malwatta Maha Viharaya",
                "bic_robing_nikaya": "Siam",
                "bic_robing_parshawaya": "Malwatta",
                "bic_samanera_reg_no": "SAM2005001",
                "bic_upasampada_reg_no": "UPA2010001",
                "bic_higher_ord_date": "2010-06-20",
                "bic_higher_ord_name": "Mahanama",
                "bic_perm_residence": "Malwatta Maha Viharaya, Kandy",
                "bic_national_id": "850152345V",
                "bic_stay_history": [],
                "bic_left_thumbprint_url": "/storage/2025/11/15/BH202500001/left_thumbprint.jpg",
                "bic_applicant_photo_url": "/storage/2025/11/15/BH202500001/applicant_photo.jpg",
                "bic_workflow_status": "PENDING",
                "bic_is_deleted": False,
                "bic_created_at": "2025-11-15T10:30:00",
                "bic_updated_at": "2025-11-15T10:30:00",
                "bic_version_number": 1
            }
        }


# --- Manage Request Schema ---
class BhikkuIDCardManageRequest(BaseModel):
    """
    Schema for the /manage endpoint.
    The action field determines which operation to perform.
    """
    action: BhikkuIDCardAction = Field(..., description="The CRUD action to perform")
    
    # For READ_ONE, UPDATE, DELETE, APPROVE, REJECT, MARK_PRINTED
    bic_id: Optional[int] = Field(None, description="ID of the Bhikku ID Card (required for READ_ONE, UPDATE, DELETE, etc.)")
    bic_br_regn: Optional[str] = Field(None, description="Bhikku registration number (alternative to bic_id for lookups)")
    
    # For CREATE
    data: Optional[BhikkuIDCardCreate] = Field(None, description="Data for CREATE action")
    
    # For UPDATE
    update_data: Optional[BhikkuIDCardUpdate] = Field(None, description="Data for UPDATE action")
    
    # For REJECT
    rejection_reason: Optional[str] = Field(None, description="Reason for rejection (required for REJECT action)")
    
    # For READ_ALL (pagination)
    skip: Optional[int] = Field(0, ge=0, description="Number of records to skip")
    limit: Optional[int] = Field(100, ge=1, le=1000, description="Maximum number of records to return")
    
    # For READ_ALL (filtering)
    workflow_status: Optional[BhikkuIDCardWorkflowStatus] = Field(None, description="Filter by workflow status")
    search_key: Optional[str] = Field(None, description="Search across multiple fields")
    
    class Config:
        json_schema_extra = {
            "example": {
                "action": "CREATE",
                "data": {
                    "bic_br_regn": "BH202500001",
                    "bic_full_bhikku_name": "Ven. Mahanama Thero",
                    "bic_lay_name_full": "Karunaratne Mudiyanselage Somapala",
                    "bic_dob": "1985-05-15"
                }
            }
        }


# --- Manage Response Schema ---
class BhikkuIDCardManageResponse(BaseModel):
    """Standard response wrapper for /manage endpoint"""
    status: str = Field(..., description="Response status: success or error")
    message: str = Field(..., description="Human-readable message")
    data: Optional[Any] = Field(None, description="Response data (single record, list, or None)")
    total: Optional[int] = Field(None, description="Total count for READ_ALL")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Bhikku ID Card created successfully",
                "data": {
                    "bic_id": 1,
                    "bic_br_regn": "BH202500001",
                    "bic_form_no": "FORM-2025-0001",
                    "bic_workflow_status": "PENDING"
                }
            }
        }


# --- Workflow Action Types ---
class BhikkuIDCardWorkflowActionType(str, Enum):
    """Workflow actions available for Bhikku ID Card records"""
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    MARK_PRINTING_COMPLETE = "MARK_PRINTING_COMPLETE"
    MARK_COMPLETED = "MARK_COMPLETED"


# --- Workflow Request/Response Schemas ---
class BhikkuIDCardWorkflowRequest(BaseModel):
    """Request to update workflow status of a Bhikku ID Card record"""
    bic_id: Optional[int] = Field(None, description="Bhikku ID Card ID")
    bic_form_no: Optional[str] = Field(None, description="Bhikku ID Card form number")
    action: BhikkuIDCardWorkflowActionType
    rejection_reason: Optional[str] = Field(None, max_length=500, description="Required when action is REJECT")
    
    class Config:
        json_schema_extra = {
            "example": {
                "bic_form_no": "FORM-2025-0001",
                "action": "APPROVE"
            }
        }


class BhikkuIDCardWorkflowResponse(BaseModel):
    """Response after workflow action"""
    status: str
    message: str
    data: Optional[BhikkuIDCardResponse] = None
    
    class Config:
        from_attributes = True
