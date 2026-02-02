"""add_bhikku_workflow_fields

Revision ID: b5c8e3f4d2a1
Revises: a4090ddd5179
Create Date: 2025-11-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b5c8e3f4d2a1'
down_revision = 'a4090ddd5179'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add workflow fields to bhikku_regist table"""
    
    # Check and add columns only if they don't exist
    conn = op.get_bind()
    
    # Helper function to check if column exists
    def column_exists(table_name, column_name):
        result = conn.execute(sa.text(
            f"SELECT column_name FROM information_schema.columns "
            f"WHERE table_name='{table_name}' AND column_name='{column_name}'"
        ))
        return result.fetchone() is not None
    
    # Add workflow status field with default PENDING
    if not column_exists('bhikku_regist', 'br_workflow_status'):
        op.add_column('bhikku_regist', 
            sa.Column('br_workflow_status', sa.String(20), nullable=False, server_default='PENDING')
        )
        op.create_index('ix_bhikku_regist_br_workflow_status', 'bhikku_regist', ['br_workflow_status'])
    
    # Add approval status field
    if not column_exists('bhikku_regist', 'br_approval_status'):
        op.add_column('bhikku_regist', 
            sa.Column('br_approval_status', sa.String(20), nullable=True)
        )
    
    # Add approval tracking fields
    if not column_exists('bhikku_regist', 'br_approved_by'):
        op.add_column('bhikku_regist', 
            sa.Column('br_approved_by', sa.String(25), nullable=True)
        )
    if not column_exists('bhikku_regist', 'br_approved_at'):
        op.add_column('bhikku_regist', 
            sa.Column('br_approved_at', sa.TIMESTAMP(), nullable=True)
        )
    
    # Add rejection tracking fields
    if not column_exists('bhikku_regist', 'br_rejected_by'):
        op.add_column('bhikku_regist', 
            sa.Column('br_rejected_by', sa.String(25), nullable=True)
        )
    if not column_exists('bhikku_regist', 'br_rejected_at'):
        op.add_column('bhikku_regist', 
            sa.Column('br_rejected_at', sa.TIMESTAMP(), nullable=True)
        )
    if not column_exists('bhikku_regist', 'br_rejection_reason'):
        op.add_column('bhikku_regist', 
            sa.Column('br_rejection_reason', sa.String(500), nullable=True)
        )
    
    # Add printing tracking fields
    if not column_exists('bhikku_regist', 'br_printed_at'):
        op.add_column('bhikku_regist', 
            sa.Column('br_printed_at', sa.TIMESTAMP(), nullable=True)
        )
    if not column_exists('bhikku_regist', 'br_printed_by'):
        op.add_column('bhikku_regist', 
            sa.Column('br_printed_by', sa.String(25), nullable=True)
        )
    
    # Add scanning tracking fields
    if not column_exists('bhikku_regist', 'br_scanned_at'):
        op.add_column('bhikku_regist', 
            sa.Column('br_scanned_at', sa.TIMESTAMP(), nullable=True)
        )
    if not column_exists('bhikku_regist', 'br_scanned_by'):
        op.add_column('bhikku_regist', 
            sa.Column('br_scanned_by', sa.String(25), nullable=True)
        )


def downgrade() -> None:
    """Remove workflow fields from bhikku_regist table"""
    
    # Drop index
    op.drop_index('ix_bhikku_regist_br_workflow_status', table_name='bhikku_regist')
    
    # Drop all workflow columns
    op.drop_column('bhikku_regist', 'br_scanned_by')
    op.drop_column('bhikku_regist', 'br_scanned_at')
    op.drop_column('bhikku_regist', 'br_printed_by')
    op.drop_column('bhikku_regist', 'br_printed_at')
    op.drop_column('bhikku_regist', 'br_rejection_reason')
    op.drop_column('bhikku_regist', 'br_rejected_at')
    op.drop_column('bhikku_regist', 'br_rejected_by')
    op.drop_column('bhikku_regist', 'br_approved_at')
    op.drop_column('bhikku_regist', 'br_approved_by')
    op.drop_column('bhikku_regist', 'br_approval_status')
    op.drop_column('bhikku_regist', 'br_workflow_status')
