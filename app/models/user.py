# app/models/user.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    Enum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from .roles import Role
import enum


class UserLocationType(str, enum.Enum):
    """Enum for user location types/levels"""
    MAIN_BRANCH = "MAIN_BRANCH"
    PROVINCE_BRANCH = "PROVINCE_BRANCH"
    DISTRICT_BRANCH = "DISTRICT_BRANCH"


class UserAccount(Base):
    __tablename__ = "user_accounts"

    ua_user_id = Column(String(10), primary_key=True, index=True)
    ua_username = Column(String(50), unique=True, nullable=False, index=True)
    ua_email = Column(String(100), unique=True, nullable=False, index=True)
    ua_password_hash = Column(String(255), nullable=False)
    ua_salt = Column(String(100), nullable=False)
    ua_first_name = Column(String(50))
    ua_last_name = Column(String(50))
    ua_phone = Column(String(15))
    ua_status = Column(String(20), default="active")
    ua_last_login = Column(DateTime(timezone=True), nullable=True)
    ua_login_attempts = Column(Integer, default=0)
    ua_locked_until = Column(DateTime(timezone=True), nullable=True)
    ua_password_expires = Column(DateTime(timezone=True), nullable=True)
    ua_must_change_password = Column(Boolean, default=False)
    ua_two_factor_enabled = Column(Boolean, default=False)
    ua_two_factor_secret = Column(String(100), nullable=True)
    ua_is_deleted = Column(Boolean, default=False)
    ua_created_at = Column(DateTime(timezone=True), server_default=func.now())
    ua_updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    ua_created_by = Column(String(50))
    ua_updated_by = Column(String(50))
    ua_version_number = Column(Integer, default=1)
    
    # Location-based access control fields
    ua_location_type = Column(
        Enum(UserLocationType),
        nullable=True,  # Made nullable for backward compatibility
        index=True
    )
    ua_main_branch_id = Column(
        Integer,
        ForeignKey("main_branches.mb_id"),
        nullable=True,
        index=True
    )
    ua_province_branch_id = Column(
        Integer,
        ForeignKey("province_branches.pb_id"),
        nullable=True,
        index=True
    )
    ua_district_branch_id = Column(
        Integer,
        ForeignKey("district_branches.db_id"),
        nullable=True,
        index=True
    )
    
    # Relationships (many-to-many through junction tables)
    # User can have multiple roles via UserRole table
    user_roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    # User can belong to multiple groups via UserGroup table
    user_groups = relationship("UserGroup", back_populates="user", cascade="all, delete-orphan")
    # User can have permission overrides via UserPermission table
    user_permissions = relationship("UserPermission", back_populates="user", cascade="all, delete-orphan")
    
    # Location relationships
    main_branch = relationship("MainBranch", back_populates="users")
    province_branch = relationship("ProvinceBranch", back_populates="users")
    district_branch = relationship("DistrictBranch", back_populates="users")


class LoginHistory(Base):
    __tablename__ = "login_history"

    lh_id = Column(Integer, primary_key=True, index=True)
    lh_user_id = Column(String(20), ForeignKey("user_accounts.ua_user_id"), nullable=False)
    lh_session_id = Column(String(255), unique=True, nullable=False, index=True)
    lh_ip_address = Column(String(50))
    lh_user_agent = Column(Text)
    lh_login_time = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    lh_logout_time = Column(DateTime(timezone=True), nullable=True)
    lh_success = Column(Boolean, nullable=False)
