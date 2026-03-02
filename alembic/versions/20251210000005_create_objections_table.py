"""create objections table

Revision ID: 20251210000005
Revises: 20251210000004
Create Date: 2025-12-10 00:00:05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251210000005'
down_revision = '20251210000004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create objections table"""
    op.create_table(
        'objections',
        sa.Column('obj_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('obj_entity_type', sa.Enum('VIHARA', 'ARAMA', 'DEVALA', name='entitytype'), nullable=False, comment='Type of entity (VIHARA, ARAMA, DEVALA)'),
        sa.Column('obj_entity_trn', sa.String(length=50), nullable=False, comment='TRN of the vihara/arama/devala'),
        sa.Column('obj_entity_name', sa.String(length=200), nullable=True, comment='Name of the entity for reference'),
        sa.Column('obj_reason', sa.String(length=1000), nullable=False, comment='Reason for objection/restriction'),
        sa.Column('obj_status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', 'CANCELLED', name='objectionstatus'), server_default='PENDING', nullable=False, comment='Status of objection (PENDING, APPROVED, REJECTED, CANCELLED)'),
        sa.Column('obj_submitted_by', sa.String(length=25), nullable=True, comment='Username who submitted the objection'),
        sa.Column('obj_submitted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp of submission'),
        sa.Column('obj_approved_by', sa.String(length=25), nullable=True, comment='Username who approved the objection'),
        sa.Column('obj_approved_at', sa.DateTime(timezone=True), nullable=True, comment='Timestamp of approval'),
        sa.Column('obj_rejected_by', sa.String(length=25), nullable=True, comment='Username who rejected the objection'),
        sa.Column('obj_rejected_at', sa.DateTime(timezone=True), nullable=True, comment='Timestamp of rejection'),
        sa.Column('obj_rejection_reason', sa.String(length=500), nullable=True, comment='Reason for rejection'),
        sa.Column('obj_cancelled_by', sa.String(length=25), nullable=True, comment='Username who cancelled the objection'),
        sa.Column('obj_cancelled_at', sa.DateTime(timezone=True), nullable=True, comment='Timestamp of cancellation'),
        sa.Column('obj_cancellation_reason', sa.String(length=500), nullable=True, comment='Reason for cancellation'),
        sa.Column('obj_is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False, comment='Soft delete flag'),
        sa.Column('obj_created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Creation timestamp'),
        sa.Column('obj_updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True, comment='Last update timestamp'),
        sa.Column('obj_updated_by', sa.String(length=25), nullable=True, comment='Username who last updated'),
        sa.PrimaryKeyConstraint('obj_id')
    )
    
    # Create indexes
    op.create_index('ix_objections_obj_id', 'objections', ['obj_id'])
    op.create_index('ix_objections_obj_entity_type', 'objections', ['obj_entity_type'])
    op.create_index('ix_objections_obj_entity_trn', 'objections', ['obj_entity_trn'])
    op.create_index('ix_objections_obj_status', 'objections', ['obj_status'])
    
    # Create composite index for efficient queries
    op.create_index('ix_objections_entity_type_trn_status', 'objections', ['obj_entity_type', 'obj_entity_trn', 'obj_status'])


def downgrade() -> None:
    """Drop objections table"""
    op.drop_index('ix_objections_entity_type_trn_status', 'objections')
    op.drop_index('ix_objections_obj_status', 'objections')
    op.drop_index('ix_objections_obj_entity_trn', 'objections')
    op.drop_index('ix_objections_obj_entity_type', 'objections')
    op.drop_index('ix_objections_obj_id', 'objections')
    op.drop_table('objections')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS objectionstatus')
    op.execute('DROP TYPE IF EXISTS entitytype')
