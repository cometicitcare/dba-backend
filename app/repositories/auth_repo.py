# app/repositories/auth_repo.py
from sqlalchemy.orm import Session
from app.models.user import UserAccount, LoginHistory, Role
from app.models.user_roles import UserRole
from app.models.role_permissions import RolePermission
from app.models.permissions import Permission
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, generate_salt
from datetime import datetime
from sqlalchemy import or_
import uuid


def get_role_by_id(db: Session, role_id: str):
    """Get role by ID"""
    return db.query(Role).filter(
        Role.ro_role_id == role_id,
        Role.ro_is_deleted == False
    ).first()


def get_all_roles(db: Session):
    """Get all active roles"""
    return db.query(Role).filter(Role.ro_is_deleted == False).all()


def create_user(db: Session, user: UserCreate):
    """Create a new user with role validation and all required fields"""
    # Validate that the role exists
    role = get_role_by_id(db, user.ro_role_id)
    if not role:
        raise ValueError(f"Invalid role ID: {user.ro_role_id}")

    salt = generate_salt()
    hashed_password = get_password_hash(user.ua_password + salt)

    # Generate a unique string ID for the new user
    user_id = f"UA{str(uuid.uuid4().int)[:7]}"

    db_user = UserAccount(
        # Required fields
        ua_user_id=user_id,
        ua_username=user.ua_username,
        ua_password_hash=hashed_password,
        ua_salt=salt,
        ua_email=user.ua_email,
        ro_role_id=user.ro_role_id,
        
        # Optional personal info from registration
        ua_first_name=user.ua_first_name,
        ua_last_name=user.ua_last_name,
        ua_phone=user.ua_phone,
        
        # Status and security fields - explicitly set defaults
        ua_status="active",
        ua_login_attempts=0,
        ua_must_change_password=False,
        ua_two_factor_enabled=False,
        ua_is_deleted=False,
        ua_version_number=1,
        
        # Audit fields
        ua_created_by=user_id,  # Self-created
        ua_updated_by=user_id,
        
        # Nullable timestamp fields (set later during usage)
        ua_last_login=None,
        ua_locked_until=None,
        ua_password_expires=None,
        ua_two_factor_secret=None,
    )
    db_user_role = UserRole(
        ur_user_id=user_id,
        ur_role_id=user.ro_role_id,
        ur_assigned_date=datetime.utcnow(),
    )
    db.add(db_user)
    db.add(db_user_role)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_username(db: Session, username: str):
    """Get user by username with role information"""
    return db.query(UserAccount).filter(
        UserAccount.ua_username == username,
        UserAccount.ua_is_deleted == False
    ).first()


def create_login_history(
    db: Session, user_id: str, session_id: str, ip_address: str, user_agent: str, success: bool
):
    """Create login history record"""
    db_login_history = LoginHistory(
        lh_user_id=user_id,
        lh_session_id=session_id,
        lh_ip_address=ip_address,
        lh_user_agent=user_agent,
        lh_success=success,
    )
    db.add(db_login_history)
    db.commit()
    db.refresh(db_login_history)
    return db_login_history


def update_user_last_login(db: Session, user_id: str):
    """Update user's last login timestamp"""
    db_user = db.query(UserAccount).filter(UserAccount.ua_user_id == user_id).first()
    if db_user:
        db_user.ua_last_login = datetime.utcnow()
        db_user.ua_login_attempts = 0
        db.commit()


def user_has_permission(db: Session, user_id: str, resource: str, action: str) -> bool:
    """Check if a user has a granted permission for a given resource/action pair."""
    now = datetime.utcnow()
    match = (
        db.query(RolePermission)
        .join(UserRole, RolePermission.rp_role_id == UserRole.ur_role_id)
        .join(Permission, RolePermission.rp_permission_id == Permission.pe_permission_id)
        .filter(
            UserRole.ur_user_id == user_id,
            RolePermission.rp_granted.is_(True),
            Permission.pe_resource == resource,
            Permission.pe_action == action,
            or_(UserRole.ur_expires_date.is_(None), UserRole.ur_expires_date > now),
        )
        .first()
    )
    return match is not None


def get_login_history_by_session_id(db: Session, session_id: str):
    """Get active login session by session ID"""
    return (
        db.query(LoginHistory)
        .filter(LoginHistory.lh_session_id == session_id, LoginHistory.lh_logout_time.is_(None))
        .first()
    )


def update_logout_time(db: Session, session_id: str):
    """Update logout time for a session"""
    db_login_history = get_login_history_by_session_id(db, session_id)
    if db_login_history:
        db_login_history.lh_logout_time = datetime.utcnow()
        db.commit()
