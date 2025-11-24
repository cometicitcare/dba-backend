"""
Seed script to set up Bhikku management roles and permissions.
This script creates the necessary permissions and assigns them to bhikku_admin and bhikku_dataentry roles.
"""

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.permissions import Permission
from app.models.roles import Role
from app.models.role_permissions import RolePermission
from app.models.group import Group
from datetime import datetime


def seed_bhikku_group(db: Session):
    """Create or get the Bhikku department group"""
    print("\n1. Setting up Bhikku Department Group...")
    
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
        print(f"✓ Created Bhikku Department group (ID: {group.group_id})")
    else:
        print(f"- Bhikku Department group already exists (ID: {group.group_id})")
    
    return group


def seed_bhikku_permissions(db: Session, group_id: int):
    """Create all necessary bhikku permissions"""
    print("\n2. Setting up Bhikku Permissions...")
    
    permissions_data = [
        # Bhikku basic permissions
        {
            "pe_name": "bhikku:create",
            "pe_resource": "bhikku",
            "pe_action": "create",
            "pe_description": "Create new bhikku records"
        },
        {
            "pe_name": "bhikku:read",
            "pe_resource": "bhikku",
            "pe_action": "read",
            "pe_description": "Read bhikku records"
        },
        {
            "pe_name": "bhikku:update",
            "pe_resource": "bhikku",
            "pe_action": "update",
            "pe_description": "Update existing bhikku records"
        },
        {
            "pe_name": "bhikku:delete",
            "pe_resource": "bhikku",
            "pe_action": "delete",
            "pe_description": "Delete bhikku records"
        },
        # Bhikku High (Higher Ordination) permissions
        {
            "pe_name": "CREATE_BHIKKU_HIGH",
            "pe_resource": "bhikku_high",
            "pe_action": "create",
            "pe_description": "Create higher ordination (upasampada) records"
        },
        {
            "pe_name": "READ_BHIKKU_HIGH",
            "pe_resource": "bhikku_high",
            "pe_action": "read",
            "pe_description": "Read higher ordination records"
        },
        {
            "pe_name": "UPDATE_BHIKKU_HIGH",
            "pe_resource": "bhikku_high",
            "pe_action": "update",
            "pe_description": "Update higher ordination records"
        },
        {
            "pe_name": "DELETE_BHIKKU_HIGH",
            "pe_resource": "bhikku_high",
            "pe_action": "delete",
            "pe_description": "Delete higher ordination records"
        },
        # Bhikku ID Card permissions
        {
            "pe_name": "bhikku:manage_id_card",
            "pe_resource": "bhikku_id_card",
            "pe_action": "manage",
            "pe_description": "Manage bhikku ID card workflows"
        },
        # Bhikku Certificate permissions
        {
            "pe_name": "bhikku:manage_certificate",
            "pe_resource": "bhikku_certification",
            "pe_action": "manage",
            "pe_description": "Manage bhikku certifications"
        }
    ]
    
    created_permissions = {}
    for perm_data in permissions_data:
        existing = db.query(Permission).filter(Permission.pe_name == perm_data["pe_name"]).first()
        if not existing:
            permission = Permission(
                pe_name=perm_data["pe_name"],
                pe_resource=perm_data["pe_resource"],
                pe_action=perm_data["pe_action"],
                pe_description=perm_data["pe_description"],
                group_id=group_id,
                pe_created_by="SYSTEM",
                pe_updated_by="SYSTEM"
            )
            db.add(permission)
            db.flush()
            created_permissions[perm_data["pe_name"]] = permission.pe_permission_id
            print(f"✓ Created permission: {perm_data['pe_name']}")
        else:
            created_permissions[perm_data["pe_name"]] = existing.pe_permission_id
            print(f"- Permission already exists: {perm_data['pe_name']}")
    
    db.commit()
    return created_permissions


