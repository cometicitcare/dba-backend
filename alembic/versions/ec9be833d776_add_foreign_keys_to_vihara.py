"""add foreign keys to vihara

Revision ID: ec9be833d776
Revises: 
Create Date: 2025-01-09 00:00:00

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = 'ec9be833d776'
down_revision = 'fdb5dc86afe3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add foreign key constraints to vihaddata table"""
    
    # Clean invalid references before adding foreign keys
    # This ensures data integrity
    
    # Clean invalid nikaya references (nullable)
    op.execute("""
        UPDATE vihaddata 
        SET vh_nikaya = NULL 
        WHERE vh_nikaya IS NOT NULL 
        AND vh_nikaya NOT IN (SELECT nk_nkn FROM cmm_nikayadata WHERE nk_is_deleted = false)
    """)
    
    # Clean invalid province references (nullable)
    op.execute("""
        UPDATE vihaddata 
        SET vh_province = NULL 
        WHERE vh_province IS NOT NULL 
        AND vh_province NOT IN (SELECT cp_code FROM cmm_province WHERE cp_is_deleted = false)
    """)
    
    # Clean invalid district references (nullable)
    op.execute("""
        UPDATE vihaddata 
        SET vh_district = NULL 
        WHERE vh_district IS NOT NULL 
        AND vh_district NOT IN (SELECT dd_dcode FROM cmm_districtdata WHERE dd_is_deleted = false)
    """)
    
    # Clean invalid divisional secretariat references (nullable)
    op.execute("""
        UPDATE vihaddata 
        SET vh_divisional_secretariat = NULL 
        WHERE vh_divisional_secretariat IS NOT NULL 
        AND vh_divisional_secretariat NOT IN (SELECT dv_dvcode FROM cmm_dvsec WHERE dv_is_deleted = false)
    """)
    
    # Clean invalid GN division references (NOT NULL - required field)
    # Since vh_gndiv is NOT NULL, we need to handle this carefully
    op.execute("""
        UPDATE vihaddata 
        SET vh_gndiv = (SELECT gn_gnc FROM cmm_gndata WHERE gn_is_deleted = false LIMIT 1)
        WHERE vh_gndiv IS NOT NULL 
        AND vh_gndiv NOT IN (SELECT gn_gnc FROM cmm_gndata WHERE gn_is_deleted = false)
    """)
    
    # Note: vh_pradeshya_sabha does not have a reference table, so no FK constraint for it
    
    # Add foreign key constraints
    
    # Nikaya foreign key (nullable)
    op.create_foreign_key(
        'fk_vihaddata_nikaya',
        'vihaddata', 'cmm_nikayadata',
        ['vh_nikaya'], ['nk_nkn'],
        ondelete='SET NULL'
    )
    
    # Province foreign key (nullable)
    op.create_foreign_key(
        'fk_vihaddata_province',
        'vihaddata', 'cmm_province',
        ['vh_province'], ['cp_code'],
        ondelete='SET NULL'
    )
    
    # District foreign key (nullable)
    op.create_foreign_key(
        'fk_vihaddata_district',
        'vihaddata', 'cmm_districtdata',
        ['vh_district'], ['dd_dcode'],
        ondelete='SET NULL'
    )
    
    # Divisional Secretariat foreign key (nullable)
    op.create_foreign_key(
        'fk_vihaddata_divisional_secretariat',
        'vihaddata', 'cmm_dvsec',
        ['vh_divisional_secretariat'], ['dv_dvcode'],
        ondelete='SET NULL'
    )
    
    # GN Division (Grama Niladhari) foreign key (required)
    op.create_foreign_key(
        'fk_vihaddata_gndiv',
        'vihaddata', 'cmm_gndata',
        ['vh_gndiv'], ['gn_gnc'],
        ondelete='RESTRICT'  # Don't allow deletion if referenced
    )
    
    print(f"Added foreign key constraints to vihaddata table at {datetime.now()}")


def downgrade() -> None:
    """Remove foreign key constraints from vihaddata table"""
    
    # Drop foreign key constraints in reverse order
    op.drop_constraint('fk_vihaddata_gndiv', 'vihaddata', type_='foreignkey')
    op.drop_constraint('fk_vihaddata_divisional_secretariat', 'vihaddata', type_='foreignkey')
    op.drop_constraint('fk_vihaddata_district', 'vihaddata', type_='foreignkey')
    op.drop_constraint('fk_vihaddata_province', 'vihaddata', type_='foreignkey')
    op.drop_constraint('fk_vihaddata_nikaya', 'vihaddata', type_='foreignkey')
    
    print(f"Removed foreign key constraints from vihaddata table at {datetime.now()}")
