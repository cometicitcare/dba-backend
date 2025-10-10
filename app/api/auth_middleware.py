from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional
from app.api.deps import get_db
from app.repositories import auth_repo
from app.models.user import UserAccount
from app.services.auth_service import auth_service


def get_current_user(request: Request, db: Session = Depends(get_db)) -> UserAccount:
    """
    Dependency to get the current authenticated user from the access_token cookie.
    """
    token: Optional[str] = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    user_id = auth_service.decode_token(token)

    user = db.query(UserAccount).filter(
        UserAccount.ua_user_id == user_id,
        UserAccount.ua_is_deleted == False,
    ).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    if user.ua_status != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User account is {user.ua_status}.")

    return user