"""add workflow fields to vihara

Revision ID: 80d5302d897a
Revises: 20251123000003
Create Date: 2025-12-03 00:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "80d5302d897a"
down_revision: Union[str, None] = "20251123000003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add workflow fields to vihaddata table following bhikku_regist pattern"""
    # Add scanned document path column
    op.add_column('vihaddata', sa.Column('vh_scanned_document_path', sa.String(length=500), nullable=True))
    
    # Add workflow status columns
    op.add_column('vihaddata', sa.Column('vh_workflow_status', sa.String(length=20), server_default=sa.text("'PENDING'"), nullable=False))
    op.add_column('vihaddata', sa.Column('vh_approval_status', sa.String(length=20), nullable=True))
    
    # Add approval tracking columns
    op.add_column('vihaddata', sa.Column('vh_approved_by', sa.String(length=25), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_approved_at', sa.DateTime(timezone=True), nullable=True))
    
    # Add rejection tracking columns
    op.add_column('vihaddata', sa.Column('vh_rejected_by', sa.String(length=25), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_rejected_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_rejection_reason', sa.String(length=500), nullable=True))
    
    # Add printed tracking columns
    op.add_column('vihaddata', sa.Column('vh_printed_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_printed_by', sa.String(length=25), nullable=True))
    
    # Add scanned tracking columns
    op.add_column('vihaddata', sa.Column('vh_scanned_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_scanned_by', sa.String(length=25), nullable=True))
    
    # Add index on workflow_status for better query performance
    op.create_index('ix_vihaddata_vh_workflow_status', 'vihaddata', ['vh_workflow_status'])


def downgrade() -> None:
    """Remove workflow fields from vihaddata table"""
    # Drop index
    op.drop_index('ix_vihaddata_vh_workflow_status', 'vihaddata')
    
    # Drop all workflow columns in reverse order
    op.drop_column('vihaddata', 'vh_scanned_by')
    op.drop_column('vihaddata', 'vh_scanned_at')
    op.drop_column('vihaddata', 'vh_printed_by')
    op.drop_column('vihaddata', 'vh_printed_at')
    op.drop_column('vihaddata', 'vh_rejection_reason')
    op.drop_column('vihaddata', 'vh_rejected_at')
    op.drop_column('vihaddata', 'vh_rejected_by')
    op.drop_column('vihaddata', 'vh_approved_at')
    op.drop_column('vihaddata', 'vh_approved_by')
    op.drop_column('vihaddata', 'vh_approval_status')
    op.drop_column('vihaddata', 'vh_workflow_status')
    op.drop_column('vihaddata', 'vh_scanned_document_path')
