"""add reprint amount and remarks to bhikku regist

Revision ID: 20251117000005
Revises: 20251117000004
Create Date: 2025-11-17 00:00:05

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251117000005'
down_revision = '20251117000004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add reprint amount and remarks fields to bhikku_regist table
    op.add_column('bhikku_regist', sa.Column('br_reprint_amount', sa.Numeric(10, 2), nullable=True))
    op.add_column('bhikku_regist', sa.Column('br_reprint_remarks', sa.String(length=500), nullable=True))


def downgrade() -> None:
    # Remove reprint amount and remarks fields from bhikku_regist table
    op.drop_column('bhikku_regist', 'br_reprint_remarks')
    op.drop_column('bhikku_regist', 'br_reprint_amount')
