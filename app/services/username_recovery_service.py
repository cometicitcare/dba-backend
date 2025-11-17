"""
Username Recovery Service Module

Handles username recovery flows including email-based lookup
and sending username recovery emails to users.
"""

import logging
from typing import Optional

from app.services.email_service import email_service

logger = logging.getLogger(__name__)


class UsernameRecoveryService:
    """
    Service for handling username recovery requests.
    Allows users to recover their username using their email address.
    """

    def __init__(self):
        pass

    def recover_username_by_email(
        self, email: str, user_data: Optional[dict] = None
    ) -> tuple[bool, str]:
        """
        Recover username using email address.
        Should be integrated with your user repository to fetch user data.

        Args:
            email: User's email address
            user_data: Optional user data dict with keys: username, email, status

        Returns:
            tuple: (success, message)

        Example user_data:
        {
            "user_id": 123,
            "username": "john_doe",
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "status": "active"
        }
        """
        try:
            if not user_data:
                logger.warning(f"No user found with email: {email}")
                # Return generic message to prevent email enumeration
                return False, "If an account exists with this email, you will receive a recovery email shortly."

            username = user_data.get("username")
            first_name = user_data.get("first_name", "User")
            status = user_data.get("status", "active")

            if not username:
                logger.error(f"User with email {email} has no username")
                return False, "Unable to retrieve username for this account."

            # Load and render template
            html_content = email_service.load_template(
                "username_recovery",
                username=username,
                email=email,
                account_status=status.title(),
                user_name=first_name,
                login_url="https://your-app.com/login",  # Update with actual URL
                support_url="https://your-app.com/support",
                privacy_url="https://your-app.com/privacy",
                terms_url="https://your-app.com/terms",
            )

            # Send email (skip if policy blocks destination)
            if email_service.can_send_to(email):
                success = email_service.send_email(
                    to_email=email,
                    subject="Your DBA HRMS Username",
                    html_content=html_content,
                    plain_text=f"Your username is: {username}",
                )
            else:
                logger.warning(f"Skipping username recovery email due to deliverability policy: {email}")
                success = False

            if success:
                logger.info(f"Username recovery email sent to {email}")
                return True, "If an account exists with this email, you will receive a recovery email shortly."
            else:
                logger.error(f"Failed to send username recovery email to {email}")
                return False, "Failed to send recovery email. Please try again later."

        except Exception as e:
            logger.error(f"Error in username recovery: {str(e)}")
            return False, "An error occurred. Please try again later."

    def verify_email_exists(self, email: str, user_repo=None) -> tuple[bool, Optional[dict]]:
        """
        Verify if email exists in the system and return user data.
        This should be called with an actual user repository.

        Args:
            email: Email address to verify
            user_repo: User repository instance (inject dependency)

        Returns:
            tuple: (exists, user_data)

        Note:
            This is a template method. Integrate with your actual user repository:

            Example usage in API:
            ```python
            from app.repositories.user_repo import user_repo

            exists, user_data = username_recovery_service.verify_email_exists(
                email=email,
                user_repo=user_repo
            )
            ```
        """
        try:
            if user_repo is None:
                logger.error("User repository not provided")
                return False, None

            # This should query your database
            # Example: user = await user_repo.get_by_email(email)
            # For now, returning False - implement with your DB
            logger.info(f"Email lookup requested for: {email}")
            return False, None

        except Exception as e:
            logger.error(f"Error verifying email: {str(e)}")
            return False, None

    def handle_username_recovery_request(
        self, email: str, user_repo=None
    ) -> tuple[bool, str]:
        """
        Complete flow for handling username recovery request.
        Verifies email and sends recovery email if found.

        Args:
            email: User's email address
            user_repo: User repository instance (inject dependency)

        Returns:
            tuple: (success, message)

        Usage in API endpoint:
        ```python
        from fastapi import HTTPException
        from app.repositories.user_repo import user_repo
        from app.services.username_recovery_service import username_recovery_service

        @router.post("/auth/recover-username")
        async def recover_username(request: RecoverUsernameRequest):
            success, message = username_recovery_service.handle_username_recovery_request(
                email=request.email,
                user_repo=user_repo
            )

            if not success:
                # Log attempt for security
                logger.warning(f"Username recovery attempt: {request.email}")

            # Always return generic message for security
            return {
                "message": "If an account exists with this email, "
                           "you will receive a recovery email shortly."
            }
        ```
        """
        try:
            # Verify email exists (with your user repo)
            exists, user_data = self.verify_email_exists(email, user_repo)

            if not exists:
                # Return generic message for security (prevent email enumeration)
                logger.warning(f"Username recovery for non-existent email: {email}")
                return (
                    True,
                    "If an account exists with this email, you will receive a recovery email shortly.",
                )

            # Send recovery email
            success, message = self.recover_username_by_email(email, user_data)

            # Return generic message for security
            return (
                True,
                "If an account exists with this email, you will receive a recovery email shortly.",
            )

        except Exception as e:
            logger.error(f"Error in username recovery flow: {str(e)}")
            return (
                True,
                "If an account exists with this email, you will receive a recovery email shortly.",
            )


# Create a singleton instance
username_recovery_service = UsernameRecoveryService()
