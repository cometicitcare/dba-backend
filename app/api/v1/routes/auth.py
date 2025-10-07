# app/api/v1/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.user import UserCreate, UserLogin
from app.repositories import auth_repo
from app.core.security import verify_password, generate_session_id

router = APIRouter()


@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = auth_repo.get_user_by_username(db, username=user.ua_username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    return auth_repo.create_user(db=db, user=user)


@router.post("/login")
def login(
    request: Request,
    form_data: UserLogin,
    db: Session = Depends(get_db),
):
    user = auth_repo.get_user_by_username(db, username=form_data.ua_username)
    if not user or not verify_password(
        form_data.ua_password + user.ua_salt, user.ua_password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    session_id = generate_session_id(user.ua_username)
    auth_repo.create_login_history(
        db,
        user_id=user.ua_id,
        session_id=session_id,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        success=True,
    )
    auth_repo.update_user_last_login(db, user_id=user.ua_id)

    return {"session_id": session_id}


@router.post("/logout")
def logout(session_id: str, db: Session = Depends(get_db)):
    db_login_history = auth_repo.get_login_history_by_session_id(db, session_id)
    if not db_login_history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Active session not found"
        )

    auth_repo.update_logout_time(db, session_id)
    return {"message": "Logout successful"}