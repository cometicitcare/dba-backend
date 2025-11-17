"""
Password Reset Service Module

Handles password reset flows including OTP generation, validation,
and temporary token management.
"""

import secrets
import string
from datetime import datetime, timedelta
from typing import Optional
import logging

from app.core.config import settings
from app.services.email_service import email_service

logger = logging.getLogger(__name__)


class OTPManager:
    """
    Manages One-Time Passwords (OTP) for password reset flows.
    Stores OTP in-memory with expiration (in production, use Redis or database).
    """

    def __init__(self):
        # In-memory OTP store: {user_id: {"otp": "123456", "expires_at": datetime, "attempts": 0}}
        self._otp_store = {}
        self.max_attempts = 3
        self.otp_length = settings.OTP_LENGTH
        self.otp_expiry = settings.OTP_EXPIRE_MINUTES
        # Rate limiting per user during one OTP window
        self.resend_interval_sec = settings.OTP_RESEND_INTERVAL_SECONDS
        self.max_sends_per_window = settings.OTP_MAX_SENDS_PER_WINDOW

    def generate_otp(self, user_id: str | int) -> str:
        """
        Generate a new OTP for a user.

        Args:
            user_id: The user's ID

        Returns:
            str: Generated OTP code

        Note:
            In production, use Redis or database for persistence.
        """
        otp = "".join(secrets.choice(string.digits) for _ in range(self.otp_length))
        expires_at = datetime.utcnow() + timedelta(minutes=self.otp_expiry)

        self._otp_store[user_id] = {
            "otp": otp,
            "expires_at": expires_at,
            "attempts": 0,
            "created_at": datetime.utcnow(),
            "last_sent_at": None,
            "send_count": 0,
        }

        logger.info(f"OTP generated for user {user_id}")
        return otp

    def get_or_create_otp(self, user_id: str | int) -> tuple[str, bool]:
        """Return existing valid OTP or create a new one.

        Returns (otp, created_new)
        """
        data = self._otp_store.get(user_id)
        if data and datetime.utcnow() <= data["expires_at"]:
            return data["otp"], False
        return self.generate_otp(user_id), True

    def can_send_now(self, user_id: str | int) -> bool:
        data = self._otp_store.get(user_id)
        if not data:
            return True
        # Too many sends during window
        if data.get("send_count", 0) >= self.max_sends_per_window:
            return False
        last = data.get("last_sent_at")
        if not last:
            return True
        return (datetime.utcnow() - last).total_seconds() >= self.resend_interval_sec

    def mark_sent(self, user_id: str | int) -> None:
        data = self._otp_store.get(user_id)
        if not data:
            return
        data["last_sent_at"] = datetime.utcnow()
        data["send_count"] = int(data.get("send_count", 0)) + 1

    def validate_otp(self, user_id: str | int, otp: str) -> tuple[bool, str]:
        """
        Validate an OTP for a user.

        Args:
            user_id: The user's ID
            otp: The OTP to validate

        Returns:
            tuple: (is_valid, message)
        """
        if user_id not in self._otp_store:
            return False, "No OTP request found for this user"

        otp_data = self._otp_store[user_id]

        # Check if OTP has expired
        if datetime.utcnow() > otp_data["expires_at"]:
            del self._otp_store[user_id]
            return False, "OTP has expired. Please request a new one."

        # Check attempts
        if otp_data["attempts"] >= self.max_attempts:
            del self._otp_store[user_id]
            return False, "Maximum OTP attempts exceeded. Please request a new OTP."

        # Validate OTP
        if otp_data["otp"] != otp:
            otp_data["attempts"] += 1
            remaining_attempts = self.max_attempts - otp_data["attempts"]
            return (
                False,
                f"Invalid OTP. You have {remaining_attempts} attempt(s) remaining.",
            )

        logger.info(f"OTP validated successfully for user {user_id}")
        return True, "OTP validated successfully"

    def clear_otp(self, user_id: str | int) -> None:
        """Clear OTP for a user after successful validation."""
        if user_id in self._otp_store:
            del self._otp_store[user_id]
            logger.info(f"OTP cleared for user {user_id}")

    def get_otp_status(self, user_id: str | int) -> Optional[dict]:
        """Get OTP status for a user."""
        if user_id not in self._otp_store:
            return None

        otp_data = self._otp_store[user_id]
        time_remaining = (
            otp_data["expires_at"] - datetime.utcnow()
        ).total_seconds() / 60

        return {
            "has_otp": True,
            "time_remaining_minutes": max(0, time_remaining),
            "attempts_remaining": self.max_attempts - otp_data["attempts"],
            "is_expired": datetime.utcnow() > otp_data["expires_at"],
        }


