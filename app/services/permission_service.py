from sqlalchemy.orm import Session
from app.models.permissions import Permission
from app.models.user_roles import UserRole
from app.schemas.permission import PermissionCreate, PermissionUpdate
from app.utils.http_exceptions import validation_error
from app.models.role_permissions import RolePermission
from datetime import datetime

class PermissionService:

    def create_permission(self, db: Session, permission: PermissionCreate):
        # Create a new permission
        new_permission = Permission(
            pe_permission_name=permission.pe_name,
            pe_resource=permission.pe_resource,
            pe_action=permission.pe_action,
            pe_description=permission.pe_description,
            group_id=permission.group_id,
            created_by=permission.created_by,
            updated_by=permission.created_by,  # Initially the same as created_by
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        db.add(new_permission)
        db.commit()
        db.refresh(new_permission)
        return new_permission

    def update_permission(self, db: Session, permission_id: str, permission: PermissionUpdate):
        # Find the permission by ID
        existing_permission = db.query(Permission).filter(Permission.pe_permission_id == permission_id).first()
        if not existing_permission:
            raise validation_error([("permission_id", "Permission not found.")])
        
        # Update the permission
        existing_permission.pe_permission_name = permission.pe_name
        existing_permission.pe_resource = permission.pe_resource
        existing_permission.pe_action = permission.pe_action
        existing_permission.pe_description = permission.pe_description
        existing_permission.updated_by = permission.updated_by
        existing_permission.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(existing_permission)
        return existing_permission

    def get_permission_by_id(self, db: Session, permission_id: str):
        # Retrieve a specific permission by ID
        return db.query(Permission).filter(Permission.pe_permission_id == permission_id).first()

    def delete_permission(self, db: Session, permission_id: str):
        # Delete a permission
        permission_to_delete = db.query(Permission).filter(Permission.pe_permission_id == permission_id).first()
        if not permission_to_delete:
            raise validation_error([("permission_id", "Permission not found.")])
        
        db.delete(permission_to_delete)
        db.commit()
        return permission_to_delete
    
    def get_user_permissions(self, db: Session, user_id: str):
        # Get user's role
        user_role = db.query(UserRole).filter(UserRole.ur_user_id == user_id).first()
        if not user_role:
            raise Exception("User role not found")

        # Get permissions for the user's role
        permissions = db.query(Permission.pe_name).join(
            RolePermission,
            RolePermission.rp_permission_id == Permission.pe_permission_id
        ).filter(RolePermission.rp_role_id == user_role.ur_role_id).all()

        return [permission.pe_name for permission in permissions]


# Initialize the service
permission_service = PermissionService()