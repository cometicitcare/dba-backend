"""add reprint workflow fields

Revision ID: 20251115152104
Revises: c6d9f5e3b2c2
Create Date: 2025-11-15 15:21:04

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251115152104'
down_revision = 'c6d9f5e3b2c2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add reprint workflow fields to bhikku_regist table
    op.add_column('bhikku_regist', sa.Column('br_reprint_status', sa.String(length=20), nullable=True))
    op.add_column('bhikku_regist', sa.Column('br_reprint_requested_by', sa.String(length=25), nullable=True))
    op.add_column('bhikku_regist', sa.Column('br_reprint_requested_at', sa.TIMESTAMP(), nullable=True))
    op.add_column('bhikku_regist', sa.Column('br_reprint_request_reason', sa.String(length=500), nullable=True))
    op.add_column('bhikku_regist', sa.Column('br_reprint_approved_by', sa.String(length=25), nullable=True))
    op.add_column('bhikku_regist', sa.Column('br_reprint_approved_at', sa.TIMESTAMP(), nullable=True))
    op.add_column('bhikku_regist', sa.Column('br_reprint_rejected_by', sa.String(length=25), nullable=True))
    op.add_column('bhikku_regist', sa.Column('br_reprint_rejected_at', sa.TIMESTAMP(), nullable=True))
    op.add_column('bhikku_regist', sa.Column('br_reprint_rejection_reason', sa.String(length=500), nullable=True))
    op.add_column('bhikku_regist', sa.Column('br_reprint_completed_by', sa.String(length=25), nullable=True))
    op.add_column('bhikku_regist', sa.Column('br_reprint_completed_at', sa.TIMESTAMP(), nullable=True))


def downgrade() -> None:
    # Remove reprint workflow fields from bhikku_regist table
    op.drop_column('bhikku_regist', 'br_reprint_completed_at')
    op.drop_column('bhikku_regist', 'br_reprint_completed_by')
    op.drop_column('bhikku_regist', 'br_reprint_rejection_reason')
    op.drop_column('bhikku_regist', 'br_reprint_rejected_at')
    op.drop_column('bhikku_regist', 'br_reprint_rejected_by')
    op.drop_column('bhikku_regist', 'br_reprint_approved_at')
    op.drop_column('bhikku_regist', 'br_reprint_approved_by')
    op.drop_column('bhikku_regist', 'br_reprint_request_reason')
    op.drop_column('bhikku_regist', 'br_reprint_requested_at')
    op.drop_column('bhikku_regist', 'br_reprint_requested_by')
    op.drop_column('bhikku_regist', 'br_reprint_status')