class PasswordResetService:
    """
    Service for handling password reset flows.
    Manages OTP generation, validation, and token creation.
    """

    def __init__(self):
        self.otp_manager = OTPManager()
        self.reset_token_expiry = settings.RESET_PASSWORD_TOKEN_EXPIRE_MINUTES

    def initiate_password_reset(
        self,
        user_id: str | int,
        user_email: str,
        user_name: str,
        user_phone: str | None = None,
    ) -> tuple[bool, str]:
        """
        Initiate a password reset request.
        Generates OTP and sends it via email.

        Args:
            user_id: The user's ID
            user_email: User's email address
            user_name: User's display name

        Returns:
            tuple: (success, message)
        """
        try:
            # Get valid OTP (reuse if still valid)
            otp, created_new = self.otp_manager.get_or_create_otp(user_id)

            # Rate limit sends per user
            if not self.otp_manager.can_send_now(user_id):
                logger.warning(f"OTP send rate-limited for user {user_id}")
                # Do not send again; return success with no channels to avoid spam
                return True, "OTP recently sent; please wait before requesting again.", {"email": False, "sms": False}

            # Load and render email template
            html_content = email_service.load_template(
                "password_reset",
                user_name=user_name,
                otp=otp,
                otp_expiry=self.otp_manager.otp_expiry,
                reset_password_url="https://your-app.com/reset-password",
                support_url="https://your-app.com/support",
                privacy_url="https://your-app.com/privacy",
                terms_url="https://your-app.com/terms",
            )

            # Queue email send in background to avoid blocking request thread
            email_sent = False
            try:
                if email_service.can_send_to(user_email):
                    future = email_service.submit_email(
                        to_email=user_email,
                        subject="Password Reset Request - DBA HRMS",
                        html_content=html_content,
                        plain_text=f"Your OTP for password reset is: {otp}. Valid for {self.otp_manager.otp_expiry} minutes.",
                    )
                    # Don't block; optimistically mark queued
                    email_sent = True
                    logger.info(f"Password reset email queued for {user_email}")
                else:
                    logger.warning(f"Skipping email send due to deliverability policy: {user_email}")
            except Exception as e:
                logger.error(f"Failed to queue password reset email to {user_email}: {e}")

            # If phone provided and SMS enabled, send SMS (short message)
            sms_sent = False
            try:
                if user_phone:
                    from app.services.sms_service import sms_service

                    sms_text = sms_service.load_template(
                        "password_reset_sms", otp=otp, otp_expiry=self.otp_manager.otp_expiry
                    )
                    if sms_text:
                        fut = sms_service.submit_sms(recipient=user_phone, message=sms_text)
                        sms_sent = True
                        logger.info(f"Password reset SMS queued to {user_phone}")

            except Exception as e:
                import traceback
                logger.error(f"Failed to queue password reset SMS to {user_phone}: {e}")
                logger.error(f"SMS error traceback: {traceback.format_exc()}")

            # Mark this OTP as sent (for rate limiting)
            try:
                self.otp_manager.mark_sent(user_id)
            except Exception:
                pass

            # Overall success if at least one channel delivered
            channels = {"email": bool(email_sent), "sms": bool(sms_sent)}
            if email_sent or sms_sent:
                return True, "Password reset OTP sent", channels
            else:
                return False, "Failed to send password reset OTP. Please try again.", channels

        except Exception as e:
            logger.error(f"Error initiating password reset: {str(e)}")
            return False, f"An error occurred: {str(e)}", {"email": False, "sms": False}

    def validate_otp_for_reset(self, user_id: str | int, otp: str) -> tuple[bool, str]:
        """
        Validate OTP for password reset.

        Args:
            user_id: The user's ID
            otp: The OTP to validate

        Returns:
            tuple: (is_valid, message)
        """
        return self.otp_manager.validate_otp(user_id, otp)

    def complete_password_reset(
        self, user_id: str | int, new_password: str
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
            self.otp_manager.clear_otp(user_id)

            # Password update logic should be in auth service
            # This service just validates the OTP flow
            logger.info(f"Password reset completed for user {user_id}")
            return True, "Password reset successfully"

        except Exception as e:
            logger.error(f"Error completing password reset: {str(e)}")
            return False, f"An error occurred: {str(e)}"

    def get_reset_status(self, user_id: str | int) -> Optional[dict]:
        """Get password reset status for a user."""
        return self.otp_manager.get_otp_status(user_id)


# Create a singleton instance
password_reset_service = PasswordResetService()
