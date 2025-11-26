"""Assign District roles the Bhikku / Silmatha / High Bhikku permissions

Revision ID: 20251126010000
Revises: 20251123000003
Create Date: 2025-11-26 01:00:00
"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "20251126010000"
down_revision = "20251123000003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Grant required permissions to District Admin and Data Entry roles."""
    admin_perms = [
        "bhikku:create",
        "bhikku:read",
        "bhikku:update",
        "bhikku:delete",
        "CREATE_BHIKKU_HIGH",
        "READ_BHIKKU_HIGH",
        "UPDATE_BHIKKU_HIGH",
        "DELETE_BHIKKU_HIGH",
        "silmatha:create",
        "silmatha:read",
        "silmatha:update",
        "silmatha:delete",
        "silmatha:approve",
    ]

    dataentry_perms = [
        "bhikku:create",
        "bhikku:read",
        "bhikku:update",
        "CREATE_BHIKKU_HIGH",
        "READ_BHIKKU_HIGH",
        "UPDATE_BHIKKU_HIGH",
        "silmatha:create",
        "silmatha:read",
        "silmatha:update",
    ]

    statements = []
    for role_id, perms in (("DS_ADMIN", admin_perms), ("DS_DE001", dataentry_perms)):
        for perm in perms:
            statements.append(
                f"""
                INSERT INTO role_permissions (rp_role_id, rp_permission_id, rp_granted)
                SELECT '{role_id}', p.pe_permission_id, TRUE
                FROM permissions p
                WHERE p.pe_name = '{perm}'
                ON CONFLICT (rp_role_id, rp_permission_id)
                DO UPDATE SET rp_granted = EXCLUDED.rp_granted;
                """
            )

    op.execute("\n".join(statements))


def downgrade() -> None:
    """Revoke the permissions granted in upgrade."""
    perms_to_remove = set(
        [
            "bhikku:create",
            "bhikku:read",
            "bhikku:update",
            "bhikku:delete",
            "CREATE_BHIKKU_HIGH",
            "READ_BHIKKU_HIGH",
            "UPDATE_BHIKKU_HIGH",
            "DELETE_BHIKKU_HIGH",
            "silmatha:create",
            "silmatha:read",
            "silmatha:update",
            "silmatha:delete",
            "silmatha:approve",
        ]
    )
    op.execute(
        """
        DELETE FROM role_permissions
        USING permissions
        WHERE role_permissions.rp_permission_id = permissions.pe_permission_id
          AND permissions.pe_name = ANY (ARRAY[{perms}])
          AND role_permissions.rp_role_id IN ('DS_ADMIN', 'DS_DE001');
        """.format(
            perms=",".join(f"'{p}'" for p in sorted(perms_to_remove))
        )
    )
