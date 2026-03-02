"""add_workflow_fields_to_bhikku_high

Revision ID: 20251121000001
Revises: 20251120000003
Create Date: 2025-11-21 00:00:01.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision: str = '20251121000001'
down_revision: Union[str, None] = '20251120000003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add workflow fields to bhikku_high_regist table"""
    
    # Add workflow status field (default PENDING)
    op.add_column('bhikku_high_regist', 
        sa.Column('bhr_workflow_status', sa.String(20), 
                  server_default=text("'PENDING'"), 
                  nullable=False))
    op.create_index('ix_bhikku_high_regist_bhr_workflow_status', 'bhikku_high_regist', ['bhr_workflow_status'])
    
    # Add approval status field
    op.add_column('bhikku_high_regist', 
        sa.Column('bhr_approval_status', sa.String(20), nullable=True))
    
    # Add approval tracking fields
    op.add_column('bhikku_high_regist', 
        sa.Column('bhr_approved_by', sa.String(25), nullable=True))
    op.add_column('bhikku_high_regist', 
        sa.Column('bhr_approved_at', sa.TIMESTAMP, nullable=True))
    
    # Add rejection tracking fields
    op.add_column('bhikku_high_regist', 
        sa.Column('bhr_rejected_by', sa.String(25), nullable=True))
    op.add_column('bhikku_high_regist', 
        sa.Column('bhr_rejected_at', sa.TIMESTAMP, nullable=True))
    op.add_column('bhikku_high_regist', 
        sa.Column('bhr_rejection_reason', sa.String(500), nullable=True))
    
    # Add printing tracking fields
    op.add_column('bhikku_high_regist', 
        sa.Column('bhr_printed_by', sa.String(25), nullable=True))
    op.add_column('bhikku_high_regist', 
        sa.Column('bhr_printed_at', sa.TIMESTAMP, nullable=True))
    
    # Add scanned document tracking fields
    op.add_column('bhikku_high_regist', 
        sa.Column('bhr_scanned_by', sa.String(25), nullable=True))
    op.add_column('bhikku_high_regist', 
        sa.Column('bhr_scanned_at', sa.TIMESTAMP, nullable=True))
    op.add_column('bhikku_high_regist', 
        sa.Column('bhr_scanned_document_path', sa.String(500), nullable=True))


def downgrade() -> None:
    """Remove workflow fields from bhikku_high_regist table"""
    
    op.drop_index('ix_bhikku_high_regist_bhr_workflow_status', 'bhikku_high_regist')
    
    op.drop_column('bhikku_high_regist', 'bhr_scanned_document_path')
    op.drop_column('bhikku_high_regist', 'bhr_scanned_at')
    op.drop_column('bhikku_high_regist', 'bhr_scanned_by')
    op.drop_column('bhikku_high_regist', 'bhr_printed_at')
    op.drop_column('bhikku_high_regist', 'bhr_printed_by')
    op.drop_column('bhikku_high_regist', 'bhr_rejection_reason')
    op.drop_column('bhikku_high_regist', 'bhr_rejected_at')
    op.drop_column('bhikku_high_regist', 'bhr_rejected_by')
    op.drop_column('bhikku_high_regist', 'bhr_approved_at')
    op.drop_column('bhikku_high_regist', 'bhr_approved_by')
    op.drop_column('bhikku_high_regist', 'bhr_approval_status')
    op.drop_column('bhikku_high_regist', 'bhr_workflow_status')
