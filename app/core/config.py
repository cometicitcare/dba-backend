# app/core/config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    PROJECT_NAME: str = "Bhikku Registry API"
    PROJECT_VERSION: str = "1.0.0"
    DATABASE_URL: str = os.getenv("DATABASE_URL")

settings = Settings()

if not settings.DATABASE_URL:
    raise ValueError("No DATABASE_URL set for connection in .env file")