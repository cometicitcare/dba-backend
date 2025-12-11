# app/api/v1/routes/reprint_search.py
"""
Unified Advance Search API
Provides comprehensive search across all entity types for reprint purposes.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.api.deps import get_db
from app.schemas.reprint_search import (
    ReprintSearchRequest,
    ReprintSearchResponse,
    ReprintDetailResponse,
    ReprintSearchResultItem,
    QRStyleDetailItem
)
from app.services.reprint_search_service import reprint_search_service

router = APIRouter(prefix="/advance-search", tags=["🔎 Advance Search"])


@router.get("", response_model=ReprintSearchResponse)
def search_all_records(
    registration_number: Optional[str] = Query(None, description="Search by registration number (partial match)"),
    name: Optional[str] = Query(None, description="Search by ordained name or birth name (partial match)"),
    birth_date: Optional[date] = Query(None, description="Search by exact birth date (YYYY-MM-DD)"),
    entity_type: Optional[str] = Query(
        None,
        description="Filter by entity type",
        enum=["bhikku", "silmatha", "high_bhikku", "direct_high_bhikku", "vihara", "arama", "devala"]
    ),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
):
    """
    **Advance search across all entity types for reprint purposes.**
    
    This unified endpoint searches through:
    - **Bhikku** (Monk registrations)
    - **Silmatha** (Nun registrations)  
    - **High Bhikku** (Higher ordination records)
    - **Direct High Bhikku** (Direct higher ordination records)
    - **Vihara** (Temple registrations)
    - **Arama** (Hermitage/Nunnery registrations)
    - **Devala** (Shrine registrations)
    
    **Search Filters:**
    - Search by registration number (partial match)
    - Search by name - ordained name or birth name (partial match)
    - Search by exact birth date (applies to person records only)
    - Filter by specific entity type
    
    **Returns:**
    - Common summary data for all matching records
    - Entity type identification
    - Registration numbers, names, dates
    - Temple/location information
    - Contact details
    - Workflow status
    
    **Use Cases:**
    - Find all records for a specific person by birth date
    - Search for reprints across all entity types
    - Get quick overview of registration details
    """
    try:
        results, total = reprint_search_service.search_all_entities(
            db=db,
            registration_number=registration_number,
            name=name,
            birth_date=birth_date,
            entity_type=entity_type,
            skip=skip,
            limit=limit
        )
        
        return ReprintSearchResponse(
            status="success",
            message=f"Found {total} matching record(s)",
            total=total,
            data=results
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching records: {str(e)}"
        )


@router.get("/{entity_type}/{registration_number}", response_model=ReprintDetailResponse)
def get_record_details(
    entity_type: str = Path(
        ...,
        description="Entity type",
    ),
    registration_number: str = Path(..., description="Registration number or TRN"),
    db: Session = Depends(get_db),
):
    """
    **Get detailed information for a specific record in QR-style format.**
    
    This endpoint retrieves comprehensive details for a single entity,
    formatted similarly to QR search results.
    
    **Path Parameters:**
    - `entity_type`: Type of entity (bhikku, silmatha, high_bhikku, direct_high_bhikku, vihara, arama, devala)
    - `registration_number`: Registration number (br_regn, sil_regn, vh_trn, etc.)
    
    **Returns:**
    - Detailed information in QR-style format
    - Field labels and values
    - All relevant information for the record
    
    **Use Cases:**
    - Display detailed record information
    - Verify details before reprint
    - Show comprehensive entity data
    """
    # Validate entity_type
    valid_types = ["bhikku", "silmatha", "high_bhikku", "direct_high_bhikku", "vihara", "arama", "devala"]
    if entity_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid entity_type. Must be one of: {', '.join(valid_types)}"
        )
    
    try:
        details = reprint_search_service.get_entity_detail(
            db=db,
            entity_type=entity_type,
            registration_number=registration_number
        )
        
        if not details:
            raise HTTPException(
                status_code=404,
                detail=f"No {entity_type} record found with registration number: {registration_number}"
            )
        
        return ReprintDetailResponse(
            status="success",
            message="Record details retrieved successfully",
            entity_type=entity_type,
            data=details
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving record details: {str(e)}"
        )
