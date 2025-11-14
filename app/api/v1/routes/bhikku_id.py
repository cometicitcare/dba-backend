from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission, has_any_permission
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas.bhikku_id import BhikkuIDCardResponse
from app.services.bhikku_id_service import bhikku_id_service

router = APIRouter(tags=["Bhikku ID"])


@router.get("/{regn}", response_model=BhikkuIDCardResponse, dependencies=[has_permission("bhikku:read")])
def get_bhikku_id_card(
    regn: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    try:
        card_data = bhikku_id_service.get_id_card_details(db, regn=regn)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise HTTPException(status_code=status_code, detail=message) from exc

    return {
        "status": "success",
        "message": "Bhikku ID card data retrieved successfully.",
        "data": card_data,
    }

