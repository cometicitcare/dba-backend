import os

from app.db.session import SessionLocal
from app.schemas.users import UserCreate
from app.services.user_service import user_service


def seed() -> None:
    db = SessionLocal()
    try:
        payload = UserCreate(
            ua_user_id=os.getenv("SEED_ADMIN_USER_ID", "admin0001"),
            ua_username=os.getenv("SEED_ADMIN_USERNAME", "admin"),
            ua_email=os.getenv("SEED_ADMIN_EMAIL", "admin@example.com"),
            ua_password=os.getenv("SEED_ADMIN_PASSWORD", "Admin@123"),
            ro_role_id=os.getenv("SEED_ADMIN_ROLE_ID", "ADMIN"),
            ua_first_name="System",
            ua_last_name="Administrator",
        )
        try:
            user_service.create_user(db, payload)
            print("Admin user created successfully.")
        except ValueError as exc:
            print(f"Skipping admin seed: {exc}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
