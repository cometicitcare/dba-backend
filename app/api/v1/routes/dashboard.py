# app/api/v1/routes/dashboard.py
from fastapi import APIRouter, Depends

from app.api.auth_middleware import get_current_user
from app.models.user import UserAccount

router = APIRouter()  # Tags defined in router.py


@router.get("/session")
def session_status(current_user: UserAccount = Depends(get_current_user)):
    """Return session status for authenticated users."""
    return {
        "success": True,
        "message": "Session active.",
        "user": {
            "user_id": current_user.ua_user_id,
            "username": current_user.ua_username,
        },
    }

