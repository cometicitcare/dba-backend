# app/core/security.py
import secrets
import hashlib
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def generate_salt():
    """Generate a cryptographically secure salt"""
    return secrets.token_hex(16)


def generate_session_id(username: str = None) -> str:
    """
    Generate a cryptographically secure session ID.
    The username parameter is kept for compatibility but not embedded in the token.
    Instead, you should store the session_id -> user_id mapping in your database.
    """
    # Generate 32 bytes (256 bits) of random data
    # This is URL-safe and doesn't expose any user information
    return secrets.token_urlsafe(32)


def hash_session_id(session_id: str) -> str:
    """
    Optional: Hash session IDs before storing in database for additional security
    """
    return hashlib.sha256(session_id.encode()).hexdigest()