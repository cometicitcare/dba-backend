from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import generate_salt, get_password_hash
from app.models.user import Role, UserAccount
from app.schemas.users import UserCreate


class UserService:
    """Business logic for user accounts."""

    def create_user(self, db: Session, payload: UserCreate) -> UserAccount:
        """Create a user after enforcing uniqueness and role validity."""
        if (
            db.query(UserAccount)
            .filter(UserAccount.ua_user_id == payload.ua_user_id)
            .first()
        ):
            raise ValueError("ua_user_id already exists.")

        if (
            db.query(UserAccount)
            .filter(UserAccount.ua_username == payload.ua_username)
            .first()
        ):
            raise ValueError("ua_username already exists.")

        if (
            db.query(UserAccount)
            .filter(UserAccount.ua_email == payload.ua_email)
            .first()
        ):
            raise ValueError("ua_email already exists.")

        role = (
            db.query(Role)
            .filter(Role.ro_role_id == payload.ro_role_id, Role.ro_is_active.is_(True))
            .first()
        )
        if not role:
            raise ValueError(f"Invalid role ID: {payload.ro_role_id}")

        salt = generate_salt()
        password_hash = get_password_hash(payload.ua_password + salt)

        user_data = payload.model_dump(
            exclude={"ua_password"},
            exclude_none=True,
        )

        now = datetime.utcnow()
        user_data.setdefault("ua_created_at", now)
        user_data.setdefault("ua_updated_at", now)
        user_data.setdefault("ua_created_by", payload.ua_user_id)
        user_data.setdefault("ua_updated_by", user_data["ua_created_by"])

        user = UserAccount(
            **user_data,
            ua_password_hash=password_hash,
            ua_salt=salt,
        )

        db.add(user)
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise ValueError(
                "Unable to create user due to integrity constraint violation."
            ) from exc

        db.refresh(user)
        return user


user_service = UserService()
