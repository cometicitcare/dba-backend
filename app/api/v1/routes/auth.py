# app/api/v1/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, LoginResponse
from app.repositories import auth_repo
from app.core.security import verify_password, generate_session_id

from datetime import datetime

router = APIRouter()


@router.get("/roles")
def get_roles(db: Session = Depends(get_db)):
    """Get all available roles"""
    roles = auth_repo.get_all_roles(db)
    return {"roles": roles}


@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user with role assignment"""
    # Check if username already exists
    db_user = auth_repo.get_user_by_username(db, username=user.ua_username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    # Check if email already exists
    existing_email = db.query(auth_repo.UserAccount).filter(
        auth_repo.UserAccount.ua_email == user.ua_email,
        auth_repo.UserAccount.ua_is_deleted == False
    ).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Validate role exists
    role = auth_repo.get_role_by_id(db, user.ro_role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role ID: {user.ro_role_id}. Please use one of the available roles.",
        )
    
    try:
        created_user = auth_repo.create_user(db=db, user=user)
        return created_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=LoginResponse)
def login(
    request: Request,
    form_data: UserLogin,
    db: Session = Depends(get_db),
):
    """Login user and return session with role information"""
    user = auth_repo.get_user_by_username(db, username=form_data.ua_username)
    
    if not user or not verify_password(
        form_data.ua_password + user.ua_salt, user.ua_password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if user.ua_status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active",
        )
    
    # Check if account is locked
    if user.ua_locked_until and user.ua_locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is locked. Please try again later.",
        )

    session_id = generate_session_id(user.ua_username)
    
    # Create login history
    auth_repo.create_login_history(
        db,
        user_id=user.ua_user_id,
        session_id=session_id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        success=True,
    )
    
    # Update last login
    auth_repo.update_user_last_login(db, user_id=user.ua_user_id)

    return {
        "session_id": session_id,
        "user": user
    }


@router.post("/logout")
def logout(session_id: str, db: Session = Depends(get_db)):
    """Logout user by ending session"""
    db_login_history = auth_repo.get_login_history_by_session_id(db, session_id)
    if not db_login_history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Active session not found"
        )

    auth_repo.update_logout_time(db, session_id)
    return {"message": "Logout successful"}


