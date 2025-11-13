from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserGroupBase(BaseModel):
    user_id: str
    group_id: int
    created_by: str

class UserGroupCreate(UserGroupBase):
    pass

class UserGroupUpdate(UserGroupBase):
    updated_by: str

class UserGroupOut(UserGroupBase):
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True  # This tells Pydantic to treat the SQLAlchemy model as a dict