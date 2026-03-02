"""increase sil_mahanaacharyacd length

Revision ID: 20251210000002
Revises: 20251210000001
Create Date: 2025-12-10 00:00:02

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251210000002'
down_revision = '20251210000001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Increase sil_mahanaacharyacd column length to accommodate comma-separated sil_regn values"""
    # Increase from VARCHAR(12) to VARCHAR(500) to handle multiple comma-separated registration numbers
    op.alter_column('silmatha_regist', 'sil_mahanaacharyacd',
                    type_=sa.String(500),
                    existing_type=sa.String(12),
                    existing_nullable=True)


def downgrade() -> None:
    """Revert sil_mahanaacharyacd column length back to original size"""
    op.alter_column('silmatha_regist', 'sil_mahanaacharyacd',
                    type_=sa.String(12),
                    existing_type=sa.String(500),
                    existing_nullable=True)
