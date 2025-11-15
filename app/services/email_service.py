"""
Email Service Module

Handles all email sending operations including user notifications,
password reset, and username recovery emails.
"""

import smtplib
import logging
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """
    Email service for sending emails via SMTP.
    Supports HTML and plain text emails with retry logic for Railway deployment.
    """

    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        self.from_name = settings.SMTP_FROM_NAME
        self.timeout = settings.SMTP_TIMEOUT
        self.retry_attempts = settings.SMTP_RETRY_ATTEMPTS
        self.retry_delay = settings.SMTP_RETRY_DELAY

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_text: Optional[str] = None,
    ) -> bool:
        """
        Send an email with HTML content using retry logic.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            plain_text: Plain text fallback (optional)

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        last_error = None
        
        for attempt in range(1, self.retry_attempts + 1):
            try:
                # Create email message
                message = MIMEMultipart("alternative")
                message["Subject"] = subject
                message["From"] = f"{self.from_name} <{self.from_email}>"
                message["To"] = to_email

                # Attach plain text part
                if plain_text:
                    text_part = MIMEText(plain_text, "plain")
                    message.attach(text_part)

                # Attach HTML part
                html_part = MIMEText(html_content, "html")
                message.attach(html_part)

                # Send email with extended timeout
                with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=self.timeout) as server:
                    server.starttls()
                    server.login(self.username, self.password)
                    server.send_message(message)

                logger.info(f"Email sent successfully to {to_email} (attempt {attempt}/{self.retry_attempts})")
                return True

            except smtplib.SMTPAuthenticationError as e:
                logger.error(f"SMTP authentication failed (attempt {attempt}/{self.retry_attempts}): {str(e)}")
                last_error = e
                # Don't retry auth errors
                break
                
            except (smtplib.SMTPException, TimeoutError, OSError) as e:
                last_error = e
                logger.warning(
                    f"Email send failed to {to_email} (attempt {attempt}/{self.retry_attempts}): {str(e)}"
                )
                
                # Retry if not the last attempt
                if attempt < self.retry_attempts:
                    time.sleep(self.retry_delay)
                    continue
                else:
                    logger.error(
                        f"Failed to send email to {to_email} after {self.retry_attempts} attempts: {str(e)}"
                    )
                    
            except Exception as e:
                last_error = e
                logger.error(
                    f"Unexpected error sending email to {to_email} (attempt {attempt}/{self.retry_attempts}): {str(e)}"
                )
                
                # Retry on unexpected errors
                if attempt < self.retry_attempts:
                    time.sleep(self.retry_delay)
                    continue
                else:
                    logger.error(
                        f"Failed to send email to {to_email} after {self.retry_attempts} attempts: {str(e)}"
                    )

        # Log final failure
        logger.error(
            f"Email delivery failed to {to_email} - all {self.retry_attempts} attempts exhausted. "
            f"Last error: {str(last_error)}"
        )
        return False

    @staticmethod
    def load_template(template_name: str, **kwargs) -> str:
        """
        Load and render an HTML email template.

        Args:
            template_name: Name of the template file (without .html)
            **kwargs: Variables to interpolate in the template

        Returns:
            str: Rendered HTML content
        """
        try:
            template_path = Path(__file__).parent.parent / "templates" / f"{template_name}.html"

            if not template_path.exists():
                logger.error(f"Template not found: {template_path}")
                return ""

            with open(template_path, "r", encoding="utf-8") as f:
                template_content = f.read()

            # Simple template variable substitution
            for key, value in kwargs.items():
                placeholder = f"{{{{{key}}}}}"
                template_content = template_content.replace(placeholder, str(value))

            return template_content

        except Exception as e:
            logger.error(f"Failed to load template {template_name}: {str(e)}")
            return ""


# Create a singleton instance
email_service = EmailService()
