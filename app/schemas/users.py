from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    ua_user_id: str
    ua_username: str
    ua_email: EmailStr
    password: str


class UserOut(BaseModel):
    ua_user_id: str
    ua_username: str
    ua_email: EmailStr
    ua_first_name: str | None = None
    ua_last_name: str | None = None


    class Config:
        from_attributes = True