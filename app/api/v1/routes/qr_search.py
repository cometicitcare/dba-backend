# app/api/v1/routes/qr_search.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas import bhikku as schemas
from app.services.bhikku_service import bhikku_service

router = APIRouter(prefix="/qr_search", tags=["QR Search"])


@router.post("", response_model=schemas.QRSearchResponseWrapper)
def qr_search(
    request: schemas.QRSearchRequest,
    db: Session = Depends(get_db),
):
    """
    Get limited details via QR code search.
    This endpoint does not require authentication.
    
    Supports Bhikku, Silmatha, and High Bhikku records.
    Automatically detects record type if not specified.
    
    Returns limited information:
    - Name (ordained name)
    - Birth name
    - Date of birth
    - Contact number
    - Email
    - Live location (temple)
    - Current status
    - Category
    - Ordination date
    """
    result = bhikku_service.get_qr_search_details(
        db=db,
        record_id=request.id,
        record_type=request.record_type
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"No record found with ID: {request.id}"
        )

    return {
        "status": "success",
        "message": "Record details retrieved successfully.",
        "data": result,
    }
