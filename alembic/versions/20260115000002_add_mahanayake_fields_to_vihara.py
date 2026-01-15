"""add mahanayake fields to vihara

Revision ID: 20260115000002
Revises: 20260115000001
Create Date: 2026-01-15 14:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260115000002'
down_revision = '20260115000001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add mahanayake fields to vihaddata table."""
    op.add_column('vihaddata', sa.Column('vh_mahanayake_date', sa.Date(), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_mahanayake_letter_nu', sa.String(length=50), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_mahanayake_remarks', sa.String(length=500), nullable=True))


def downgrade() -> None:
    """Remove mahanayake fields from vihaddata table."""
    op.drop_column('vihaddata', 'vh_mahanayake_remarks')
    op.drop_column('vihaddata', 'vh_mahanayake_letter_nu')
    op.drop_column('vihaddata', 'vh_mahanayake_date')
