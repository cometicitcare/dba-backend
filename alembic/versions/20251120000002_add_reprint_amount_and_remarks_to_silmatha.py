"""add reprint amount and remarks to silmatha

Revision ID: 20251120000002
Revises: 20251119000006
Create Date: 2025-11-20 00:00:02

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251120000002'
down_revision = '20251119000006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add reprint amount and remarks fields to silmatha_regist table"""
    # Add reprint amount and remarks
    op.add_column('silmatha_regist', sa.Column('sil_reprint_amount', sa.Numeric(10, 2), nullable=True))
    op.add_column('silmatha_regist', sa.Column('sil_reprint_remarks', sa.String(length=500), nullable=True))


def downgrade() -> None:
    """Remove reprint amount and remarks fields from silmatha_regist table"""
    op.drop_column('silmatha_regist', 'sil_reprint_remarks')
    op.drop_column('silmatha_regist', 'sil_reprint_amount')
