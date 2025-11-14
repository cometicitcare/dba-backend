"""Add workflow status placeholder.

Revision ID: add_workflow_status_01
Revises: 8b0c7f02d60c
Create Date: 2024-10-08 00:00:00.000000
"""

from alembic import op  # noqa: F401
import sqlalchemy as sa  # noqa: F401


# revision identifiers, used by Alembic.
revision = "add_workflow_status_01"
down_revision = "8b0c7f02d60c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Placeholder for existing migration."""
    pass


def downgrade() -> None:
    """Placeholder for existing migration."""
    pass
