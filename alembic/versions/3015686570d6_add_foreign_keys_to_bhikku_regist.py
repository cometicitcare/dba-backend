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
    # First, clean up invalid data before adding foreign keys
    
    # Clean invalid province references
    op.execute("""
        UPDATE bhikku_regist 
        SET br_province = NULL 
        WHERE br_province IS NOT NULL 
        AND br_province NOT IN (SELECT cp_code FROM cmm_province)
    """)
    
    # br_province -> cmm_province.cp_code
    op.create_foreign_key(
        'fk_bhikku_regist_province',
        'bhikku_regist', 'cmm_province',
        ['br_province'], ['cp_code'],
        ondelete='SET NULL'
    )
    
    # Clean invalid district references
    op.execute("""
        UPDATE bhikku_regist 
        SET br_district = NULL 
        WHERE br_district IS NOT NULL 
        AND br_district NOT IN (SELECT dd_dcode FROM cmm_districtdata)
    """)
    
    # br_district -> cmm_districtdata.dd_dcode
    op.create_foreign_key(
        'fk_bhikku_regist_district',
        'bhikku_regist', 'cmm_districtdata',
        ['br_district'], ['dd_dcode'],
        ondelete='SET NULL'
    )
    
    # Clean invalid division references
    op.execute("""
        UPDATE bhikku_regist 
        SET br_division = NULL 
        WHERE br_division IS NOT NULL 
        AND br_division NOT IN (SELECT dv_dvcode FROM cmm_dvsec)
    """)
    
    # br_division -> cmm_dvsec.dv_dvcode
    op.create_foreign_key(
        'fk_bhikku_regist_division',
        'bhikku_regist', 'cmm_dvsec',
        ['br_division'], ['dv_dvcode'],
        ondelete='SET NULL'
    )
    
    # Clean invalid gndiv references
    op.execute("""
        UPDATE bhikku_regist 
        SET br_gndiv = NULL 
        WHERE br_gndiv IS NOT NULL 
        AND br_gndiv NOT IN (SELECT gn_gnc FROM cmm_gndata)
    """)
    
    # br_gndiv -> cmm_gndata.gn_gnc
    op.create_foreign_key(
        'fk_bhikku_regist_gndiv',
        'bhikku_regist', 'cmm_gndata',
        ['br_gndiv'], ['gn_gnc'],
        ondelete='RESTRICT'
    )
    
    # Clean invalid currstat references
    op.execute("""
        UPDATE bhikku_regist 
        SET br_currstat = NULL 
        WHERE br_currstat IS NOT NULL 
        AND br_currstat NOT IN (SELECT st_statcd FROM statusdata)
    """)
    
    # br_currstat -> statusdata.st_statcd
    op.create_foreign_key(
        'fk_bhikku_regist_currstat',
        'bhikku_regist', 'statusdata',
        ['br_currstat'], ['st_statcd'],
        ondelete='RESTRICT'
    )
    
    # Clean invalid parshawaya references
    op.execute("""
        UPDATE bhikku_regist 
        SET br_parshawaya = NULL 
        WHERE br_parshawaya IS NOT NULL 
        AND br_parshawaya NOT IN (SELECT pr_prn FROM cmm_parshawadata)
    """)
    
    # br_parshawaya -> cmm_parshawadata.pr_prn
    op.create_foreign_key(
        'fk_bhikku_regist_parshawaya',
        'bhikku_regist', 'cmm_parshawadata',
        ['br_parshawaya'], ['pr_prn'],
        ondelete='RESTRICT'
    )
    
    # Clean invalid livtemple references
    op.execute("""
        UPDATE bhikku_regist 
        SET br_livtemple = NULL 
        WHERE br_livtemple IS NOT NULL 
        AND br_livtemple NOT IN (SELECT vh_trn FROM vihaddata)
    """)
    
    # br_livtemple -> vihaddata.vh_trn
    op.create_foreign_key(
        'fk_bhikku_regist_livtemple',
        'bhikku_regist', 'vihaddata',
        ['br_livtemple'], ['vh_trn'],
        ondelete='SET NULL'
    )
    
    # Clean invalid mahanatemple references
    op.execute("""
        UPDATE bhikku_regist 
        SET br_mahanatemple = NULL 
        WHERE br_mahanatemple IS NOT NULL 
        AND br_mahanatemple NOT IN (SELECT vh_trn FROM vihaddata)
    """)
    
    # br_mahanatemple -> vihaddata.vh_trn
    op.create_foreign_key(
        'fk_bhikku_regist_mahanatemple',
        'bhikku_regist', 'vihaddata',
        ['br_mahanatemple'], ['vh_trn'],
        ondelete='RESTRICT'
    )
    
    # Clean invalid mahanaacharyacd references (self-join)
    op.execute("""
        UPDATE bhikku_regist 
        SET br_mahanaacharyacd = NULL 
        WHERE br_mahanaacharyacd IS NOT NULL 
        AND br_mahanaacharyacd NOT IN (SELECT br_regn FROM bhikku_regist)
    """)
    
    # br_mahanaacharyacd -> bhikku_regist.br_regn (self-join)
    op.create_foreign_key(
        'fk_bhikku_regist_mahanaacharyacd',
        'bhikku_regist', 'bhikku_regist',
        ['br_mahanaacharyacd'], ['br_regn'],
        ondelete='RESTRICT'
    )
    
    # Clean invalid cat references
    op.execute("""
        UPDATE bhikku_regist 
        SET br_cat = NULL 
        WHERE br_cat IS NOT NULL 
        AND br_cat NOT IN (SELECT cc_code FROM cmm_cat)
    """)
    
    # br_cat -> cmm_cat.cc_code
    op.create_foreign_key(
        'fk_bhikku_regist_cat',
        'bhikku_regist', 'cmm_cat',
        ['br_cat'], ['cc_code'],
        ondelete='SET NULL'
    )
    
    # Clean invalid viharadhipathi references (self-join)
    op.execute("""
        UPDATE bhikku_regist 
        SET br_viharadhipathi = NULL 
        WHERE br_viharadhipathi IS NOT NULL 
        AND br_viharadhipathi NOT IN (SELECT br_regn FROM bhikku_regist)
    """)
    
    # br_viharadhipathi -> bhikku_regist.br_regn (self-join)
    op.create_foreign_key(
        'fk_bhikku_regist_viharadhipathi',
        'bhikku_regist', 'bhikku_regist',
        ['br_viharadhipathi'], ['br_regn'],
        ondelete='SET NULL'
    )
    
    # Clean invalid nikaya references
    op.execute("""
        UPDATE bhikku_regist 
        SET br_nikaya = NULL 
        WHERE br_nikaya IS NOT NULL 
        AND br_nikaya NOT IN (SELECT nk_nkn FROM cmm_nikayadata)
    """)
    
    # br_nikaya -> cmm_nikayadata.nk_nkn
    op.create_foreign_key(
        'fk_bhikku_regist_nikaya',
        'bhikku_regist', 'cmm_nikayadata',
        ['br_nikaya'], ['nk_nkn'],
        ondelete='SET NULL'
    )
    
    # Clean invalid mahanayaka_name references (self-join)
    op.execute("""
        UPDATE bhikku_regist 
        SET br_mahanayaka_name = NULL 
        WHERE br_mahanayaka_name IS NOT NULL 
        AND br_mahanayaka_name NOT IN (SELECT br_regn FROM bhikku_regist)
    """)
    
    # br_mahanayaka_name -> bhikku_regist.br_regn (self-join)
    op.create_foreign_key(
        'fk_bhikku_regist_mahanayaka_name',
        'bhikku_regist', 'bhikku_regist',
        ['br_mahanayaka_name'], ['br_regn'],
        ondelete='SET NULL'
    )
    
    # Clean invalid robing_tutor_residence references
    op.execute("""
        UPDATE bhikku_regist 
        SET br_robing_tutor_residence = NULL 
        WHERE br_robing_tutor_residence IS NOT NULL 
        AND br_robing_tutor_residence NOT IN (SELECT vh_trn FROM vihaddata)
    """)
    
    # br_robing_tutor_residence -> vihaddata.vh_trn
    op.create_foreign_key(
        'fk_bhikku_regist_robing_tutor_residence',
        'bhikku_regist', 'vihaddata',
        ['br_robing_tutor_residence'], ['vh_trn'],
        ondelete='SET NULL'
    )
    
    # Clean invalid robing_after_residence_temple references
    op.execute("""
        UPDATE bhikku_regist 
        SET br_robing_after_residence_temple = NULL 
        WHERE br_robing_after_residence_temple IS NOT NULL 
        AND br_robing_after_residence_temple NOT IN (SELECT vh_trn FROM vihaddata)
    """)
    
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
