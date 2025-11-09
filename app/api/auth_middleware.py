# app/api/auth_middleware.py
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional
from app.api.deps import get_db
from app.models.user import UserAccount
from app.services.auth_service import auth_service


def get_current_user(request: Request, db: Session = Depends(get_db)) -> UserAccount:
    """
    Dependency to get the current authenticated user from the access_token cookie.
    This function reads the JWT token from HTTP-only cookies (not from Authorization header).
    """
    # Read access token from cookie (not from Authorization header)
    token: Optional[str] = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please login to access this resource."
        )

    # Decode and validate the JWT token
    try:
        user_id = auth_service.decode_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token. Please login again."
        )

    # Fetch user from database
    user = db.query(UserAccount).filter(
        UserAccount.ua_user_id == user_id,
        UserAccount.ua_is_deleted == False,
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or has been deleted."
        )

    # Check if user account is active
    if user.ua_status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User account is {user.ua_status}. Please contact administrator."
        )

    return user


def get_optional_user(request: Request, db: Session = Depends(get_db)) -> Optional[UserAccount]:
    """
    Optional dependency to get the current user if authenticated.
    Returns None if not authenticated, useful for endpoints that work with or without auth.
    """
    token: Optional[str] = request.cookies.get("access_token")
    
    if not token:
        return None

    try:
        user_id = auth_service.decode_token(token)
        user = db.query(UserAccount).filter(
            UserAccount.ua_user_id == user_id,
            UserAccount.ua_is_deleted == False,
            UserAccount.ua_status == "active"
        ).first()
        return user
    except Exception:
        return None


def require_permission(resource: str, action: str):
    """
    Dependency factory that ensures the current user has the given resource/action permission.
    """

    def dependency(
        request: Request,
        db: Session = Depends(get_db),
        current_user: UserAccount = Depends(get_current_user),
    ) -> UserAccount:
        auth_service.require_permission(
            db=db,
            user_id=current_user.ua_user_id,
            resource=resource,
            action=action,
        )
        return current_user

    return dependency
