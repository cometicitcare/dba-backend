"""add bhikku id card workflow completion fields

Revision ID: 20251115160000
Revises: c7d97c3a5127
Create Date: 2025-11-15 16:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251115160000'
down_revision = 'c7d97c3a5127'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add completion workflow fields to bhikku_id_card table
    op.add_column('bhikku_id_card', sa.Column('bic_completed_by', sa.String(length=50), nullable=True, comment='User who marked as completed'))
    op.add_column('bhikku_id_card', sa.Column('bic_completed_at', sa.TIMESTAMP(), nullable=True, comment='Timestamp when marked as completed'))


def downgrade() -> None:
    # Remove completion workflow fields from bhikku_id_card table
    op.drop_column('bhikku_id_card', 'bic_completed_at')
    op.drop_column('bhikku_id_card', 'bic_completed_by')
