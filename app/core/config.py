# app/core/config.py
import os
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    PROJECT_NAME: str = "Bhikku Registry API"
    PROJECT_VERSION: str = "1.0.0"
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    
    # CORS - CRITICAL: Must include your frontend URL
    BACKEND_CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv("BACKEND_CORS_ORIGINS", "").split(",")
        if origin.strip()
    ]
    
    # Frontend & Backend URLs
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "https://hrms.dbagovlk.com")
    BACKEND_URL: str = os.getenv("BACKEND_URL", "https://api.dbagovlk.com")
    
    # Auth / JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-prod")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # Cookie settings - FIXED for browser compatibility
    COOKIE_DOMAIN: str | None = os.getenv("COOKIE_DOMAIN") or None  # Don't set domain for localhost
    COOKIE_PATH: str = os.getenv("COOKIE_PATH", "/")
    # CRITICAL: Use "none" for cross-origin, "lax" for same-origin
    COOKIE_SAMESITE: str = os.getenv("COOKIE_SAMESITE", "none")  # Changed from "lax"
    # CRITICAL: Must be True when SameSite=none
    COOKIE_SECURE: bool = os.getenv("COOKIE_SECURE", "true").lower() == "true"  # Changed logic

    # Email / SMTP Configuration
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "mail.smtp2go.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "2525"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL: str = os.getenv("SMTP_FROM_EMAIL", "no-reply@dbagovlk.com")
    SMTP_FROM_NAME: str = os.getenv("SMTP_FROM_NAME", "DBA HRMS")
    SMTP_TIMEOUT: int = int(os.getenv("SMTP_TIMEOUT", "30"))  # Increased timeout for Railway
    SMTP_RETRY_ATTEMPTS: int = int(os.getenv("SMTP_RETRY_ATTEMPTS", "3"))
    SMTP_RETRY_DELAY: int = int(os.getenv("SMTP_RETRY_DELAY", "2"))  # Seconds between retries
    
    # Password Reset & OTP Configuration
    RESET_PASSWORD_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("RESET_PASSWORD_TOKEN_EXPIRE_MINUTES", "30"))
    OTP_EXPIRE_MINUTES: int = int(os.getenv("OTP_EXPIRE_MINUTES", "10"))
    OTP_LENGTH: int = int(os.getenv("OTP_LENGTH", "6"))
    OTP_MAX_ATTEMPTS: int = int(os.getenv("OTP_MAX_ATTEMPTS", "3"))
    OTP_MAX_REQUESTS_PER_HOUR: int = int(os.getenv("OTP_MAX_REQUESTS_PER_HOUR", "5"))
    OTP_MAX_REQUESTS_PER_DAY: int = int(os.getenv("OTP_MAX_REQUESTS_PER_DAY", "10"))
    
    # File Storage Configuration
    STORAGE_DIR: str = os.getenv("STORAGE_DIR", "app/storage")
    
    # Redis Configuration (for OTP storage in production)
    REDIS_ENABLED: bool = os.getenv("REDIS_ENABLED", "false").lower() == "true"
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))

    # SMS / Text service configuration (text.lk example)
    SMS_ENABLED: bool = os.getenv("SMS_ENABLED", "false").lower() == "true"
    SMS_API_URL: str = os.getenv("SMS_API_URL", "https://app.text.lk/api/v3/sms/send")
    SMS_BEARER_TOKEN: str = os.getenv("SMS_BEARER_TOKEN", "")
    SMS_DEFAULT_SENDER_ID: str = os.getenv("SMS_DEFAULT_SENDER_ID", "COMETICINSY")
    SMS_MAX_LENGTH: int = int(os.getenv("SMS_MAX_LENGTH", "160"))
    # Protected test key for triggering test SMS via a dev-only endpoint
    SMS_TEST_KEY: str = os.getenv("SMS_TEST_KEY", "")

    def __init__(self) -> None:
        # Normalize DATABASE_URL for SQLAlchemy/psycopg2 and Railway
        if self.DATABASE_URL:
            self.DATABASE_URL = self._normalize_database_url(self.DATABASE_URL)

    @staticmethod
    def _normalize_database_url(raw_url: str) -> str:
        """Normalize Postgres URL to explicit psycopg2 driver and enforce SSL in prod.

        - Convert schemes like postgres:// to postgresql+psycopg2://
        - Ensure sslmode=require when APP_ENV=production unless already present
        """
        parsed = urlparse(raw_url)

        # Upgrade/translate scheme to explicit sync driver for SQLAlchemy engine
        scheme = parsed.scheme
        if scheme.startswith("postgres") and "+" not in scheme:
            # e.g., postgres:// or postgresql:// -> postgresql+psycopg2://
            scheme = "postgresql+psycopg2"
        elif scheme == "postgresql+asyncpg":
            # Translate async driver URL provided by hosting to sync driver
            scheme = "postgresql+psycopg2"

        # Rebuild URL with possibly updated scheme
        rebuilt = parsed._replace(scheme=scheme)

        # Manage query params for SSL
        query_params = dict(parse_qsl(rebuilt.query))
        app_env = os.getenv("APP_ENV", "development").lower()
        if app_env == "production" and "sslmode" not in query_params:
            query_params["sslmode"] = "require"

        # Finalize URL
        final_url = urlunparse(
            (
                rebuilt.scheme,
                rebuilt.netloc,
                rebuilt.path,
                rebuilt.params,
                urlencode(query_params),
                rebuilt.fragment,
            )
        )
        return final_url

settings = Settings()

if not settings.DATABASE_URL:
    raise ValueError("No DATABASE_URL set for connection in .env file")