"""make vh_email nullable

Revision ID: 20260115000001
Revises: 20260106000001
Create Date: 2026-01-15 12:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260115000001'
down_revision = '20260106000001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Make vh_email column nullable in vihaddata table."""
    op.alter_column('vihaddata', 'vh_email',
                    existing_type=sa.String(length=200),
                    nullable=True)


def downgrade() -> None:
    """Revert vh_email column to not nullable."""
    op.alter_column('vihaddata', 'vh_email',
                    existing_type=sa.String(length=200),
                    nullable=False)
