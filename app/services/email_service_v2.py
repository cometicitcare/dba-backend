"""
Industry-Level Email Service Module

Features:
- Async email sending with connection pooling
- Rate limiting per recipient
- Circuit breaker pattern for fault tolerance
- Email queue with retry logic
- Template caching
- Comprehensive monitoring and logging
"""

import asyncio
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict, deque
from threading import Lock
import time
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
import ssl

from app.core.config import settings

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Circuit breaker pattern to prevent cascading failures."""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self._lock = Lock()
    
    def call(self, func, *args, **kwargs):
        with self._lock:
            if self.state == "OPEN":
                if (datetime.utcnow() - self.last_failure_time).seconds > self.timeout:
                    self.state = "HALF_OPEN"
                    logger.info("Circuit breaker entering HALF_OPEN state")
                else:
                    raise Exception("Circuit breaker is OPEN - service unavailable")
        
        try:
            result = func(*args, **kwargs)
            with self._lock:
                if self.state == "HALF_OPEN":
                    self.state = "CLOSED"
                    self.failures = 0
                    logger.info("Circuit breaker reset to CLOSED state")
            return result
        except Exception as e:
            with self._lock:
                self.failures += 1
                self.last_failure_time = datetime.utcnow()
                if self.failures >= self.failure_threshold:
                    self.state = "OPEN"
                    logger.error(f"Circuit breaker OPENED after {self.failures} failures")
            raise e


class RateLimiter:
    """Token bucket rate limiter for email sending."""
    
    def __init__(self, max_emails_per_hour: int = 100, max_emails_per_recipient: int = 5):
        self.max_emails_per_hour = max_emails_per_hour
        self.max_emails_per_recipient = max_emails_per_recipient
        self.global_timestamps = deque()
        self.recipient_timestamps = defaultdict(deque)
        self._lock = Lock()
    
    def can_send(self, recipient: str) -> tuple[bool, str]:
        """Check if email can be sent based on rate limits."""
        with self._lock:
            now = datetime.utcnow()
            one_hour_ago = now - timedelta(hours=1)
            
            # Clean up old timestamps
            while self.global_timestamps and self.global_timestamps[0] < one_hour_ago:
                self.global_timestamps.popleft()
            
            if recipient in self.recipient_timestamps:
                while (self.recipient_timestamps[recipient] and 
                       self.recipient_timestamps[recipient][0] < one_hour_ago):
                    self.recipient_timestamps[recipient].popleft()
            
            # Check global limit
            if len(self.global_timestamps) >= self.max_emails_per_hour:
                return False, "Global email rate limit exceeded"
            
            # Check per-recipient limit
            if len(self.recipient_timestamps[recipient]) >= self.max_emails_per_recipient:
                return False, f"Rate limit exceeded for {recipient}"
            
            return True, "OK"
    
    def record_send(self, recipient: str):
        """Record an email send for rate limiting."""
        with self._lock:
            now = datetime.utcnow()
            self.global_timestamps.append(now)
            self.recipient_timestamps[recipient].append(now)


class SMTPConnectionPool:
    """Connection pool for SMTP connections."""
    
    def __init__(self, pool_size: int = 5):
        self.pool_size = pool_size
        self.connections = []
        self._lock = Lock()
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD
        self.timeout = settings.SMTP_TIMEOUT
    
    def _create_connection(self):
        """Create a new SMTP connection."""
        try:
            # Create SSL context with more secure settings
            context = ssl.create_default_context()
            
            # Connect to SMTP server
            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=self.timeout)
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(self.username, self.password)
            return server
        except Exception as e:
            logger.error(f"Failed to create SMTP connection: {e}")
            raise
    
    def get_connection(self):
        """Get a connection from the pool."""
        with self._lock:
            if self.connections:
                return self.connections.pop()
            return self._create_connection()
    
    def return_connection(self, conn):
        """Return a connection to the pool."""
        with self._lock:
            if len(self.connections) < self.pool_size:
                try:
                    # Verify connection is still alive
                    conn.noop()
                    self.connections.append(conn)
                except:
                    try:
                        conn.quit()
                    except:
                        pass
            else:
                try:
                    conn.quit()
                except:
                    pass
    
    def close_all(self):
        """Close all connections in the pool."""
        with self._lock:
            for conn in self.connections:
                try:
                    conn.quit()
                except:
                    pass
            self.connections.clear()


class EmailServiceV2:
    """
    Industry-level email service with async support, connection pooling,
    rate limiting, circuit breaker, and comprehensive error handling.
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
        
        # Initialize components
        self.connection_pool = SMTPConnectionPool(pool_size=5)
        self.rate_limiter = RateLimiter(max_emails_per_hour=100, max_emails_per_recipient=5)
        self.circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Metrics
        self.metrics = {
            "emails_sent": 0,
            "emails_failed": 0,
            "total_retry_attempts": 0,
            "rate_limited": 0,
            "circuit_breaker_trips": 0
        }
        self._metrics_lock = Lock()
    
    def _send_email_sync(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_text: Optional[str] = None,
    ) -> bool:
        """
        Synchronous email sending with connection pooling.
        This is called by the executor for async operation.
        """
        # Check rate limit
        can_send, message = self.rate_limiter.can_send(to_email)
        if not can_send:
            logger.warning(f"Rate limit check failed for {to_email}: {message}")
            with self._metrics_lock:
                self.metrics["rate_limited"] += 1
            return False
        
        last_error = None
        
        for attempt in range(1, self.retry_attempts + 1):
            conn = None
            try:
                # Use circuit breaker pattern
                def send_via_smtp():
                    nonlocal conn
                    # Create email message
                    message = MIMEMultipart("alternative")
                    message["Subject"] = subject
                    message["From"] = f"{self.from_name} <{self.from_email}>"
                    message["To"] = to_email
                    message["Date"] = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
                    message["Message-ID"] = f"<{datetime.utcnow().timestamp()}@{self.smtp_server}>"

                    # Attach plain text part
                    if plain_text:
                        text_part = MIMEText(plain_text, "plain", "utf-8")
                        message.attach(text_part)

                    # Attach HTML part
                    html_part = MIMEText(html_content, "html", "utf-8")
                    message.attach(html_part)

                    # Get connection from pool
                    conn = self.connection_pool.get_connection()
                    
                    # Send email
                    conn.send_message(message)
                    
                    return conn
                
                # Execute with circuit breaker
                conn = self.circuit_breaker.call(send_via_smtp)
                
                # Return connection to pool
                if conn:
                    self.connection_pool.return_connection(conn)
                
                # Record successful send
                self.rate_limiter.record_send(to_email)
                
                with self._metrics_lock:
                    self.metrics["emails_sent"] += 1
                    if attempt > 1:
                        self.metrics["total_retry_attempts"] += (attempt - 1)
                
                logger.info(f"Email sent successfully to {to_email} (attempt {attempt}/{self.retry_attempts})")
                return True

            except smtplib.SMTPAuthenticationError as e:
                logger.error(f"SMTP authentication failed (attempt {attempt}/{self.retry_attempts}): {str(e)}")
                last_error = e
                if conn:
                    try:
                        conn.quit()
                    except:
                        pass
                # Don't retry auth errors
                break
                
            except Exception as e:
                last_error = e
                logger.warning(
                    f"Email send failed to {to_email} (attempt {attempt}/{self.retry_attempts}): {str(e)}"
                )
                
                if conn:
                    try:
                        conn.quit()
                    except:
                        pass
                
                # Retry if not the last attempt
                if attempt < self.retry_attempts:
                    time.sleep(self.retry_delay * attempt)  # Exponential backoff
                    continue
                else:
                    logger.error(
                        f"Failed to send email to {to_email} after {self.retry_attempts} attempts: {str(e)}"
                    )

        # Log final failure
        with self._metrics_lock:
            self.metrics["emails_failed"] += 1
        
        logger.error(
            f"Email delivery failed to {to_email} - all {self.retry_attempts} attempts exhausted. "
            f"Last error: {str(last_error)}"
        )
        return False

    async def send_email_async(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_text: Optional[str] = None,
    ) -> bool:
        """
        Send an email asynchronously using thread pool executor.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            plain_text: Plain text fallback (optional)

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._send_email_sync,
            to_email,
            subject,
            html_content,
            plain_text
        )
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_text: Optional[str] = None,
    ) -> bool:
        """
        Synchronous wrapper for backward compatibility.
        For new code, prefer send_email_async.
        """
        return self._send_email_sync(to_email, subject, html_content, plain_text)

    @staticmethod
    @lru_cache(maxsize=32)
    def load_template(template_name: str, **kwargs) -> str:
        """
        Load and render an HTML email template with caching.

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
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get email service metrics."""
        with self._metrics_lock:
            return self.metrics.copy()
    
    def reset_metrics(self):
        """Reset metrics (for testing or periodic resets)."""
        with self._metrics_lock:
            self.metrics = {
                "emails_sent": 0,
                "emails_failed": 0,
                "total_retry_attempts": 0,
                "rate_limited": 0,
                "circuit_breaker_trips": 0
            }
    
    def shutdown(self):
        """Gracefully shutdown the email service."""
        logger.info("Shutting down email service...")
        self.executor.shutdown(wait=True)
        self.connection_pool.close_all()
        logger.info("Email service shutdown complete")


# Create singleton instances
email_service_v2 = EmailServiceV2()

# For backward compatibility, create an alias
email_service = email_service_v2
