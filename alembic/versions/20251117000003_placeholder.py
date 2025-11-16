"""Placeholder for missing migration.

Revision ID: 20251117000003
Revises: 1d61d5571d9f
Create Date: 2025-11-17 00:00:03.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20251117000003"
down_revision = "1d61d5571d9f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Placeholder migration - changes already applied directly to database."""
    pass


def downgrade() -> None:
    """Placeholder migration - no downgrade available."""
    pass
