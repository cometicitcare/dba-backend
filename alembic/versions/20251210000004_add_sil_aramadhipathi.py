"""add sil_aramadhipathi column

Revision ID: 20251210000004
Revises: 20251210000003
Create Date: 2025-12-10 00:00:04

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251210000004'
down_revision = '20251210000003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add sil_aramadhipathi column to silmatha_regist table"""
    op.add_column('silmatha_regist', 
                  sa.Column('sil_aramadhipathi', sa.String(length=20), nullable=True))


def downgrade() -> None:
    """Remove sil_aramadhipathi column from silmatha_regist table"""
    op.drop_column('silmatha_regist', 'sil_aramadhipathi')
