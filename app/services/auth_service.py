from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from jose import jwt, JWTError
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.models.user_accounts import UserAccount

class AuthService:
    async def authenticate(self, db: AsyncSession, username: str, password: str) -> tuple[str, str]:
        stmt = select(UserAccount).where(UserAccount.ua_username == username)
        res = await db.execute(stmt)
        user = res.scalar_one_or_none()
        if not user or not verify_password(password, user.ua_password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        access = create_access_token(user.ua_user_id)
        refresh = create_refresh_token(user.ua_user_id)
        return access, refresh

    def decode_token(self, token: str) -> str:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return str(payload.get("sub"))
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

auth_service = AuthService()
