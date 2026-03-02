"""make br_livtemple nullable

Revision ID: 14f4a3921216
Revises: 20251115160000
Create Date: 2025-11-15 16:30:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '14f4a3921216'
down_revision = '20251115160000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Make br_livtemple column nullable in bhikku_regist table."""
    op.alter_column('bhikku_regist', 'br_livtemple',
                    existing_type=sa.String(length=10),
                    nullable=True)


def downgrade() -> None:
    """Revert br_livtemple column to not nullable."""
    op.alter_column('bhikku_regist', 'br_livtemple',
                    existing_type=sa.String(length=10),
                    nullable=False)
