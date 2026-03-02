"""update objections table with entity foreign keys

Revision ID: 20251210000007
Revises: 20251210000006
Create Date: 2025-12-10 00:00:07

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251210000007'
down_revision = '20251210000006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Replace obj_entity_type and obj_entity_trn with three foreign key columns:
    - vh_id (vihara)
    - ar_id (arama)
    - dv_id (devala)
    
    Only ONE of these three should be set per objection.
    """
    
    # Step 1: Add new foreign key columns (nullable for now)
    op.add_column('objections', sa.Column('vh_id', sa.Integer(), nullable=True, comment='Foreign key to vihara (if objection is for vihara)'))
    op.add_column('objections', sa.Column('ar_id', sa.Integer(), nullable=True, comment='Foreign key to arama (if objection is for arama)'))
    op.add_column('objections', sa.Column('dv_id', sa.Integer(), nullable=True, comment='Foreign key to devala (if objection is for devala)'))
    
    # Step 2: Migrate existing data based on obj_entity_type and obj_entity_trn
    # This SQL will populate the FK columns by looking up the entity IDs from TRNs
    op.execute("""
        UPDATE objections obj
        SET vh_id = vh.vh_id
        FROM vihaddata vh
        WHERE obj.obj_entity_type = 'VIHARA' 
        AND obj.obj_entity_trn = vh.vh_trn
    """)
    
    op.execute("""
        UPDATE objections obj
        SET ar_id = ar.ar_id
        FROM aramadata ar
        WHERE obj.obj_entity_type = 'ARAMA' 
        AND obj.obj_entity_trn = ar.ar_trn
    """)
    
    op.execute("""
        UPDATE objections obj
        SET dv_id = dv.dv_id
        FROM devaladata dv
        WHERE obj.obj_entity_type = 'DEVALA' 
        AND obj.obj_entity_trn = dv.dv_trn
    """)
    
    # Step 3: Create indexes for the FK columns
    op.create_index('ix_objections_vh_id', 'objections', ['vh_id'], unique=False)
    op.create_index('ix_objections_ar_id', 'objections', ['ar_id'], unique=False)
    op.create_index('ix_objections_dv_id', 'objections', ['dv_id'], unique=False)
    
    # Step 4: Create foreign key constraints
    op.create_foreign_key('fk_objections_vh_id', 'objections', 'vihaddata', ['vh_id'], ['vh_id'])
    op.create_foreign_key('fk_objections_ar_id', 'objections', 'aramadata', ['ar_id'], ['ar_id'])
    op.create_foreign_key('fk_objections_dv_id', 'objections', 'devaladata', ['dv_id'], ['dv_id'])
    
    # Step 5: Add check constraint to ensure exactly one entity FK is set
    op.create_check_constraint(
        'objection_one_entity_check',
        'objections',
        '(vh_id IS NOT NULL AND ar_id IS NULL AND dv_id IS NULL) OR '
        '(vh_id IS NULL AND ar_id IS NOT NULL AND dv_id IS NULL) OR '
        '(vh_id IS NULL AND ar_id IS NULL AND dv_id IS NOT NULL)'
    )
    
    # Step 6: Drop old columns and enum type
    op.drop_index('ix_objections_obj_entity_type', table_name='objections')
    op.drop_index('ix_objections_obj_entity_trn', table_name='objections')
    op.drop_column('objections', 'obj_entity_name')
    op.drop_column('objections', 'obj_entity_trn')
    op.drop_column('objections', 'obj_entity_type')
    
    # Drop the enum type (PostgreSQL specific)
    op.execute("DROP TYPE IF EXISTS entitytype")


def downgrade() -> None:
    """
    Restore obj_entity_type and obj_entity_trn columns
    """
    
    # Recreate enum type
    op.execute("CREATE TYPE entitytype AS ENUM ('VIHARA', 'ARAMA', 'DEVALA')")
    
    # Add back old columns
    op.add_column('objections', sa.Column('obj_entity_type', postgresql.ENUM('VIHARA', 'ARAMA', 'DEVALA', name='entitytype'), nullable=True))
    op.add_column('objections', sa.Column('obj_entity_trn', sa.String(length=50), nullable=True))
    op.add_column('objections', sa.Column('obj_entity_name', sa.String(length=200), nullable=True))
    
    # Migrate data back
    op.execute("""
        UPDATE objections obj
        SET obj_entity_type = 'VIHARA',
            obj_entity_trn = vh.vh_trn,
            obj_entity_name = vh.vh_vname
        FROM vihaddata vh
        WHERE obj.vh_id = vh.vh_id
    """)
    
    op.execute("""
        UPDATE objections obj
        SET obj_entity_type = 'ARAMA',
            obj_entity_trn = ar.ar_trn,
            obj_entity_name = ar.ar_vname
        FROM aramadata ar
        WHERE obj.ar_id = ar.ar_id
    """)
    
    op.execute("""
        UPDATE objections obj
        SET obj_entity_type = 'DEVALA',
            obj_entity_trn = dv.dv_trn,
            obj_entity_name = dv.dv_vname
        FROM devaladata dv
        WHERE obj.dv_id = dv.dv_id
    """)
    
    # Make old columns non-nullable
    op.alter_column('objections', 'obj_entity_type', nullable=False)
    op.alter_column('objections', 'obj_entity_trn', nullable=False)
    
    # Recreate indexes
    op.create_index('ix_objections_obj_entity_type', 'objections', ['obj_entity_type'], unique=False)
    op.create_index('ix_objections_obj_entity_trn', 'objections', ['obj_entity_trn'], unique=False)
    
    # Drop new stuff
    op.drop_constraint('objection_one_entity_check', 'objections', type_='check')
    op.drop_constraint('fk_objections_dv_id', 'objections', type_='foreignkey')
    op.drop_constraint('fk_objections_ar_id', 'objections', type_='foreignkey')
    op.drop_constraint('fk_objections_vh_id', 'objections', type_='foreignkey')
    op.drop_index('ix_objections_dv_id', table_name='objections')
    op.drop_index('ix_objections_ar_id', table_name='objections')
    op.drop_index('ix_objections_vh_id', table_name='objections')
    op.drop_column('objections', 'dv_id')
    op.drop_column('objections', 'ar_id')
    op.drop_column('objections', 'vh_id')
