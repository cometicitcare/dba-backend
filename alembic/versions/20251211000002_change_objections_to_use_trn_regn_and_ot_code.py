"""change objections to use trn/regn and ot_code

Revision ID: 20251211000002
Revises: 20251211000001
Create Date: 2025-12-11 06:50:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251211000002'
down_revision = '20251211000001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Change objections table to:
    1. Store TRN/REGN strings instead of FK IDs
    2. Store ot_code instead of ot_id
    """
    
    # Step 1: Add new string columns for entity identifiers
    op.add_column('objections', sa.Column('vh_trn', sa.String(20), nullable=True, index=True, comment='Vihara TRN'))
    op.add_column('objections', sa.Column('ar_trn', sa.String(20), nullable=True, index=True, comment='Arama TRN'))
    op.add_column('objections', sa.Column('dv_trn', sa.String(20), nullable=True, index=True, comment='Devala TRN'))
    op.add_column('objections', sa.Column('bh_regn', sa.String(20), nullable=True, index=True, comment='Bhikku registration number'))
    op.add_column('objections', sa.Column('sil_regn', sa.String(20), nullable=True, index=True, comment='Silmatha registration number'))
    op.add_column('objections', sa.Column('dbh_regn', sa.String(20), nullable=True, index=True, comment='High Bhikku registration number'))
    
    # Step 2: Add ot_code column
    op.add_column('objections', sa.Column('ot_code', sa.String(50), nullable=True, index=True, comment='Objection type code'))
    
    # Step 3: Migrate existing data - populate new string columns from FK relationships
    # Vihara
    op.execute("""
        UPDATE objections o
        SET vh_trn = v.vh_trn
        FROM vihaddata v
        WHERE o.vh_id = v.vh_id AND o.vh_id IS NOT NULL
    """)
    
    # Arama
    op.execute("""
        UPDATE objections o
        SET ar_trn = a.ar_trn
        FROM aramadata a
        WHERE o.ar_id = a.ar_id AND o.ar_id IS NOT NULL
    """)
    
    # Devala
    op.execute("""
        UPDATE objections o
        SET dv_trn = d.dv_trn
        FROM devaladata d
        WHERE o.dv_id = d.dv_id AND o.dv_id IS NOT NULL
    """)
    
    # Bhikku
    op.execute("""
        UPDATE objections o
        SET bh_regn = b.br_regn
        FROM bhikku_regist b
        WHERE o.bh_id = b.br_id AND o.bh_id IS NOT NULL
    """)
    
    # Silmatha
    op.execute("""
        UPDATE objections o
        SET sil_regn = s.sil_regn
        FROM silmatha_regist s
        WHERE o.sil_id = s.sil_id AND o.sil_id IS NOT NULL
    """)
    
    # High Bhikku
    op.execute("""
        UPDATE objections o
        SET dbh_regn = d.dbh_regn
        FROM direct_bhikku_high d
        WHERE o.dbh_id = d.dbh_id AND o.dbh_id IS NOT NULL
    """)
    
    # Step 4: Migrate objection type - populate ot_code from ot_id
    op.execute("""
        UPDATE objections o
        SET ot_code = ot.ot_code
        FROM objection_types ot
        WHERE o.obj_type_id = ot.ot_id
    """)
    
    # Step 5: Make ot_code NOT NULL
    op.alter_column('objections', 'ot_code', nullable=False)
    
    # Step 6: Drop old FK constraints
    op.drop_constraint('fk_objections_vh_id', 'objections', type_='foreignkey')
    op.drop_constraint('fk_objections_ar_id', 'objections', type_='foreignkey')
    op.drop_constraint('fk_objections_dv_id', 'objections', type_='foreignkey')
    op.drop_constraint('fk_objections_bhikku', 'objections', type_='foreignkey')
    op.drop_constraint('fk_objections_silmatha', 'objections', type_='foreignkey')
    op.drop_constraint('fk_objections_high_bhikku', 'objections', type_='foreignkey')
    op.drop_constraint('fk_objections_obj_type_id', 'objections', type_='foreignkey')
    
    # Step 7: Drop old check constraint
    op.drop_constraint('objection_one_entity_check', 'objections', type_='check')
    
    # Step 8: Drop old FK ID columns
    op.drop_column('objections', 'vh_id')
    op.drop_column('objections', 'ar_id')
    op.drop_column('objections', 'dv_id')
    op.drop_column('objections', 'bh_id')
    op.drop_column('objections', 'sil_id')
    op.drop_column('objections', 'dbh_id')
    op.drop_column('objections', 'obj_type_id')
    
    # Step 9: Add new check constraint for string-based entity identifiers
    op.create_check_constraint(
        'objection_one_entity_identifier_check',
        'objections',
        '''(vh_trn IS NOT NULL AND ar_trn IS NULL AND dv_trn IS NULL AND bh_regn IS NULL AND sil_regn IS NULL AND dbh_regn IS NULL) OR 
           (vh_trn IS NULL AND ar_trn IS NOT NULL AND dv_trn IS NULL AND bh_regn IS NULL AND sil_regn IS NULL AND dbh_regn IS NULL) OR 
           (vh_trn IS NULL AND ar_trn IS NULL AND dv_trn IS NOT NULL AND bh_regn IS NULL AND sil_regn IS NULL AND dbh_regn IS NULL) OR 
           (vh_trn IS NULL AND ar_trn IS NULL AND dv_trn IS NULL AND bh_regn IS NOT NULL AND sil_regn IS NULL AND dbh_regn IS NULL) OR 
           (vh_trn IS NULL AND ar_trn IS NULL AND dv_trn IS NULL AND bh_regn IS NULL AND sil_regn IS NOT NULL AND dbh_regn IS NULL) OR 
           (vh_trn IS NULL AND ar_trn IS NULL AND dv_trn IS NULL AND bh_regn IS NULL AND sil_regn IS NULL AND dbh_regn IS NOT NULL)'''
    )


