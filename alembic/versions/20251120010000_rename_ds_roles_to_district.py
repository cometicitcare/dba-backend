"""Rename Divisional Secretariat roles to District naming

Revision ID: 20251120010000
Revises: 20251120000002
Create Date: 2025-11-20 01:00:00
"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "20251120010000"
down_revision = "20251120000002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Rename DS Admin/Data Entry roles to District naming."""
    op.execute(
        "UPDATE roles SET ro_role_name = 'District Admin' "
        "WHERE ro_role_id = 'DS_ADMIN'"
    )
    op.execute(
        "UPDATE roles SET ro_role_name = 'District Data Entry' "
        "WHERE ro_role_id = 'DS_DE001'"
    )


def downgrade() -> None:
    """Revert role names back to Divisional Secretariat naming."""
    op.execute(
        "UPDATE roles SET ro_role_name = 'Divisional Secretariat Admin' "
        "WHERE ro_role_id = 'DS_ADMIN'"
    )
    op.execute(
        "UPDATE roles SET ro_role_name = 'Divisional Secretariat Data Entry' "
        "WHERE ro_role_id = 'DS_DE001'"
    )
