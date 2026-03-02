"""add foreign keys to silmatha_regist

Revision ID: 20251117000004
Revises: 20251117000003
Create Date: 2025-11-17 00:00:04

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251117000004'
down_revision = '20251117000003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add foreign key constraints to silmatha_regist table"""
    
    # Clean invalid references before adding foreign keys
    # This ensures data integrity
    
    # Clean invalid province references (nullable)
    op.execute("""
        UPDATE silmatha_regist 
        SET sil_province = NULL 
        WHERE sil_province IS NOT NULL 
        AND sil_province NOT IN (SELECT cp_code FROM cmm_province WHERE cp_is_deleted = false)
    """)
    
    # Clean invalid district references (nullable)
    op.execute("""
        UPDATE silmatha_regist 
        SET sil_district = NULL 
        WHERE sil_district IS NOT NULL 
        AND sil_district NOT IN (SELECT dd_dcode FROM cmm_districtdata WHERE dd_is_deleted = false)
    """)
    
    # Clean invalid division references (nullable)
    op.execute("""
        UPDATE silmatha_regist 
        SET sil_division = NULL 
        WHERE sil_division IS NOT NULL 
        AND sil_division NOT IN (SELECT dv_dvcode FROM cmm_dvsec WHERE dv_is_deleted = false)
    """)
    
    # Clean invalid GN division references (NOT NULL - set to a default value or fail if no valid data)
    # Since sil_gndiv is NOT NULL, we need to handle this carefully
    op.execute("""
        UPDATE silmatha_regist 
        SET sil_gndiv = (SELECT gn_gnc FROM cmm_gndata WHERE gn_is_deleted = false LIMIT 1)
        WHERE sil_gndiv IS NOT NULL 
        AND sil_gndiv NOT IN (SELECT gn_gnc FROM cmm_gndata WHERE gn_is_deleted = false)
    """)
    
    # Clean invalid viharadhipathi references (nullable)
    op.execute("""
        UPDATE silmatha_regist 
        SET sil_viharadhipathi = NULL 
        WHERE sil_viharadhipathi IS NOT NULL 
        AND sil_viharadhipathi NOT IN (SELECT br_regn FROM bhikku_regist WHERE br_is_deleted = false)
    """)
    
    # Clean invalid category references (nullable)
    op.execute("""
        UPDATE silmatha_regist 
        SET sil_cat = NULL 
        WHERE sil_cat IS NOT NULL 
        AND sil_cat NOT IN (SELECT cc_code FROM cmm_cat WHERE cc_is_deleted = false)
    """)
    
    # Clean invalid status references (NOT NULL - set to a default value)
    op.execute("""
        UPDATE silmatha_regist 
        SET sil_currstat = (SELECT st_statcd FROM statusdata WHERE st_is_deleted = false LIMIT 1)
        WHERE sil_currstat IS NOT NULL 
        AND sil_currstat NOT IN (SELECT st_statcd FROM statusdata WHERE st_is_deleted = false)
    """)
    
    # Clean invalid robing_tutor_residence references (nullable)
    op.execute("""
        UPDATE silmatha_regist 
        SET sil_robing_tutor_residence = NULL 
        WHERE sil_robing_tutor_residence IS NOT NULL 
        AND sil_robing_tutor_residence NOT IN (SELECT vh_trn FROM vihaddata WHERE vh_is_deleted = false)
    """)
    
    # Clean invalid mahanatemple references (nullable)
    op.execute("""
        UPDATE silmatha_regist 
        SET sil_mahanatemple = NULL 
        WHERE sil_mahanatemple IS NOT NULL 
        AND sil_mahanatemple NOT IN (SELECT vh_trn FROM vihaddata WHERE vh_is_deleted = false)
    """)
    
    # Clean invalid robing_after_residence_temple references (nullable)
    op.execute("""
        UPDATE silmatha_regist 
        SET sil_robing_after_residence_temple = NULL 
        WHERE sil_robing_after_residence_temple IS NOT NULL 
        AND sil_robing_after_residence_temple NOT IN (SELECT vh_trn FROM vihaddata WHERE vh_is_deleted = false)
    """)
    
    # Add foreign key constraints (with existence checks to handle partial migrations)
    
    # Helper function to check if constraint exists
    from sqlalchemy import inspect
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_fks = {fk['name'] for fk in inspector.get_foreign_keys('silmatha_regist')}
    
    # sil_province -> cmm_province.cp_code
    if 'fk_silmatha_regist_province' not in existing_fks:
        op.create_foreign_key(
            'fk_silmatha_regist_province',
            'silmatha_regist', 'cmm_province',
            ['sil_province'], ['cp_code'],
            ondelete='SET NULL'
        )
    
    # sil_district -> cmm_districtdata.dd_dcode
    if 'fk_silmatha_regist_district' not in existing_fks:
        op.create_foreign_key(
            'fk_silmatha_regist_district',
            'silmatha_regist', 'cmm_districtdata',
            ['sil_district'], ['dd_dcode'],
            ondelete='SET NULL'
        )
    
    # sil_division -> cmm_dvsec.dv_dvcode
    if 'fk_silmatha_regist_division' not in existing_fks:
        op.create_foreign_key(
            'fk_silmatha_regist_division',
            'silmatha_regist', 'cmm_dvsec',
            ['sil_division'], ['dv_dvcode'],
            ondelete='SET NULL'
        )
    
    # sil_gndiv -> cmm_gndata.gn_gnc
    if 'fk_silmatha_regist_gndiv' not in existing_fks:
        op.create_foreign_key(
            'fk_silmatha_regist_gndiv',
            'silmatha_regist', 'cmm_gndata',
            ['sil_gndiv'], ['gn_gnc'],
            ondelete='RESTRICT'  # NOT NULL, so restrict deletion
        )
    
    # sil_viharadhipathi -> bhikku_regist.br_regn
    if 'fk_silmatha_regist_viharadhipathi' not in existing_fks:
        op.create_foreign_key(
            'fk_silmatha_regist_viharadhipathi',
            'silmatha_regist', 'bhikku_regist',
            ['sil_viharadhipathi'], ['br_regn'],
            ondelete='SET NULL'
        )
    
    # sil_cat -> cmm_cat.cc_code
    if 'fk_silmatha_regist_cat' not in existing_fks:
        op.create_foreign_key(
            'fk_silmatha_regist_cat',
            'silmatha_regist', 'cmm_cat',
            ['sil_cat'], ['cc_code'],
            ondelete='SET NULL'
        )
    
    # sil_currstat -> statusdata.st_statcd
    if 'fk_silmatha_regist_currstat' not in existing_fks:
        op.create_foreign_key(
            'fk_silmatha_regist_currstat',
            'silmatha_regist', 'statusdata',
            ['sil_currstat'], ['st_statcd'],
            ondelete='RESTRICT'  # NOT NULL, so restrict deletion
        )
    
    # sil_robing_tutor_residence -> vihaddata.vh_trn
    if 'fk_silmatha_regist_robing_tutor_residence' not in existing_fks:
        op.create_foreign_key(
            'fk_silmatha_regist_robing_tutor_residence',
            'silmatha_regist', 'vihaddata',
            ['sil_robing_tutor_residence'], ['vh_trn'],
            ondelete='SET NULL'
        )
    
    # sil_mahanatemple -> vihaddata.vh_trn
    if 'fk_silmatha_regist_mahanatemple' not in existing_fks:
        op.create_foreign_key(
            'fk_silmatha_regist_mahanatemple',
            'silmatha_regist', 'vihaddata',
            ['sil_mahanatemple'], ['vh_trn'],
            ondelete='SET NULL'
        )
    
    # sil_robing_after_residence_temple -> vihaddata.vh_trn
    if 'fk_silmatha_regist_robing_after_residence_temple' not in existing_fks:
        op.create_foreign_key(
            'fk_silmatha_regist_robing_after_residence_temple',
            'silmatha_regist', 'vihaddata',
            ['sil_robing_after_residence_temple'], ['vh_trn'],
            ondelete='SET NULL'
        )
    
    # Note: sil_mahanaacharyacd can contain comma-separated sil_regn values,
    # so we cannot create a direct foreign key constraint for it.
    # Validation will be done at the application level in the service layer.


