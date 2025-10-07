# app/core/security.py
import base64
import os
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def generate_salt():
    return os.urandom(16).hex()


def generate_session_id(username: str) -> str:
    # Create a secure, random session ID and encode it
    raw_session_id = f"{os.urandom(24).hex()}.{username}"
    return base64.urlsafe_b64encode(raw_session_id.encode()).decode()