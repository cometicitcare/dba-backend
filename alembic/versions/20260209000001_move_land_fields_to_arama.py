"""move_land_fields_to_arama

Revision ID: 20260209000001
Revises: 20260205000002
Create Date: 2026-02-09 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260209000001'
down_revision: Union[str, None] = 'add_land_size_ownership'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new fields to aramadata table
    op.add_column('aramadata', sa.Column('ar_landsize', sa.String(length=200), nullable=True))
    op.add_column('aramadata', sa.Column('ar_landownershiptype', sa.String(length=500), nullable=True))
    
    # Remove fields from arama_land table
    op.drop_column('arama_land', 'land_size')
    op.drop_column('arama_land', 'land_ownership')


def downgrade() -> None:
    # Add fields back to arama_land table
    op.add_column('arama_land', sa.Column('land_ownership', sa.String(length=500), nullable=True))
    op.add_column('arama_land', sa.Column('land_size', sa.String(length=200), nullable=True))
    
    # Remove fields from aramadata table
    op.drop_column('aramadata', 'ar_landownershiptype')
    op.drop_column('aramadata', 'ar_landsize')
