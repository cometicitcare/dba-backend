# app/schemas/reprint_search.py
"""
Schema definitions for the unified reprint search endpoint.
This endpoint searches across all entity types for reprint purposes.
"""
from datetime import date, datetime
from typing import Optional, List, Literal
from pydantic import BaseModel


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class ReprintSearchRequest(BaseModel):
    """Request schema for unified reprint search"""
    # Optional filters
    registration_number: Optional[str] = None
    name: Optional[str] = None  # Searches ordained name or birth name
    birth_date: Optional[date] = None
    entity_type: Optional[Literal["bhikku", "silmatha", "high_bhikku", "direct_high_bhikku", "vihara", "arama", "devala"]] = None
    
    # Pagination
    skip: int = 0
    limit: int = 50
    
    class Config:
        json_schema_extra = {
            "example": {
                "birth_date": "1990-01-15",
                "entity_type": "bhikku",
                "skip": 0,
                "limit": 50
            }
        }


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class ReprintSearchResultItem(BaseModel):
    """Individual search result item with common summary data"""
    entity_type: str  # "bhikku", "silmatha", "high_bhikku", etc.
    registration_number: str
    form_id: Optional[str] = None
    
    # Names
    ordained_name: Optional[str] = None  # Mahana name / Silmatha name
    birth_name: Optional[str] = None  # Gihi name
    
    # Basic info
    date_of_birth: Optional[date] = None
    birth_place: Optional[str] = None
    
    # Contact
    mobile: Optional[str] = None
    email: Optional[str] = None
    
    # Location/Temple info
    temple_name: Optional[str] = None  # Vihara/Arama name for residency
    temple_address: Optional[str] = None
    
    # Status info
    current_status: Optional[str] = None
    workflow_status: Optional[str] = None
    
    # Dates
    ordination_date: Optional[date] = None  # Mahana date
    request_date: Optional[date] = None
    
    class Config:
        from_attributes = True


class ReprintSearchResponse(BaseModel):
    """Response wrapper for search results"""
    status: str
    message: str
    total: int
    data: List[ReprintSearchResultItem]


# ============================================================================
# DETAILED ITEM SCHEMAS (for read-one endpoint)
# ============================================================================

class QRStyleDetailItem(BaseModel):
    """Individual detail field in QR style format"""
    titel: str
    text: Optional[str] = None


class ReprintDetailResponse(BaseModel):
    """Response for single record details (QR style)"""
    status: str
    message: str
    entity_type: str
    data: List[QRStyleDetailItem]
