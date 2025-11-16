"""
Example FastAPI Endpoints using Industry-Level Email & OTP Services

These examples show how to integrate the new services into your API endpoints.
"""

from fastapi import APIRouter, HTTPException, Request, status, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime

from app.services.password_reset_service_v2 import password_reset_service
from app.services.email_service_v2 import email_service
from app.services.otp_service_v2 import otp_service
from app.services.background_tasks import send_email_async, background_task_service

router = APIRouter(prefix="/api/v1", tags=["auth"])


# ============================================================================
# Request/Response Models
# ============================================================================

class PasswordResetRequestModel(BaseModel):
    """Request model for initiating password reset."""
    email: EmailStr
    phone: Optional[str] = None


class OTPValidationModel(BaseModel):
    """Request model for OTP validation."""
    email: EmailStr
    otp: str


class PasswordResetCompleteModel(BaseModel):
    """Request model for completing password reset."""
    email: EmailStr
    otp: str
    new_password: str


class ServiceMetricsResponse(BaseModel):
    """Response model for service metrics."""
    email_service: Dict[str, Any]
    otp_service: Dict[str, Any]
    background_tasks: Dict[str, Any]


# ============================================================================
# Password Reset Endpoints
# ============================================================================

@router.post("/auth/password-reset/request")
async def request_password_reset(
    payload: PasswordResetRequestModel,
    request: Request
) -> Dict[str, Any]:
    """
    Initiate password reset process.
    
    Generates OTP and sends it via email (and optionally SMS).
    Uses async email delivery for better performance.
    
    Rate limits:
    - 5 requests per hour per user
    - 10 requests per day per user
    """
    try:
        # TODO: Get user from database by email
        # user = await get_user_by_email(payload.email)
        # if not user:
        #     raise HTTPException(status_code=404, detail="User not found")
        
        # For demo, using mock user data
        user_id = "mock_user_123"
        user_name = "Mock User"
        
        # Initiate password reset
        success, message, delivery_info = password_reset_service.initiate_password_reset(
            user_id=user_id,
            user_email=payload.email,
            user_name=user_name,
            user_phone=payload.phone,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            async_send=True  # Use async email delivery
        )
        
        if not success:
            # Check if it's a rate limit error
            if "rate limit" in message.lower():
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=message
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=message
            )
        
        return {
            "success": True,
            "message": message,
            "delivery_info": {
                "email_sent": delivery_info.get("email", False),
                "sms_sent": delivery_info.get("sms", False),
                "async": delivery_info.get("async", False)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


@router.post("/auth/password-reset/validate-otp")
async def validate_otp(payload: OTPValidationModel) -> Dict[str, Any]:
    """
    Validate OTP for password reset.
    
    Rate limits:
    - Maximum 3 attempts per OTP
    - OTP expires after 10 minutes (configurable)
    """
    try:
        # TODO: Get user from database by email
        # user = await get_user_by_email(payload.email)
        # if not user:
        #     raise HTTPException(status_code=404, detail="User not found")
        
        user_id = "mock_user_123"
        
        # Validate OTP
        valid, message, metadata = password_reset_service.validate_otp_for_reset(
            user_id=user_id,
            otp=payload.otp
        )
        
        if not valid:
            # Return appropriate error based on message
            if "expired" in message.lower():
                status_code = status.HTTP_410_GONE
            elif "maximum" in message.lower():
                status_code = status.HTTP_429_TOO_MANY_REQUESTS
            else:
                status_code = status.HTTP_400_BAD_REQUEST
            
            raise HTTPException(status_code=status_code, detail=message)
        
        return {
            "success": True,
            "message": message,
            "metadata": metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


@router.post("/auth/password-reset/complete")
async def complete_password_reset(payload: PasswordResetCompleteModel) -> Dict[str, Any]:
    """
    Complete password reset after OTP validation.
    
    This endpoint assumes OTP has been validated separately.
    In production, you might want to validate OTP again here.
    """
    try:
        # TODO: Get user from database by email
        # user = await get_user_by_email(payload.email)
        # if not user:
        #     raise HTTPException(status_code=404, detail="User not found")
        
        user_id = "mock_user_123"
        
        # Validate OTP one more time (recommended)
        valid, message, _ = password_reset_service.validate_otp_for_reset(
            user_id=user_id,
            otp=payload.otp
        )
        
        if not valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        # TODO: Hash and update password in database
        # await update_user_password(user_id, payload.new_password)
        
        # Complete password reset (clears OTP)
        success, message = password_reset_service.complete_password_reset(
            user_id=user_id,
            new_password=payload.new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=message
            )
        
        return {
            "success": True,
            "message": "Password reset successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


@router.get("/auth/password-reset/status/{email}")
async def get_password_reset_status(email: EmailStr) -> Dict[str, Any]:
    """
    Get password reset status for a user.
    
    Returns OTP status including time remaining and attempts left.
    """
    try:
        # TODO: Get user from database by email
        # user = await get_user_by_email(email)
        # if not user:
        #     raise HTTPException(status_code=404, detail="User not found")
        
        user_id = "mock_user_123"
        
        # Get reset status
        status_info = password_reset_service.get_reset_status(user_id)
        
        if not status_info:
            return {
                "has_active_reset": False,
                "message": "No active password reset request"
            }
        
        return {
            "has_active_reset": True,
            "status": status_info
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


# ============================================================================
# Email Service Endpoints
# ============================================================================

@router.post("/admin/email/send")
async def send_email_endpoint(
    to_email: EmailStr,
    subject: str,
    html_content: str,
    plain_text: Optional[str] = None,
    async_send: bool = True
) -> Dict[str, Any]:
    """
    Send an email (admin endpoint).
    
    Can send synchronously or asynchronously.
    """
    try:
        if async_send:
            # Send asynchronously via background task
            task_id = send_email_async(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                plain_text=plain_text
            )
            
            return {
                "success": True,
                "message": "Email queued for delivery",
                "task_id": task_id,
                "async": True
            }
        else:
            # Send synchronously
            success = email_service.send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                plain_text=plain_text
            )
            
            return {
                "success": success,
                "message": "Email sent" if success else "Failed to send email",
                "async": False
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


@router.get("/admin/email/metrics")
async def get_email_metrics() -> Dict[str, Any]:
    """Get email service metrics (admin endpoint)."""
    try:
        metrics = email_service.get_metrics()
        return {
            "success": True,
            "metrics": metrics
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


# ============================================================================
# OTP Service Endpoints
# ============================================================================

@router.post("/admin/otp/generate")
async def generate_otp_endpoint(
    user_id: str,
    user_identifier: str,
    delivery_channel: str = "email",
    purpose: str = "password_reset",
    request: Request = None
) -> Dict[str, Any]:
    """
    Generate OTP (admin/testing endpoint).
    
    In production, this should be protected and used for testing only.
    """
    try:
        success, message, otp = otp_service.generate_otp(
            user_id=user_id,
            user_identifier=user_identifier,
            delivery_channel=delivery_channel,
            purpose=purpose,
            ip_address=request.client.host if request else None
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        # In production, don't return the OTP in the response
        # Return it only for testing/development
        return {
            "success": True,
            "message": message,
            "otp": otp  # Remove in production!
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


@router.get("/admin/otp/metrics")
async def get_otp_metrics() -> Dict[str, Any]:
    """Get OTP service metrics (admin endpoint)."""
    try:
        metrics = otp_service.get_metrics()
        return {
            "success": True,
            "metrics": metrics
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


# ============================================================================
# Background Task Endpoints
# ============================================================================

@router.get("/admin/tasks/{task_id}")
async def get_task_status(task_id: str) -> Dict[str, Any]:
    """Get background task status (admin endpoint)."""
    try:
        task_status = background_task_service.get_task_status(task_id)
        
        if not task_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        return {
            "success": True,
            "task": task_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


@router.get("/admin/tasks/metrics")
async def get_background_task_metrics() -> Dict[str, Any]:
    """Get background task service metrics (admin endpoint)."""
    try:
        metrics = background_task_service.get_metrics()
        return {
            "success": True,
            "metrics": metrics
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


# ============================================================================
# Combined Service Metrics Endpoint
# ============================================================================

@router.get("/admin/services/metrics", response_model=Dict[str, Any])
async def get_all_service_metrics() -> Dict[str, Any]:
    """
    Get metrics from all services (admin endpoint).
    
    Returns combined metrics for email, OTP, and background task services.
    Useful for monitoring and dashboards.
    """
    try:
        metrics = password_reset_service.get_service_metrics()
        
        return {
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
            "services": metrics
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


# ============================================================================
# Health Check Endpoint
# ============================================================================

@router.get("/health/services")
async def health_check_services() -> Dict[str, Any]:
    """
    Health check for email and OTP services.
    
    Returns service status and basic health indicators.
    """
    try:
        # Get metrics
        email_metrics = email_service.get_metrics()
        otp_metrics = otp_service.get_metrics()
        task_metrics = background_task_service.get_metrics()
        
        # Determine health status
        email_healthy = (
            email_metrics.get('circuit_breaker_trips', 0) == 0 and
            email_metrics.get('emails_failed', 0) < 10
        )
        
        otp_healthy = otp_metrics.get('storage_type') in ['redis', 'memory']
        
        tasks_healthy = task_metrics.get('queue_size', 0) < 100
        
        overall_healthy = email_healthy and otp_healthy and tasks_healthy
        
        return {
            "healthy": overall_healthy,
            "services": {
                "email": {
                    "healthy": email_healthy,
                    "circuit_breaker_trips": email_metrics.get('circuit_breaker_trips', 0),
                    "emails_sent": email_metrics.get('emails_sent', 0),
                    "emails_failed": email_metrics.get('emails_failed', 0)
                },
                "otp": {
                    "healthy": otp_healthy,
                    "storage_type": otp_metrics.get('storage_type', 'unknown'),
                    "otps_generated": otp_metrics.get('otps_generated', 0),
                    "rate_limited": otp_metrics.get('rate_limited', 0)
                },
                "background_tasks": {
                    "healthy": tasks_healthy,
                    "queue_size": task_metrics.get('queue_size', 0),
                    "tasks_completed": task_metrics.get('tasks_completed', 0),
                    "tasks_failed": task_metrics.get('tasks_failed', 0)
                }
            }
        }
        
    except Exception as e:
        return {
            "healthy": False,
            "error": str(e)
        }


# ============================================================================
# Import to include in your main app
# ============================================================================

# In your main.py:
# from app.api.v1.email_otp_endpoints import router as email_otp_router
# app.include_router(email_otp_router)
