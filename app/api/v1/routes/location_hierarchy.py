from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas.gramasewaka import GramasewakaOut
from app.schemas.location import (
    DivisionalGramasewakaResponse,
    LocationHierarchyResponse,
)
from app.services.location_service import location_service
from app.services.gramasewaka_service import gramasewaka_service

router = APIRouter(tags=["Location Hierarchy"])


@router.get("/hierarchy", response_model=LocationHierarchyResponse)
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
