from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_password_hash
from app.repositories.user_repo import UserRepository


user_repo = UserRepository()


class UserService:
    async def create_user(self, db: AsyncSession, *, user_id: str, username: str, email: str, password: str):
        return await user_repo.create(
        db,
        {
        "ua_user_id": user_id,
        "ua_username": username,
        "ua_email": email,
        "ua_password_hash": get_password_hash(password),
        "ua_salt": "", # optional if you want separate salt storage
        },
    )


user_service = UserService()