"""
Utility script to assign bhikku roles to users and verify permissions.
Usage: python -m app.utils.assign_bhikku_roles
"""

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import UserAccount
from app.models.roles import Role
from app.models.user_roles import UserRole
from app.core.security import get_password_hash, generate_salt
from datetime import datetime


def create_user_if_not_exists(db: Session, username: str, password: str, role_id: str, full_name: str):
    """Create a user if they don't exist"""
    user = db.query(UserAccount).filter(UserAccount.ua_username == username).first()
    
    if not user:
        # Generate user ID
        last_user = db.query(UserAccount).order_by(UserAccount.ua_user_id.desc()).first()
        if last_user and last_user.ua_user_id.startswith("USR"):
            last_number = int(last_user.ua_user_id[3:])
            new_user_id = f"USR{str(last_number + 1).zfill(7)}"
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
            ua_first_name=full_name.split()[0],
            ua_last_name=" ".join(full_name.split()[1:]) if len(full_name.split()) > 1 else "",
            ua_status="active",
            ua_is_deleted=False,
            ua_created_at=datetime.utcnow(),
            ua_updated_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✓ Created user: {username} (ID: {new_user_id})")
    else:
        print(f"- User already exists: {username} (ID: {user.ua_user_id})")
    
    return user


def assign_role_to_user(db: Session, user_id: str, role_id: str):
    """Assign a role to a user"""
    existing = db.query(UserRole).filter(
        UserRole.ur_user_id == user_id,
        UserRole.ur_role_id == role_id
    ).first()
    
    if not existing:
        user_role = UserRole(
            ur_user_id=user_id,
            ur_role_id=role_id,
            ur_is_active=True,
            ur_assigned_date=datetime.utcnow()
        )
        db.add(user_role)
        db.commit()
        print(f"  ✓ Assigned role {role_id} to user {user_id}")
    else:
        if not existing.ur_is_active:
            existing.ur_is_active = True
            db.commit()
            print(f"  ✓ Re-activated role {role_id} for user {user_id}")
        else:
            print(f"  - Role {role_id} already assigned to user {user_id}")


def verify_permissions(db: Session, user_id: str):
    """Verify what permissions a user has"""
    from app.api.auth_dependencies import get_user_permissions
    from app.models.user import UserAccount
    
    user = db.query(UserAccount).filter(UserAccount.ua_user_id == user_id).first()
    if not user:
        print(f"  ⚠ User {user_id} not found")
        return
    
    permissions = get_user_permissions(db, user)
    print(f"\n  Permissions for {user.ua_username}:")
    for perm in sorted(permissions):
        print(f"    - {perm}")


def main():
    """Main function to set up bhikku users"""
    print("=" * 70)
    print("Setting up Bhikku Users and Role Assignments")
    print("=" * 70)
    
    db = SessionLocal()
    try:
        # Verify roles exist
        print("\n1. Verifying roles exist...")
        bhik_admin_role = db.query(Role).filter(Role.ro_role_id == "BHIK_ADM").first()
        bhik_data_role = db.query(Role).filter(Role.ro_role_id == "BHIK_DATA").first()
        
        if not bhik_admin_role or not bhik_data_role:
            print("\n❌ Error: Bhikku roles not found!")
            print("Please run seed_bhikku_permissions.py first:")
            print("  python -m app.utils.seed_bhikku_permissions")
            return
        
        print(f"✓ Found role: {bhik_admin_role.ro_role_name}")
        print(f"✓ Found role: {bhik_data_role.ro_role_name}")
        
        # Users to set up
        users_config = [
            {
                "username": "bhikku_admin",
                "password": "Bhikku@123",
                "role_id": "BHIK_ADM",
                "full_name": "Bhikku Admin"
            },
            {
                "username": "bhikku_dataentry",
                "password": "Bhikku@123",
                "role_id": "BHIK_DATA",
                "full_name": "Bhikku Data Entry"
            }
        ]
        
        print("\n2. Setting up users and role assignments...")
        for user_config in users_config:
            print(f"\n   User: {user_config['username']}")
            user = create_user_if_not_exists(
                db,
                username=user_config["username"],
                password=user_config["password"],
                role_id=user_config["role_id"],
                full_name=user_config["full_name"]
            )
            assign_role_to_user(db, user.ua_user_id, user_config["role_id"])
            verify_permissions(db, user.ua_user_id)
        
        print("\n" + "=" * 70)
        print("✅ User setup completed successfully!")
        print("=" * 70)
        print("\nUsers ready to use:")
        print("  1. Username: bhikku_admin")
        print("     Password: Bhikku@123")
        print("     Role: Bhikku Administrator (Full Access)")
        print()
        print("  2. Username: bhikku_dataentry")
        print("     Password: Bhikku@123")
        print("     Role: Bhikku Data Entry (Create/Update Access)")
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
