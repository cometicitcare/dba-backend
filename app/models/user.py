# app/models/user.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
)
from sqlalchemy.sql import func
from app.db.base import Base


class UserAccount(Base):
    __tablename__ = "user_accounts"

    # IMPORTANT: Replace 'ua_id' with the actual primary key column name from your database table
    ua_id = Column(String, primary_key=True, index=True) 
    ua_username = Column(String(50), unique=True, nullable=False, index=True)
    ua_password_hash = Column(String(255), nullable=False)
    ua_salt = Column(String(255), nullable=False)
    ua_email = Column(String(100), unique=True, nullable=False, index=True)
    ua_full_name = Column(String(100))
    ua_status = Column(String(20), default="active")
    ua_locked_until = Column(DateTime(timezone=True), nullable=True)
    ua_login_attempts = Column(Integer, default=0)
    ua_last_login = Column(DateTime(timezone=True), nullable=True)
    ua_created_at = Column(DateTime(timezone=True), server_default=func.now())
    ua_updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class LoginHistory(Base):
    __tablename__ = "login_history"

    lh_id = Column(Integer, primary_key=True, index=True)
    # This must also match the column name above
    lh_user_id = Column(String, ForeignKey("user_accounts.ua_id"), nullable=False) 
    lh_session_id = Column(String(255), unique=True, nullable=False, index=True)
    lh_ip_address = Column(String(50))
    lh_user_agent = Column(Text)
    lh_login_time = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    lh_logout_time = Column(DateTime(timezone=True), nullable=True)
    lh_success = Column(Boolean, nullable=False)