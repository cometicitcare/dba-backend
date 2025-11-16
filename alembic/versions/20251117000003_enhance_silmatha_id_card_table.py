"""enhance_silmatha_id_card_table

Revision ID: 20251117000003
Revises: 20251117000001
Create Date: 2025-01-17 00:00:03

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20251117000003'
down_revision: Union[str, None] = '20251117000001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create silmatha_id_card table with comprehensive structure matching bhikku_id_card.
    """
    
    op.create_table(
        'silmatha_id_card',
        # --- Primary Key ---
        sa.Column('sic_id', sa.Integer(), autoincrement=True, nullable=False),
        
        # --- Auto-generated Form Number (Unique) ---
        sa.Column('sic_form_no', sa.String(length=20), nullable=False),
        
        # --- Foreign Key to silmatha_regist ---
        sa.Column('sic_sil_regn', sa.String(length=20), nullable=False),
        
        # --- Top Section ---
        sa.Column('sic_divisional_secretariat', sa.String(length=100), nullable=True),
        sa.Column('sic_district', sa.String(length=100), nullable=True),
        
        # --- 01. Declaration Full Name ---
        sa.Column('sic_full_silmatha_name', sa.String(length=200), nullable=False),
        sa.Column('sic_title_post', sa.String(length=100), nullable=True),
        
        # --- 02. As per birth certificate ---
        sa.Column('sic_lay_name_full', sa.String(length=200), nullable=False),
        sa.Column('sic_dob', sa.Date(), nullable=False),
        sa.Column('sic_birth_place', sa.String(length=200), nullable=True),
        
        # --- 03. Ordination details ---
        sa.Column('sic_robing_date', sa.Date(), nullable=True),
        sa.Column('sic_robing_place', sa.String(length=200), nullable=True),
        sa.Column('sic_robing_nikaya', sa.String(length=100), nullable=True),
        sa.Column('sic_robing_parshawaya', sa.String(length=100), nullable=True),
        
        # --- 04. Registration numbers & higher ordination ---
        sa.Column('sic_samaneri_reg_no', sa.String(length=50), nullable=True),
        sa.Column('sic_dasa_sil_mata_reg_no', sa.String(length=50), nullable=True),
        sa.Column('sic_higher_ord_date', sa.Date(), nullable=True),
        
        # --- 05. Name at Higher Ordinance ---
        sa.Column('sic_higher_ord_name', sa.String(length=200), nullable=True),
        
        # --- 06. Permanent residence ---
        sa.Column('sic_perm_residence', sa.Text(), nullable=True),
        
        # --- 07. National ID ---
        sa.Column('sic_national_id', sa.String(length=20), nullable=True),
        
        # --- 08. Places stayed so far (JSON array) ---
        sa.Column('sic_stay_history', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        
        # --- File Upload URLs ---
        sa.Column('sic_left_thumbprint_url', sa.String(), nullable=True),
        sa.Column('sic_applicant_photo_url', sa.String(), nullable=True),
        
        # --- Workflow Status ---
        sa.Column('sic_workflow_status', sa.String(length=50), nullable=False, server_default='PENDING'),
        
        # --- Approval/Rejection Tracking ---
        sa.Column('sic_approved_by', sa.String(length=100), nullable=True),
        sa.Column('sic_approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sic_rejection_reason', sa.Text(), nullable=True),
        sa.Column('sic_rejected_by', sa.String(length=100), nullable=True),
        sa.Column('sic_rejected_at', sa.DateTime(timezone=True), nullable=True),
        
        # --- Printing Tracking ---
        sa.Column('sic_printed_by', sa.String(length=100), nullable=True),
        sa.Column('sic_printed_at', sa.DateTime(timezone=True), nullable=True),
        
        # --- Audit Fields ---
        sa.Column('sic_created_by', sa.String(length=100), nullable=True),
        sa.Column('sic_created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('sic_updated_by', sa.String(length=100), nullable=True),
        sa.Column('sic_updated_at', sa.DateTime(timezone=True), nullable=True),
        
        # --- Constraints ---
        sa.PrimaryKeyConstraint('sic_id'),
        sa.ForeignKeyConstraint(['sic_sil_regn'], ['silmatha_regist.sil_regn'], name='fk_silmatha_id_card_sil_regn'),
    )
    
    # Create indexes
    op.create_index('ix_silmatha_id_card_sic_id', 'silmatha_id_card', ['sic_id'], unique=False)
    op.create_index('ix_silmatha_id_card_sic_form_no', 'silmatha_id_card', ['sic_form_no'], unique=True)
    op.create_index('ix_silmatha_id_card_sic_sil_regn', 'silmatha_id_card', ['sic_sil_regn'], unique=True)


def downgrade() -> None:
    """
    Drop the silmatha_id_card table.
    """
    op.drop_index('ix_silmatha_id_card_sic_sil_regn', 'silmatha_id_card')
    op.drop_index('ix_silmatha_id_card_sic_form_no', 'silmatha_id_card')
    op.drop_index('ix_silmatha_id_card_sic_id', 'silmatha_id_card')
    op.drop_table('silmatha_id_card')
