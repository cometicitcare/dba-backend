from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, field_validator
from typing import List
import secrets



class Settings(BaseSettings):
    APP_NAME: str = "Temple/Vihara Management API"
    APP_ENV: str = "dev"


    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] | List[str] = []


    DATABASE_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60            # short-lived
    REFRESH_TOKEN_EXPIRE_DAYS: int = 2               # long-lived

    COOKIE_DOMAIN: str | None = None                 # e.g., ".example.com" or None for default
    COOKIE_SECURE: bool = True                       # must be True in prod (HTTPS)
    COOKIE_SAMESITE: str = "Strict"                  # "Strict" per your requirement
    COOKIE_PATH: str = "/"                           # sent to all routes

    class Config:
        env_file = ".env"



    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i]
        return v


    class Config:
        env_file = ".env"


settings = Settings()