def seed_bhikku_roles(db: Session, group_id: int):
    """Create or update bhikku roles"""
    print("\n3. Setting up Bhikku Roles...")
    
    roles_data = [
        {
            "ro_role_id": "BHIK_ADM",
            "ro_role_name": "bhikku_admin",
            "ro_description": "Bhikku Administrator - Full access to bhikku management",
            "ro_level": "ADMIN"
        },
        {
            "ro_role_id": "BHIK_DATA",
            "ro_role_name": "bhikku_dataentry",
            "ro_description": "Bhikku Data Entry - Can create and update bhikku records",
            "ro_level": "DATA_ENTRY"
        }
    ]
    
    created_roles = {}
    for role_data in roles_data:
        existing = db.query(Role).filter(Role.ro_role_id == role_data["ro_role_id"]).first()
        if not existing:
            role = Role(
                ro_role_id=role_data["ro_role_id"],
                ro_role_name=role_data["ro_role_name"],
                ro_description=role_data["ro_description"],
                ro_level=role_data["ro_level"],
                ro_department_id=group_id,
                ro_is_system_role=True,
                ro_is_active=True,
                ro_created_by="SYSTEM",
                ro_updated_by="SYSTEM"
            )
            db.add(role)
            db.flush()
            created_roles[role_data["ro_role_id"]] = role
            print(f"✓ Created role: {role_data['ro_role_name']} ({role_data['ro_role_id']})")
        else:
            created_roles[role_data["ro_role_id"]] = existing
            print(f"- Role already exists: {role_data['ro_role_name']} ({role_data['ro_role_id']})")
    
    db.commit()
    return created_roles


def assign_permissions_to_roles(db: Session, permissions: dict, roles: dict):
    """Assign permissions to roles"""
    print("\n4. Assigning Permissions to Roles...")
    
    # Bhikku Admin gets all permissions
    admin_permissions = [
        "bhikku:create",
        "bhikku:read",
        "bhikku:update",
        "bhikku:delete",
        "CREATE_BHIKKU_HIGH",
        "READ_BHIKKU_HIGH",
        "UPDATE_BHIKKU_HIGH",
        "DELETE_BHIKKU_HIGH",
        "bhikku:manage_id_card",
        "bhikku:manage_certificate"
    ]
    
    # Bhikku Data Entry gets create, read, update permissions (no delete)
    dataentry_permissions = [
        "bhikku:create",
        "bhikku:read",
        "bhikku:update",
        "CREATE_BHIKKU_HIGH",
        "READ_BHIKKU_HIGH",
        "UPDATE_BHIKKU_HIGH",
        "bhikku:manage_id_card",
        "bhikku:manage_certificate"
    ]
    
    role_permission_mapping = {
        "BHIK_ADM": admin_permissions,
        "BHIK_DATA": dataentry_permissions
    }
    
    for role_id, permission_names in role_permission_mapping.items():
        role = roles.get(role_id)
        if not role:
            print(f"⚠ Warning: Role {role_id} not found, skipping...")
            continue
        
        print(f"\n   Assigning permissions to {role.ro_role_name}:")
        for perm_name in permission_names:
            perm_id = permissions.get(perm_name)
            if not perm_id:
                print(f"   ⚠ Warning: Permission {perm_name} not found, skipping...")
                continue
            
            # Check if already assigned
            existing = db.query(RolePermission).filter(
                RolePermission.rp_role_id == role_id,
                RolePermission.rp_permission_id == perm_id
            ).first()
            
            if not existing:
                role_perm = RolePermission(
                    rp_role_id=role_id,
                    rp_permission_id=perm_id,
                    rp_granted=True
                )
                db.add(role_perm)
                print(f"   ✓ Assigned: {perm_name}")
            else:
                # Update to ensure it's granted
                existing.rp_granted = True
                print(f"   - Already assigned: {perm_name}")
    
    db.commit()
    print("\n✓ Permission assignments completed")


def main():
    """Main seeding function"""
    print("=" * 70)
    print("Seeding Bhikku Management Roles and Permissions")
    print("=" * 70)
    
    db = SessionLocal()
    try:
        # Step 1: Create/get group
        group = seed_bhikku_group(db)
        
        # Step 2: Create permissions
        permissions = seed_bhikku_permissions(db, group.group_id)
        
        # Step 3: Create roles
        roles = seed_bhikku_roles(db, group.group_id)
        
        # Step 4: Assign permissions to roles
        assign_permissions_to_roles(db, permissions, roles)
        
        print("\n" + "=" * 70)
        print("✅ Seeding completed successfully!")
        print("=" * 70)
        print("\nRoles created:")
        print("  - bhikku_admin (BHIK_ADM) - Full bhikku management access")
        print("  - bhikku_dataentry (BHIK_DATA) - Create and update access")
        print("\nUsers with these roles can now access bhikku management APIs.")
        print("=" * 70)
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error during seeding: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
