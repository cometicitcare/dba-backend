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
    
    # Auth / JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-prod")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # Cookie settings - FIXED for browser compatibility
    COOKIE_DOMAIN: str | None = os.getenv("COOKIE_DOMAIN") or None  # Don't set domain for localhost
    COOKIE_PATH: str = os.getenv("COOKIE_PATH", "/")
    # CRITICAL: Use "none" for cross-origin, "lax" for same-origin
    COOKIE_SAMESITE: str = os.getenv("COOKIE_SAMESITE", "none")  # Changed from "lax"
    # CRITICAL: Must be True when SameSite=none
    COOKIE_SECURE: bool = os.getenv("COOKIE_SECURE", "true").lower() == "true"  # Changed logic

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