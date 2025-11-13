from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.models.user import UserAccount
from app.models.roles import Role
from app.models.user_roles import UserRole
from app.models.user_group import UserGroup
from app.models.group import Group
from app.core.config import settings
from app.core.security import verify_password

class AuthService:
    def authenticate(self, db: Session, username: str, password: str) -> tuple[str, str, UserAccount]:
        user = db.query(UserAccount).filter(
            UserAccount.ua_username == username,
            UserAccount.ua_is_deleted == False,
        ).first()

        # Passwords are stored as hash(plain_password + ua_salt)
        if not user or not verify_password(password + user.ua_salt, user.ua_password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
        # Fetch the user's role and group information
        user_role = db.query(Role).join(UserRole).filter(UserRole.user_id == user.ua_user_id).first()
        user_group = db.query(Group).join(UserGroup).filter(UserGroup.user_id == user.ua_user_id).first()

        if not user_role or not user_group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User role or group not found")
        
        # Create access and refresh tokens with role and group included
        access = self.create_access_token(user.ua_user_id, user_role.ro_role_name, user_group.group_name)
        refresh = self.create_refresh_token(user.ua_user_id)

        return access, refresh, user

    def create_access_token(self, user_id: str, role: str, group: str, expires_delta: timedelta = timedelta(hours=1)) -> str:
        to_encode = {
            "sub": user_id,
            "role": role,
            "group": group,
            "exp": datetime.utcnow() + expires_delta
        }
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    def create_jwt_token(user_id: str, role: str, group: str):
        expiration = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        payload = {
            "sub": user_id,
            "role": role,
            "group": group,
            "exp": expiration
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return token

    def create_refresh_token(self, user_id: str, expires_delta: timedelta = timedelta(days=7)) -> str:
        to_encode = {
            "sub": user_id,
            "exp": datetime.utcnow() + expires_delta
        }
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    def decode_token(self, token: str) -> str:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return str(payload.get("sub"))
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# Create an instance of the AuthService
auth_service = AuthService()
