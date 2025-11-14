# app/services/rbac_service.py
"""
RBAC Management Service
Business logic for managing user roles, groups, and permissions
"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from fastapi import HTTPException

from app.models.user import UserAccount
from app.models.user_roles import UserRole
from app.models.user_group import UserGroup
from app.models.user_permission import UserPermission
from app.models.roles import Role
from app.models.group import Group
from app.models.permissions import Permission
from app.api.auth_dependencies import get_user_access_context


class RBACService:
    """Service for RBAC administration operations"""
    
    def assign_role_to_user(
        self,
        db: Session,
        user_id: str,
        role_id: str,
        expires_days: Optional[int],
        is_active: bool,
        actor_id: str
    ) -> Tuple[bool, dict]:
        """
        Assign a role to a user
        Returns: (is_new, data_dict)
        """
        # Verify user exists
        user = db.query(UserAccount).filter(UserAccount.ua_user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User ID {user_id} not found")
        
        # Verify role exists
        role = db.query(Role).filter(Role.ro_role_id == role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail=f"Role '{role_id}' not found")
        
        # Check if assignment already exists
        existing = db.query(UserRole).filter(
            UserRole.ur_user_id == user_id,
            UserRole.ur_role_id == role_id
        ).first()
        
        expires_date = None
        if expires_days:
            expires_date = datetime.utcnow() + timedelta(days=expires_days)
        
        if existing:
            # Update existing assignment
            existing.ur_is_active = is_active
            existing.ur_expires_date = expires_date
            existing.ur_assigned_by = actor_id
            db.commit()
            is_new = False
        else:
            # Create new assignment
            user_role = UserRole(
                ur_user_id=user_id,
                ur_role_id=role_id,
                ur_is_active=is_active,
                ur_expires_date=expires_date,
                ur_assigned_by=actor_id
            )
            db.add(user_role)
            db.commit()
            is_new = True
        
        return is_new, {
            "user_id": user_id,
            "username": user.ua_username,
            "role_id": role_id,
            "role_name": role.ro_role_name,
            "is_active": is_active,
            "expires_date": expires_date.isoformat() if expires_date else None
        }
    
    def revoke_role_from_user(
        self,
        db: Session,
        user_id: str,
        role_id: str,
        actor_id: str
    ) -> dict:
        """Revoke a role from a user"""
        user_role = db.query(UserRole).filter(
            UserRole.ur_user_id == user_id,
            UserRole.ur_role_id == role_id
        ).first()
        
        if not user_role:
            raise HTTPException(
                status_code=404,
                detail=f"User ID {user_id} does not have role '{role_id}'"
            )
        
        # Deactivate instead of delete
        user_role.ur_is_active = False
        user_role.ur_assigned_by = actor_id
        db.commit()
        
        user = db.query(UserAccount).filter(UserAccount.ua_user_id == user_id).first()
        
        return {
            "user_id": user_id,
            "username": user.ua_username,
            "role_id": role_id
        }
    
    def assign_group_to_user(
        self,
        db: Session,
        user_id: str,
        group_id: str,
        actor_id: str
    ) -> Tuple[bool, dict]:
        """
        Add user to a group
        Returns: (is_new, data_dict)
        """
        # Verify user exists
        user = db.query(UserAccount).filter(UserAccount.ua_user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User ID {user_id} not found")
        
        # Verify group exists
        group = db.query(Group).filter(Group.group_id == group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail=f"Group '{group_id}' not found")
        
        # Check if already in group
        existing = db.query(UserGroup).filter(
            UserGroup.user_id == user_id,
            UserGroup.group_id == group_id
        ).first()
        
        if existing:
            if existing.is_active:
                return False, {
                    "user_id": user_id,
                    "username": user.ua_username,
                    "group_id": group_id,
                    "group_name": group.group_name,
                    "already_member": True
                }
            else:
                # Reactivate
                existing.is_active = True
                existing.modified_by = actor_id
                existing.modified_date = datetime.utcnow()
                db.commit()
                return False, {
                    "user_id": user_id,
                    "username": user.ua_username,
                    "group_id": group_id,
                    "group_name": group.group_name,
                    "reactivated": True
                }
        else:
            # Create new group assignment
            user_group = UserGroup(
                user_id=user_id,
                group_id=group_id,
                is_active=True,
                created_by=actor_id,
                created_date=datetime.utcnow()
            )
            db.add(user_group)
            db.commit()
            return True, {
                "user_id": user_id,
                "username": user.ua_username,
                "group_id": group_id,
                "group_name": group.group_name
            }
    
    def remove_group_from_user(
        self,
        db: Session,
        user_id: str,
        group_id: str,
        actor_id: str
    ) -> dict:
        """Remove user from a group"""
        user_group = db.query(UserGroup).filter(
            UserGroup.user_id == user_id,
            UserGroup.group_id == group_id
        ).first()
        
        if not user_group:
            raise HTTPException(
                status_code=404,
                detail=f"User ID {user_id} is not in group '{group_id}'"
            )
        
        # Deactivate
        user_group.is_active = False
        user_group.modified_by = actor_id
        user_group.modified_date = datetime.utcnow()
        db.commit()
        
        user = db.query(UserAccount).filter(UserAccount.ua_user_id == user_id).first()
        group = db.query(Group).filter(Group.group_id == group_id).first()
        
        return {
            "user_id": user_id,
            "username": user.ua_username,
            "group_id": group_id,
            "group_name": group.group_name
        }
    
    def override_user_permission(
        self,
        db: Session,
        user_id: str,
        permission_id: str,
        granted: bool,
        expires_days: Optional[int],
        is_active: bool,
        actor_id: str
    ) -> Tuple[bool, dict]:
        """
        Grant or deny a specific permission to a user
        Returns: (is_new, data_dict)
        """
        # Verify user exists
        user = db.query(UserAccount).filter(UserAccount.ua_user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User ID {user_id} not found")
        
        # Verify permission exists
        permission = db.query(Permission).filter(Permission.pe_permission_id == permission_id).first()
        if not permission:
            raise HTTPException(status_code=404, detail=f"Permission '{permission_id}' not found")
        
        # Check if override exists
        existing = db.query(UserPermission).filter(
            UserPermission.up_user_id == user_id,
            UserPermission.up_permission_id == permission_id
        ).first()
        
        expires_date = None
        if expires_days:
            expires_date = datetime.utcnow() + timedelta(days=expires_days)
        
        if existing:
            # Update existing override
            existing.up_granted = granted
            existing.up_is_active = is_active
            existing.up_expires_date = expires_date
            existing.up_assigned_by = actor_id
            db.commit()
            is_new = False
        else:
            # Create new override
            user_permission = UserPermission(
                up_user_id=user_id,
                up_permission_id=permission_id,
                up_granted=granted,
                up_is_active=is_active,
                up_expires_date=expires_date,
                up_assigned_by=actor_id
            )
            db.add(user_permission)
            db.commit()
            is_new = True
        
        return is_new, {
            "user_id": user_id,
            "username": user.ua_username,
            "permission_id": permission_id,
            "permission_name": permission.pe_name,
            "granted": granted,
            "expires_date": expires_date.isoformat() if expires_date else None
        }
    
    def remove_permission_override(
        self,
        db: Session,
        user_id: str,
        permission_id: str,
        actor_id: str
    ) -> dict:
        """Remove a permission override"""
        user_permission = db.query(UserPermission).filter(
            UserPermission.up_user_id == user_id,
            UserPermission.up_permission_id == permission_id
        ).first()
        
        if not user_permission:
            raise HTTPException(
                status_code=404,
                detail=f"No permission override found for user ID {user_id} and permission '{permission_id}'"
            )
        
        # Deactivate
        user_permission.up_is_active = False
        user_permission.up_assigned_by = actor_id
        db.commit()
        
        user = db.query(UserAccount).filter(UserAccount.ua_user_id == user_id).first()
        permission = db.query(Permission).filter(Permission.pe_permission_id == permission_id).first()
        
        return {
            "user_id": user_id,
            "username": user.ua_username,
            "permission_id": permission_id,
            "permission_name": permission.pe_name
        }
    
    def get_user_rbac_context(self, db: Session, user_id: str) -> dict:
        """Get complete RBAC context for a user"""
        user = db.query(UserAccount).filter(UserAccount.ua_user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User ID {user_id} not found")
        
        context = get_user_access_context(db, user)
        
        # Get permission overrides
        overrides = db.query(UserPermission).join(
            Permission,
            Permission.pe_permission_id == UserPermission.up_permission_id
        ).filter(
            UserPermission.up_user_id == user_id,
            UserPermission.up_is_active == True
        ).all()
        
        override_list = [
            {
                "permission_id": ov.up_permission_id,
                "permission_name": db.query(Permission.pe_name).filter(
                    Permission.pe_permission_id == ov.up_permission_id
                ).scalar(),
                "granted": ov.up_granted,
                "expires_date": ov.up_expires_date.isoformat() if ov.up_expires_date else None
            }
            for ov in overrides
        ]
        
        full_name = f"{user.ua_first_name or ''} {user.ua_last_name or ''}".strip() or user.ua_username
        
        return {
            "user_id": user_id,
            "username": user.ua_username,
            "full_name": full_name,
            "email": user.ua_email,
            "is_active": user.ua_status == "active",
            "roles": context.get("roles", []),
            "groups": context.get("groups", []),
            "permissions": context.get("permissions", []),
            "permission_overrides": override_list,
            "is_super_admin": context.get("is_super_admin", False),
            "is_admin": context.get("is_admin", False),
            "can_manage_users": context.get("can_manage_users", False)
        }
    
    def list_users_with_rbac(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[int, List[dict]]:
        """List all users with RBAC summary"""
        users = db.query(UserAccount).offset(skip).limit(limit).all()
        total = db.query(UserAccount).count()
        
        user_list = []
        for user in users:
            context = get_user_access_context(db, user)
            full_name = f"{user.ua_first_name or ''} {user.ua_last_name or ''}".strip() or user.ua_username
            
            user_list.append({
                "user_id": user.ua_user_id,
                "username": user.ua_username,
                "full_name": full_name,
                "email": user.ua_email,
                "is_active": user.ua_status == "active",
                "roles": [r["ro_role_name"] for r in context.get("roles", [])],
                "groups": [g["group_name"] for g in context.get("groups", [])],
                "is_super_admin": context.get("is_super_admin", False),
                "is_admin": context.get("is_admin", False)
            })
        
        return total, user_list


# Singleton instance
rbac_service = RBACService()
