# app/api/v1/routes/dashboard.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.auth_middleware import get_current_user
from app.models.user import UserAccount

router = APIRouter()  # Tags defined in router.py


class SessionStatusResponse(BaseModel):
    """Response model for session status"""
    success: bool
    message: str
    user: dict


@router.get("/session", response_model=SessionStatusResponse)
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

