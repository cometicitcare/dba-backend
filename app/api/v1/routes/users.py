from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.api.auth_middleware import get_current_user
from app.models.user import UserAccount
from app.schemas.users import UserCreate, UserOut
from app.services.user_service import user_service


router = APIRouter()


@router.post("/", response_model=UserOut)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = user_service.create_user(
        db,
        user_id=payload.ua_user_id,
        username=payload.ua_username,
        email=payload.ua_email,
        password=payload.password,
    )
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=dict)
def me(current_user: UserAccount = Depends(get_current_user)):
    return {"user_id": current_user.ua_user_id, "username": current_user.ua_username}