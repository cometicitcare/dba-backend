"""add location tracking to registration tables

Revision ID: 20251122000001
Revises: 20251121000003
Create Date: 2025-11-22 00:00:01.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20251122000001'
down_revision: Union[str, None] = '20251121000003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add location tracking fields to bhikku_regist
    op.add_column('bhikku_regist', sa.Column('br_created_by_district', sa.String(length=10), nullable=True))
    op.create_index(op.f('ix_bhikku_regist_br_created_by_district'), 'bhikku_regist', ['br_created_by_district'], unique=False)
    
    # Add location tracking fields to silmatha_regist
    op.add_column('silmatha_regist', sa.Column('sil_created_by_district', sa.String(length=10), nullable=True))
    op.create_index(op.f('ix_silmatha_regist_sil_created_by_district'), 'silmatha_regist', ['sil_created_by_district'], unique=False)
    
    # Add location tracking fields to bhikku_high_regist
    op.add_column('bhikku_high_regist', sa.Column('bhr_created_by_district', sa.String(length=10), nullable=True))
    op.create_index(op.f('ix_bhikku_high_regist_bhr_created_by_district'), 'bhikku_high_regist', ['bhr_created_by_district'], unique=False)


def downgrade() -> None:
    # Remove location tracking fields from bhikku_high_regist
    op.drop_index(op.f('ix_bhikku_high_regist_bhr_created_by_district'), table_name='bhikku_high_regist')
    op.drop_column('bhikku_high_regist', 'bhr_created_by_district')
    
    # Remove location tracking fields from silmatha_regist
    op.drop_index(op.f('ix_silmatha_regist_sil_created_by_district'), table_name='silmatha_regist')
    op.drop_column('silmatha_regist', 'sil_created_by_district')
    
    # Remove location tracking fields from bhikku_regist
    op.drop_index(op.f('ix_bhikku_regist_br_created_by_district'), table_name='bhikku_regist')
    op.drop_column('bhikku_regist', 'br_created_by_district')
