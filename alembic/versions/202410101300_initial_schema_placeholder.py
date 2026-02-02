"""Baseline placeholder migration.

Revision ID: 202410101300
Revises: 4e2b9f6d8c1a
Create Date: 2024-10-10 13:00:00.000000
"""

from alembic import op  # noqa: F401
import sqlalchemy as sa  # noqa: F401


# revision identifiers, used by Alembic.
revision = "202410101300"
down_revision = "4e2b9f6d8c1a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Placeholder upgrade. Schema already managed outside Alembic."""
    pass


def downgrade() -> None:
    """Placeholder downgrade."""
    pass
