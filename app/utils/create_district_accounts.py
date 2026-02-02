"""
Utility: Create District Admin and District Data Entry users for every district branch.

Usage:
    python -m app.utils.create_district_accounts

Notes:
- Creates two users per district branch (not deleted): Admin + Data Entry.
- Skips users if the username already exists.
- Prints generated usernames/passwords so you can share them securely.
"""

from __future__ import annotations

import secrets
import string
from typing import List, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.security import generate_salt, get_password_hash
from app.db.session import SessionLocal
from app.models.district_branch import DistrictBranch
from app.models.user import UserAccount
from app.models.user_roles import UserRole
from app.models.roles import Role

DIST_ADMIN_ROLE_ID = "DS_ADMIN"
DIST_DATA_ENTRY_ROLE_ID = "DS_DE001"


def _next_user_id(db: Session) -> str:
    """Generate next UA-style user id (UA0001...)."""
    max_num = (
        db.query(func.max(func.substr(UserAccount.ua_user_id, 3)))
        .filter(UserAccount.ua_user_id.like("UA%"))
        .scalar()
    )
    try:
        next_num = int(max_num) + 1
    except (TypeError, ValueError):
        next_num = 1
    return f"UA{next_num:04d}"


def _random_password() -> str:
    """Generate a strong but memorable password."""
    alphabet = string.ascii_letters + string.digits
    core = "".join(secrets.choice(alphabet) for _ in range(8))
    # Ensure at least one symbol for complexity
    return f"{core}@{secrets.choice('!$%?')}"


def _create_user(
    db: Session,
    *,
    username: str,
    email: str,
    password: str,
    role_id: str,
    district_branch_id: int,
    first_name: str,
    last_name: str,
) -> UserAccount:
    """Create a single user with the given role."""
    salt = generate_salt()
    hashed = get_password_hash(password + salt)

    user = UserAccount(
        ua_user_id=_next_user_id(db),
        ua_username=username,
        ua_email=email,
        ua_password_hash=hashed,
        ua_salt=salt,
        ua_first_name=first_name,
        ua_last_name=last_name,
        ua_status="active",
        ua_is_deleted=False,
        ua_location_type="DISTRICT_BRANCH",
        ua_district_branch_id=district_branch_id,
    )
    db.add(user)
    db.flush()

    db.add(
        UserRole(
            ur_user_id=user.ua_user_id,
            ur_role_id=role_id,
            ur_is_active=True,
        )
    )
    return user


def create_accounts(db: Session) -> List[Tuple[str, str, str]]:
    """
    Create district admin and data entry accounts.
    Returns list of tuples: (district_code, username, password)
    """
    creds: List[Tuple[str, str, str]] = []

    # Ensure roles exist
    role_ids = {r.ro_role_id for r in db.query(Role.ro_role_id).all()}
    missing = {DIST_ADMIN_ROLE_ID, DIST_DATA_ENTRY_ROLE_ID} - role_ids
    if missing:
        raise RuntimeError(f"Missing roles: {', '.join(sorted(missing))}. Seed roles before running.")

    branches = (
        db.query(DistrictBranch)
        .filter(DistrictBranch.db_is_deleted.is_(False))
        .order_by(DistrictBranch.db_district_code)
        .all()
    )

    for branch in branches:
        base = branch.db_district_code or branch.db_code or "DIST"
        base_clean = base.lower()

        # Admin
        admin_username = f"{base_clean}-admin"
        if not db.query(UserAccount).filter(UserAccount.ua_username == admin_username).first():
            admin_pw = _random_password()
            admin_user = _create_user(
                db,
                username=admin_username,
                email=f"{admin_username}@dba.local",
                password=admin_pw,
                role_id=DIST_ADMIN_ROLE_ID,
                district_branch_id=branch.db_id,
                first_name=branch.db_name or base,
                last_name="Admin",
            )
            creds.append((base, admin_username, admin_pw))
            print(f"[NEW] {admin_username} -> {admin_pw} (user_id={admin_user.ua_user_id})")
        else:
            print(f"[SKIP] {admin_username} already exists")

        # Data Entry
        de_username = f"{base_clean}-de"
        if not db.query(UserAccount).filter(UserAccount.ua_username == de_username).first():
            de_pw = _random_password()
            de_user = _create_user(
                db,
                username=de_username,
                email=f"{de_username}@dba.local",
                password=de_pw,
                role_id=DIST_DATA_ENTRY_ROLE_ID,
                district_branch_id=branch.db_id,
                first_name=branch.db_name or base,
                last_name="DataEntry",
            )
            creds.append((base, de_username, de_pw))
            print(f"[NEW] {de_username} -> {de_pw} (user_id={de_user.ua_user_id})")
        else:
            print(f"[SKIP] {de_username} already exists")

    db.commit()
    return creds


def main() -> None:
    db = SessionLocal()
    try:
        creds = create_accounts(db)
        print("\n=== Created Accounts ===")
        for district_code, username, password in creds:
            print(f"{district_code}: {username} / {password}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
