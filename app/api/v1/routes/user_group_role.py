from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.user import UserAccount
from app.models.group import Group
from app.models.role import Role
from app.models.permission import Permission
from app.models.user_group import UserGroup
from app.models.user_roles import UserRole
from app.schemas.user_group_role import UserGroupRoleResponse
from app.api.auth_middleware import get_current_user

router = APIRouter()  # Tags defined in router.py

@router.get("/user_group_role", response_model=UserGroupRoleResponse)
def get_user_group_role(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    user_id = current_user.ua_user_id
    
    # Fetch user's group and role information
    user_group = db.query(UserGroup).join(Group).filter(UserGroup.user_id == user_id).first()
    user_role = db.query(UserRole).join(Role).filter(UserRole.user_id == user_id).first()
    
    if not user_group or not user_role:
        raise HTTPException(status_code=404, detail="User group or role not found")

    permissions = db.query(Permission).filter(Permission.group_id == user_group.group_id).all()
    
    return UserGroupRoleResponse(
        user_id=user_id,
        group_name=user_group.group.group_name,
        role_name=user_role.role.role_name,
        permissions=[permission.pe_name for permission in permissions]
    )
