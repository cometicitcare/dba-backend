"""add vihara extended fields and related tables

Revision ID: 20251206000001
Revises: 
Create Date: 2025-12-06

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251206000001'
down_revision = '20251205000001'
branch_labels = None
depends_on = None


def upgrade():
    # Add new fields to vihaddata table
    op.add_column('vihaddata', sa.Column('vh_province', sa.String(length=100), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_district', sa.String(length=100), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_divisional_secretariat', sa.String(length=100), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_pradeshya_sabha', sa.String(length=100), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_nikaya', sa.String(length=50), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_viharadhipathi_name', sa.String(length=200), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_period_established', sa.String(length=100), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_buildings_description', sa.String(length=1000), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_dayaka_families_count', sa.String(length=50), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_kulangana_committee', sa.String(length=500), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_dayaka_sabha', sa.String(length=500), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_temple_working_committee', sa.String(length=500), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_other_associations', sa.String(length=500), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_land_info_certified', sa.Boolean(), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_resident_bhikkhus_certified', sa.Boolean(), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_inspection_report', sa.String(length=1000), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_inspection_code', sa.String(length=100), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_grama_niladhari_division_ownership', sa.String(length=200), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_sanghika_donation_deed', sa.Boolean(), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_government_donation_deed', sa.Boolean(), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_government_donation_deed_in_progress', sa.Boolean(), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_authority_consent_attached', sa.Boolean(), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_recommend_new_center', sa.Boolean(), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_recommend_registered_temple', sa.Boolean(), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_annex2_recommend_construction', sa.Boolean(), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_annex2_land_ownership_docs', sa.Boolean(), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_annex2_chief_incumbent_letter', sa.Boolean(), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_annex2_coordinator_recommendation', sa.Boolean(), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_annex2_divisional_secretary_recommendation', sa.Boolean(), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_annex2_approval_construction', sa.Boolean(), nullable=True))
    op.add_column('vihaddata', sa.Column('vh_annex2_referral_resubmission', sa.Boolean(), nullable=True))

    # Create temple_land table
    op.create_table(
        'temple_land',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vh_id', sa.Integer(), nullable=False),
        sa.Column('serial_number', sa.Integer(), nullable=False),
        sa.Column('land_name', sa.String(length=200), nullable=True),
        sa.Column('village', sa.String(length=200), nullable=True),
        sa.Column('district', sa.String(length=100), nullable=True),
        sa.Column('extent', sa.String(length=100), nullable=True),
        sa.Column('cultivation_description', sa.String(length=500), nullable=True),
        sa.Column('ownership_nature', sa.String(length=200), nullable=True),
        sa.Column('deed_number', sa.String(length=100), nullable=True),
        sa.Column('title_registration_number', sa.String(length=100), nullable=True),
        sa.Column('tax_details', sa.String(length=500), nullable=True),
        sa.Column('land_occupants', sa.String(length=500), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['vh_id'], ['vihaddata.vh_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_temple_land_id'), 'temple_land', ['id'], unique=False)
    op.create_index(op.f('ix_temple_land_vh_id'), 'temple_land', ['vh_id'], unique=False)

    # Create resident_bhikkhu table
    op.create_table(
        'resident_bhikkhu',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vh_id', sa.Integer(), nullable=False),
        sa.Column('serial_number', sa.Integer(), nullable=False),
        sa.Column('bhikkhu_name', sa.String(length=200), nullable=True),
        sa.Column('registration_number', sa.String(length=100), nullable=True),
        sa.Column('occupation_education', sa.String(length=500), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['vh_id'], ['vihaddata.vh_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_resident_bhikkhu_id'), 'resident_bhikkhu', ['id'], unique=False)
    op.create_index(op.f('ix_resident_bhikkhu_vh_id'), 'resident_bhikkhu', ['vh_id'], unique=False)


def downgrade():
    # Drop tables
    op.drop_index(op.f('ix_resident_bhikkhu_vh_id'), table_name='resident_bhikkhu')
    op.drop_index(op.f('ix_resident_bhikkhu_id'), table_name='resident_bhikkhu')
    op.drop_table('resident_bhikkhu')
    
    op.drop_index(op.f('ix_temple_land_vh_id'), table_name='temple_land')
    op.drop_index(op.f('ix_temple_land_id'), table_name='temple_land')
    op.drop_table('temple_land')

    # Drop columns from vihaddata
    op.drop_column('vihaddata', 'vh_annex2_referral_resubmission')
    op.drop_column('vihaddata', 'vh_annex2_approval_construction')
    op.drop_column('vihaddata', 'vh_annex2_divisional_secretary_recommendation')
    op.drop_column('vihaddata', 'vh_annex2_coordinator_recommendation')
    op.drop_column('vihaddata', 'vh_annex2_chief_incumbent_letter')
    op.drop_column('vihaddata', 'vh_annex2_land_ownership_docs')
    op.drop_column('vihaddata', 'vh_annex2_recommend_construction')
    op.drop_column('vihaddata', 'vh_recommend_registered_temple')
    op.drop_column('vihaddata', 'vh_recommend_new_center')
    op.drop_column('vihaddata', 'vh_authority_consent_attached')
    op.drop_column('vihaddata', 'vh_government_donation_deed_in_progress')
    op.drop_column('vihaddata', 'vh_government_donation_deed')
    op.drop_column('vihaddata', 'vh_sanghika_donation_deed')
    op.drop_column('vihaddata', 'vh_grama_niladhari_division_ownership')
    op.drop_column('vihaddata', 'vh_inspection_code')
    op.drop_column('vihaddata', 'vh_inspection_report')
    op.drop_column('vihaddata', 'vh_resident_bhikkhus_certified')
    op.drop_column('vihaddata', 'vh_land_info_certified')
    op.drop_column('vihaddata', 'vh_other_associations')
    op.drop_column('vihaddata', 'vh_temple_working_committee')
    op.drop_column('vihaddata', 'vh_dayaka_sabha')
    op.drop_column('vihaddata', 'vh_kulangana_committee')
    op.drop_column('vihaddata', 'vh_dayaka_families_count')
    op.drop_column('vihaddata', 'vh_buildings_description')
    op.drop_column('vihaddata', 'vh_period_established')
    op.drop_column('vihaddata', 'vh_viharadhipathi_name')
    op.drop_column('vihaddata', 'vh_nikaya')
    op.drop_column('vihaddata', 'vh_pradeshya_sabha')
    op.drop_column('vihaddata', 'vh_divisional_secretariat')
    op.drop_column('vihaddata', 'vh_district')
    op.drop_column('vihaddata', 'vh_province')
