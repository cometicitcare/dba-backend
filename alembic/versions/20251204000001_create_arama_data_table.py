"""create arama_data table

Revision ID: 20251204000001
Revises: 80d5302d897a
Create Date: 2025-12-04 00:00:01
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20251204000001"
down_revision: Union[str, None] = "80d5302d897a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create aramadata table with workflow fields (mirroring vihaddata structure)"""
    op.create_table(
        'aramadata',
        # Primary Key
        sa.Column('ar_id', sa.Integer(), nullable=False),
        sa.Column('ar_trn', sa.String(length=10), nullable=False),
        
        # Basic Information
        sa.Column('ar_vname', sa.String(length=200), nullable=True),
        sa.Column('ar_addrs', sa.String(length=200), nullable=True),
        sa.Column('ar_mobile', sa.String(length=10), nullable=False),
        sa.Column('ar_whtapp', sa.String(length=10), nullable=False),
        sa.Column('ar_email', sa.String(length=200), nullable=False),
        sa.Column('ar_typ', sa.String(length=10), nullable=False),
        sa.Column('ar_gndiv', sa.String(length=10), nullable=False),
        sa.Column('ar_fmlycnt', sa.Integer(), nullable=True),
        sa.Column('ar_bgndate', sa.Date(), nullable=True),
        sa.Column('ar_ownercd', sa.String(length=12), nullable=False),
        sa.Column('ar_parshawa', sa.String(length=10), nullable=False),
        sa.Column('ar_ssbmcode', sa.String(length=10), nullable=True),
        sa.Column('ar_syojakarmakrs', sa.String(length=100), nullable=True),
        sa.Column('ar_syojakarmdate', sa.Date(), nullable=True),
        sa.Column('ar_landownrship', sa.String(length=150), nullable=True),
        sa.Column('ar_pralename', sa.String(length=50), nullable=True),
        sa.Column('ar_pralesigdate', sa.Date(), nullable=True),
        sa.Column('ar_bacgrecmn', sa.String(length=100), nullable=True),
        sa.Column('ar_bacgrcmdate', sa.Date(), nullable=True),
        sa.Column('ar_minissecrsigdate', sa.Date(), nullable=True),
        sa.Column('ar_minissecrmrks', sa.String(length=200), nullable=True),
        sa.Column('ar_ssbmsigdate', sa.Date(), nullable=True),
        
        # Document Storage
        sa.Column('ar_scanned_document_path', sa.String(length=500), nullable=True),
        
        # Workflow Fields (following bhikku_regist pattern)
        sa.Column('ar_workflow_status', sa.String(length=20), server_default=sa.text("'PENDING'"), nullable=False),
        sa.Column('ar_approval_status', sa.String(length=20), nullable=True),
        sa.Column('ar_approved_by', sa.String(length=25), nullable=True),
        sa.Column('ar_approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ar_rejected_by', sa.String(length=25), nullable=True),
        sa.Column('ar_rejected_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ar_rejection_reason', sa.String(length=500), nullable=True),
        sa.Column('ar_printed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ar_printed_by', sa.String(length=25), nullable=True),
        sa.Column('ar_scanned_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ar_scanned_by', sa.String(length=25), nullable=True),
        
        # Audit/System Fields
        sa.Column('ar_version', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('ar_is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('ar_created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('ar_updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('ar_created_by', sa.String(length=25), nullable=True),
        sa.Column('ar_updated_by', sa.String(length=25), nullable=True),
        sa.Column('ar_version_number', sa.Integer(), server_default='1', nullable=False),
        
        # Constraints
        sa.PrimaryKeyConstraint('ar_id'),
        sa.UniqueConstraint('ar_trn'),
        sa.UniqueConstraint('ar_email')
    )
    
    # Create indexes for better query performance
    op.create_index('ix_aramadata_ar_id', 'aramadata', ['ar_id'])
    op.create_index('ix_aramadata_ar_trn', 'aramadata', ['ar_trn'])
    op.create_index('ix_aramadata_ar_email', 'aramadata', ['ar_email'])
    op.create_index('ix_aramadata_ar_workflow_status', 'aramadata', ['ar_workflow_status'])


def downgrade() -> None:
    """Drop aramadata table"""
    # Drop indexes
    op.drop_index('ix_aramadata_ar_workflow_status', 'aramadata')
    op.drop_index('ix_aramadata_ar_email', 'aramadata')
    op.drop_index('ix_aramadata_ar_trn', 'aramadata')
    op.drop_index('ix_aramadata_ar_id', 'aramadata')
    
    # Drop table
    op.drop_table('aramadata')
