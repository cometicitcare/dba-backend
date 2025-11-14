# app/api/v1/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
import logging

from app.api.deps import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.repositories import auth_repo
from app.core.security import create_access_token
from app.services.auth_service import auth_service
from app.utils.cookies import set_auth_cookies, clear_auth_cookies
from app.utils.http_exceptions import validation_error
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# ============================================================================
# REQUEST/RESPONSE MODELS FOR EMAIL ENDPOINTS
# ============================================================================


class ForgotPasswordRequest(BaseModel):
    """Request model for password reset initiation.

    Accepts an identifier which can be an email, username or phone number.
    """

    identifier: str = Field(..., description="Email, username, or phone number")


class ValidateOTPRequest(BaseModel):
    """Request model for OTP validation"""

    user_id: str = Field(..., description="User ID")
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit OTP")


class ResetPasswordRequest(BaseModel):
    """Request model for password reset completion"""

    user_id: str = Field(..., description="User ID")
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit OTP")
    new_password: str = Field(..., min_length=8, description="New password (min 8 characters)")
    confirm_password: str = Field(..., description="Password confirmation")


class RecoverUsernameRequest(BaseModel):
    """Request model for username recovery"""

    email: EmailStr = Field(..., description="Email address to recover username for")


class PasswordResetResponse(BaseModel):
    """Response model for password reset operations"""

    success: bool
    message: str
    user_id: str | None = None
    channels: dict | None = None
    masked: dict | None = None


class OTPStatusResponse(BaseModel):
    """Response model for OTP status"""

    has_otp: bool
    time_remaining_minutes: float
    attempts_remaining: int
    is_expired: bool


# ============================================================================
# STANDARD AUTH ENDPOINTS
# ============================================================================


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


# ============================================================================
# EMAIL & PASSWORD RECOVERY ENDPOINTS
# ============================================================================


