"""add_foreign_keys_to_bhikku_regist

Revision ID: 3015686570d6
Revises: 14f4a3921216
Create Date: 2025-11-15 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3015686570d6'
down_revision = '14f4a3921216'
branch_labels = None
depends_on = None


def upgrade():
    # Add foreign key constraints to bhikku_regist table
    
    # br_province -> cmm_province.cp_code
    op.create_foreign_key(
        'fk_bhikku_regist_province',
        'bhikku_regist', 'cmm_province',
        ['br_province'], ['cp_code'],
        ondelete='SET NULL'
    )
    
    # br_district -> cmm_districtdata.dd_dcode
    op.create_foreign_key(
        'fk_bhikku_regist_district',
        'bhikku_regist', 'cmm_districtdata',
        ['br_district'], ['dd_dcode'],
        ondelete='SET NULL'
    )
    
    # br_division -> cmm_dvsec.dv_dvcode
    op.create_foreign_key(
        'fk_bhikku_regist_division',
        'bhikku_regist', 'cmm_dvsec',
        ['br_division'], ['dv_dvcode'],
        ondelete='SET NULL'
    )
    
    # br_gndiv -> cmm_gndata.gn_gnc
    op.create_foreign_key(
        'fk_bhikku_regist_gndiv',
        'bhikku_regist', 'cmm_gndata',
        ['br_gndiv'], ['gn_gnc'],
        ondelete='RESTRICT'
    )
    
    # br_currstat -> statusdata.st_statcd
    op.create_foreign_key(
        'fk_bhikku_regist_currstat',
        'bhikku_regist', 'statusdata',
        ['br_currstat'], ['st_statcd'],
        ondelete='RESTRICT'
    )
    
    # br_parshawaya -> cmm_parshawadata.pr_prn
    op.create_foreign_key(
        'fk_bhikku_regist_parshawaya',
        'bhikku_regist', 'cmm_parshawadata',
        ['br_parshawaya'], ['pr_prn'],
        ondelete='RESTRICT'
    )
    
    # br_livtemple -> vihaddata.vh_trn
    op.create_foreign_key(
        'fk_bhikku_regist_livtemple',
        'bhikku_regist', 'vihaddata',
        ['br_livtemple'], ['vh_trn'],
        ondelete='SET NULL'
    )
    
    # br_mahanatemple -> vihaddata.vh_trn
    op.create_foreign_key(
        'fk_bhikku_regist_mahanatemple',
        'bhikku_regist', 'vihaddata',
        ['br_mahanatemple'], ['vh_trn'],
        ondelete='RESTRICT'
    )
    
    # br_mahanaacharyacd -> bhikku_regist.br_regn (self-join)
    op.create_foreign_key(
        'fk_bhikku_regist_mahanaacharyacd',
        'bhikku_regist', 'bhikku_regist',
        ['br_mahanaacharyacd'], ['br_regn'],
        ondelete='RESTRICT'
    )
    
    # br_cat -> cmm_cat.cc_code
    op.create_foreign_key(
        'fk_bhikku_regist_cat',
        'bhikku_regist', 'cmm_cat',
        ['br_cat'], ['cc_code'],
        ondelete='SET NULL'
    )
    
    # br_viharadhipathi -> bhikku_regist.br_regn (self-join)
    op.create_foreign_key(
        'fk_bhikku_regist_viharadhipathi',
        'bhikku_regist', 'bhikku_regist',
        ['br_viharadhipathi'], ['br_regn'],
        ondelete='SET NULL'
    )
    
    # br_nikaya -> cmm_nikayadata.nk_nkn
    op.create_foreign_key(
        'fk_bhikku_regist_nikaya',
        'bhikku_regist', 'cmm_nikayadata',
        ['br_nikaya'], ['nk_nkn'],
        ondelete='SET NULL'
    )
    
    # br_mahanayaka_name -> bhikku_regist.br_regn (self-join)
    op.create_foreign_key(
        'fk_bhikku_regist_mahanayaka_name',
        'bhikku_regist', 'bhikku_regist',
        ['br_mahanayaka_name'], ['br_regn'],
        ondelete='SET NULL'
    )
    
    # br_robing_tutor_residence -> vihaddata.vh_trn
    op.create_foreign_key(
        'fk_bhikku_regist_robing_tutor_residence',
        'bhikku_regist', 'vihaddata',
        ['br_robing_tutor_residence'], ['vh_trn'],
        ondelete='SET NULL'
    )
    
    # br_robing_after_residence_temple -> vihaddata.vh_trn
    op.create_foreign_key(
        'fk_bhikku_regist_robing_after_residence_temple',
        'bhikku_regist', 'vihaddata',
        ['br_robing_after_residence_temple'], ['vh_trn'],
        ondelete='SET NULL'
    )


def downgrade():
    # Drop all foreign key constraints
    op.drop_constraint('fk_bhikku_regist_robing_after_residence_temple', 'bhikku_regist', type_='foreignkey')
    op.drop_constraint('fk_bhikku_regist_robing_tutor_residence', 'bhikku_regist', type_='foreignkey')
    op.drop_constraint('fk_bhikku_regist_mahanayaka_name', 'bhikku_regist', type_='foreignkey')
    op.drop_constraint('fk_bhikku_regist_nikaya', 'bhikku_regist', type_='foreignkey')
    op.drop_constraint('fk_bhikku_regist_viharadhipathi', 'bhikku_regist', type_='foreignkey')
    op.drop_constraint('fk_bhikku_regist_cat', 'bhikku_regist', type_='foreignkey')
    op.drop_constraint('fk_bhikku_regist_mahanaacharyacd', 'bhikku_regist', type_='foreignkey')
    op.drop_constraint('fk_bhikku_regist_mahanatemple', 'bhikku_regist', type_='foreignkey')
    op.drop_constraint('fk_bhikku_regist_livtemple', 'bhikku_regist', type_='foreignkey')
    op.drop_constraint('fk_bhikku_regist_parshawaya', 'bhikku_regist', type_='foreignkey')
    op.drop_constraint('fk_bhikku_regist_currstat', 'bhikku_regist', type_='foreignkey')
    op.drop_constraint('fk_bhikku_regist_gndiv', 'bhikku_regist', type_='foreignkey')
    op.drop_constraint('fk_bhikku_regist_division', 'bhikku_regist', type_='foreignkey')
    op.drop_constraint('fk_bhikku_regist_district', 'bhikku_regist', type_='foreignkey')
    op.drop_constraint('fk_bhikku_regist_province', 'bhikku_regist', type_='foreignkey')
