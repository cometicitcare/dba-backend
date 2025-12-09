"""add arama resident silmathas and update land fields

Revision ID: 20251209000002
Revises: 20251209000001
Create Date: 2025-12-09 00:00:02

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251209000002'
down_revision = '20251209000001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add arama_resident_silmathas table and update arama_land fields"""
    
    # Create arama_resident_silmathas table
    op.create_table(
        'arama_resident_silmathas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ar_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('national_id', sa.String(length=20), nullable=True),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('ordination_date', sa.Date(), nullable=True),
        sa.Column('position', sa.String(length=200), nullable=True),
        sa.Column('notes', sa.String(length=1000), nullable=True),
        sa.Column('is_head_nun', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['ar_id'], ['aramadata.ar_id'], ondelete='CASCADE')
    )
    op.create_index('ix_arama_resident_silmathas_id', 'arama_resident_silmathas', ['id'])
    op.create_index('ix_arama_resident_silmathas_ar_id', 'arama_resident_silmathas', ['ar_id'])
    
    # Add ar_resident_silmathas_certified field to aramadata
    op.add_column('aramadata', sa.Column('ar_resident_silmathas_certified', sa.Boolean(), nullable=True))
    
    # Add new fields to arama_land table
    op.add_column('arama_land', sa.Column('plot_number', sa.String(length=100), nullable=True))
    op.add_column('arama_land', sa.Column('survey_number', sa.String(length=100), nullable=True))
    op.add_column('arama_land', sa.Column('title_number', sa.String(length=100), nullable=True))
    op.add_column('arama_land', sa.Column('extent_unit', sa.String(length=50), nullable=True))
    op.add_column('arama_land', sa.Column('ownership_type', sa.String(length=200), nullable=True))
    op.add_column('arama_land', sa.Column('land_notes', sa.String(length=1000), nullable=True))


def downgrade() -> None:
    """Remove arama resident silmathas table and new land fields"""
    
    # Remove new fields from arama_land
    op.drop_column('arama_land', 'land_notes')
    op.drop_column('arama_land', 'ownership_type')
    op.drop_column('arama_land', 'extent_unit')
    op.drop_column('arama_land', 'title_number')
    op.drop_column('arama_land', 'survey_number')
    op.drop_column('arama_land', 'plot_number')
    
    # Remove ar_resident_silmathas_certified from aramadata
    op.drop_column('aramadata', 'ar_resident_silmathas_certified')
    
    # Drop arama_resident_silmathas table
    op.drop_index('ix_arama_resident_silmathas_ar_id', 'arama_resident_silmathas')
    op.drop_index('ix_arama_resident_silmathas_id', 'arama_resident_silmathas')
    op.drop_table('arama_resident_silmathas')
