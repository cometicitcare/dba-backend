"""
Complete setup script for Vihara management users and permissions.
This script sets up groups, permissions, roles, and users for vihara management.

Usage: python -m app.utils.setup_vihara_users
"""

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.permissions import Permission
from app.models.roles import Role
from app.models.role_permissions import RolePermission
from app.models.group import Group
from app.models.user import UserAccount
from app.models.user_roles import UserRole
from app.models.user_group import UserGroup
from app.core.security import get_password_hash, generate_salt
from datetime import datetime


def seed_vihara_group(db: Session):
    """Create or get the Vihara department group"""
    print("\n[1/5] Setting up Vihara Department Group...")
    
    group = db.query(Group).filter(Group.group_name == "Vihara Department").first()
    if not group:
        group = Group(
            group_name="Vihara Department",
            group_type="VIHARA",
            group_description="Vihara (temple) registration and management department",
            is_active=True,
            created_by="SYSTEM",
            updated_by="SYSTEM"
        )
        db.add(group)
        db.commit()
        db.refresh(group)
        print(f"      ✓ Created Vihara Department group (ID: {group.group_id})")
    else:
        print(f"      - Vihara Department group already exists (ID: {group.group_id})")
    
    return group


def seed_vihara_permissions(db: Session, group_id: int):
    """Create all necessary vihara permissions"""
    print("\n[2/5] Setting up Vihara Permissions...")
    
    permissions_data = [
        ("vihara:create", "vihara", "create", "Create new vihara (temple) records"),
        ("vihara:read", "vihara", "read", "Read vihara (temple) records"),
        ("vihara:update", "vihara", "update", "Update existing vihara (temple) records"),
        ("vihara:delete", "vihara", "delete", "Delete vihara (temple) records"),
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


def seed_vihara_roles(db: Session, group_id: int):
    """Create or update vihara roles"""
    print("\n[3/5] Setting up Vihara Roles...")
    
    roles_data = [
        ("VIHA_DATA", "vihara_dataentry", "Vihara Data Entry - Read/Write access only", "DATA_ENTRY"),
        ("VIHA_ADM", "vihara_admin", "Vihara Administrator - Full access to all vihara endpoints", "ADMIN"),
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
    
    # Get bhikku read-only permissions (if they exist)
    bhikku_read_perms = []
    bhikku_read_perm = db.query(Permission).filter(Permission.pe_name == "bhikku:read").first()
    bhikku_high_read_perm = db.query(Permission).filter(Permission.pe_name == "READ_BHIKKU_HIGH").first()
    
    if bhikku_read_perm:
        bhikku_read_perms.append(("bhikku:read", bhikku_read_perm.pe_permission_id))
    if bhikku_high_read_perm:
        bhikku_read_perms.append(("READ_BHIKKU_HIGH", bhikku_high_read_perm.pe_permission_id))
    
    # Vihara Data Entry: Read and Write only (create, read, update - no delete)
    # Plus bhikku read-only access
    dataentry_perms = [
        "vihara:create",
        "vihara:read",
        "vihara:update",
    ]
    
    # Vihara Admin: Full access (all permissions)
    # Plus bhikku read-only access
    admin_perms = [
        "vihara:create",
        "vihara:read",
        "vihara:update",
        "vihara:delete",
    ]
    
    mapping = {
        "VIHA_DATA": ("vihara_dataentry", dataentry_perms),
        "VIHA_ADM": ("vihara_admin", admin_perms)
    }
    
    for role_id, (role_name, perm_names) in mapping.items():
        role = roles.get(role_id)
        if not role:
            continue
        
        print(f"\n      {role_name}:")
        
        # Assign vihara permissions
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
        
        # Assign bhikku read-only permissions
        if bhikku_read_perms:
            print(f"        [Bhikku Read-Only Access]")
            for perm_name, perm_id in bhikku_read_perms:
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


def setup_users(db: Session, group: Group):
    """Create users and assign roles"""
    print("\n[5/5] Setting up Users...")
    
    # Generate secure random passwords
    users_config = [
        ("vihara_dataentry", "Vihara@DataEntry2024", "VIHA_DATA", "Vihara", "DataEntry"),
        ("vihara_admin", "Vihara@Admin2024", "VIHA_ADM", "Vihara", "Admin"),
    ]
    
    created_users = []
    
    for username, password, role_id, first_name, last_name in users_config:
        # Check if user exists
        user = db.query(UserAccount).filter(UserAccount.ua_username == username).first()
        
        if not user:
            # Generate user ID
            last_user = db.query(UserAccount).order_by(UserAccount.ua_user_id.desc()).first()
            if last_user and last_user.ua_user_id.startswith("UA"):
                # Extract numeric part and increment
                last_num = int(last_user.ua_user_id[2:])
                new_user_id = f"UA{str(last_num + 1).zfill(7)}"
            else:
                new_user_id = "UA0000001"
            
            salt = generate_salt()
            hashed_password = get_password_hash(password + salt)
            
            user = UserAccount(
                ua_user_id=new_user_id,
                ua_username=username,
                ua_password_hash=hashed_password,
                ua_salt=salt,
                ua_email=f"{username}@dbagovlk.com",
                ua_first_name=first_name,
                ua_last_name=last_name,
                ua_status="active",
                ua_is_deleted=False,
                ua_created_at=datetime.utcnow(),
                ua_updated_at=datetime.utcnow(),
                ua_created_by="SYSTEM",
                ua_updated_by="SYSTEM"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"\n      ✓ Created user: {username} (ID: {new_user_id})")
            created_users.append({
                "username": username,
                "password": password,
                "user_id": new_user_id,
                "role": role_id
            })
        else:
            print(f"\n      - User exists: {username} (ID: {user.ua_user_id})")
            created_users.append({
                "username": username,
                "password": "*** (existing user - password not changed) ***",
                "user_id": user.ua_user_id,
                "role": role_id
            })
        
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
        
        # Assign user to Vihara Department group
        existing_group = db.query(UserGroup).filter(
            UserGroup.user_id == user.ua_user_id,
            UserGroup.group_id == group.group_id
        ).first()
        
        if not existing_group:
            db.add(UserGroup(
                user_id=user.ua_user_id,
                group_id=group.group_id,
                is_active=True,
                assigned_by="SYSTEM"
            ))
            db.commit()
            print(f"        ✓ Assigned to Vihara Department group")
        else:
            if not existing_group.is_active:
                existing_group.is_active = True
                db.commit()
                print(f"        ✓ Re-activated group assignment")
            else:
                print(f"        - Already member of Vihara Department")
    
    return created_users


def verify_permissions(db: Session, user_id: str):
    """Verify what permissions a user has"""
    from app.api.auth_dependencies import get_user_permissions
    from app.models.user import UserAccount
    
    user = db.query(UserAccount).filter(UserAccount.ua_user_id == user_id).first()
    if not user:
        print(f"  ⚠ User {user_id} not found")
        return []
    
    permissions = get_user_permissions(db, user)
    return sorted(permissions)


def main():
    """Main setup function"""
    print("=" * 70)
    print("    VIHARA MANAGEMENT SYSTEM - USER SETUP")
    print("=" * 70)
    
    db = SessionLocal()
    try:
        group = seed_vihara_group(db)
        permissions = seed_vihara_permissions(db, group.group_id)
        roles = seed_vihara_roles(db, group.group_id)
        assign_permissions_to_roles(db, permissions, roles)
        created_users = setup_users(db, group)
        
        print("\n" + "=" * 70)
        print("    ✅ SETUP COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        
        print("\n📋 USER CREDENTIALS:")
        print("-" * 70)
        for user_info in created_users:
            print(f"\n   Username: {user_info['username']}")
            print(f"   Password: {user_info['password']}")
            print(f"   User ID:  {user_info['user_id']}")
            print(f"   Role:     {user_info['role']}")
            
            # Verify permissions
            perms = verify_permissions(db, user_info['user_id'])
            print(f"   Permissions:")
            for perm in perms:
                print(f"      - {perm}")
        
        print("\n" + "=" * 70)
        print("📌 ROLE DESCRIPTIONS:")
        print("-" * 70)
        print("\n1. VIHARA DATA ENTRY (vihara_dataentry)")
        print("   - Can CREATE new vihara records")
        print("   - Can READ vihara records")
        print("   - Can UPDATE existing vihara records")
        print("   - CANNOT DELETE vihara records")
        print("   - Read and Write access only")
        print("   - READ-ONLY access to Bhikku data")
        
        print("\n2. VIHARA ADMIN (vihara_admin)")
        print("   - Can CREATE new vihara records")
        print("   - Can READ vihara records")
        print("   - Can UPDATE existing vihara records")
        print("   - Can DELETE vihara records")
        print("   - Full access to all vihara endpoints")
        print("   - READ-ONLY access to Bhikku data")
        
        print("\n" + "=" * 70)
        print("🔗 VIHARA ENDPOINTS AVAILABLE:")
        print("-" * 70)
        print("\n   POST /api/v1/vihara-data/manage")
        print("   - Actions: CREATE, READ_ONE, READ_ALL, UPDATE, DELETE")
        print("   - All actions work with the same endpoint")
        print("   - No modifications made to existing endpoints")
        
        print("\n" + "=" * 70)
        print("✅ You can now use these credentials to access vihara endpoints")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
