from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission, has_any_permission
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas.silmatha_id import SilmathaIDCardResponse
from app.services.silmatha_id_service import silmatha_id_service

router = APIRouter()  # Tags defined in router.py


@router.get("/{regn}", response_model=SilmathaIDCardResponse, dependencies=[has_permission("silmatha:read")])
def get_silmatha_id_card(
    regn: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    try:
        card_data = silmatha_id_service.get_id_card_details(db, regn=regn)
    except ValueError as exc:
        message = str(exc)
        lowered = message.lower()
        if "not found" in lowered:
            status_code = 404
        elif "silmatha" in lowered:
            status_code = 400
        else:
            status_code = 400
        raise HTTPException(status_code=status_code, detail=message) from exc

    return {
        "status": "success",
        "message": "Silmatha ID card data retrieved successfully.",
        "data": card_data,
    }

