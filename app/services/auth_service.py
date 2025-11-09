from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from jose import JWTError
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.models.user import UserAccount
from app.core.config import settings

class AuthService:
    def authenticate(self, db: Session, username: str, password: str) -> tuple[str, str, UserAccount]:
        user = db.query(UserAccount).filter(
            UserAccount.ua_username == username,
            UserAccount.ua_is_deleted == False,
        ).first()
        # Passwords are stored as hash(plain_password + ua_salt)
        if not user or not verify_password(password + user.ua_salt, user.ua_password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        access = create_access_token(user.ua_user_id)
        refresh = create_refresh_token(user.ua_user_id)
        return access, refresh, user

    def decode_token(self, token: str) -> str:
        try:
            from jose import jwt
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return str(payload.get("sub"))
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

auth_service = AuthService()
