"""add reprint form number to silmatha

Revision ID: 20251120000003
Revises: 20251120000002
Create Date: 2025-11-20 00:00:03

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20251120000003'
down_revision = '20251120000002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add reprint form number field to silmatha_regist table"""
    op.add_column('silmatha_regist', sa.Column('sil_reprint_form_no', sa.String(length=50), nullable=True))
    
    # Add index for faster lookups
    op.create_index('ix_silmatha_regist_sil_reprint_form_no', 'silmatha_regist', ['sil_reprint_form_no'])


def downgrade() -> None:
    """Remove reprint form number field from silmatha_regist table"""
    op.drop_index('ix_silmatha_regist_sil_reprint_form_no', table_name='silmatha_regist')
    op.drop_column('silmatha_regist', 'sil_reprint_form_no')
