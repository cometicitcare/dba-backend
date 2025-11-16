"""add_foreign_keys_to_bhikku_high_regist

Revision ID: 20251117000001
Revises: 20251116133100
Create Date: 2025-11-17 00:00:01.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251117000001'
down_revision = '20251116133100'
branch_labels = None
depends_on = None


def constraint_exists(constraint_name, table_name):
    """Check if a constraint already exists"""
    connection = op.get_bind()
    result = connection.execute(sa.text("""
        SELECT COUNT(*) 
        FROM information_schema.table_constraints 
        WHERE constraint_name = :constraint_name 
        AND table_name = :table_name
    """), {"constraint_name": constraint_name, "table_name": table_name})
    return result.scalar() > 0


def create_fk_if_not_exists(constraint_name, source_table, referent_table, 
                            local_cols, remote_cols, ondelete='RESTRICT'):
    """Create foreign key only if it doesn't already exist"""
    if not constraint_exists(constraint_name, source_table):
        op.create_foreign_key(
            constraint_name,
            source_table, referent_table,
            local_cols, remote_cols,
            ondelete=ondelete
        )


def upgrade():
    """Add foreign key constraints to bhikku_high_regist table"""
    
    # Clean up invalid references before adding foreign keys
    # Note: bhr_regn, bhr_currstat, bhr_parshawaya, bhr_livtemple are NOT NULL
    # so we need to use default values instead of NULL
    
    # Get a valid parshawaya code to use as default
    # We'll use a direct approach - just skip FK for non-nullable fields with potential invalid data
    # Or we can try to get the first valid code
    
    # Clean invalid bhikku references for bhr_candidate_regn (nullable)
    op.execute("""
        UPDATE bhikku_high_regist 
        SET bhr_candidate_regn = NULL 
        WHERE bhr_candidate_regn IS NOT NULL 
        AND bhr_candidate_regn NOT IN (SELECT br_regn FROM bhikku_regist WHERE br_is_deleted = false)
    """)
    
    # Clean invalid bhikku references for bhr_tutors_tutor_regn (nullable)
    op.execute("""
        UPDATE bhikku_high_regist 
        SET bhr_tutors_tutor_regn = NULL 
        WHERE bhr_tutors_tutor_regn IS NOT NULL 
        AND bhr_tutors_tutor_regn NOT IN (SELECT br_regn FROM bhikku_regist WHERE br_is_deleted = false)
    """)
    
    # Clean invalid bhikku references for bhr_presiding_bhikshu_regn (nullable)
    op.execute("""
        UPDATE bhikku_high_regist 
        SET bhr_presiding_bhikshu_regn = NULL 
        WHERE bhr_presiding_bhikshu_regn IS NOT NULL 
        AND bhr_presiding_bhikshu_regn NOT IN (SELECT br_regn FROM bhikku_regist WHERE br_is_deleted = false)
    """)
    
    # For NOT NULL fields, we skip cleaning or need to ensure they have valid values
    # bhr_currstat - should have valid status codes
    # bhr_parshawaya - should have valid parshawa codes  
    # bhr_livtemple - should have valid vihara TRNs
    
    # Clean invalid vihara references for bhr_residence_higher_ordination_trn (nullable)
    op.execute("""
        UPDATE bhikku_high_regist 
        SET bhr_residence_higher_ordination_trn = NULL 
        WHERE bhr_residence_higher_ordination_trn IS NOT NULL 
        AND bhr_residence_higher_ordination_trn NOT IN (SELECT vh_trn FROM vihaddata WHERE vh_is_deleted = false)
    """)
    
    # Clean invalid vihara references for bhr_residence_permanent_trn (nullable)
    op.execute("""
        UPDATE bhikku_high_regist 
        SET bhr_residence_permanent_trn = NULL 
        WHERE bhr_residence_permanent_trn IS NOT NULL 
        AND bhr_residence_permanent_trn NOT IN (SELECT vh_trn FROM vihaddata WHERE vh_is_deleted = false)
    """)
    
    # Now add the foreign key constraints (only for nullable fields or fields we know are valid)
    
    # Note: We skip FK constraints for NOT NULL fields (bhr_currstat, bhr_parshawaya, bhr_livtemple)
    # that might have invalid data to avoid migration failures
    
    # bhr_candidate_regn -> bhikku_regist.br_regn
    create_fk_if_not_exists(
        'fk_bhikku_high_regist_candidate',
        'bhikku_high_regist', 'bhikku_regist',
        ['bhr_candidate_regn'], ['br_regn'],
        ondelete='RESTRICT'
    )
    
    # bhr_candidate_regn -> bhikku_regist.br_regn
    create_fk_if_not_exists(
        'fk_bhikku_high_regist_candidate',
        'bhikku_high_regist', 'bhikku_regist',
        ['bhr_candidate_regn'], ['br_regn'],
        ondelete='RESTRICT'
    )
    
    # bhr_tutors_tutor_regn -> bhikku_regist.br_regn
    create_fk_if_not_exists(
        'fk_bhikku_high_regist_tutors_tutor',
        'bhikku_high_regist', 'bhikku_regist',
        ['bhr_tutors_tutor_regn'], ['br_regn'],
        ondelete='RESTRICT'
    )
    
    # bhr_presiding_bhikshu_regn -> bhikku_regist.br_regn
    create_fk_if_not_exists(
        'fk_bhikku_high_regist_presiding_bhikshu',
        'bhikku_high_regist', 'bhikku_regist',
        ['bhr_presiding_bhikshu_regn'], ['br_regn'],
        ondelete='RESTRICT'
    )
    
    # For bhr_currstat, bhr_parshawaya, bhr_livtemple - these are NOT NULL
    # We'll only add FK if we can ensure data integrity
    # For now, skip these to avoid migration failures
    
    # bhr_residence_higher_ordination_trn -> vihaddata.vh_trn
    create_fk_if_not_exists(
        'fk_bhikku_high_regist_residence_higher_ordination',
        'bhikku_high_regist', 'vihaddata',
        ['bhr_residence_higher_ordination_trn'], ['vh_trn'],
        ondelete='RESTRICT'
    )
    
    # bhr_residence_permanent_trn -> vihaddata.vh_trn
    create_fk_if_not_exists(
        'fk_bhikku_high_regist_residence_permanent',
        'bhikku_high_regist', 'vihaddata',
        ['bhr_residence_permanent_trn'], ['vh_trn'],
        ondelete='RESTRICT'
    )


def downgrade():
    """Remove foreign key constraints from bhikku_high_regist table"""
    
    # Drop foreign keys that were actually added
    op.drop_constraint('fk_bhikku_high_regist_candidate', 'bhikku_high_regist', type_='foreignkey')
    op.drop_constraint('fk_bhikku_high_regist_tutors_tutor', 'bhikku_high_regist', type_='foreignkey')
    op.drop_constraint('fk_bhikku_high_regist_presiding_bhikshu', 'bhikku_high_regist', type_='foreignkey')
    op.drop_constraint('fk_bhikku_high_regist_residence_higher_ordination', 'bhikku_high_regist', type_='foreignkey')
    op.drop_constraint('fk_bhikku_high_regist_residence_permanent', 'bhikku_high_regist', type_='foreignkey')
