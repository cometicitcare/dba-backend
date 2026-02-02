"""create silmatha_regist table

Revision ID: 20251117000002
Revises: 20251116133100
Create Date: 2025-11-17 00:00:02

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251117000002'
down_revision = '20251116133100'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create silmatha_regist table
    op.create_table(
        'silmatha_regist',
        sa.Column('sil_id', sa.Integer(), nullable=False),
        sa.Column('sil_regn', sa.String(length=20), nullable=False),
        sa.Column('sil_reqstdate', sa.Date(), nullable=False),
        
        # Personal Information
        sa.Column('sil_gihiname', sa.String(length=50), nullable=True),
        sa.Column('sil_dofb', sa.Date(), nullable=True),
        sa.Column('sil_fathrname', sa.String(length=50), nullable=True),
        sa.Column('sil_email', sa.String(length=50), nullable=True),
        sa.Column('sil_mobile', sa.String(length=10), nullable=True),
        sa.Column('sil_fathrsaddrs', sa.String(length=200), nullable=True),
        sa.Column('sil_fathrsmobile', sa.String(length=10), nullable=True),
        
        # Geographic/Birth Information
        sa.Column('sil_birthpls', sa.String(length=50), nullable=True),
        sa.Column('sil_province', sa.String(length=50), nullable=True),
        sa.Column('sil_district', sa.String(length=50), nullable=True),
        sa.Column('sil_korale', sa.String(length=50), nullable=True),
        sa.Column('sil_pattu', sa.String(length=50), nullable=True),
        sa.Column('sil_division', sa.String(length=50), nullable=True),
        sa.Column('sil_vilage', sa.String(length=50), nullable=True),
        sa.Column('sil_gndiv', sa.String(length=10), nullable=False),
        
        # Temple/Religious Information
        sa.Column('sil_viharadhipathi', sa.String(length=20), nullable=True),
        sa.Column('sil_cat', sa.String(length=5), nullable=True),
        sa.Column('sil_currstat', sa.String(length=5), nullable=False),
        sa.Column('sil_declaration_date', sa.Date(), nullable=True),
        sa.Column('sil_remarks', sa.String(length=100), nullable=True),
        sa.Column('sil_mahanadate', sa.Date(), nullable=True),
        sa.Column('sil_mahananame', sa.String(length=50), nullable=True),
        sa.Column('sil_mahanaacharyacd', sa.String(length=12), nullable=True),
        sa.Column('sil_robing_tutor_residence', sa.String(length=20), nullable=True),
        sa.Column('sil_mahanatemple', sa.String(length=10), nullable=True),
        sa.Column('sil_robing_after_residence_temple', sa.String(length=20), nullable=True),
        
        # Document Storage
        sa.Column('sil_scanned_document_path', sa.String(length=500), nullable=True),
        
        # Workflow Fields
        sa.Column('sil_workflow_status', sa.String(length=20), nullable=False, server_default=sa.text("'PENDING'")),
        sa.Column('sil_approval_status', sa.String(length=20), nullable=True),
        sa.Column('sil_approved_by', sa.String(length=25), nullable=True),
        sa.Column('sil_approved_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('sil_rejected_by', sa.String(length=25), nullable=True),
        sa.Column('sil_rejected_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('sil_rejection_reason', sa.String(length=500), nullable=True),
        sa.Column('sil_printed_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('sil_printed_by', sa.String(length=25), nullable=True),
        sa.Column('sil_scanned_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('sil_scanned_by', sa.String(length=25), nullable=True),
        
        # Reprint Workflow Fields
        sa.Column('sil_reprint_status', sa.String(length=20), nullable=True),
        sa.Column('sil_reprint_requested_by', sa.String(length=25), nullable=True),
        sa.Column('sil_reprint_requested_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('sil_reprint_request_reason', sa.String(length=500), nullable=True),
        sa.Column('sil_reprint_approved_by', sa.String(length=25), nullable=True),
        sa.Column('sil_reprint_approved_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('sil_reprint_rejected_by', sa.String(length=25), nullable=True),
        sa.Column('sil_reprint_rejected_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('sil_reprint_rejection_reason', sa.String(length=500), nullable=True),
        sa.Column('sil_reprint_completed_by', sa.String(length=25), nullable=True),
        sa.Column('sil_reprint_completed_at', sa.TIMESTAMP(), nullable=True),
        
        # Audit Fields
        sa.Column('sil_version', sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        sa.Column('sil_is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=True),
        sa.Column('sil_created_at', sa.TIMESTAMP(), server_default=sa.func.now(), nullable=True),
        sa.Column('sil_updated_at', sa.TIMESTAMP(), server_default=sa.func.now(), nullable=True),
        sa.Column('sil_created_by', sa.String(length=25), nullable=True),
        sa.Column('sil_updated_by', sa.String(length=25), nullable=True),
        sa.Column('sil_version_number', sa.Integer(), server_default=sa.text('1'), nullable=True),
        
        sa.PrimaryKeyConstraint('sil_id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_silmatha_regist_sil_id'), 'silmatha_regist', ['sil_id'], unique=False)
    op.create_index(op.f('ix_silmatha_regist_sil_regn'), 'silmatha_regist', ['sil_regn'], unique=True)
    op.create_index(op.f('ix_silmatha_regist_sil_workflow_status'), 'silmatha_regist', ['sil_workflow_status'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_silmatha_regist_sil_workflow_status'), table_name='silmatha_regist')
    op.drop_index(op.f('ix_silmatha_regist_sil_regn'), table_name='silmatha_regist')
    op.drop_index(op.f('ix_silmatha_regist_sil_id'), table_name='silmatha_regist')
    
    # Drop table
    op.drop_table('silmatha_regist')
