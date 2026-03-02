"""add extended fields to arama and devala

Revision ID: f74081132d7d
Revises: 80d5302d897a
Create Date: 2025-12-07 00:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "f74081132d7d"
down_revision: Union[str, None] = "20251206000001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add extended fields to aramadata and devaladata tables"""
    
    # Add extended fields to aramadata table
    op.add_column('aramadata', sa.Column('ar_province', sa.String(length=100), nullable=True))
    op.add_column('aramadata', sa.Column('ar_district', sa.String(length=100), nullable=True))
    op.add_column('aramadata', sa.Column('ar_divisional_secretariat', sa.String(length=100), nullable=True))
    op.add_column('aramadata', sa.Column('ar_pradeshya_sabha', sa.String(length=100), nullable=True))
    op.add_column('aramadata', sa.Column('ar_nikaya', sa.String(length=50), nullable=True))
    op.add_column('aramadata', sa.Column('ar_viharadhipathi_name', sa.String(length=200), nullable=True))
    op.add_column('aramadata', sa.Column('ar_period_established', sa.String(length=100), nullable=True))
    op.add_column('aramadata', sa.Column('ar_buildings_description', sa.String(length=1000), nullable=True))
    op.add_column('aramadata', sa.Column('ar_dayaka_families_count', sa.String(length=50), nullable=True))
    op.add_column('aramadata', sa.Column('ar_kulangana_committee', sa.String(length=500), nullable=True))
    op.add_column('aramadata', sa.Column('ar_dayaka_sabha', sa.String(length=500), nullable=True))
    op.add_column('aramadata', sa.Column('ar_temple_working_committee', sa.String(length=500), nullable=True))
    op.add_column('aramadata', sa.Column('ar_other_associations', sa.String(length=500), nullable=True))
    op.add_column('aramadata', sa.Column('ar_temple_owned_land', sa.String(length=2000), nullable=True))
    op.add_column('aramadata', sa.Column('ar_land_info_certified', sa.Boolean(), nullable=True))
    op.add_column('aramadata', sa.Column('ar_resident_bhikkhus', sa.String(length=2000), nullable=True))
    op.add_column('aramadata', sa.Column('ar_resident_bhikkhus_certified', sa.Boolean(), nullable=True))
    op.add_column('aramadata', sa.Column('ar_inspection_report', sa.String(length=1000), nullable=True))
    op.add_column('aramadata', sa.Column('ar_inspection_code', sa.String(length=100), nullable=True))
    op.add_column('aramadata', sa.Column('ar_grama_niladhari_division_ownership', sa.String(length=200), nullable=True))
    op.add_column('aramadata', sa.Column('ar_sanghika_donation_deed', sa.Boolean(), nullable=True))
    op.add_column('aramadata', sa.Column('ar_government_donation_deed', sa.Boolean(), nullable=True))
    op.add_column('aramadata', sa.Column('ar_government_donation_deed_in_progress', sa.Boolean(), nullable=True))
    op.add_column('aramadata', sa.Column('ar_authority_consent_attached', sa.Boolean(), nullable=True))
    op.add_column('aramadata', sa.Column('ar_recommend_new_center', sa.Boolean(), nullable=True))
    op.add_column('aramadata', sa.Column('ar_recommend_registered_temple', sa.Boolean(), nullable=True))
    op.add_column('aramadata', sa.Column('ar_annex2_recommend_construction', sa.Boolean(), nullable=True))
    op.add_column('aramadata', sa.Column('ar_annex2_land_ownership_docs', sa.Boolean(), nullable=True))
    op.add_column('aramadata', sa.Column('ar_annex2_chief_incumbent_letter', sa.Boolean(), nullable=True))
    op.add_column('aramadata', sa.Column('ar_annex2_coordinator_recommendation', sa.Boolean(), nullable=True))
    op.add_column('aramadata', sa.Column('ar_annex2_divisional_secretary_recommendation', sa.Boolean(), nullable=True))
    op.add_column('aramadata', sa.Column('ar_annex2_approval_construction', sa.Boolean(), nullable=True))
    op.add_column('aramadata', sa.Column('ar_annex2_referral_resubmission', sa.Boolean(), nullable=True))
    
    # Add extended fields to devaladata table
    op.add_column('devaladata', sa.Column('dv_province', sa.String(length=100), nullable=True))
    op.add_column('devaladata', sa.Column('dv_district', sa.String(length=100), nullable=True))
    op.add_column('devaladata', sa.Column('dv_divisional_secretariat', sa.String(length=100), nullable=True))
    op.add_column('devaladata', sa.Column('dv_pradeshya_sabha', sa.String(length=100), nullable=True))
    op.add_column('devaladata', sa.Column('dv_nikaya', sa.String(length=50), nullable=True))
    op.add_column('devaladata', sa.Column('dv_viharadhipathi_name', sa.String(length=200), nullable=True))
    op.add_column('devaladata', sa.Column('dv_period_established', sa.String(length=100), nullable=True))
    op.add_column('devaladata', sa.Column('dv_buildings_description', sa.String(length=1000), nullable=True))
    op.add_column('devaladata', sa.Column('dv_dayaka_families_count', sa.String(length=50), nullable=True))
    op.add_column('devaladata', sa.Column('dv_kulangana_committee', sa.String(length=500), nullable=True))
    op.add_column('devaladata', sa.Column('dv_dayaka_sabha', sa.String(length=500), nullable=True))
    op.add_column('devaladata', sa.Column('dv_temple_working_committee', sa.String(length=500), nullable=True))
    op.add_column('devaladata', sa.Column('dv_other_associations', sa.String(length=500), nullable=True))
    op.add_column('devaladata', sa.Column('dv_temple_owned_land', sa.String(length=2000), nullable=True))
    op.add_column('devaladata', sa.Column('dv_land_info_certified', sa.Boolean(), nullable=True))
    op.add_column('devaladata', sa.Column('dv_resident_bhikkhus', sa.String(length=2000), nullable=True))
    op.add_column('devaladata', sa.Column('dv_resident_bhikkhus_certified', sa.Boolean(), nullable=True))
    op.add_column('devaladata', sa.Column('dv_inspection_report', sa.String(length=1000), nullable=True))
    op.add_column('devaladata', sa.Column('dv_inspection_code', sa.String(length=100), nullable=True))
    op.add_column('devaladata', sa.Column('dv_grama_niladhari_division_ownership', sa.String(length=200), nullable=True))
    op.add_column('devaladata', sa.Column('dv_sanghika_donation_deed', sa.Boolean(), nullable=True))
    op.add_column('devaladata', sa.Column('dv_government_donation_deed', sa.Boolean(), nullable=True))
    op.add_column('devaladata', sa.Column('dv_government_donation_deed_in_progress', sa.Boolean(), nullable=True))
    op.add_column('devaladata', sa.Column('dv_authority_consent_attached', sa.Boolean(), nullable=True))
    op.add_column('devaladata', sa.Column('dv_recommend_new_center', sa.Boolean(), nullable=True))
    op.add_column('devaladata', sa.Column('dv_recommend_registered_temple', sa.Boolean(), nullable=True))
    op.add_column('devaladata', sa.Column('dv_annex2_recommend_construction', sa.Boolean(), nullable=True))
    op.add_column('devaladata', sa.Column('dv_annex2_land_ownership_docs', sa.Boolean(), nullable=True))
    op.add_column('devaladata', sa.Column('dv_annex2_chief_incumbent_letter', sa.Boolean(), nullable=True))
    op.add_column('devaladata', sa.Column('dv_annex2_coordinator_recommendation', sa.Boolean(), nullable=True))
    op.add_column('devaladata', sa.Column('dv_annex2_divisional_secretary_recommendation', sa.Boolean(), nullable=True))
    op.add_column('devaladata', sa.Column('dv_annex2_approval_construction', sa.Boolean(), nullable=True))
    op.add_column('devaladata', sa.Column('dv_annex2_referral_resubmission', sa.Boolean(), nullable=True))


