# app/core/config.py
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, field_validator
from typing import List, Optional
import secrets
import urllib.parse
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]   # folder that contains app/ and alembic/
sys.path.insert(0, str(BASE_DIR))

dotenv_path = BASE_DIR / ".env"
load_dotenv(find_dotenv()) 

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Temple/Vihara Management API"
    APP_ENV: str = "dev"
    API_V1_STR: str = "/api/v1"

    # Auth
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60          # short-lived access token
    REFRESH_TOKEN_EXPIRE_DAYS: int = 2             # long-lived refresh token

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] | List[str] = []

    # DB (either supply DATABASE_URL OR the POSTGRES_* pieces)
    DATABASE_URL: Optional[str] = None
    POSTGRES_HOST: Optional[str] = None
    POSTGRES_PORT: Optional[int] = None
    POSTGRES_DB: Optional[str] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None

    # Cookies
    COOKIE_DOMAIN: str | None = None               # e.g., ".example.com"
    COOKIE_SECURE: bool = True                     # True in prod (HTTPS)
    COOKIE_SAMESITE: str = "Strict"                # per your FE request
    COOKIE_PATH: str = "/"

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i]
        return v

    @field_validator("DATABASE_URL", mode="after")
    @classmethod
    def build_database_url_if_missing(cls, v, values):
        if v:  # if DATABASE_URL provided explicitly, use it
            return v
        host = values.data.get("POSTGRES_HOST")
        port = values.data.get("POSTGRES_PORT")
        db   = values.data.get("POSTGRES_DB")
        user = values.data.get("POSTGRES_USER")
        pwd  = values.data.get("POSTGRES_PASSWORD")
        if all([host, port, db, user, pwd]):
            enc_pwd = urllib.parse.quote_plus(str(pwd))
            return f"postgresql+asyncpg://{user}:{enc_pwd}@{host}:{port}/{db}"
        raise ValueError(
            "DATABASE_URL not provided and POSTGRES_* is incomplete. "
            "Set DATABASE_URL or all of POSTGRES_HOST/PORT/DB/USER/PASSWORD."
        )

    class Config:
        env_file = ".env"
        extra = "ignore"  # don't explode on unknown env keys

settings = Settings()
