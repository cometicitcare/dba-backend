"""
Email Service Module

Handles all email sending operations including user notifications,
password reset, and username recovery emails.

Performance note:
- SMTP operations are blocking. To avoid blocking FastAPI's event loop
    under concurrent requests, use the provided background submitter
    to run sends in a thread pool.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, Future
import threading
import time
from app.services.suppression_list import suppression_list

from app.core.config import settings

logger = logging.getLogger(__name__)

# Small, module-level pool for background email sending
_EMAIL_EXECUTOR = ThreadPoolExecutor(max_workers=4, thread_name_prefix="email-sender")


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

    def can_send_to(self, to_email: str) -> bool:
        """Basic deliverability guard.

        - Mailinator blocks addresses containing words like 'admin' or 'office'.
        - Short-circuit to avoid wasted SMTP attempts and error noise.
        """
        try:
            local, domain = to_email.split("@", 1)
            domain = domain.lower().strip()
            local_lc = local.lower().strip()
        except Exception:
            logger.error(f"Invalid email address format: {to_email}")
            return False

        # Temporary suppression list check
        if suppression_list.is_suppressed(to_email):
            info = suppression_list.get(to_email)
            logger.warning(
                f"Email suppressed for {to_email}; reason={info.get('reason') if info else 'unknown'}"
            )
            return False

        if domain == "mailinator.com" and ("admin" in local_lc or "office" in local_lc):
            logger.warning(
                f"Email blocked by policy: '{to_email}' (restricted local-part for mailinator.com)"
            )
            return False
        return True

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
            if not self.can_send_to(to_email):
                return False
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

            # Send with simple retry/backoff for transient issues
            max_retries = settings.EMAIL_MAX_RETRIES
            backoff = settings.EMAIL_RETRY_BACKOFF_BASE
            attempt = 0
            while True:
                try:
                    with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                        server.starttls()
                        server.login(self.username, self.password)
                        server.send_message(message)
                    break
                except smtplib.SMTPResponseException as e:
                    code = getattr(e, 'smtp_code', None)
                    # Retry on 4xx; fail fast on 5xx
                    if code is not None and code >= 500:
                        logger.error(f"SMTP 5xx for {to_email} (code={code}): {e}")
                        raise
                    attempt += 1
                    if attempt > max_retries:
                        logger.error(f"SMTP retry exhausted for {to_email}: code={code} {e}")
                        raise
                    sleep_for = backoff * (2 ** (attempt - 1))
                    logger.warning(f"SMTP transient error (code={code}); retrying in {sleep_for:.2f}s")
                    time.sleep(sleep_for)
                except (smtplib.SMTPServerDisconnected, smtplib.SMTPConnectError, TimeoutError) as e:
                    attempt += 1
                    if attempt > max_retries:
                        logger.error(f"SMTP connection retry exhausted for {to_email}: {e}")
                        raise
                    sleep_for = backoff * (2 ** (attempt - 1))
                    logger.warning(f"SMTP connection issue; retrying in {sleep_for:.2f}s")
                    time.sleep(sleep_for)

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

    def submit_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_text: Optional[str] = None,
    ) -> Future:
        """
        Schedule an email send on a background thread and return immediately.

        Returns a Future; callers can ignore it to avoid blocking the request
        cycle, or add callbacks/logging if needed.
        """
        try:
            fut = _EMAIL_EXECUTOR.submit(
                self.send_email, to_email, subject, html_content, plain_text
            )
            def _cb(f: Future):
                try:
                    ok = f.result()
                    if ok:
                        logger.info(f"Email send completed to {to_email}")
                    else:
                        logger.error(f"Email send failed to {to_email}")
                except Exception as e:
                    logger.error(f"Email future raised for {to_email}: {e}")
            fut.add_done_callback(_cb)
            return fut
        except Exception as e:
            logger.error(f"Failed to submit email to background executor: {e}")
            # Return a dummy completed future with result False
            fut: Future = Future()
            fut.set_result(False)
            return fut

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
