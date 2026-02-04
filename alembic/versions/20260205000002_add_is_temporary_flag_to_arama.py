"""add is_temporary flag to aramadata

Revision ID: 20260205000002
Revises: 20260205000001
Create Date: 2026-02-05 00:00:02.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260205000002'
down_revision = '20260205000001'
branch_labels = None
depends_on = None


def upgrade():
    """Add ar_is_temporary_record flag to aramadata table"""
    op.add_column('aramadata', sa.Column('ar_is_temporary_record', sa.Boolean(), nullable=True, server_default=sa.text('false'), comment='Flag to identify records created from temporary arama endpoint'))


def downgrade():
    """Remove ar_is_temporary_record flag from aramadata table"""
    op.drop_column('aramadata', 'ar_is_temporary_record')
