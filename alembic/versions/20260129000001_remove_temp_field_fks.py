"""Remove foreign key constraints for fields supporting TEMP references

Revision ID: 20260129000001
Revises: 20251210000003
Create Date: 2026-01-29 09:58:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260129000001'
down_revision = '20251210000003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Remove foreign key constraints for fields that can contain TEMP- references"""
    
    # Get existing foreign key constraints
    conn = op.get_bind()
    existing_fks = set()
    try:
        result = conn.execute(
            sa.text("SELECT constraint_name FROM information_schema.table_constraints WHERE table_name = 'silmatha_regist' AND constraint_type = 'FOREIGN KEY'")
        )
        existing_fks = {row[0] for row in result}
    except Exception:
        # If query fails, assume all constraints exist
        existing_fks = {
            'fk_silmatha_regist_robing_tutor_residence',
            'fk_silmatha_regist_mahanatemple', 
            'fk_silmatha_regist_robing_after_residence_temple'
        }
    
    # Drop foreign key constraints for arama fields that can contain TEMP- references
    if 'fk_silmatha_regist_robing_tutor_residence' in existing_fks:
        op.drop_constraint('fk_silmatha_regist_robing_tutor_residence', 'silmatha_regist', type_='foreignkey')
    
    if 'fk_silmatha_regist_mahanatemple' in existing_fks:
        op.drop_constraint('fk_silmatha_regist_mahanatemple', 'silmatha_regist', type_='foreignkey')
        
    if 'fk_silmatha_regist_robing_after_residence_temple' in existing_fks:
        op.drop_constraint('fk_silmatha_regist_robing_after_residence_temple', 'silmatha_regist', type_='foreignkey')


def downgrade() -> None:
    """Re-add foreign key constraints (Note: This may fail if TEMP- values exist in the database)"""
    
    # Get existing foreign key constraints
    conn = op.get_bind()
    existing_fks = set()
    try:
        result = conn.execute(
            sa.text("SELECT constraint_name FROM information_schema.table_constraints WHERE table_name = 'silmatha_regist' AND constraint_type = 'FOREIGN KEY'")
        )
        existing_fks = {row[0] for row in result}
    except Exception:
        existing_fks = set()
    
    # Re-add foreign key constraints for arama fields
    if 'fk_silmatha_regist_robing_tutor_residence' not in existing_fks:
        op.create_foreign_key(
            'fk_silmatha_regist_robing_tutor_residence',
            'silmatha_regist', 'aramadata',
            ['sil_robing_tutor_residence'], ['ar_trn'],
            onupdate='CASCADE', ondelete='SET NULL'
        )
    
    if 'fk_silmatha_regist_mahanatemple' not in existing_fks:
        op.create_foreign_key(
            'fk_silmatha_regist_mahanatemple',
            'silmatha_regist', 'aramadata',
            ['sil_mahanatemple'], ['ar_trn'],
            onupdate='CASCADE', ondelete='SET NULL'
        )
        
    if 'fk_silmatha_regist_robing_after_residence_temple' not in existing_fks:
        op.create_foreign_key(
            'fk_silmatha_regist_robing_after_residence_temple', 
            'silmatha_regist', 'aramadata',
            ['sil_robing_after_residence_temple'], ['ar_trn'],
            onupdate='CASCADE', ondelete='SET NULL'
        )