def downgrade() -> None:
    """
    Revert changes - restore FK columns
    """
    
    # Add back FK columns
    op.add_column('objections', sa.Column('vh_id', sa.Integer(), nullable=True))
    op.add_column('objections', sa.Column('ar_id', sa.Integer(), nullable=True))
    op.add_column('objections', sa.Column('dv_id', sa.Integer(), nullable=True))
    op.add_column('objections', sa.Column('bh_id', sa.Integer(), nullable=True))
    op.add_column('objections', sa.Column('sil_id', sa.Integer(), nullable=True))
    op.add_column('objections', sa.Column('dbh_id', sa.Integer(), nullable=True))
    op.add_column('objections', sa.Column('obj_type_id', sa.Integer(), nullable=True))
    
    # Restore data (reverse migration)
    op.execute("""
        UPDATE objections o
        SET vh_id = v.vh_id
        FROM vihaddata v
        WHERE o.vh_trn = v.vh_trn AND o.vh_trn IS NOT NULL
    """)
    
    op.execute("""
        UPDATE objections o
        SET ar_id = a.ar_id
        FROM aramadata a
        WHERE o.ar_trn = a.ar_trn AND o.ar_trn IS NOT NULL
    """)
    
    op.execute("""
        UPDATE objections o
        SET dv_id = d.dv_id
        FROM devaladata d
        WHERE o.dv_trn = d.dv_trn AND o.dv_trn IS NOT NULL
    """)
    
    op.execute("""
        UPDATE objections o
        SET bh_id = b.br_id
        FROM bhikku_regist b
        WHERE o.bh_regn = b.br_regn AND o.bh_regn IS NOT NULL
    """)
    
    op.execute("""
        UPDATE objections o
        SET sil_id = s.sil_id
        FROM silmatha_regist s
        WHERE o.sil_regn = s.sil_regn AND o.sil_regn IS NOT NULL
    """)
    
    op.execute("""
        UPDATE objections o
        SET dbh_id = d.dbh_id
        FROM direct_bhikku_high d
        WHERE o.dbh_regn = d.dbh_regn AND o.dbh_regn IS NOT NULL
    """)
    
    op.execute("""
        UPDATE objections o
        SET obj_type_id = ot.ot_id
        FROM objection_types ot
        WHERE o.ot_code = ot.ot_code
    """)
    
    # Restore constraints
    op.create_foreign_key('fk_objections_vh_id', 'objections', 'vihaddata', ['vh_id'], ['vh_id'])
    op.create_foreign_key('fk_objections_ar_id', 'objections', 'aramadata', ['ar_id'], ['ar_id'])
    op.create_foreign_key('fk_objections_dv_id', 'objections', 'devaladata', ['dv_id'], ['dv_id'])
    op.create_foreign_key('fk_objections_bhikku', 'objections', 'bhikku_regist', ['bh_id'], ['br_id'])
    op.create_foreign_key('fk_objections_silmatha', 'objections', 'silmatha_regist', ['sil_id'], ['sil_id'])
    op.create_foreign_key('fk_objections_high_bhikku', 'objections', 'direct_bhikku_high', ['dbh_id'], ['dbh_id'])
    op.create_foreign_key('fk_objections_obj_type_id', 'objections', 'objection_types', ['obj_type_id'], ['ot_id'])
    
    # Drop new constraint
    op.drop_constraint('objection_one_entity_identifier_check', 'objections', type_='check')
    
    # Add back old constraint
    op.create_check_constraint(
        'objection_one_entity_check',
        'objections',
        '''(vh_id IS NOT NULL AND ar_id IS NULL AND dv_id IS NULL AND bh_id IS NULL AND sil_id IS NULL AND dbh_id IS NULL) OR 
           (vh_id IS NULL AND ar_id IS NOT NULL AND dv_id IS NULL AND bh_id IS NULL AND sil_id IS NULL AND dbh_id IS NULL) OR 
           (vh_id IS NULL AND ar_id IS NULL AND dv_id IS NOT NULL AND bh_id IS NULL AND sil_id IS NULL AND dbh_id IS NULL) OR 
           (vh_id IS NULL AND ar_id IS NULL AND dv_id IS NULL AND bh_id IS NOT NULL AND sil_id IS NULL AND dbh_id IS NULL) OR 
           (vh_id IS NULL AND ar_id IS NULL AND dv_id IS NULL AND bh_id IS NULL AND sil_id IS NOT NULL AND dbh_id IS NULL) OR 
           (vh_id IS NULL AND ar_id IS NULL AND dv_id IS NULL AND bh_id IS NULL AND sil_id IS NULL AND dbh_id IS NOT NULL)'''
    )
    
    # Drop new columns
    op.drop_column('objections', 'vh_trn')
    op.drop_column('objections', 'ar_trn')
    op.drop_column('objections', 'dv_trn')
    op.drop_column('objections', 'bh_regn')
    op.drop_column('objections', 'sil_regn')
    op.drop_column('objections', 'dbh_regn')
    op.drop_column('objections', 'ot_code')
