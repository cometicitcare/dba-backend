"""create arama_land table

Revision ID: b8937b675af3
Revises: f74081132d7d
Create Date: 2025-12-08 00:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b8937b675af3"
down_revision: Union[str, None] = "f74081132d7d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create arama_land table for storing land records associated with arama"""
    op.create_table(
        'arama_land',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ar_id', sa.Integer(), nullable=False),
        sa.Column('serial_number', sa.Integer(), nullable=False),
        sa.Column('land_name', sa.String(length=200), nullable=True),
        sa.Column('village', sa.String(length=200), nullable=True),
        sa.Column('district', sa.String(length=100), nullable=True),
        sa.Column('extent', sa.String(length=100), nullable=True),
        sa.Column('cultivation_description', sa.String(length=500), nullable=True),
        sa.Column('ownership_nature', sa.String(length=200), nullable=True),
        sa.Column('deed_number', sa.String(length=100), nullable=True),
        sa.Column('title_registration_number', sa.String(length=100), nullable=True),
        sa.Column('tax_details', sa.String(length=500), nullable=True),
        sa.Column('land_occupants', sa.String(length=500), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['ar_id'], ['aramadata.ar_id'], ondelete='CASCADE')
    )
    op.create_index('ix_arama_land_id', 'arama_land', ['id'])
    op.create_index('ix_arama_land_ar_id', 'arama_land', ['ar_id'])


def downgrade() -> None:
    """Drop arama_land table"""
    op.drop_index('ix_arama_land_ar_id', 'arama_land')
    op.drop_index('ix_arama_land_id', 'arama_land')
    op.drop_table('arama_land')
