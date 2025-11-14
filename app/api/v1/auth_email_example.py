"""
Example API Routes for Email and Authentication Services

This file demonstrates how to integrate the email, password reset, 
and username recovery services into your FastAPI application.

USAGE:
1. Copy relevant endpoint implementations to your actual router
2. Update imports based on your project structure
3. Inject your user repository as a dependency
4. Update URL placeholders (login_url, support_url, etc.)

Do NOT import directly - use as reference only.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import logging

# These imports are examples - adjust based on your project
# from app.services.email_service import email_service
# from app.services.password_reset_service import password_reset_service
# from app.services.username_recovery_service import username_recovery_service
# from app.repositories.user_repo import user_repo
# from app.core.security import get_password_hash

logger = logging.getLogger(__name__)

# ============================================================================
# REQUEST/RESPONSE SCHEMAS
# ============================================================================


class ForgotPasswordRequest(BaseModel):
    """Request model for password reset initiation"""

    email: EmailStr = Field(..., description="User's email address")


class ValidateOTPRequest(BaseModel):
    """Request model for OTP validation"""

    user_id: int = Field(..., description="User ID")
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit OTP")


class ResetPasswordRequest(BaseModel):
    """Request model for password reset completion"""

    user_id: int = Field(..., description="User ID")
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit OTP")
    new_password: str = Field(
        ..., min_length=8, description="New password (min 8 characters)"
    )
    confirm_password: str = Field(..., description="Password confirmation")


class RecoverUsernameRequest(BaseModel):
    """Request model for username recovery"""

    email: EmailStr = Field(..., description="Email address to recover username for")


class PasswordResetResponse(BaseModel):
    """Response model for password reset operations"""

    success: bool
    message: str
    user_id: Optional[int] = None


class OTPStatusResponse(BaseModel):
    """Response model for OTP status"""

    has_otp: bool
    time_remaining_minutes: float
    attempts_remaining: int
    is_expired: bool


class NewUserRegistrationRequest(BaseModel):
    """Request model for new user registration"""

    email: EmailStr = Field(..., description="User's email")
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    username: str = Field(..., min_length=3, max_length=50)
    temporary_password: str = Field(..., description="Temporary password")


# ============================================================================
# EXAMPLE ROUTER SETUP
# ============================================================================


def create_auth_email_router(user_repo, auth_service, email_service):
    """
    Factory function to create auth+email router with dependencies.

    Usage in your main.py:
    ```python
    from app.api.v1.auth import create_auth_email_router
    from app.repositories.user_repo import user_repo
    from app.services.auth_service import auth_service
    from app.services.email_service import email_service

    router = create_auth_email_router(user_repo, auth_service, email_service)
    app.include_router(router)
    ```
    """

    router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])

    # ========================================================================
    # PASSWORD RESET ENDPOINTS
    # ========================================================================

    @router.post(
        "/forgot-password",
        response_model=PasswordResetResponse,
        status_code=status.HTTP_202_ACCEPTED,
    )
    async def forgot_password(request: ForgotPasswordRequest):
        """
        Initiate password reset request.

        Generates OTP and sends it via email.
        Returns generic message for security (prevents email enumeration).

        Args:
            request: ForgotPasswordRequest with user email

        Returns:
            PasswordResetResponse with success status
        """
        try:
            # Find user by email
            user = await user_repo.get_by_email(request.email)

            if user:
                # Initiate password reset (sends OTP email)
                from app.services.password_reset_service import password_reset_service

                success, message = password_reset_service.initiate_password_reset(
                    user_id=user.id,
                    user_email=user.email,
                    user_name=user.first_name or "User",
                )

                if not success:
                    logger.error(f"Failed to send reset email to {request.email}")

            # Always return generic message for security
            return PasswordResetResponse(
                success=True,
                message="If an account exists with this email address, "
                "you will receive a password reset link shortly.",
            )

        except Exception as e:
            logger.error(f"Error in forgot password: {str(e)}")
            # Still return generic message for security
            return PasswordResetResponse(
                success=True,
                message="If an account exists with this email address, "
                "you will receive a password reset link shortly.",
            )

    @router.post(
        "/validate-otp", response_model=PasswordResetResponse, status_code=status.HTTP_200_OK
    )
    async def validate_otp(request: ValidateOTPRequest):
        """
        Validate OTP for password reset.

        Args:
            request: ValidateOTPRequest with user_id and OTP

        Returns:
            PasswordResetResponse indicating validation result
        """
        from app.services.password_reset_service import password_reset_service

        is_valid, message = password_reset_service.validate_otp_for_reset(
            user_id=request.user_id, otp=request.otp
        )

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message,
            )

        return PasswordResetResponse(
            success=True, message="OTP validated. You can now reset your password."
        )

    @router.post(
        "/reset-password", response_model=PasswordResetResponse, status_code=status.HTTP_200_OK
    )
    async def reset_password(request: ResetPasswordRequest):
        """
        Complete password reset with OTP and new password.

        Args:
            request: ResetPasswordRequest with user_id, OTP, and new password

        Returns:
            PasswordResetResponse indicating success/failure
        """
        from app.services.password_reset_service import password_reset_service

        # Validate passwords match
        if request.new_password != request.confirm_password:
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

        # Validate OTP
        is_valid, message = password_reset_service.validate_otp_for_reset(
            user_id=request.user_id, otp=request.otp
        )

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message,
            )

        # Get user
        user = await user_repo.get_by_id(request.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # Update password
        try:
            # from app.core.security import get_password_hash
            hashed_password = get_password_hash(request.new_password)
            await user_repo.update(request.user_id, {"password": hashed_password})

            # Complete the reset flow
            success, msg = password_reset_service.complete_password_reset(
                user_id=request.user_id, new_password=request.new_password
            )

            logger.info(f"Password reset successful for user {request.user_id}")

            return PasswordResetResponse(
                success=True,
                message="Password reset successful. You can now log in with your new password.",
            )

        except Exception as e:
            logger.error(f"Error resetting password: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reset password. Please try again.",
            )

    @router.get(
        "/reset-status/{user_id}", response_model=OTPStatusResponse, status_code=status.HTTP_200_OK
    )
    async def get_reset_status(user_id: int):
        """
        Get status of ongoing password reset for a user.

        Args:
            user_id: User ID

        Returns:
            OTPStatusResponse with OTP status and timing info
        """
        from app.services.password_reset_service import password_reset_service

        status_data = password_reset_service.get_reset_status(user_id)

        if not status_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active reset request for this user",
            )

        return OTPStatusResponse(**status_data)

    # ========================================================================
    # USERNAME RECOVERY ENDPOINTS
    # ========================================================================

    @router.post(
        "/recover-username",
        response_model=PasswordResetResponse,
        status_code=status.HTTP_202_ACCEPTED,
    )
    async def recover_username(request: RecoverUsernameRequest):
        """
        Recover username using email address.

        Searches for user by email and sends username recovery email.
        Returns generic message for security (prevents email enumeration).

        Args:
            request: RecoverUsernameRequest with email

        Returns:
            PasswordResetResponse with generic success message
        """
        try:
            from app.services.username_recovery_service import username_recovery_service

            # Try to find user by email
            user = await user_repo.get_by_email(request.email)

            if user:
                # Send username recovery email
                user_data = {
                    "user_id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name or "User",
                    "last_name": user.last_name or "",
                    "status": user.status or "active",
                }

                success, message = username_recovery_service.recover_username_by_email(
                    email=request.email, user_data=user_data
                )

                logger.info(f"Username recovery email sent to {request.email}")

            # Always return generic message for security
            return PasswordResetResponse(
                success=True,
                message="If an account exists with this email address, "
                "you will receive your username shortly.",
            )

        except Exception as e:
            logger.error(f"Error in username recovery: {str(e)}")
            # Still return generic message for security
            return PasswordResetResponse(
                success=True,
                message="If an account exists with this email address, "
                "you will receive your username shortly.",
            )

    # ========================================================================
    # NEW USER REGISTRATION WITH EMAIL
    # ========================================================================

    @router.post(
        "/register-new-user",
        response_model=PasswordResetResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def register_new_user(request: NewUserRegistrationRequest):
        """
        Register new user and send welcome email.

        Args:
            request: NewUserRegistrationRequest with user details

        Returns:
            PasswordResetResponse indicating success/failure
        """
        try:
            # Check if user already exists
            existing_user = await user_repo.get_by_email(request.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User with this email already exists",
                )

            # Create new user
            new_user = await user_repo.create(
                {
                    "email": request.email,
                    "username": request.username,
                    "first_name": request.first_name,
                    "last_name": request.last_name,
                    "password": get_password_hash(request.temporary_password),
                    "status": "active",
                    "requires_password_change": True,  # Force password change on first login
                }
            )

            # Load and send welcome email
            html_content = email_service.load_template(
                "new_user",
                user_name=request.first_name,
                username=request.username,
                temporary_password=request.temporary_password,
                email=request.email,
                login_url="https://your-app.com/login",
                support_url="https://your-app.com/support",
                privacy_url="https://your-app.com/privacy",
                terms_url="https://your-app.com/terms",
            )

            success = email_service.send_email(
                to_email=request.email,
                subject="Welcome to DBA HRMS - Your Account Has Been Created",
                html_content=html_content,
            )

            if not success:
                logger.warning(f"Failed to send welcome email to {request.email}")
                # Continue anyway - user was created

            logger.info(f"New user created: {request.username}")

            return PasswordResetResponse(
                success=True,
                message="User registered successfully. Welcome email sent.",
                user_id=new_user.id,
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error registering new user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to register user",
            )

    return router


# ============================================================================
# USAGE IN MAIN.PY
# ============================================================================

"""
# In your main.py or app initialization:

from fastapi import FastAPI
from app.api.v1.auth_email import create_auth_email_router
from app.repositories.user_repo import user_repo
from app.services.auth_service import auth_service
from app.services.email_service import email_service

app = FastAPI()

# Create and include router
auth_router = create_auth_email_router(user_repo, auth_service, email_service)
app.include_router(auth_router)

# Now these endpoints are available:
# POST /api/v1/auth/forgot-password
# POST /api/v1/auth/validate-otp
# POST /api/v1/auth/reset-password
# GET  /api/v1/auth/reset-status/{user_id}
# POST /api/v1/auth/recover-username
# POST /api/v1/auth/register-new-user
"""
