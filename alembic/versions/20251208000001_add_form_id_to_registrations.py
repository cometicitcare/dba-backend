"""add form_id to bhikku, silmatha, and bhikku_high registrations

Revision ID: 20251208000001
Revises: cfe58799c86d
Create Date: 2025-12-08 00:00:01

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251208000001'
down_revision = 'cfe58799c86d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add form_id column to bhikku_regist table
    op.add_column('bhikku_regist', sa.Column('br_form_id', sa.String(length=50), nullable=True))
    
    # Add form_id column to silmatha_regist table
    op.add_column('silmatha_regist', sa.Column('sil_form_id', sa.String(length=50), nullable=True))
    
    # Add form_id column to bhikku_high_regist table
    op.add_column('bhikku_high_regist', sa.Column('bhr_form_id', sa.String(length=50), nullable=True))


def downgrade() -> None:
    # Remove form_id column from bhikku_high_regist table
    op.drop_column('bhikku_high_regist', 'bhr_form_id')
    
    # Remove form_id column from silmatha_regist table
    op.drop_column('silmatha_regist', 'sil_form_id')
    
    # Remove form_id column from bhikku_regist table
    op.drop_column('bhikku_regist', 'br_form_id')