def downgrade() -> None:
    """Remove extended fields from aramadata and devaladata tables"""
    
    # Remove extended fields from aramadata table
    op.drop_column('aramadata', 'ar_annex2_referral_resubmission')
    op.drop_column('aramadata', 'ar_annex2_approval_construction')
    op.drop_column('aramadata', 'ar_annex2_divisional_secretary_recommendation')
    op.drop_column('aramadata', 'ar_annex2_coordinator_recommendation')
    op.drop_column('aramadata', 'ar_annex2_chief_incumbent_letter')
    op.drop_column('aramadata', 'ar_annex2_land_ownership_docs')
    op.drop_column('aramadata', 'ar_annex2_recommend_construction')
    op.drop_column('aramadata', 'ar_recommend_registered_temple')
    op.drop_column('aramadata', 'ar_recommend_new_center')
    op.drop_column('aramadata', 'ar_authority_consent_attached')
    op.drop_column('aramadata', 'ar_government_donation_deed_in_progress')
    op.drop_column('aramadata', 'ar_government_donation_deed')
    op.drop_column('aramadata', 'ar_sanghika_donation_deed')
    op.drop_column('aramadata', 'ar_grama_niladhari_division_ownership')
    op.drop_column('aramadata', 'ar_inspection_code')
    op.drop_column('aramadata', 'ar_inspection_report')
    op.drop_column('aramadata', 'ar_resident_bhikkhus_certified')
    op.drop_column('aramadata', 'ar_resident_bhikkhus')
    op.drop_column('aramadata', 'ar_land_info_certified')
    op.drop_column('aramadata', 'ar_temple_owned_land')
    op.drop_column('aramadata', 'ar_other_associations')
    op.drop_column('aramadata', 'ar_temple_working_committee')
    op.drop_column('aramadata', 'ar_dayaka_sabha')
    op.drop_column('aramadata', 'ar_kulangana_committee')
    op.drop_column('aramadata', 'ar_dayaka_families_count')
    op.drop_column('aramadata', 'ar_buildings_description')
    op.drop_column('aramadata', 'ar_period_established')
    op.drop_column('aramadata', 'ar_viharadhipathi_name')
    op.drop_column('aramadata', 'ar_nikaya')
    op.drop_column('aramadata', 'ar_pradeshya_sabha')
    op.drop_column('aramadata', 'ar_divisional_secretariat')
    op.drop_column('aramadata', 'ar_district')
    op.drop_column('aramadata', 'ar_province')
    
    # Remove extended fields from devaladata table
    op.drop_column('devaladata', 'dv_annex2_referral_resubmission')
    op.drop_column('devaladata', 'dv_annex2_approval_construction')
    op.drop_column('devaladata', 'dv_annex2_divisional_secretary_recommendation')
    op.drop_column('devaladata', 'dv_annex2_coordinator_recommendation')
    op.drop_column('devaladata', 'dv_annex2_chief_incumbent_letter')
    op.drop_column('devaladata', 'dv_annex2_land_ownership_docs')
    op.drop_column('devaladata', 'dv_annex2_recommend_construction')
    op.drop_column('devaladata', 'dv_recommend_registered_temple')
    op.drop_column('devaladata', 'dv_recommend_new_center')
    op.drop_column('devaladata', 'dv_authority_consent_attached')
    op.drop_column('devaladata', 'dv_government_donation_deed_in_progress')
    op.drop_column('devaladata', 'dv_government_donation_deed')
    op.drop_column('devaladata', 'dv_sanghika_donation_deed')
    op.drop_column('devaladata', 'dv_grama_niladhari_division_ownership')
    op.drop_column('devaladata', 'dv_inspection_code')
    op.drop_column('devaladata', 'dv_inspection_report')
    op.drop_column('devaladata', 'dv_resident_bhikkhus_certified')
    op.drop_column('devaladata', 'dv_resident_bhikkhus')
    op.drop_column('devaladata', 'dv_land_info_certified')
    op.drop_column('devaladata', 'dv_temple_owned_land')
    op.drop_column('devaladata', 'dv_other_associations')
    op.drop_column('devaladata', 'dv_temple_working_committee')
    op.drop_column('devaladata', 'dv_dayaka_sabha')
    op.drop_column('devaladata', 'dv_kulangana_committee')
    op.drop_column('devaladata', 'dv_dayaka_families_count')
    op.drop_column('devaladata', 'dv_buildings_description')
    op.drop_column('devaladata', 'dv_period_established')
    op.drop_column('devaladata', 'dv_viharadhipathi_name')
    op.drop_column('devaladata', 'dv_nikaya')
    op.drop_column('devaladata', 'dv_pradeshya_sabha')
    op.drop_column('devaladata', 'dv_divisional_secretariat')
    op.drop_column('devaladata', 'dv_district')
    op.drop_column('devaladata', 'dv_province')
