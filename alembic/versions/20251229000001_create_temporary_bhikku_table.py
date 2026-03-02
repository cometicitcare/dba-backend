"""create temporary_bhikku table

Revision ID: 20251229000001
Revises: 20251226000001
Create Date: 2025-12-29 00:00:01
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20251229000001"
down_revision: Union[str, None] = "20251226000001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create temporary_bhikku table for storing incomplete bhikku information"""
    op.create_table(
        'temporary_bhikku',
        # Primary Key
        sa.Column('tb_id', sa.Integer(), nullable=False, autoincrement=True),
        
        # Basic Information Fields
        sa.Column('tb_name', sa.String(length=100), nullable=False, comment='Bhikku name'),
        sa.Column('tb_id_number', sa.String(length=20), nullable=True, comment='National ID or other identification number'),
        sa.Column('tb_contact_number', sa.String(length=15), nullable=True, comment='Contact/mobile number'),
        sa.Column('tb_samanera_name', sa.String(length=100), nullable=True, comment='Samanera (novice) name'),
        sa.Column('tb_address', sa.String(length=500), nullable=True, comment='Residential address'),
        sa.Column('tb_living_temple', sa.String(length=200), nullable=True, comment='Current living temple/vihara'),
        
        # Audit Fields
        sa.Column('tb_created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('tb_created_by', sa.String(length=25), nullable=True, comment='User ID who created this record'),
        sa.Column('tb_updated_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('tb_updated_by', sa.String(length=25), nullable=True, comment='User ID who last updated this record'),
        
        # Primary Key Constraint
        sa.PrimaryKeyConstraint('tb_id'),
    )
    
    # Create indexes
    op.create_index('ix_temporary_bhikku_tb_id', 'temporary_bhikku', ['tb_id'])
    op.create_index('ix_temporary_bhikku_tb_name', 'temporary_bhikku', ['tb_name'])
    op.create_index('ix_temporary_bhikku_tb_id_number', 'temporary_bhikku', ['tb_id_number'])


def downgrade() -> None:
    """Drop temporary_bhikku table and its indexes"""
    op.drop_index('ix_temporary_bhikku_tb_id_number', 'temporary_bhikku')
    op.drop_index('ix_temporary_bhikku_tb_name', 'temporary_bhikku')
    op.drop_index('ix_temporary_bhikku_tb_id', 'temporary_bhikku')
    op.drop_table('temporary_bhikku')
