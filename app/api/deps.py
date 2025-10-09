from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.services.auth_service import auth_service


reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db() -> AsyncSession:
    async for s in get_session():
        yield s


async def get_current_user_id(token: str = Depends(reusable_oauth2)) -> str:
    return auth_service.decode_token(token)