"""add bhikku_id_card table

Revision ID: c7d97c3a5127
Revises: 20251115152104
Create Date: 2025-11-15 16:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c7d97c3a5127'
down_revision = '20251115152104'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create bhikku_id_card table with all required fields."""
    op.create_table(
        'bhikku_id_card',
        sa.Column('bic_id', sa.Integer(), nullable=False, comment='Primary key'),
        sa.Column('bic_br_regn', sa.String(length=20), nullable=False, comment='Bhikku registration number (FK to bhikku_regist.br_regn)'),
        sa.Column('bic_form_no', sa.String(length=30), nullable=False, comment='Auto-generated unique form number (e.g., FORM-2025-0001)'),
        
        # Top Section Fields
        sa.Column('bic_divisional_secretariat', sa.String(length=100), nullable=True, comment='Divisional Secretariat'),
        sa.Column('bic_district', sa.String(length=100), nullable=True, comment='District'),
        
        # 01. Declaration Full Name
        sa.Column('bic_full_bhikku_name', sa.String(length=200), nullable=False, comment='Full Bhikku Name'),
        sa.Column('bic_title_post', sa.String(length=100), nullable=True, comment='Title/Post'),
        
        # 02. As per birth certificate
        sa.Column('bic_lay_name_full', sa.String(length=200), nullable=False, comment='Gihi/Lay Name in full'),
        sa.Column('bic_dob', sa.Date(), nullable=False, comment='Date of Birth'),
        sa.Column('bic_birth_place', sa.String(length=200), nullable=True, comment='Place of Birth'),
        
        # 03. Ordination details
        sa.Column('bic_robing_date', sa.Date(), nullable=True, comment='Date of Robing'),
        sa.Column('bic_robing_place', sa.String(length=200), nullable=True, comment='Place of Robing'),
        sa.Column('bic_robing_nikaya', sa.String(length=100), nullable=True, comment='Nikaya at robing'),
        sa.Column('bic_robing_parshawaya', sa.String(length=100), nullable=True, comment='Parshawaya at robing'),
        
        # 04. Registration numbers & higher ordination
        sa.Column('bic_samanera_reg_no', sa.String(length=50), nullable=True, comment='Samanera Registration Number'),
        sa.Column('bic_upasampada_reg_no', sa.String(length=50), nullable=True, comment='Upasampada Registration Number'),
        sa.Column('bic_higher_ord_date', sa.Date(), nullable=True, comment='Date of Higher Ordinance'),
        
        # 05. Name at Higher Ordinance
        sa.Column('bic_higher_ord_name', sa.String(length=200), nullable=True, comment='Name taken at Higher Ordinance'),
        
        # 06. Permanent residence
        sa.Column('bic_perm_residence', sa.Text(), nullable=True, comment='Permanent residence address'),
        
        # 07. National ID
        sa.Column('bic_national_id', sa.String(length=20), nullable=True, comment='National ID Card Number'),
        
        # 08. Places stayed so far (JSONB array)
        sa.Column('bic_stay_history', sa.JSON(), nullable=True, comment='Array of stay history: [{temple_name, temple_address, from_date, to_date}]'),
        
        # File Upload Fields
        sa.Column('bic_left_thumbprint_url', sa.String(length=500), nullable=True, comment='File path for left thumbprint image'),
        sa.Column('bic_applicant_photo_url', sa.String(length=500), nullable=True, comment='File path for applicant photo (3cm x 2.5cm)'),
        
        # Workflow Status
        sa.Column('bic_workflow_status', sa.String(length=20), server_default=sa.text("'PENDING'"), nullable=False, comment='Workflow status: PENDING, APPROVED, REJECTED, COMPLETED'),
        
        # Approval/Rejection tracking
        sa.Column('bic_approved_by', sa.String(length=50), nullable=True, comment='User who approved the ID card'),
        sa.Column('bic_approved_at', sa.TIMESTAMP(), nullable=True, comment='Timestamp of approval'),
        sa.Column('bic_rejected_by', sa.String(length=50), nullable=True, comment='User who rejected the ID card'),
        sa.Column('bic_rejected_at', sa.TIMESTAMP(), nullable=True, comment='Timestamp of rejection'),
        sa.Column('bic_rejection_reason', sa.Text(), nullable=True, comment='Reason for rejection'),
        
        # Print tracking
        sa.Column('bic_printed_by', sa.String(length=50), nullable=True, comment='User who marked as printed'),
        sa.Column('bic_printed_at', sa.TIMESTAMP(), nullable=True, comment='Timestamp when marked as printed'),
        
        # Audit Fields
        sa.Column('bic_is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('bic_created_at', sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False),
        sa.Column('bic_updated_at', sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False),
        sa.Column('bic_created_by', sa.String(length=50), nullable=True, comment='User who created the record'),
        sa.Column('bic_updated_by', sa.String(length=50), nullable=True, comment='User who last updated the record'),
        sa.Column('bic_version_number', sa.Integer(), server_default=sa.text('1'), nullable=False),
        
        # Primary Key
        sa.PrimaryKeyConstraint('bic_id'),
        
        # Foreign Key to bhikku_regist
        sa.ForeignKeyConstraint(['bic_br_regn'], ['bhikku_regist.br_regn'], ondelete='CASCADE'),
        
        # Unique Constraints
        sa.UniqueConstraint('bic_br_regn', name='uq_bhikku_id_card_br_regn'),
        sa.UniqueConstraint('bic_form_no', name='uq_bhikku_id_card_form_no'),
    )
    
    # Create indexes
    op.create_index('ix_bhikku_id_card_bic_id', 'bhikku_id_card', ['bic_id'])
    op.create_index('ix_bhikku_id_card_bic_br_regn', 'bhikku_id_card', ['bic_br_regn'])
    op.create_index('ix_bhikku_id_card_bic_form_no', 'bhikku_id_card', ['bic_form_no'])
    op.create_index('ix_bhikku_id_card_bic_workflow_status', 'bhikku_id_card', ['bic_workflow_status'])


def downgrade() -> None:
    """Drop bhikku_id_card table and all indexes."""
    op.drop_index('ix_bhikku_id_card_bic_workflow_status', table_name='bhikku_id_card')
    op.drop_index('ix_bhikku_id_card_bic_form_no', table_name='bhikku_id_card')
    op.drop_index('ix_bhikku_id_card_bic_br_regn', table_name='bhikku_id_card')
    op.drop_index('ix_bhikku_id_card_bic_id', table_name='bhikku_id_card')
    op.drop_table('bhikku_id_card')
