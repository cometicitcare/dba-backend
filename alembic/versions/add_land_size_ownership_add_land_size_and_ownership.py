"""add land_size and land_ownership to arama_land

Revision ID: add_land_size_ownership
Revises: fdb5dc86afe3
Create Date: 2026-02-09 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_land_size_ownership'
down_revision = '20260205000002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add land_size and land_ownership columns to arama_land table
    op.add_column('arama_land', sa.Column('land_size', sa.String(length=200), nullable=True))
    op.add_column('arama_land', sa.Column('land_ownership', sa.String(length=500), nullable=True))


def downgrade() -> None:
    # Remove land_size and land_ownership columns from arama_land table
    op.drop_column('arama_land', 'land_ownership')
    op.drop_column('arama_land', 'land_size')
