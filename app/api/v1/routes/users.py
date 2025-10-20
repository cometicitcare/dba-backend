from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas.users import UserCreate, UserOut
from app.services.user_service import user_service

router = APIRouter()


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    try:
        return user_service.create_user(db, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get("/me", response_model=dict)
def me(current_user: UserAccount = Depends(get_current_user)):
    return {
        "user_id": current_user.ua_user_id,
        "username": current_user.ua_username,
    }
