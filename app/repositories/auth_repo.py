# app/repositories/auth_repo.py
from sqlalchemy.orm import Session
from app.models.user import UserAccount, LoginHistory
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, generate_salt
from datetime import datetime
import uuid # Import uuid

def create_user(db: Session, user: UserCreate):
    salt = generate_salt()
    hashed_password = get_password_hash(user.ua_password + salt)
    
    # Generate a unique string ID for the new user
    user_id = f"UA{str(uuid.uuid4().int)[:9]}" 

    db_user = UserAccount(
        ua_id=user_id, # Assign the generated string ID
        ua_username=user.ua_username,
        ua_password_hash=hashed_password,
        ua_salt=salt,
        ua_email=user.ua_email,
        ua_full_name=user.ua_full_name,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_username(db: Session, username: str):
    return db.query(UserAccount).filter(UserAccount.ua_username == username).first()


def create_login_history(
    db: Session, user_id: str, session_id: str, ip_address: str, user_agent: str, success: bool
):
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
    db_user = db.query(UserAccount).filter(UserAccount.ua_id == user_id).first()
    if db_user:
        db_user.ua_last_login = datetime.utcnow()
        db_user.ua_login_attempts = 0
        db.commit()


def get_login_history_by_session_id(db: Session, session_id: str):
    return (
        db.query(LoginHistory)
        .filter(LoginHistory.lh_session_id == session_id, LoginHistory.lh_logout_time.is_(None))
        .first()
    )


def update_logout_time(db: Session, session_id: str):
    db_login_history = get_login_history_by_session_id(db, session_id)
    if db_login_history:
        db_login_history.lh_logout_time = datetime.utcnow()
        db.commit()