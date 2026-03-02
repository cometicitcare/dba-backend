"""expand objection system to support all entities

Revision ID: 20251211000001
Revises: 20251210000007
Create Date: 2025-12-11 00:00:01

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251211000001'
down_revision = '20251210000007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Expand objection system to support all 6 entity types:
    1. Add FK columns for: bhikku (bh_id), silmatha (sil_id), high_bhikku (dbh_id)
    2. Add new fields: form_id, requester details, time period
    3. Update check constraint to include all 6 entity types
    4. Update objection_types table with two specific types
    """
    
    # Step 1: Add new entity foreign key columns
    op.add_column('objections', sa.Column('bh_id', sa.Integer(), nullable=True, comment='Foreign key to bhikku'))
    op.add_column('objections', sa.Column('sil_id', sa.Integer(), nullable=True, comment='Foreign key to silmatha'))
    op.add_column('objections', sa.Column('dbh_id', sa.Integer(), nullable=True, comment='Foreign key to high bhikku'))
    
    # Step 2: Add form_id and requester information columns
    op.add_column('objections', sa.Column('form_id', sa.String(length=50), nullable=True, comment='Related form ID/number'))
    op.add_column('objections', sa.Column('obj_requester_name', sa.String(length=200), nullable=True, comment='Name of the person making the request'))
    op.add_column('objections', sa.Column('obj_requester_contact', sa.String(length=20), nullable=True, comment='Contact number of requester'))
    op.add_column('objections', sa.Column('obj_requester_id_num', sa.String(length=20), nullable=True, comment='ID number of requester (NIC/Passport)'))
    
    # Step 3: Add time period columns
    op.add_column('objections', sa.Column('obj_valid_from', sa.DateTime(timezone=True), nullable=True, comment='Objection validity start date'))
    op.add_column('objections', sa.Column('obj_valid_until', sa.DateTime(timezone=True), nullable=True, comment='Objection validity end date (null = indefinite)'))
    
    # Step 4: Create foreign key constraints for new entity columns
    op.create_foreign_key('fk_objections_bhikku', 'objections', 'bhikku_regist', ['bh_id'], ['br_id'])
    op.create_foreign_key('fk_objections_silmatha', 'objections', 'silmatha_regist', ['sil_id'], ['sil_id'])
    op.create_foreign_key('fk_objections_high_bhikku', 'objections', 'direct_bhikku_high', ['dbh_id'], ['dbh_id'])
    
    # Step 5: Create indexes for new FK columns
    op.create_index('ix_objections_bh_id', 'objections', ['bh_id'])
    op.create_index('ix_objections_sil_id', 'objections', ['sil_id'])
    op.create_index('ix_objections_dbh_id', 'objections', ['dbh_id'])
    op.create_index('ix_objections_form_id', 'objections', ['form_id'])
    
    # Step 6: Drop old check constraint
    op.drop_constraint('objection_one_entity_check', 'objections', type_='check')
    
    # Step 7: Create new check constraint for all 6 entity types
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
    
    # Step 8: Expand ot_code column to accommodate longer codes
    op.alter_column('objection_types', 'ot_code',
                    existing_type=sa.String(20),
                    type_=sa.String(50),
                    existing_nullable=False)
    
    # Step 9: Update objection_types table - replace old types with two new specific ones
    # First, insert the two new types (they will get new IDs)
    op.execute("""
        INSERT INTO objection_types (ot_code, ot_name_en, ot_name_si, ot_name_ta, ot_description, ot_is_active) VALUES
        ('REPRINT_RESTRICTION', 'Reprint Restriction', 'නැවත මුද්‍රණය කිරීමේ සීමාව', 'மறு அச்சு கட்டுப்பாடு', 'Objection to block reprint requests', true),
        ('RESIDENCY_RESTRICTION', 'Residency Restriction', 'පදිංචිය සීමා කිරීම', 'குடியிருப்பு கட்டுப்பாடு', 'Objection to block adding more residents', true)
    """)
    
    # Map all existing objections to RESIDENCY_RESTRICTION (the second type we just added)
    op.execute("""
        UPDATE objections 
        SET obj_type_id = (SELECT ot_id FROM objection_types WHERE ot_code = 'RESIDENCY_RESTRICTION')
        WHERE obj_type_id IS NOT NULL
    """)
    
    # Now delete old objection types (those NOT in our two new types)
    op.execute("""
        DELETE FROM objection_types 
        WHERE ot_code NOT IN ('REPRINT_RESTRICTION', 'RESIDENCY_RESTRICTION')
    """)


def downgrade() -> None:
    """
    Reverse the changes
    """
    # Drop indexes
    op.drop_index('ix_objections_form_id', 'objections')
    op.drop_index('ix_objections_dbh_id', 'objections')
    op.drop_index('ix_objections_sil_id', 'objections')
    op.drop_index('ix_objections_bh_id', 'objections')
    
    # Drop foreign keys
    op.drop_constraint('fk_objections_high_bhikku', 'objections', type_='foreignkey')
    op.drop_constraint('fk_objections_silmatha', 'objections', type_='foreignkey')
    op.drop_constraint('fk_objections_bhikku', 'objections', type_='foreignkey')
    
    # Drop check constraint
    op.drop_constraint('objection_one_entity_check', 'objections', type_='check')
    
    # Recreate old check constraint (3 entities only)
    op.create_check_constraint(
        'objection_one_entity_check',
        'objections',
        '''(vh_id IS NOT NULL AND ar_id IS NULL AND dv_id IS NULL) OR 
           (vh_id IS NULL AND ar_id IS NOT NULL AND dv_id IS NULL) OR 
           (vh_id IS NULL AND ar_id IS NULL AND dv_id IS NOT NULL)'''
    )
    
    # Drop new columns
    op.drop_column('objections', 'obj_valid_until')
    op.drop_column('objections', 'obj_valid_from')
    op.drop_column('objections', 'obj_requester_id_num')
    op.drop_column('objections', 'obj_requester_contact')
    op.drop_column('objections', 'obj_requester_name')
    op.drop_column('objections', 'form_id')
    op.drop_column('objections', 'dbh_id')
    op.drop_column('objections', 'sil_id')
    op.drop_column('objections', 'bh_id')
