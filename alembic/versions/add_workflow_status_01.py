"""Add workflow status placeholder.

Revision ID: add_workflow_status_01
Revises: 8b0c7f02d60c
Create Date: 2024-10-08 00:00:00.000000
"""

from alembic import op  # noqa: F401
import sqlalchemy as sa  # noqa: F401


# revision identifiers, used by Alembic.
revision = "add_workflow_status_01"
down_revision = "8b0c7f02d60c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add workflow status column to bhikku_regist and create bhikku_workflow_flags table."""
    # Add workflow_status column to bhikku_regist table
    op.add_column(
        'bhikku_regist',
        sa.Column('br_workflow_status', sa.String(20), nullable=False, server_default='pending')
    )
    
    # Create bhikku_workflow_flags table
    op.create_table(
        'bhikku_workflow_flags',
        sa.Column('bwf_id', sa.Integer(), nullable=False),
        sa.Column('bwf_bhikku_id', sa.Integer(), nullable=False),
        sa.Column('bwf_bhikku_regn', sa.String(20), nullable=False),
        sa.Column('bwf_current_flag', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('bwf_pending_date', sa.TIMESTAMP(), nullable=True),
        sa.Column('bwf_approval_date', sa.TIMESTAMP(), nullable=True),
        sa.Column('bwf_approval_by', sa.String(25), nullable=True),
        sa.Column('bwf_approval_notes', sa.String(500), nullable=True),
        sa.Column('bwf_printing_date', sa.TIMESTAMP(), nullable=True),
        sa.Column('bwf_print_by', sa.String(25), nullable=True),
        sa.Column('bwf_scan_date', sa.TIMESTAMP(), nullable=True),
        sa.Column('bwf_scan_by', sa.String(25), nullable=True),
        sa.Column('bwf_completion_date', sa.TIMESTAMP(), nullable=True),
        sa.Column('bwf_completed_by', sa.String(25), nullable=True),
        sa.Column('bwf_created_at', sa.TIMESTAMP(), server_default=sa.func.now()),
        sa.Column('bwf_updated_at', sa.TIMESTAMP(), server_default=sa.func.now()),
        sa.Column('bwf_created_by', sa.String(25), nullable=True),
        sa.Column('bwf_updated_by', sa.String(25), nullable=True),
        sa.Column('bwf_is_deleted', sa.Boolean(), server_default='false'),
        sa.Column('bwf_version_number', sa.Integer(), server_default='1'),
        sa.ForeignKeyConstraint(['bwf_bhikku_id'], ['bhikku_regist.br_id'], onupdate='CASCADE', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['bwf_created_by'], ['user_accounts.ua_user_id'], onupdate='CASCADE', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['bwf_updated_by'], ['user_accounts.ua_user_id'], onupdate='CASCADE', ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('bwf_id')
    )
    op.create_index(op.f('ix_bhikku_workflow_flags_bwf_bhikku_id'), 'bhikku_workflow_flags', ['bwf_bhikku_id'], unique=False)
    op.create_index(op.f('ix_bhikku_workflow_flags_bwf_bhikku_regn'), 'bhikku_workflow_flags', ['bwf_bhikku_regn'], unique=False)
    op.create_index(op.f('ix_bhikku_workflow_flags_bwf_current_flag'), 'bhikku_workflow_flags', ['bwf_current_flag'], unique=False)


def downgrade() -> None:
    """Revert workflow status changes."""
    op.drop_index(op.f('ix_bhikku_workflow_flags_bwf_current_flag'), table_name='bhikku_workflow_flags')
    op.drop_index(op.f('ix_bhikku_workflow_flags_bwf_bhikku_regn'), table_name='bhikku_workflow_flags')
    op.drop_index(op.f('ix_bhikku_workflow_flags_bwf_bhikku_id'), table_name='bhikku_workflow_flags')
    op.drop_table('bhikku_workflow_flags')
    op.drop_column('bhikku_regist', 'br_workflow_status')

