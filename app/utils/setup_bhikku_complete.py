"""
Complete setup script for Bhikku management system.
This script sets up groups, permissions, roles, and users in one go.

Usage: python -m app.utils.setup_bhikku_complete
"""

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.permissions import Permission
from app.models.roles import Role
from app.models.role_permissions import RolePermission
from app.models.group import Group
from app.models.user import UserAccount
from app.models.user_roles import UserRole
from app.core.security import get_password_hash, generate_salt
from datetime import datetime


def seed_bhikku_group(db: Session):
    """Create or get the Bhikku department group"""
    print("\n[1/5] Setting up Bhikku Department Group...")
    
    group = db.query(Group).filter(Group.group_name == "Bhikku Department").first()
    if not group:
        group = Group(
            group_name="Bhikku Department",
            group_type="BHIKKU",
            group_description="Bhikku registration and management department",
            is_active=True,
            created_by="SYSTEM",
            updated_by="SYSTEM"
        )
        db.add(group)
        db.commit()
        db.refresh(group)
        print(f"      ✓ Created Bhikku Department group (ID: {group.group_id})")
    else:
        print(f"      - Bhikku Department group already exists (ID: {group.group_id})")
    
    return group


def seed_bhikku_permissions(db: Session, group_id: int):
    """Create all necessary bhikku permissions"""
    print("\n[2/5] Setting up Bhikku Permissions...")
    
    permissions_data = [
        ("bhikku:create", "bhikku", "create", "Create new bhikku records"),
        ("bhikku:read", "bhikku", "read", "Read bhikku records"),
        ("bhikku:update", "bhikku", "update", "Update existing bhikku records"),
        ("bhikku:delete", "bhikku", "delete", "Delete bhikku records"),
        ("CREATE_BHIKKU_HIGH", "bhikku_high", "create", "Create higher ordination records"),
        ("READ_BHIKKU_HIGH", "bhikku_high", "read", "Read higher ordination records"),
        ("UPDATE_BHIKKU_HIGH", "bhikku_high", "update", "Update higher ordination records"),
        ("DELETE_BHIKKU_HIGH", "bhikku_high", "delete", "Delete higher ordination records"),
        ("bhikku:manage_id_card", "bhikku_id_card", "manage", "Manage bhikku ID cards"),
        ("bhikku:manage_certificate", "bhikku_certification", "manage", "Manage bhikku certifications"),
    ]
    
    created_permissions = {}
    for name, resource, action, description in permissions_data:
        existing = db.query(Permission).filter(Permission.pe_name == name).first()
        if not existing:
            permission = Permission(
                pe_name=name,
                pe_resource=resource,
                pe_action=action,
                pe_description=description,
                group_id=group_id,
                pe_created_by="SYSTEM",
                pe_updated_by="SYSTEM"
            )
            db.add(permission)
            db.flush()
            created_permissions[name] = permission.pe_permission_id
            print(f"      ✓ Created: {name}")
        else:
            created_permissions[name] = existing.pe_permission_id
            print(f"      - Exists: {name}")
    
    db.commit()
    return created_permissions


def seed_bhikku_roles(db: Session, group_id: int):
    """Create or update bhikku roles"""
    print("\n[3/5] Setting up Bhikku Roles...")
    
    roles_data = [
        ("BHIK_ADM", "bhikku_admin", "Bhikku Administrator - Full access", "ADMIN"),
        ("BHIK_DATA", "bhikku_dataentry", "Bhikku Data Entry - Create/Update access", "DATA_ENTRY"),
    ]
    
    created_roles = {}
    for role_id, role_name, description, level in roles_data:
        existing = db.query(Role).filter(Role.ro_role_id == role_id).first()
        if not existing:
            role = Role(
                ro_role_id=role_id,
                ro_role_name=role_name,
                ro_description=description,
                ro_level=level,
                ro_department_id=group_id,
                ro_is_system_role=True,
                ro_is_active=True,
                ro_created_by="SYSTEM",
                ro_updated_by="SYSTEM"
            )
            db.add(role)
            db.flush()
            created_roles[role_id] = role
            print(f"      ✓ Created: {role_name} ({role_id})")
        else:
            created_roles[role_id] = existing
            print(f"      - Exists: {role_name} ({role_id})")
    
    db.commit()
    return created_roles


