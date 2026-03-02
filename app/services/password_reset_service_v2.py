"""
Updated Password Reset Service using Industry-Level Email and OTP Services

Integrates:
- EmailServiceV2 with async support and connection pooling
- OTPServiceV2 with Redis backend
- Background task processing for async operations
"""

import logging
from typing import Optional, Dict, Any

from app.core.config import settings
from app.services.email_service_v2 import email_service_v2
from app.services.otp_service_v2 import otp_service_v2
from app.services.background_tasks import send_otp_email_async, background_task_service

logger = logging.getLogger(__name__)


class PasswordResetServiceV2:
    """
    Industry-level password reset service with async email delivery,
    Redis-backed OTP storage, and comprehensive error handling.
    """

    def __init__(self):
        self.otp_service = otp_service_v2
        self.email_service = email_service_v2
        self.reset_token_expiry = settings.RESET_PASSWORD_TOKEN_EXPIRE_MINUTES

    def initiate_password_reset(
        self,
        user_id: str | int,
        user_email: str,
        user_name: str,
        user_phone: str | None = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        async_send: bool = True
    ) -> tuple[bool, str, Dict[str, Any]]:
        """
        Initiate a password reset request.
        Generates OTP and sends it via email (and optionally SMS).

        Args:
            user_id: The user's ID
            user_email: User's email address
            user_name: User's display name
            user_phone: User's phone number (optional)
            ip_address: Client IP address for security logging
            user_agent: Client user agent for security logging
            async_send: Whether to send emails asynchronously (default: True)

        Returns:
            tuple: (success, message, delivery_info)
        """
        try:
            # Determine delivery channel
            delivery_channel = "email"
            if user_phone and settings.SMS_ENABLED:
                delivery_channel = "both"
            
            # Generate OTP using the new service
            success, message, otp_code = self.otp_service.generate_otp(
                user_id=user_id,
                user_identifier=user_email,
                delivery_channel=delivery_channel,
                purpose="password_reset",
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            if not success or not otp_code:
                logger.error(f"Failed to generate OTP for user {user_id}: {message}")
                return False, message, {"email": False, "sms": False}
            
            # Load email template
            html_content = self.email_service.load_template(
                "password_reset",
                user_name=user_name,
                otp=otp_code,
                otp_expiry=self.otp_service.otp_expiry_minutes,
                reset_password_url=f"{settings.FRONTEND_URL}/reset-password",
                support_url=f"{settings.FRONTEND_URL}/support",
                privacy_url=f"{settings.FRONTEND_URL}/privacy",
                terms_url=f"{settings.FRONTEND_URL}/terms",
            )
            
            plain_text = (
                f"Your OTP for password reset is: {otp_code}. "
                f"Valid for {self.otp_service.otp_expiry_minutes} minutes."
            )
            
            # Send email
            email_sent = False
            email_task_id = None
            
            try:
                if async_send:
                    # Send email asynchronously via background task
                    email_task_id = send_otp_email_async(
                        user_id=user_id,
                        user_email=user_email,
                        user_name=user_name,
                        otp=otp_code,
                        otp_expiry_minutes=self.otp_service.otp_expiry_minutes
                    )
                    # For async, assume success (task was queued)
                    email_sent = True
                    logger.info(
                        f"Password reset email queued for {user_email} "
                        f"(task ID: {email_task_id})"
                    )
                else:
                    # Send email synchronously
                    email_sent = self.email_service.send_email(
                        to_email=user_email,
                        subject="Password Reset Request - DBA HRMS",
                        html_content=html_content,
                        plain_text=plain_text
                    )
                    
                    if email_sent:
                        logger.info(f"Password reset email sent to {user_email}")
                    else:
                        logger.warning(f"Failed to send password reset email to {user_email}")
                        
            except Exception as e:
                logger.error(f"Failed to send password reset email to {user_email}: {e}")
                email_sent = False
            
            # Send SMS if enabled and phone provided
            sms_sent = False
            try:
                if user_phone and settings.SMS_ENABLED:
                    from app.services.sms_service import sms_service
                    
                    sms_text = sms_service.load_template(
                        "password_reset_sms",
                        otp=otp_code,
                        otp_expiry=self.otp_service.otp_expiry_minutes
                    )
                    
                    if sms_text:
                        sms_result = sms_service.send_sms(
                            recipient=user_phone,
                            message=sms_text
                        )
                        sms_sent = (
                            sms_result.get('success', False) 
                            if isinstance(sms_result, dict) 
                            else bool(sms_result)
                        )
                        
                        if sms_sent:
                            logger.info(f"Password reset SMS sent to {user_phone}")
                        
            except Exception as e:
                logger.error(f"Failed to send password reset SMS to {user_phone}: {e}")
                sms_sent = False
            
            # Build delivery info
            delivery_info = {
                "email": email_sent,
                "sms": sms_sent,
                "email_task_id": email_task_id if async_send else None,
                "delivery_channel": delivery_channel,
                "async": async_send
            }
            
            # Check if at least one channel succeeded
            if email_sent or sms_sent:
                channels = []
                if email_sent:
                    channels.append("email")
                if sms_sent:
                    channels.append("SMS")
                
                return (
                    True,
                    f"Password reset OTP sent via {' and '.join(channels)}",
                    delivery_info
                )
            else:
                # OTP was generated but delivery failed
                # Clear the OTP since we couldn't deliver it
                self.otp_service.clear_otp(user_id, "password_reset")
                
                return (
                    False,
                    "Failed to send password reset OTP. Please try again.",
                    delivery_info
                )
            
        except Exception as e:
            logger.error(f"Error initiating password reset for user {user_id}: {e}", exc_info=True)
            return (
                False,
                f"An error occurred: {str(e)}",
                {"email": False, "sms": False}
            )

    def validate_otp_for_reset(
        self,
        user_id: str | int,
        otp: str
    ) -> tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Validate OTP for password reset.

        Args:
            user_id: The user's ID
            otp: The OTP to validate

        Returns:
            tuple: (is_valid, message, metadata)
        """
        return self.otp_service.validate_otp(user_id, otp, purpose="password_reset")

    def complete_password_reset(
        self,
        user_id: str | int,
        new_password: str
    ) -> tuple[bool, str]:
        """
        Complete password reset after OTP validation.
        Clear OTP and update user's password (to be implemented in auth service).

        Args:
            user_id: The user's ID
            new_password: The new password

        Returns:
            tuple: (success, message)
        """
        try:
            # Clear OTP
            self.otp_service.clear_otp(user_id, purpose="password_reset")

            # Password update logic should be in auth service
            # This service just validates the OTP flow
            logger.info(f"Password reset completed for user {user_id}")
            return True, "Password reset successfully"

        except Exception as e:
            logger.error(f"Error completing password reset for user {user_id}: {e}")
            return False, f"An error occurred: {str(e)}"

    def get_reset_status(self, user_id: str | int) -> Optional[Dict[str, Any]]:
        """Get password reset status for a user."""
        return self.otp_service.get_otp_status(user_id, purpose="password_reset")
    
    def get_service_metrics(self) -> Dict[str, Any]:
        """Get metrics from email and OTP services."""
        return {
            "email_service": self.email_service.get_metrics(),
            "otp_service": self.otp_service.get_metrics(),
            "background_tasks": background_task_service.get_metrics()
        }


# Create singleton instance - V2 is now the default
password_reset_service_v2 = PasswordResetServiceV2()

# For backward compatibility
password_reset_service = password_reset_service_v2
