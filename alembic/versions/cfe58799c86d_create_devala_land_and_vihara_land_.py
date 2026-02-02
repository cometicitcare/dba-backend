"""create devala_land and vihara_land tables

Revision ID: cfe58799c86d
Revises: b8937b675af3
Create Date: 2024-12-08 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'cfe58799c86d'
down_revision = 'b8937b675af3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create devala_land table
    op.create_table(
        'devala_land',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('dv_id', sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(['dv_id'], ['devaladata.dv_id'], ondelete='CASCADE'),
    )
    op.create_index(op.f('ix_devala_land_id'), 'devala_land', ['id'], unique=False)
    op.create_index(op.f('ix_devala_land_dv_id'), 'devala_land', ['dv_id'], unique=False)
    
    # Create vihara_land table
    op.create_table(
        'vihara_land',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vh_id', sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(['vh_id'], ['vihaddata.vh_id'], ondelete='CASCADE'),
    )
    op.create_index(op.f('ix_vihara_land_id'), 'vihara_land', ['id'], unique=False)
    op.create_index(op.f('ix_vihara_land_vh_id'), 'vihara_land', ['vh_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_vihara_land_vh_id'), table_name='vihara_land')
    op.drop_index(op.f('ix_vihara_land_id'), table_name='vihara_land')
    op.drop_table('vihara_land')
    
    op.drop_index(op.f('ix_devala_land_dv_id'), table_name='devala_land')
    op.drop_index(op.f('ix_devala_land_id'), table_name='devala_land')
    op.drop_table('devala_land')