def assign_permissions_to_roles(db: Session, permissions: dict, roles: dict):
    """Assign permissions to roles"""
    print("\n[4/5] Assigning Permissions to Roles...")
    
    # Bhikku Admin: Full access (all permissions)
    admin_perms = [
        "bhikku:create", "bhikku:read", "bhikku:update", "bhikku:delete",
        "CREATE_BHIKKU_HIGH", "READ_BHIKKU_HIGH", "UPDATE_BHIKKU_HIGH", "DELETE_BHIKKU_HIGH",
        "bhikku:manage_id_card", "bhikku:manage_certificate"
    ]
    
    # Bhikku Data Entry: Create, read, update (no delete)
    dataentry_perms = [
        "bhikku:create", "bhikku:read", "bhikku:update",
        "CREATE_BHIKKU_HIGH", "READ_BHIKKU_HIGH", "UPDATE_BHIKKU_HIGH",
        "bhikku:manage_id_card", "bhikku:manage_certificate"
    ]
    
    mapping = {
        "BHIK_ADM": ("bhikku_admin", admin_perms),
        "BHIK_DATA": ("bhikku_dataentry", dataentry_perms)
    }
    
    for role_id, (role_name, perm_names) in mapping.items():
        role = roles.get(role_id)
        if not role:
            continue
        
        print(f"\n      {role_name}:")
        for perm_name in perm_names:
            perm_id = permissions.get(perm_name)
            if not perm_id:
                continue
            
            existing = db.query(RolePermission).filter(
                RolePermission.rp_role_id == role_id,
                RolePermission.rp_permission_id == perm_id
            ).first()
            
            if not existing:
                db.add(RolePermission(
                    rp_role_id=role_id,
                    rp_permission_id=perm_id,
                    rp_granted=True
                ))
                print(f"        ✓ {perm_name}")
            else:
                existing.rp_granted = True
                print(f"        - {perm_name}")
    
    db.commit()


def setup_users(db: Session):
    """Create users and assign roles"""
    print("\n[5/5] Setting up Users...")
    
    users_config = [
        ("bhikku_admin", "Bhikku@123", "BHIK_ADM", "Bhikku", "Admin"),
        ("bhikku_dataentry", "Bhikku@123", "BHIK_DATA", "Bhikku", "DataEntry"),
    ]
    
    for username, password, role_id, first_name, last_name in users_config:
        # Check if user exists
        user = db.query(UserAccount).filter(UserAccount.ua_username == username).first()
        
        if not user:
            # Generate user ID
            last_user = db.query(UserAccount).order_by(UserAccount.ua_user_id.desc()).first()
            if last_user and last_user.ua_user_id.startswith("USR"):
                last_num = int(last_user.ua_user_id[3:])
                new_user_id = f"USR{str(last_num + 1).zfill(7)}"
            else:
                new_user_id = "USR0000001"
            
            salt = generate_salt()
            hashed_password = get_password_hash(password + salt)
            
            user = UserAccount(
                ua_user_id=new_user_id,
                ua_username=username,
                ua_password=hashed_password,
                ua_salt=salt,
                ua_email=f"{username}@dbagovlk.com",
                ua_first_name=first_name,
                ua_last_name=last_name,
                ua_status="active",
                ua_is_deleted=False
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"\n      ✓ Created user: {username} (ID: {new_user_id})")
        else:
            print(f"\n      - User exists: {username} (ID: {user.ua_user_id})")
        
        # Assign role
        existing_role = db.query(UserRole).filter(
            UserRole.ur_user_id == user.ua_user_id,
            UserRole.ur_role_id == role_id
        ).first()
        
        if not existing_role:
            db.add(UserRole(
                ur_user_id=user.ua_user_id,
                ur_role_id=role_id,
                ur_is_active=True,
                ur_assigned_date=datetime.utcnow()
            ))
            db.commit()
            print(f"        ✓ Assigned role: {role_id}")
        else:
            if not existing_role.ur_is_active:
                existing_role.ur_is_active = True
                db.commit()
                print(f"        ✓ Re-activated role: {role_id}")
            else:
                print(f"        - Role already assigned: {role_id}")


def main():
    """Main setup function"""
    print("=" * 70)
    print("    BHIKKU MANAGEMENT SYSTEM - COMPLETE SETUP")
    print("=" * 70)
    
    db = SessionLocal()
    try:
        group = seed_bhikku_group(db)
        permissions = seed_bhikku_permissions(db, group.group_id)
        roles = seed_bhikku_roles(db, group.group_id)
        assign_permissions_to_roles(db, permissions, roles)
        setup_users(db)
        
        print("\n" + "=" * 70)
        print("✅ SETUP COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\nCreated Users:")
        print("  1. Username: bhikku_admin")
        print("     Password: Bhikku@123")
        print("     Role: Bhikku Administrator (Full Access)")
        print()
        print("  2. Username: bhikku_dataentry")
        print("     Password: Bhikku@123")
        print("     Role: Bhikku Data Entry (Create/Update Access)")
        print("\nBoth users can now access:")
        print("  - POST https://api.dbagovlk.com/api/v1/bhikkus-high/manage")
        print("  - All bhikku management endpoints")
        print("=" * 70)
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
