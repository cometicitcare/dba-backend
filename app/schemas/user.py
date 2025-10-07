# app/schemas/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    ua_username: str
    ua_password: str
    ua_email: EmailStr
    ua_full_name: Optional[str] = None


class UserLogin(BaseModel):
    ua_username: str
    ua_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None