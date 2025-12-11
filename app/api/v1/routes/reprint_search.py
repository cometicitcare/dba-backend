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
    ReprintDetailRequest,
    ReprintSearchResponse,
    ReprintDetailResponse,
    ReprintSearchResultItem,
    QRStyleDetailItem
)
from app.services.reprint_search_service import reprint_search_service

router = APIRouter(prefix="/advance-search", tags=["🔎 Advance Search"])


def detect_entity_type(registration_id: str) -> str:
    """
    Detect entity type from registration number prefix.
    
    Prefix mapping:
    - BH -> bhikku
    - SIL -> silmatha
    - UPS -> high_bhikku
    - DBH -> direct_high_bhikku
    - TRN -> vihara
    - ARN -> arama
    - DVL -> devala
    """
    prefix = registration_id[:3].upper()
    
    prefix_map = {
        "BH": "bhikku",
        "SIL": "silmatha",
        "UPS": "high_bhikku",
        "DBH": "direct_high_bhikku",
        "TRN": "vihara",
        "ARN": "arama",
        "DVL": "devala"
    }
    
    # Try 3-letter prefix first
    if prefix in prefix_map:
        return prefix_map[prefix]
    
    # Try 2-letter prefix for BH
    prefix_2 = registration_id[:2].upper()
    if prefix_2 == "BH":
        return "bhikku"
    
    raise ValueError(f"Unable to determine entity type from registration ID: {registration_id}")


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


@router.post("", response_model=ReprintSearchResponse)
def search_all_records_post(
    request: ReprintSearchRequest,
    db: Session = Depends(get_db),
):
    """
    **Advance search across all entity types for reprint purposes (POST version).**
    
    This unified endpoint searches through:
    - **Bhikku** (Monk registrations)
    - **Silmatha** (Nun registrations)  
    - **High Bhikku** (Higher ordination records)
    - **Direct High Bhikku** (Direct higher ordination records)
    - **Vihara** (Temple registrations)
    - **Arama** (Hermitage/Nunnery registrations)
    - **Devala** (Shrine registrations)
    
    **Request Body:**
    ```json
    {
      "registration_number": "BH2025",
      "name": "John",
      "birth_date": "1990-01-15",
      "entity_type": "bhikku",
      "skip": 0,
      "limit": 50
    }
    ```
    
    **All fields are optional.**
    
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
            registration_number=request.registration_number,
            name=request.name,
            birth_date=request.birth_date,
            entity_type=request.entity_type,
            skip=request.skip,
            limit=request.limit
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


@router.post("/detail", response_model=ReprintDetailResponse)
def get_record_details_by_id(
    request: ReprintDetailRequest,
    db: Session = Depends(get_db),
):
    """
    **Get detailed information for a specific record by ID (auto-detects entity type).**
    
    This endpoint automatically identifies the entity type from the registration number prefix
    and retrieves comprehensive details in QR-style format.
    
    **Prefix Mapping:**
    - **BH** → Bhikku (e.g., BH2025000175)
    - **SIL** → Silmatha (e.g., SIL2025000002)
    - **UPS** → High Bhikku (e.g., UPS2025025)
    - **DBH** → Direct High Bhikku (e.g., DBH2025009)
    - **TRN** → Vihara (e.g., TRN0000082)
    - **ARN** → Arama (e.g., ARN0000051)
    - **DVL** → Devala (e.g., DVL0000002)
    
    **Request Body:**
    ```json
    {
      "id": "UPS2025025"
    }
    ```
    
    **Returns:**
    - Detailed information in QR-style format
    - Field labels and values
    - All relevant information for the record
    
    **Use Cases:**
    - Display detailed record information
    - Verify details before reprint
    - Show comprehensive entity data
    """
    try:
        # Detect entity type from registration ID
        entity_type = detect_entity_type(request.id)
        
        # Get record details
        details = reprint_search_service.get_entity_detail(
            db=db,
            entity_type=entity_type,
            registration_number=request.id
        )
        
        if not details:
            raise HTTPException(
                status_code=404,
                detail=f"No {entity_type} record found with registration number: {request.id}"
            )
        
        return ReprintDetailResponse(
            status="success",
            message="Record details retrieved successfully",
            entity_type=entity_type,
            data=details
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving record details: {str(e)}"
        )
