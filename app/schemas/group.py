from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class GroupBase(BaseModel):
    group_name: str
    group_description: Optional[str] = None

class GroupCreate(GroupBase):
    created_by: str

class GroupUpdate(GroupBase):
    updated_by: str

class GroupOut(GroupBase):
    group_id: int
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str

    class Config:
        orm_mode = True  # This tells Pydantic to treat the SQLAlchemy model as a dict

class GroupListResponse(BaseModel):
    status: str
    message: str
    data: list[GroupOut]
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None