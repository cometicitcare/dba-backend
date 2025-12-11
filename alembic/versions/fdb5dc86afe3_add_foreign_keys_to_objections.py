"""add foreign keys to objections

Revision ID: fdb5dc86afe3
Revises: 20251211000002
Create Date: 2025-12-11 08:00:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'fdb5dc86afe3'
down_revision = '20251211000002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add foreign key constraints to objections table for:
    - vh_trn -> vihaddata.vh_trn
    - ar_trn -> aramadata.ar_trn
    - dv_trn -> devaladata.dv_trn
    - bh_regn -> bhikku_regist.br_regn
    - sil_regn -> silmatha_regist.sil_regn
    - dbh_regn -> direct_bhikku_high.dbh_regn
    - ot_code -> objection_types.ot_code
    """
    
    # Add foreign key for vh_trn
    op.create_foreign_key(
        'fk_objections_vh_trn',
        'objections',
        'vihaddata',
        ['vh_trn'],
        ['vh_trn'],
        ondelete='CASCADE'
    )
    
    # Add foreign key for ar_trn
    op.create_foreign_key(
        'fk_objections_ar_trn',
        'objections',
        'aramadata',
        ['ar_trn'],
        ['ar_trn'],
        ondelete='CASCADE'
    )
    
    # Add foreign key for dv_trn
    op.create_foreign_key(
        'fk_objections_dv_trn',
        'objections',
        'devaladata',
        ['dv_trn'],
        ['dv_trn'],
        ondelete='CASCADE'
    )
    
    # Add foreign key for bh_regn
    op.create_foreign_key(
        'fk_objections_bh_regn',
        'objections',
        'bhikku_regist',
        ['bh_regn'],
        ['br_regn'],
        ondelete='CASCADE'
    )
    
    # Add foreign key for sil_regn
    op.create_foreign_key(
        'fk_objections_sil_regn',
        'objections',
        'silmatha_regist',
        ['sil_regn'],
        ['sil_regn'],
        ondelete='CASCADE'
    )
    
    # Add foreign key for dbh_regn
    op.create_foreign_key(
        'fk_objections_dbh_regn',
        'objections',
        'direct_bhikku_high',
        ['dbh_regn'],
        ['dbh_regn'],
        ondelete='CASCADE'
    )
    
    # Add foreign key for ot_code
    op.create_foreign_key(
        'fk_objections_ot_code',
        'objections',
        'objection_types',
        ['ot_code'],
        ['ot_code'],
        ondelete='RESTRICT'  # Don't allow deleting objection types that are in use
    )


def downgrade() -> None:
    """Remove all foreign key constraints"""
    
    op.drop_constraint('fk_objections_ot_code', 'objections', type_='foreignkey')
    op.drop_constraint('fk_objections_dbh_regn', 'objections', type_='foreignkey')
    op.drop_constraint('fk_objections_sil_regn', 'objections', type_='foreignkey')
    op.drop_constraint('fk_objections_bh_regn', 'objections', type_='foreignkey')
    op.drop_constraint('fk_objections_dv_trn', 'objections', type_='foreignkey')
    op.drop_constraint('fk_objections_ar_trn', 'objections', type_='foreignkey')
    op.drop_constraint('fk_objections_vh_trn', 'objections', type_='foreignkey')
