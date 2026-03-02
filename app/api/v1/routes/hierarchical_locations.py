"""
Hierarchical Location API Routes
Provides endpoints for smart cascading location filters
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.hierarchical_location_service import HierarchicalLocationService
from app.utils.auth import verify_token


router = APIRouter(prefix="/api/v1/locations", tags=["locations"])
location_service = HierarchicalLocationService()


@router.get("/provinces")
def get_provinces(
    db: Session = Depends(get_db),
    current_user = Depends(verify_token),
):
    """
    Get all provinces
    
    Returns:
        - List of provinces with code and names
    """
    try:
        provinces = location_service.get_all_provinces(db)
        return {
            "status": "success",
            "data": provinces,
            "count": len(provinces)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving provinces: {str(e)}"
        )


@router.get("/districts")
def get_districts(
    province: str = Query(..., description="Province code (e.g., WP, CP)"),
    db: Session = Depends(get_db),
    current_user = Depends(verify_token),
):
    """
    Get districts in a specific province
    
    Query Parameters:
        - province: Province code (e.g., "WP" for Western Province)
    
    Returns:
        - List of districts in the province with code and names
    """
    try:
        districts = location_service.get_districts_by_province(db, province)
        if not districts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No districts found for province: {province}"
            )
        return {
            "status": "success",
            "province": province,
            "data": districts,
            "count": len(districts)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving districts: {str(e)}"
        )


@router.get("/divisional-secretariats")
def get_divisional_secretariats(
    district: str = Query(..., description="District code (e.g., DC001)"),
    db: Session = Depends(get_db),
    current_user = Depends(verify_token),
):
    """
    Get divisional secretariats in a specific district
    
    Query Parameters:
        - district: District code (e.g., "DC001" for Colombo)
    
    Returns:
        - List of divisional secretariats with code and names
    """
    try:
        dvsecs = location_service.get_divisional_secretariats_by_district(db, district)
        if not dvsecs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No divisional secretariats found for district: {district}"
            )
        return {
            "status": "success",
            "district": district,
            "data": dvsecs,
            "count": len(dvsecs)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving divisional secretariats: {str(e)}"
        )


@router.get("/gn-divisions")
def get_gn_divisions(
    divisional_secretariat: str = Query(..., description="Divisional Secretariat code (e.g., DV0001)"),
    db: Session = Depends(get_db),
    current_user = Depends(verify_token),
):
    """
    Get GN divisions under a specific divisional secretariat
    
    Query Parameters:
        - divisional_secretariat: Divisional Secretariat code (e.g., "DV0001")
    
    Returns:
        - List of GN divisions with code and names
    """
    try:
        gn_divs = location_service.get_gn_divisions_by_divisional_secretariat(
            db, divisional_secretariat
        )
        if not gn_divs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No GN divisions found for divisional secretariat: {divisional_secretariat}"
            )
        return {
            "status": "success",
            "divisional_secretariat": divisional_secretariat,
            "data": gn_divs,
            "count": len(gn_divs)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving GN divisions: {str(e)}"
        )


@router.get("/ssbm")
def get_ssbm(
    divisional_secretariat: str = Query(..., description="Divisional Secretariat code (e.g., DV0001)"),
    db: Session = Depends(get_db),
    current_user = Depends(verify_token),
):
    """
    Get Sasanarakshaka Bala Mandala (SSBM) under a specific divisional secretariat
    
    Query Parameters:
        - divisional_secretariat: Divisional Secretariat code (e.g., "DV0001")
    
    Returns:
        - List of SSBM with code and names
    """
    try:
        ssbms = location_service.get_ssbm_by_divisional_secretariat(db, divisional_secretariat)
        if not ssbms:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No SSBM found for divisional secretariat: {divisional_secretariat}"
            )
        return {
            "status": "success",
            "divisional_secretariat": divisional_secretariat,
            "data": ssbms,
            "count": len(ssbms)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving SSBM: {str(e)}"
        )


@router.get("/hierarchy")
def get_complete_hierarchy(
    province: str = Query(None, description="Province code (optional)"),
    district: str = Query(None, description="District code (optional)"),
    divisional_secretariat: str = Query(None, description="Divisional Secretariat code (optional)"),
    db: Session = Depends(get_db),
    current_user = Depends(verify_token),
):
    """
    Get complete location hierarchy with smart cascading
    
    Query Parameters (all optional - provide parent selections for smart filtering):
        - province: Province code (e.g., "WP")
        - district: District code (e.g., "DC001")
        - divisional_secretariat: Divisional Secretariat code (e.g., "DV0001")
    
    Returns:
        - Complete location hierarchy:
          - provinces: All provinces
          - districts: Filtered by province if provided, otherwise all
          - divisional_secretariats: Filtered by district if provided
          - gn_divisions: Only if divisional_secretariat provided
          - ssbm: Only if divisional_secretariat provided
    
    Example:
        GET /api/v1/locations/hierarchy?province=WP&district=DC001
        → Returns all districts in WP, and divisional secretariats in DC001
        
        GET /api/v1/locations/hierarchy?divisional_secretariat=DV0001
        → Returns GN divisions and SSBM under DV0001
    """
    try:
        hierarchy = location_service.get_complete_hierarchy(
            db,
            province_code=province,
            district_code=district,
            divisional_secretariat_code=divisional_secretariat
        )
        return {
            "status": "success",
            "filters": {
                "province": province,
                "district": district,
                "divisional_secretariat": divisional_secretariat
            },
            "data": hierarchy,
            "counts": {
                "provinces": len(hierarchy["provinces"]),
                "districts": len(hierarchy["districts"]),
                "divisional_secretariats": len(hierarchy["divisional_secretariats"]),
                "gn_divisions": len(hierarchy["gn_divisions"]),
                "ssbm": len(hierarchy["ssbm"])
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving hierarchy: {str(e)}"
        )
