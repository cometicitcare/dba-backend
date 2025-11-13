# app/api/v1/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.repositories import auth_repo
from app.core.security import create_access_token
from app.services.auth_service import auth_service
from app.utils.cookies import set_auth_cookies, clear_auth_cookies
from app.utils.http_exceptions import validation_error
from app.core.config import settings

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
        raise validation_error(
            [("ua_username", "Username already registered")]
        )
    
    # Check if email already exists
    existing_email = db.query(auth_repo.UserAccount).filter(
        auth_repo.UserAccount.ua_email == user.ua_email,
        auth_repo.UserAccount.ua_is_deleted == False
    ).first()
    if existing_email:
        raise validation_error(
            [("ua_email", "Email already registered")]
        )
    
    # Validate role exists
    role = auth_repo.get_role_by_id(db, user.ro_role_id)
    if not role:
        raise validation_error(
            [
                (
                    "ro_role_id",
                    f"Invalid role ID: {user.ro_role_id}. Please use one of the available roles.",
                )
            ]
        )
    
    try:
        created_user = auth_repo.create_user(db=db, user=user)
        return created_user
    except ValueError as e:
        raise validation_error([(None, str(e))])


# @router.post("/login")
# def login(
#     request: Request,
#     form_data: UserLogin,
#     db: Session = Depends(get_db),
# ):
#     """Login user, set http-only cookies with access/refresh tokens, and return user info"""
#     access, refresh, user = auth_service.authenticate(db, form_data.ua_username, form_data.ua_password)

#     # Create login history for observability (store token hash if needed, but skip here)
#     auth_repo.create_login_history(
#         db,
#         user_id=user.ua_user_id,
#         session_id=f"login-{user.ua_user_id}",
#         ip_address=request.client.host if request.client else None,
#         user_agent=request.headers.get("user-agent"),
#         success=True,
#     )
#     auth_repo.update_user_last_login(db, user_id=user.ua_user_id)
#     user_payload = UserResponse.model_validate(user, from_attributes=True).model_dump()

#     response = JSONResponse(content={"user": user_payload})
#     set_auth_cookies(response, access_token=access, refresh_token=refresh)
#     return response

@router.post("/login")
def login(
    request: Request,
    form_data: UserLogin,
    db: Session = Depends(get_db),
):
    """Login user, set http-only cookies with access/refresh tokens, and return user info"""
    # Authenticate the user
    access, refresh, user = auth_service.authenticate(db, form_data.ua_username, form_data.ua_password)

    # Fetch user's role and group
    user_role = db.query(auth_repo.Role).join(auth_repo.UserRole).filter(auth_repo.UserRole.user_id == user.ua_user_id).first()
    user_group = db.query(auth_repo.Group).join(auth_repo.UserGroup).filter(auth_repo.UserGroup.user_id == user.ua_user_id).first()

    if not user_role or not user_group:
        raise HTTPException(status_code=404, detail="User role or group not found")

    # Create login history for observability
    auth_repo.create_login_history(
        db,
        user_id=user.ua_user_id,
        session_id=f"login-{user.ua_user_id}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        success=True,
    )
    
    # Update user's last login time
    auth_repo.update_user_last_login(db, user_id=user.ua_user_id)

    # Create the JWT token with role and group info
    user_payload = UserResponse.model_validate(user, from_attributes=True).model_dump()
    user_payload["role"] = user_role.ro_role_name if user_role else None
    user_payload["group"] = user_group.group_name if user_group else None

    # Create access and refresh tokens
    response = JSONResponse(content={"user": user_payload})
    set_auth_cookies(response, access_token=access, refresh_token=refresh)
    
    return response

@router.post("/logout")
def logout(db: Session = Depends(get_db)):
    """Logout user by clearing auth cookies"""
    response = JSONResponse(content={"message": "Logout successful"})
    clear_auth_cookies(response)
    return response


@router.post("/refresh")
def refresh_token(request: Request, db: Session = Depends(get_db)):
    """Refresh access token using refresh token from cookie"""
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")
    
    try:
        user_id = auth_service.decode_token(refresh_token)
        user = db.query(auth_repo.UserAccount).filter(
            auth_repo.UserAccount.ua_user_id == user_id,
            auth_repo.UserAccount.ua_is_deleted == False
        ).first()
        
        if not user or user.ua_status != "active":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        
        new_access = create_access_token(user.ua_user_id)
        response = JSONResponse(content={"message": "Token refreshed"})
        response.set_cookie(
            key="access_token",
            value=new_access,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            domain=settings.COOKIE_DOMAIN,
            path=settings.COOKIE_PATH,
        )
        return response
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
