# app/schemas/permission.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PermissionBase(BaseModel):
    pe_name: str  # Permission name, should be unique
    pe_resource: str  # The resource this permission applies to (e.g., "BhikkuHigh")
    pe_action: str  # The action allowed by this permission (e.g., "CREATE")
    pe_description: Optional[str] = None  # Description of the permission
    group_id: int  # The group this permission belongs to
    pe_code: Optional[str] = None  # Unique code for the permission (e.g., CREATE_BHIKKU_HIGH_1)

class PermissionCreate(PermissionBase):
    pe_created_by: str  # User who created the permission

class PermissionUpdate(PermissionBase):
    pe_updated_by: str  # User who updated the permission

class PermissionOut(PermissionBase):
    pe_permission_id: int  # ID of the permission
    pe_created_at: datetime  # Timestamp when the permission was created
    pe_updated_at: datetime  # Timestamp when the permission was last updated
    pe_created_by: str  # User who created the permission
    pe_updated_by: str  # User who last updated the permission

    class Config:
        orm_mode = True  # This tells Pydantic to treat the SQLAlchemy model as a dict

class PermissionListResponse(BaseModel):
    status: str
    message: str
    data: list[PermissionOut]
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None
