from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_user_id
from app.schemas.users import UserCreate, UserOut
from app.services.user_service import user_service


router = APIRouter()


@router.post("/", response_model=UserOut)
async def create_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await user_service.create_user(
        db,
        user_id=payload.ua_user_id,
        username=payload.ua_username,
        email=payload.ua_email,
        password=payload.password,
    )
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/me", response_model=dict)
async def me(current_user_id: str = Depends(get_current_user_id)):
    return {"user_id": current_user_id}