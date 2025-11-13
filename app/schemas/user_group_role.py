from pydantic import BaseModel
from typing import List

class UserGroupRoleResponse(BaseModel):
    user_id: str
    group_name: str
    role_name: str
    permissions: List[str]  # List of permissions for the user's role

    class Config:
        orm_mode = True