def downgrade() -> None:
    """Remove foreign key constraints from silmatha_regist table"""
    
    # Check which constraints exist before dropping
    from sqlalchemy import inspect
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_fks = {fk['name'] for fk in inspector.get_foreign_keys('silmatha_regist')}
    
    # Drop constraints only if they exist
    if 'fk_silmatha_regist_robing_after_residence_temple' in existing_fks:
        op.drop_constraint('fk_silmatha_regist_robing_after_residence_temple', 'silmatha_regist', type_='foreignkey')
    if 'fk_silmatha_regist_mahanatemple' in existing_fks:
        op.drop_constraint('fk_silmatha_regist_mahanatemple', 'silmatha_regist', type_='foreignkey')
    if 'fk_silmatha_regist_robing_tutor_residence' in existing_fks:
        op.drop_constraint('fk_silmatha_regist_robing_tutor_residence', 'silmatha_regist', type_='foreignkey')
    if 'fk_silmatha_regist_currstat' in existing_fks:
        op.drop_constraint('fk_silmatha_regist_currstat', 'silmatha_regist', type_='foreignkey')
    if 'fk_silmatha_regist_cat' in existing_fks:
        op.drop_constraint('fk_silmatha_regist_cat', 'silmatha_regist', type_='foreignkey')
    if 'fk_silmatha_regist_viharadhipathi' in existing_fks:
        op.drop_constraint('fk_silmatha_regist_viharadhipathi', 'silmatha_regist', type_='foreignkey')
    if 'fk_silmatha_regist_gndiv' in existing_fks:
        op.drop_constraint('fk_silmatha_regist_gndiv', 'silmatha_regist', type_='foreignkey')
    if 'fk_silmatha_regist_division' in existing_fks:
        op.drop_constraint('fk_silmatha_regist_division', 'silmatha_regist', type_='foreignkey')
    if 'fk_silmatha_regist_district' in existing_fks:
        op.drop_constraint('fk_silmatha_regist_district', 'silmatha_regist', type_='foreignkey')
    if 'fk_silmatha_regist_province' in existing_fks:
        op.drop_constraint('fk_silmatha_regist_province', 'silmatha_regist', type_='foreignkey')
