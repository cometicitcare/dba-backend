"""
Email Service Module

Handles all email sending operations including user notifications,
password reset, and username recovery emails.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """
    Email service for sending emails via SMTP.
    Supports HTML and plain text emails.
    """

    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        self.from_name = settings.SMTP_FROM_NAME

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_text: Optional[str] = None,
    ) -> bool:
        """
        Send an email with HTML content.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            plain_text: Plain text fallback (optional)

        Returns:
            bool: True if email sent successfully, False otherwise
        """
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

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(message)

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed. Check credentials.")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error occurred: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
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
