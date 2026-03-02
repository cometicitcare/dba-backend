from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission, has_any_permission
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas.gramasewaka import GramasewakaOut
from app.schemas.location import (
    DivisionalGramasewakaResponse,
    LocationHierarchyResponse,
)
from app.services.location_service import location_service
from app.services.location_hierarchy_service import LocationHierarchyService
from app.services.gramasewaka_service import gramasewaka_service

router = APIRouter()  # Tags defined in router.py


@router.get("/hierarchy", response_model=LocationHierarchyResponse, dependencies=[has_permission("public:view")])
def get_location_hierarchy(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    hierarchy = location_service.get_location_hierarchy(db)
    return LocationHierarchyResponse(
        status="success",
        message="Location hierarchy retrieved successfully.",
        data=hierarchy,
    )


@router.get(
    "/divisional-secretariats/{dv_code}/gramasewaka",
    response_model=DivisionalGramasewakaResponse,
)
def list_gramasewaka_by_divisional_secretariat(
    dv_code: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    records = gramasewaka_service.list_by_divisional_secretariat(
        db, divisional_code=dv_code
    )
    return DivisionalGramasewakaResponse(
        status="success",
        message="Gramasewaka records retrieved successfully.",
        data=[GramasewakaOut.model_validate(item) for item in records],
    )


# Smart Cascading Filter Endpoints for Vihara Filters
# Users see names, but backend works with codes


@router.get("/cascading/full")
def get_full_hierarchy(db: Session = Depends(get_db)):
    """
    Get complete location hierarchy for cascading filters
    Used by frontend for Province → District → DV → GN/SBM filtering
    """
    try:
        hierarchy = LocationHierarchyService.get_full_hierarchy(db)
        return {
            "status": "success",
            "message": "Location hierarchy retrieved",
            "data": hierarchy
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching location hierarchy: {str(e)}"
        )


@router.get("/cascading/provinces")
def get_provinces(db: Session = Depends(get_db)):
    """Get all provinces with codes and names (user-friendly)"""
    try:
        provinces = LocationHierarchyService.get_provinces(db)
        return {
            "status": "success",
            "message": "Provinces retrieved",
            "data": provinces
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching provinces: {str(e)}"
        )


@router.get("/cascading/districts/{province_code}")
def get_districts_by_province(
    province_code: str,
    db: Session = Depends(get_db)
):
    """
    Get districts for a specific province
    Args: province_code (e.g., "WP", "CP")
    Returns: Districts with codes (e.g., DC001, DC003) and Sinhala/English names
    """
    try:
        districts = LocationHierarchyService.get_districts_by_province(db, province_code)
        if not districts:
            return {
                "status": "success",
                "message": f"No districts found for province {province_code}",
                "data": []
            }
        return {
            "status": "success",
            "message": f"Districts for {province_code} retrieved",
            "data": districts
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching districts: {str(e)}"
        )


@router.get("/cascading/divisional-secretariats/{district_code}")
def get_divisional_secretariats_by_district(
    district_code: str,
    db: Session = Depends(get_db)
):
    """
    Get divisional secretariats for a specific district
    Args: district_code (e.g., "DC001", "DC003")
    """
    try:
        dvs = LocationHierarchyService.get_divisional_secretariats_by_district(db, district_code)
        if not dvs:
            return {
                "status": "success",
                "message": f"No divisional secretariats found for district {district_code}",
                "data": []
            }
        return {
            "status": "success",
            "message": f"Divisional secretariats for {district_code} retrieved",
            "data": dvs
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching divisional secretariats: {str(e)}"
        )


@router.get("/cascading/gn-divisions/{divisional_secretariat_code}")
def get_gn_divisions_by_dv(
    divisional_secretariat_code: str,
    db: Session = Depends(get_db)
):
    """
    Get GN divisions for a specific divisional secretariat
    Args: divisional_secretariat_code (e.g., "DV0001")
    """
    try:
        gns = LocationHierarchyService.get_gn_divisions_by_divisional_secretariat(
            db, divisional_secretariat_code
        )
        if not gns:
            return {
                "status": "success",
                "message": f"No GN divisions found for {divisional_secretariat_code}",
                "data": []
            }
        return {
            "status": "success",
            "message": f"GN divisions for {divisional_secretariat_code} retrieved",
            "data": gns
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching GN divisions: {str(e)}"
        )


@router.get("/cascading/sasanarakshaka-bala-mandalas/{divisional_secretariat_code}")
def get_sbms_by_dv(
    divisional_secretariat_code: str,
    db: Session = Depends(get_db)
):
    """
    Get Sasanarakshaka Bala Mandalas for a specific divisional secretariat
    This allows filtering viharas by their administrative SBM level
    Args: divisional_secretariat_code (e.g., "DV0001")
    """
    try:
        sbms = LocationHierarchyService.get_sasanarakshaka_bala_mandalas_by_divisional_secretariat(
            db, divisional_secretariat_code
        )
        if not sbms:
            return {
                "status": "success",
                "message": f"No SBMs found for {divisional_secretariat_code}",
                "data": []
            }
        return {
            "status": "success",
            "message": f"SBMs for {divisional_secretariat_code} retrieved",
            "data": sbms
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching SBMs: {str(e)}"
        )


@router.get("/cascading/sasanarakshaka-bala-mandalas-by-district/{district_code}")
def get_sbms_by_district(
    district_code: str,
    db: Session = Depends(get_db)
):
    """
    Get all Sasanarakshaka Bala Mandalas for a district (all DVs combined)
    Args: district_code (e.g., "DC001")
    """
    try:
        sbms = LocationHierarchyService.get_sasanarakshaka_bala_mandalas_by_district(
            db, district_code
        )
        return {
            "status": "success",
            "message": f"SBMs for district {district_code} retrieved",
            "data": sbms
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching SBMs by district: {str(e)}"
        )