@router.post(
    "/forgot-password",
    response_model=PasswordResetResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Initiate password reset request.
    
    Generates OTP and sends it via email to the user.
    Returns generic message for security (prevents email enumeration).
    
    **Endpoint**: `POST /api/v1/auth/forgot-password`
    
    **Request**:
    ```json
    {
        "email": "user@example.com"
    }
    ```
    
    **Response** (202 Accepted):
    ```json
    {
        "success": true,
        "message": "If an account exists with this email address, you will receive a password reset link shortly."
    }
    ```
    
    **Frontend URL**: `https://hrms.dbagovlk.com/auth/forgot-password`
    """
    try:
        # Use generic success message for safety; auth_service will return masked contact info
        success, _message, payload = auth_service.initiate_password_reset(db=db, identifier=request.identifier)

        logger.info(f"Password reset initiation requested for identifier: {request.identifier}")

        return PasswordResetResponse(
            success=True,
            message="If an account exists you'll receive an OTP",
            user_id=payload.get("user_id"),
            channels=payload.get("channels"),
            masked=payload.get("masked"),
        )

    except Exception as e:
        logger.error(f"Error in forgot password: {str(e)}")
        # Return generic message for security
        return PasswordResetResponse(
            success=True,
            message="If an account exists with this email address, you will receive a password reset link shortly.",
        )


@router.post(
    "/validate-otp",
    response_model=PasswordResetResponse,
    status_code=status.HTTP_200_OK,
)
async def validate_otp(request: ValidateOTPRequest, db: Session = Depends(get_db)):
    """
    Validate OTP for password reset.
    
    User enters the 6-digit OTP sent to their email.
    Max 3 attempts allowed.
    
    **Endpoint**: `POST /api/v1/auth/validate-otp`
    
    **Request**:
    ```json
    {
        "user_id": "USR001",
        "otp": "123456"
    }
    ```
    
    **Response** (200 OK):
    ```json
    {
        "success": true,
        "message": "OTP validated. You can now reset your password.",
        "user_id": "USR001"
    }
    ```
    
    **Error Response** (400 Bad Request):
    ```json
    {
        "success": false,
        "message": "Invalid OTP. You have 2 attempt(s) remaining."
    }
    ```
    
    **Frontend URL**: `https://hrms.dbagovlk.com/auth/reset-password`
    """
    try:
        is_valid, message = auth_service.validate_password_reset_otp(
            user_id=request.user_id,
            otp=request.otp
        )

        if not is_valid:
            logger.warning(f"OTP validation failed for user: {request.user_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message,
            )

        logger.info(f"OTP validated successfully for user: {request.user_id}")

        return PasswordResetResponse(
            success=True,
            message="OTP validated. You can now reset your password.",
            user_id=request.user_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating OTP: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during OTP validation",
        )


@router.post(
    "/reset-password",
    response_model=PasswordResetResponse,
    status_code=status.HTTP_200_OK,
)
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Complete password reset after OTP validation.
    
    User enters new password after successfully validating OTP.
    
    **Endpoint**: `POST /api/v1/auth/reset-password`
    
    **Request**:
    ```json
    {
        "user_id": "USR001",
        "otp": "123456",
        "new_password": "NewSecurePassword123!",
        "confirm_password": "NewSecurePassword123!"
    }
    ```
    
    **Response** (200 OK):
    ```json
    {
        "success": true,
        "message": "Password reset successful. You can now log in with your new password.",
        "user_id": "USR001"
    }
    ```
    
    **Validation Rules**:
    - Passwords must match
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one number
    
    **Frontend URL**: `https://hrms.dbagovlk.com/auth/reset-password`
    """
    try:
        # Validate passwords match
        if request.new_password != request.confirm_password:
            logger.warning(f"Password mismatch for user: {request.user_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match",
            )

        # Validate password requirements
        if len(request.new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long",
            )

        if not any(c.isupper() for c in request.new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one uppercase letter",
            )

        if not any(c.isdigit() for c in request.new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one number",
            )

        # Validate OTP first
        is_valid, message = auth_service.validate_password_reset_otp(
            user_id=request.user_id,
            otp=request.otp
        )

        if not is_valid:
            logger.warning(f"OTP validation failed for user: {request.user_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message,
            )

        # Update password
        success, result_msg = auth_service.complete_password_reset(
            db=db,
            user_id=request.user_id,
            new_password=request.new_password
        )

        if not success:
            logger.error(f"Failed to reset password for user: {request.user_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result_msg,
            )

        logger.info(f"Password reset completed successfully for user: {request.user_id}")

        return PasswordResetResponse(
            success=True,
            message="Password reset successful. You can now log in with your new password.",
            user_id=request.user_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password. Please try again.",
        )


@router.get(
    "/reset-status/{user_id}",
    response_model=OTPStatusResponse,
    status_code=status.HTTP_200_OK,
)
async def get_reset_status(user_id: str, db: Session = Depends(get_db)):
    """
    Get status of ongoing password reset for a user.
    
    Check how much time is remaining for OTP validation and remaining attempts.
    
    **Endpoint**: `GET /api/v1/auth/reset-status/{user_id}`
    
    **URL Parameters**:
    - `user_id` (string, required): User ID
    
    **Response** (200 OK):
    ```json
    {
        "has_otp": true,
        "time_remaining_minutes": 8.5,
        "attempts_remaining": 2,
        "is_expired": false
    }
    ```
    
    **Error Response** (404 Not Found):
    ```json
    {
        "detail": "No active reset request for this user"
    }
    ```
    
    **Frontend URL**: `https://hrms.dbagovlk.com/auth/reset-password`
    """
    try:
        from app.services.password_reset_service import password_reset_service

        status_data = password_reset_service.get_reset_status(user_id)

        if not status_data:
            logger.info(f"No active reset request for user: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active reset request for this user",
            )

        return OTPStatusResponse(**status_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting reset status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get reset status",
        )


@router.post(
    "/recover-username",
    response_model=PasswordResetResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def recover_username(request: RecoverUsernameRequest, db: Session = Depends(get_db)):
    """
    Recover username using email address.
    
    Searches for user by email and sends username recovery email.
    Returns generic message for security (prevents email enumeration).
    
    **Endpoint**: `POST /api/v1/auth/recover-username`
    
    **Request**:
    ```json
    {
        "email": "user@example.com"
    }
    ```
    
    **Response** (202 Accepted):
    ```json
    {
        "success": true,
        "message": "If an account exists with this email address, you will receive your username shortly."
    }
    ```
    
    **Frontend URL**: `https://hrms.dbagovlk.com/auth/recover-username`
    """
    try:
        success, message = auth_service.recover_username(
            db=db,
            email=request.email
        )

        logger.info(f"Username recovery requested for email: {request.email}")

        # Always return generic message for security
        return PasswordResetResponse(
            success=True,
            message="If an account exists with this email address, you will receive your username shortly.",
        )

    except Exception as e:
        logger.error(f"Error in username recovery: {str(e)}")
        # Still return generic message for security
        return PasswordResetResponse(
            success=True,
            message="If an account exists with this email address, you will receive your username shortly.",
        )
