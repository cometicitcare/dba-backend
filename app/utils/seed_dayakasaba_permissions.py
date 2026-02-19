"""
Seed script to create Dayakasaba registration permissions and assign them to
vihara and silmatha roles.

Roles that receive access:
  - VIHA_ADM  (vihara_admin)       → full access: create/read/update/delete/approve
  - VIHA_DATA (vihara_dataentry)   → create/read/update
  - SL_ADMIN  (silmatha_admin)     → full access: create/read/update/delete/approve
  - SL_DE001  (silmatha_dataentry) → create/read/update

Usage:
    python -m app.utils.seed_dayakasaba_permissions
"""

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.group import Group
from app.models.permissions import Permission
from app.models.role_permissions import RolePermission
from app.models.roles import Role


# ─────────────────────────────────────────────────────────────────────────────
# Permission definitions
# ─────────────────────────────────────────────────────────────────────────────

PERMISSIONS_DATA = [
    ("dayakasaba:create",  "dayakasaba", "create",  "Create new Dayaka Sabha registration records"),
    ("dayakasaba:read",    "dayakasaba", "read",    "Read Dayaka Sabha registration records"),
    ("dayakasaba:update",  "dayakasaba", "update",  "Update existing Dayaka Sabha registration records"),
    ("dayakasaba:delete",  "dayakasaba", "delete",  "Delete Dayaka Sabha registration records"),
    ("dayakasaba:approve", "dayakasaba", "approve", "Approve or reject Dayaka Sabha registration records"),
]

# Role → list of permissions to assign
ROLE_PERMISSION_MAPPING = {
    "VIHA_ADM":  ["dayakasaba:create", "dayakasaba:read", "dayakasaba:update", "dayakasaba:delete", "dayakasaba:approve"],
    "VIHA_DATA": ["dayakasaba:create", "dayakasaba:read", "dayakasaba:update"],
    "SL_ADMIN":  ["dayakasaba:create", "dayakasaba:read", "dayakasaba:update", "dayakasaba:delete", "dayakasaba:approve"],
    "SL_DE001":  ["dayakasaba:create", "dayakasaba:read", "dayakasaba:update"],
}


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _get_or_create_group(db: Session) -> "Group":
    """Return the existing Vihara Department group (or any system group) for FK."""
    group = db.query(Group).filter(Group.group_name == "Vihara Department").first()
    if not group:
        # Fall back to any group so FK is satisfied
        group = db.query(Group).first()
    return group


def seed_permissions(db: Session, group_id: int) -> dict:
    """Create dayakasaba:* permissions if they don't exist yet."""
    print("\n[1/2] Setting up Dayakasaba Permissions...")
    created = {}

    for name, resource, action, description in PERMISSIONS_DATA:
        existing = db.query(Permission).filter(Permission.pe_name == name).first()
        if not existing:
            perm = Permission(
                pe_name=name,
                pe_resource=resource,
                pe_action=action,
                pe_description=description,
                group_id=group_id,
                pe_created_by="SYSTEM",
                pe_updated_by="SYSTEM",
            )
            db.add(perm)
            db.flush()
            created[name] = perm.pe_permission_id
            print(f"      ✓ Created: {name}")
        else:
            created[name] = existing.pe_permission_id
            print(f"      - Exists:  {name}")

    db.commit()
    return created


def assign_permissions(db: Session, permissions: dict) -> None:
    """Assign the dayakasaba permissions to each target role."""
    print("\n[2/2] Assigning Permissions to Roles...")

    role_labels = {
        "VIHA_ADM":  "vihara_admin",
        "VIHA_DATA": "vihara_dataentry",
        "SL_ADMIN":  "silmatha_admin",
        "SL_DE001":  "silmatha_dataentry",
    }

    for role_id, perm_names in ROLE_PERMISSION_MAPPING.items():
        role = db.query(Role).filter(Role.ro_role_id == role_id).first()
        if not role:
            print(f"\n      ⚠  Role {role_id} ({role_labels.get(role_id, '?')}) not found — skipping.")
            continue

        print(f"\n      {role_labels.get(role_id, role_id)} ({role_id}):")

        for perm_name in perm_names:
            perm_id = permissions.get(perm_name)
            if not perm_id:
                print(f"        ⚠  Permission {perm_name} not found — skipping.")
                continue

            existing = (
                db.query(RolePermission)
                .filter(
                    RolePermission.rp_role_id == role_id,
                    RolePermission.rp_permission_id == perm_id,
                )
                .first()
            )

            if not existing:
                db.add(
                    RolePermission(
                        rp_role_id=role_id,
                        rp_permission_id=perm_id,
                        rp_granted=True,
                    )
                )
                print(f"        ✓ Assigned: {perm_name}")
            else:
                existing.rp_granted = True
                print(f"        - Already assigned: {perm_name}")

    db.commit()
    print("\n      ✓ All assignments complete.")


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 70)
    print("Seeding Dayakasaba Registration Permissions")
    print("=" * 70)

    db: Session = SessionLocal()
    try:
        group = _get_or_create_group(db)
        if not group:
            raise RuntimeError("No group found in DB. Run the vihara/bhikku setup scripts first.")

        permissions = seed_permissions(db, group.group_id)
        assign_permissions(db, permissions)

        print("\n" + "=" * 70)
        print("✅ Seeding completed successfully!")
        print("=" * 70)
        print("\nRoles that now have Dayakasaba access:")
        print("  - VIHA_ADM  (vihara_admin)       → create / read / update / delete / approve")
        print("  - VIHA_DATA (vihara_dataentry)   → create / read / update")
        print("  - SL_ADMIN  (silmatha_admin)     → create / read / update / delete / approve")
        print("  - SL_DE001  (silmatha_dataentry) → create / read / update")
        print("=" * 70)

    except Exception as exc:
        db.rollback()
        print(f"\n❌ Error during seeding: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
