"""add objection types table and foreign key

Revision ID: 20251210000006
Revises: 20251210000005
Create Date: 2025-12-10 00:00:06

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251210000006'
down_revision = '20251210000005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add objection_types table and foreign key to objections table"""
    
    # Create objection_types table
    op.create_table(
        'objection_types',
        sa.Column('ot_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('ot_code', sa.String(length=20), nullable=False, comment='Unique type code (e.g., CAPACITY, CONSTRUCTION, ADMIN)'),
        sa.Column('ot_name_en', sa.String(length=200), nullable=False, comment='Type name in English'),
        sa.Column('ot_name_si', sa.String(length=200), nullable=True, comment='Type name in Sinhala'),
        sa.Column('ot_name_ta', sa.String(length=200), nullable=True, comment='Type name in Tamil'),
        sa.Column('ot_description', sa.String(length=500), nullable=True, comment='Description of this objection type'),
        sa.Column('ot_is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False, comment='Whether this type is active'),
        sa.Column('ot_is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False, comment='Soft delete flag'),
        sa.Column('ot_created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Creation timestamp'),
        sa.Column('ot_updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True, comment='Last update timestamp'),
        sa.Column('ot_created_by', sa.String(length=25), nullable=True, comment='Username who created'),
        sa.Column('ot_updated_by', sa.String(length=25), nullable=True, comment='Username who last updated'),
        sa.PrimaryKeyConstraint('ot_id'),
        sa.UniqueConstraint('ot_code')
    )
    
    # Create indexes
    op.create_index('ix_objection_types_ot_id', 'objection_types', ['ot_id'])
    op.create_index('ix_objection_types_ot_code', 'objection_types', ['ot_code'])
    
    # Insert default objection types
    op.execute("""
        INSERT INTO objection_types (ot_code, ot_name_en, ot_name_si, ot_description, ot_is_active, ot_created_by)
        VALUES 
            ('CAPACITY', 'Capacity Full', 'ධාරිතාව සම්පූර්ණයි', 'Maximum capacity reached, cannot accommodate more residents', true, 'SYSTEM'),
            ('CONSTRUCTION', 'Construction Work', 'ඉදිකිරීම් කටයුතු', 'Ongoing construction or renovation work', true, 'SYSTEM'),
            ('ADMIN', 'Administrative Review', 'පරිපාලන සමාලෝචනය', 'Under administrative review or investigation', true, 'SYSTEM'),
            ('MAINTENANCE', 'Maintenance', 'නඩත්තු කටයුතු', 'Facility maintenance or repairs in progress', true, 'SYSTEM'),
            ('TEMPORARY', 'Temporary Restriction', 'තාවකාලික සීමා කිරීම', 'Temporary restriction for specific reasons', true, 'SYSTEM'),
            ('OTHER', 'Other', 'වෙනත්', 'Other reasons not listed above', true, 'SYSTEM')
    """)
    
    # Add obj_type_id column to objections table (nullable temporarily)
    op.add_column('objections', sa.Column('obj_type_id', sa.Integer(), nullable=True, comment='Foreign key to objection_types table'))
    
    # Set default type for existing objections (use 'OTHER' type)
    op.execute("""
        UPDATE objections 
        SET obj_type_id = (SELECT ot_id FROM objection_types WHERE ot_code = 'OTHER' LIMIT 1)
        WHERE obj_type_id IS NULL
    """)
    
    # Make obj_type_id non-nullable
    op.alter_column('objections', 'obj_type_id', nullable=False)
    
    # Create foreign key constraint
    op.create_foreign_key(
        'fk_objections_obj_type_id',
        'objections',
        'objection_types',
        ['obj_type_id'],
        ['ot_id']
    )
    
    # Create index on obj_type_id
    op.create_index('ix_objections_obj_type_id', 'objections', ['obj_type_id'])


def downgrade() -> None:
    """Remove objection_types table and foreign key"""
    
    # Drop foreign key and index
    op.drop_index('ix_objections_obj_type_id', 'objections')
    op.drop_constraint('fk_objections_obj_type_id', 'objections', type_='foreignkey')
    
    # Drop obj_type_id column
    op.drop_column('objections', 'obj_type_id')
    
    # Drop objection_types table
    op.drop_index('ix_objection_types_ot_code', 'objection_types')
    op.drop_index('ix_objection_types_ot_id', 'objection_types')
    op.drop_table('objection_types')
