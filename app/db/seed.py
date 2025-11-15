import os
import logging

from app.db.session import SessionLocal
from app.schemas.users import UserCreate
from app.services.user_service import user_service
from app.models.roles import Role
from app.models.group import Group
from app.models.user_roles import UserRole
from app.models.user_group import UserGroup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed() -> None:
    """Seed the database with initial data: roles, groups, and admin user."""
    db = SessionLocal()
    try:
        # 1. Create ADMIN role if it doesn't exist
        admin_role_id = os.getenv("SEED_ADMIN_ROLE_ID", "ADMIN")
        admin_role = db.query(Role).filter(Role.ro_role_id == admin_role_id).first()
        if not admin_role:
            admin_role = Role(
                ro_role_id=admin_role_id,
                ro_role_name="Administrator",
                ro_description="System administrator with full access",
                ro_level="SUPER_ADMIN",
                ro_is_system_role=True,
                ro_is_active=True,
            )
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
            logger.info(f"✓ Created role: {admin_role_id}")
        else:
            logger.info(f"Role {admin_role_id} already exists")

        # 2. Create SYSTEM group if it doesn't exist
        system_group = db.query(Group).filter(Group.group_name == "SYSTEM").first()
        if not system_group:
            system_group = Group(
                group_name="SYSTEM",
                group_type="SYSTEM",
                group_description="System administrators group",
                is_active=True,
                created_by="system",
            )
            db.add(system_group)
            db.commit()
            db.refresh(system_group)
            logger.info(f"✓ Created group: SYSTEM (id={system_group.group_id})")
        else:
            logger.info(f"Group SYSTEM already exists (id={system_group.group_id})")

        # 3. Create admin user
        admin_user_id = os.getenv("SEED_ADMIN_USER_ID", "admin0001")
        payload = UserCreate(
            ua_user_id=admin_user_id,
            ua_username=os.getenv("SEED_ADMIN_USERNAME", "admin"),
            ua_email=os.getenv("SEED_ADMIN_EMAIL", "admin@example.com"),
            ua_password=os.getenv("SEED_ADMIN_PASSWORD", "Admin@123"),
            ro_role_id=admin_role_id,
            ua_first_name=os.getenv("SEED_ADMIN_FIRST_NAME", "System"),
            ua_last_name=os.getenv("SEED_ADMIN_LAST_NAME", "Administrator"),
        )
        
        try:
            user = user_service.create_user(db, payload)
            logger.info(f"✓ Created admin user: {payload.ua_username}")
            
            # 4. Assign role to user (UserRole)
            user_role = db.query(UserRole).filter(
                UserRole.ur_user_id == admin_user_id,
                UserRole.ur_role_id == admin_role_id
            ).first()
            
            if not user_role:
                user_role = UserRole(
                    ur_user_id=admin_user_id,
                    ur_role_id=admin_role_id,
                    ur_is_active=True,
                    ur_assigned_by="system",
                )
                db.add(user_role)
                db.commit()
                logger.info(f"✓ Assigned role {admin_role_id} to user {admin_user_id}")
            
            # 5. Assign group to user (UserGroup)
            user_group = db.query(UserGroup).filter(
                UserGroup.user_id == admin_user_id,
                UserGroup.group_id == system_group.group_id
            ).first()
            
            if not user_group:
                user_group = UserGroup(
                    user_id=admin_user_id,
                    group_id=system_group.group_id,
                    is_active=True,
                    assigned_by="system",
                )
                db.add(user_group)
                db.commit()
                logger.info(f"✓ Assigned group SYSTEM to user {admin_user_id}")
                
            logger.info("="*50)
            logger.info("Database seeding completed successfully!")
            logger.info(f"Admin Username: {payload.ua_username}")
            logger.info(f"Admin Password: {payload.ua_password}")
            logger.info("="*50)
            
        except ValueError as exc:
            logger.info(f"Skipping admin user creation: {exc}")
            # Even if user exists, ensure role and group assignments exist
            
            user_role = db.query(UserRole).filter(
                UserRole.ur_user_id == admin_user_id,
                UserRole.ur_role_id == admin_role_id
            ).first()
            
            if not user_role:
                user_role = UserRole(
                    ur_user_id=admin_user_id,
                    ur_role_id=admin_role_id,
                    ur_is_active=True,
                    ur_assigned_by="system",
                )
                db.add(user_role)
                db.commit()
                logger.info(f"✓ Assigned role {admin_role_id} to existing user {admin_user_id}")
            
            user_group = db.query(UserGroup).filter(
                UserGroup.user_id == admin_user_id,
                UserGroup.group_id == system_group.group_id
            ).first()
            
            if not user_group:
                user_group = UserGroup(
                    user_id=admin_user_id,
                    group_id=system_group.group_id,
                    is_active=True,
                    assigned_by="system",
                )
                db.add(user_group)
                db.commit()
                logger.info(f"✓ Assigned group SYSTEM to existing user {admin_user_id}")
                
    except Exception as e:
        logger.error(f"✗ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()

