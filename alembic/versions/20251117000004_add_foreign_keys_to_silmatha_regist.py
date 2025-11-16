"""Add foreign keys to silmatha_regist table.

Revision ID: 20251117000004
Revises: 20251117000003
Create Date: 2025-11-17 00:00:04.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20251117000004"
down_revision = "20251117000003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add foreign key constraints to silmatha_regist table."""
    
    # Add foreign key for sil_province -> cmm_province.cp_code
    op.create_foreign_key(
        'fk_silmatha_regist_province',
        'silmatha_regist',
        'cmm_province',
        ['sil_province'],
        ['cp_code'],
        onupdate='CASCADE',
        ondelete='SET NULL'
    )
    
    # Add foreign key for sil_district -> cmm_districtdata.dd_dcode
    op.create_foreign_key(
        'fk_silmatha_regist_district',
        'silmatha_regist',
        'cmm_districtdata',
        ['sil_district'],
        ['dd_dcode'],
        onupdate='CASCADE',
        ondelete='SET NULL'
    )
    
    # Add foreign key for sil_division -> cmm_dvsec.dv_dvcode
    op.create_foreign_key(
        'fk_silmatha_regist_division',
        'silmatha_regist',
        'cmm_dvsec',
        ['sil_division'],
        ['dv_dvcode'],
        onupdate='CASCADE',
        ondelete='SET NULL'
    )
    
    # Add foreign key for sil_gndiv -> cmm_gndata.gn_gnc
    op.create_foreign_key(
        'fk_silmatha_regist_gndiv',
        'silmatha_regist',
        'cmm_gndata',
        ['sil_gndiv'],
        ['gn_gnc'],
        onupdate='CASCADE',
        ondelete='RESTRICT'
    )
    
    # Add foreign key for sil_viharadhipathi -> bhikku_regist.br_regn
    op.create_foreign_key(
        'fk_silmatha_regist_viharadhipathi',
        'silmatha_regist',
        'bhikku_regist',
        ['sil_viharadhipathi'],
        ['br_regn'],
        onupdate='CASCADE',
        ondelete='SET NULL'
    )
    
    # Add foreign key for sil_cat -> cmm_cat.cc_code
    op.create_foreign_key(
        'fk_silmatha_regist_cat',
        'silmatha_regist',
        'cmm_cat',
        ['sil_cat'],
        ['cc_code'],
        onupdate='CASCADE',
        ondelete='SET NULL'
    )
    
    # Add foreign key for sil_currstat -> statusdata.st_statcd
    op.create_foreign_key(
        'fk_silmatha_regist_currstat',
        'silmatha_regist',
        'statusdata',
        ['sil_currstat'],
        ['st_statcd'],
        onupdate='CASCADE',
        ondelete='RESTRICT'
    )
    
    # Add foreign key for sil_mahanaacharyacd -> bhikku_regist.br_regn
    op.create_foreign_key(
        'fk_silmatha_regist_mahanaacharyacd',
        'silmatha_regist',
        'bhikku_regist',
        ['sil_mahanaacharyacd'],
        ['br_regn'],
        onupdate='CASCADE',
        ondelete='RESTRICT'
    )
    
    # Add foreign key for sil_robing_tutor_residence -> vihaddata.vh_trn
    op.create_foreign_key(
        'fk_silmatha_regist_robing_tutor_residence',
        'silmatha_regist',
        'vihaddata',
        ['sil_robing_tutor_residence'],
        ['vh_trn'],
        onupdate='CASCADE',
        ondelete='SET NULL'
    )
    
    # Add foreign key for sil_mahanatemple -> vihaddata.vh_trn
    op.create_foreign_key(
        'fk_silmatha_regist_mahanatemple',
        'silmatha_regist',
        'vihaddata',
        ['sil_mahanatemple'],
        ['vh_trn'],
        onupdate='CASCADE',
        ondelete='RESTRICT'
    )
    
    # Add foreign key for sil_robing_after_residence_temple -> vihaddata.vh_trn
    op.create_foreign_key(
        'fk_silmatha_regist_robing_after_residence_temple',
        'silmatha_regist',
        'vihaddata',
        ['sil_robing_after_residence_temple'],
        ['vh_trn'],
        onupdate='CASCADE',
        ondelete='SET NULL'
    )


def downgrade() -> None:
    """Remove foreign key constraints from silmatha_regist table."""
    
    # Drop all foreign keys in reverse order
    op.drop_constraint('fk_silmatha_regist_robing_after_residence_temple', 'silmatha_regist', type_='foreignkey')
    op.drop_constraint('fk_silmatha_regist_mahanatemple', 'silmatha_regist', type_='foreignkey')
    op.drop_constraint('fk_silmatha_regist_robing_tutor_residence', 'silmatha_regist', type_='foreignkey')
    op.drop_constraint('fk_silmatha_regist_mahanaacharyacd', 'silmatha_regist', type_='foreignkey')
    op.drop_constraint('fk_silmatha_regist_currstat', 'silmatha_regist', type_='foreignkey')
    op.drop_constraint('fk_silmatha_regist_cat', 'silmatha_regist', type_='foreignkey')
    op.drop_constraint('fk_silmatha_regist_viharadhipathi', 'silmatha_regist', type_='foreignkey')
    op.drop_constraint('fk_silmatha_regist_gndiv', 'silmatha_regist', type_='foreignkey')
    op.drop_constraint('fk_silmatha_regist_division', 'silmatha_regist', type_='foreignkey')
    op.drop_constraint('fk_silmatha_regist_district', 'silmatha_regist', type_='foreignkey')
    op.drop_constraint('fk_silmatha_regist_province', 'silmatha_regist', type_='foreignkey')
