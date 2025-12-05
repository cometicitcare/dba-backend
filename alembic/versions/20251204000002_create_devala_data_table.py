"""create devala_data table

Revision ID: 20251204000002
Revises: c4554117a309
Create Date: 2025-12-04 00:00:02
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20251204000002"
down_revision: Union[str, None] = "c4554117a309"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create devaladata table with workflow fields (mirroring vihaddata structure)"""
    op.create_table(
        'devaladata',
        # Primary Key
        sa.Column('dv_id', sa.Integer(), nullable=False),
        sa.Column('dv_trn', sa.String(length=10), nullable=False),
        
        # Basic Information
        sa.Column('dv_vname', sa.String(length=200), nullable=True),
        sa.Column('dv_addrs', sa.String(length=200), nullable=True),
        sa.Column('dv_mobile', sa.String(length=10), nullable=False),
        sa.Column('dv_whtapp', sa.String(length=10), nullable=False),
        sa.Column('dv_email', sa.String(length=200), nullable=False),
        sa.Column('dv_typ', sa.String(length=10), nullable=False),
        sa.Column('dv_gndiv', sa.String(length=10), nullable=False),
        sa.Column('dv_fmlycnt', sa.Integer(), nullable=True),
        sa.Column('dv_bgndate', sa.Date(), nullable=True),
        sa.Column('dv_ownercd', sa.String(length=12), nullable=False),
        sa.Column('dv_parshawa', sa.String(length=10), nullable=False),
        sa.Column('dv_ssbmcode', sa.String(length=10), nullable=True),
        sa.Column('dv_syojakarmakrs', sa.String(length=100), nullable=True),
        sa.Column('dv_syojakarmdate', sa.Date(), nullable=True),
        sa.Column('dv_landownrship', sa.String(length=150), nullable=True),
        sa.Column('dv_pralename', sa.String(length=50), nullable=True),
        sa.Column('dv_pralesigdate', sa.Date(), nullable=True),
        sa.Column('dv_bacgrecmn', sa.String(length=100), nullable=True),
        sa.Column('dv_bacgrcmdate', sa.Date(), nullable=True),
        sa.Column('dv_minissecrsigdate', sa.Date(), nullable=True),
        sa.Column('dv_minissecrmrks', sa.String(length=200), nullable=True),
        sa.Column('dv_ssbmsigdate', sa.Date(), nullable=True),
        
        # Document Storage
        sa.Column('dv_scanned_document_path', sa.String(length=500), nullable=True),
        
        # Workflow Fields (following bhikku_regist pattern)
        sa.Column('dv_workflow_status', sa.String(length=20), server_default=sa.text("'PENDING'"), nullable=False),
        sa.Column('dv_approval_status', sa.String(length=20), nullable=True),
        sa.Column('dv_approved_by', sa.String(length=25), nullable=True),
        sa.Column('dv_approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('dv_rejected_by', sa.String(length=25), nullable=True),
        sa.Column('dv_rejected_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('dv_rejection_reason', sa.String(length=500), nullable=True),
        sa.Column('dv_printed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('dv_printed_by', sa.String(length=25), nullable=True),
        sa.Column('dv_scanned_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('dv_scanned_by', sa.String(length=25), nullable=True),
        
        # Audit/System Fields
        sa.Column('dv_version', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('dv_is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('dv_created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('dv_updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('dv_created_by', sa.String(length=25), nullable=True),
        sa.Column('dv_updated_by', sa.String(length=25), nullable=True),
        sa.Column('dv_version_number', sa.Integer(), server_default='1', nullable=False),
        
        # Constraints
        sa.PrimaryKeyConstraint('dv_id'),
        sa.UniqueConstraint('dv_trn'),
        sa.UniqueConstraint('dv_email')
    )
    
    # Create indexes for better query performance
    op.create_index('ix_devaladata_dv_id', 'devaladata', ['dv_id'])
    op.create_index('ix_devaladata_dv_trn', 'devaladata', ['dv_trn'])
    op.create_index('ix_devaladata_dv_email', 'devaladata', ['dv_email'])
    op.create_index('ix_devaladata_dv_workflow_status', 'devaladata', ['dv_workflow_status'])


def downgrade() -> None:
    """Drop devaladata table"""
    # Drop indexes
    op.drop_index('ix_devaladata_dv_workflow_status', 'devaladata')
    op.drop_index('ix_devaladata_dv_email', 'devaladata')
    op.drop_index('ix_devaladata_dv_trn', 'devaladata')
    op.drop_index('ix_devaladata_dv_id', 'devaladata')
    
    # Drop table
    op.drop_table('devaladata')
