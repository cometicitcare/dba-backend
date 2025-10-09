from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional
from app.api.deps import get_db
from app.repositories import auth_repo
from app.models.user import UserAccount


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> UserAccount:
    """
    Dependency to get the current authenticated user from session ID.
    Expects Authorization header with format: "Bearer <session_id>"
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Authorization header missing.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract session ID from "Bearer <session_id>"
    try:
        scheme, session_id = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme. Use 'Bearer <session_id>'",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Use 'Bearer <session_id>'",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify session exists and is active
    login_history = auth_repo.get_login_history_by_session_id(db, session_id)
    if not login_history:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session. Please login again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get the user associated with this session
    user = db.query(UserAccount).filter(
        UserAccount.ua_user_id == login_history.lh_user_id
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if user.ua_status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User account is {user.ua_status}. Access denied.",
        )
    
    return user