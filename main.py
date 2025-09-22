from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import hashlib
import secrets
import os

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./user_accounts.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Model
class UserAccount(Base):
    __tablename__ = "user_accounts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(10), nullable=False, unique=True)
    username = Column(String(25), nullable=False, unique=True)
    email = Column(String(40), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    salt = Column(String(32), nullable=False)
    user_role = Column(String(50), nullable=False)
    user_type = Column(Integer, nullable=False)
    mobile = Column(String(10))
    is_active = Column(Boolean, default=True)
    is_locked = Column(Boolean, default=False)
    failed_login_attempts = Column(Integer, default=0)
    last_login = Column(DateTime)
    password_changed_at = Column(DateTime)
    must_change_password = Column(Boolean, default=False)
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(32))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(10))
    updated_by = Column(String(10))

# Pydantic Models
class UserAccountBase(BaseModel):
    user_id: str
    username: str
    email: EmailStr
    user_role: str
    user_type: int
    mobile: Optional[str] = None
    is_active: bool = True
    is_locked: bool = False
    must_change_password: bool = False
    two_factor_enabled: bool = False
    created_by: Optional[str] = None

class UserAccountCreate(UserAccountBase):
    password: str

class UserAccountUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    user_role: Optional[str] = None
    user_type: Optional[int] = None
    mobile: Optional[str] = None
    is_active: Optional[bool] = None
    is_locked: Optional[bool] = None
    must_change_password: Optional[bool] = None
    two_factor_enabled: Optional[bool] = None
    updated_by: Optional[str] = None

class UserAccountResponse(UserAccountBase):
    id: int
    failed_login_attempts: int
    last_login: Optional[datetime] = None
    password_changed_at: Optional[datetime] = None
    two_factor_secret: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    updated_by: Optional[str] = None
    
    class Config:
        from_attributes = True

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(title="User Accounts API", version="1.0.0")

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Utility functions
def generate_salt():
    return secrets.token_hex(16)

def hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()

def verify_password(password: str, salt: str, password_hash: str) -> bool:
    return hash_password(password, salt) == password_hash

def generate_user_id():
    return secrets.token_hex(5).upper()

# API Endpoints
@app.get("/")
async def root():
    return {"message": "User Accounts API is running"}

@app.post("/users/", response_model=UserAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserAccountCreate, db: Session = Depends(get_db)):
    # Check if user_id, username, or email already exists
    existing_user = db.query(UserAccount).filter(
        (UserAccount.user_id == user.user_id) |
        (UserAccount.username == user.username) |
        (UserAccount.email == user.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID, username, or email already exists"
        )
    
    # Generate salt and hash password
    salt = generate_salt()
    password_hash = hash_password(user.password, salt)
    
    # Create user account
    db_user = UserAccount(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        password_hash=password_hash,
        salt=salt,
        user_role=user.user_role,
        user_type=user.user_type,
        mobile=user.mobile,
        is_active=user.is_active,
        is_locked=user.is_locked,
        must_change_password=user.must_change_password,
        two_factor_enabled=user.two_factor_enabled,
        password_changed_at=datetime.utcnow(),
        created_by=user.created_by
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.get("/users/", response_model=List[UserAccountResponse])
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(UserAccount).offset(skip).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=UserAccountResponse)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(UserAccount).filter(UserAccount.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@app.put("/users/{user_id}", response_model=UserAccountResponse)
async def update_user(user_id: str, user_update: UserAccountUpdate, db: Session = Depends(get_db)):
    user = db.query(UserAccount).filter(UserAccount.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    return user

@app.delete("/users/{user_id}")
async def delete_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(UserAccount).filter(UserAccount.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}

@app.post("/users/{user_id}/change-password")
async def change_password(user_id: str, password_data: PasswordChange, db: Session = Depends(get_db)):
    user = db.query(UserAccount).filter(UserAccount.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify current password
    if not verify_password(password_data.current_password, user.salt, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Generate new salt and hash new password
    new_salt = generate_salt()
    new_password_hash = hash_password(password_data.new_password, new_salt)
    
    # Update password
    user.salt = new_salt
    user.password_hash = new_password_hash
    user.password_changed_at = datetime.utcnow()
    user.must_change_password = False
    user.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Password changed successfully"}

@app.post("/users/{user_id}/lock")
async def lock_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(UserAccount).filter(UserAccount.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_locked = True
    user.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "User locked successfully"}

@app.post("/users/{user_id}/unlock")
async def unlock_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(UserAccount).filter(UserAccount.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_locked = False
    user.failed_login_attempts = 0
    user.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "User unlocked successfully"}

@app.get("/users/{user_id}/login-attempts")
async def get_login_attempts(user_id: str, db: Session = Depends(get_db)):
    user = db.query(UserAccount).filter(UserAccount.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "user_id": user_id,
        "failed_login_attempts": user.failed_login_attempts,
        "is_locked": user.is_locked
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)