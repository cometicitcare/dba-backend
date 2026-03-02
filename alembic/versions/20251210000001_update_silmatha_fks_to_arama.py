"""update silmatha foreign keys to arama

Revision ID: 20251210000001
Revises: 20251209000002
Create Date: 2025-12-10 00:00:01

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '20251210000001'
down_revision = '20251209000002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Update foreign keys from vihaddata to aramadata for silmatha temple fields"""
    
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_fks = {fk['name'] for fk in inspector.get_foreign_keys('silmatha_regist')}
    
    # Clean invalid references - update to use aramadata instead of vihaddata
    # Clean invalid robing_tutor_residence references (nullable)
    op.execute("""
        UPDATE silmatha_regist 
        SET sil_robing_tutor_residence = NULL 
        WHERE sil_robing_tutor_residence IS NOT NULL 
        AND sil_robing_tutor_residence NOT IN (SELECT ar_trn FROM aramadata WHERE ar_is_deleted = false)
    """)
    
    # Clean invalid mahanatemple references (nullable)
    op.execute("""
        UPDATE silmatha_regist 
        SET sil_mahanatemple = NULL 
        WHERE sil_mahanatemple IS NOT NULL 
        AND sil_mahanatemple NOT IN (SELECT ar_trn FROM aramadata WHERE ar_is_deleted = false)
    """)
    
    # Clean invalid robing_after_residence_temple references (nullable)
    op.execute("""
        UPDATE silmatha_regist 
        SET sil_robing_after_residence_temple = NULL 
        WHERE sil_robing_after_residence_temple IS NOT NULL 
        AND sil_robing_after_residence_temple NOT IN (SELECT ar_trn FROM aramadata WHERE ar_is_deleted = false)
    """)
    
    # Drop old foreign keys to vihaddata
    if 'fk_silmatha_regist_robing_tutor_residence' in existing_fks:
        op.drop_constraint('fk_silmatha_regist_robing_tutor_residence', 'silmatha_regist', type_='foreignkey')
    
    if 'fk_silmatha_regist_mahanatemple' in existing_fks:
        op.drop_constraint('fk_silmatha_regist_mahanatemple', 'silmatha_regist', type_='foreignkey')
    
    if 'fk_silmatha_regist_robing_after_residence_temple' in existing_fks:
        op.drop_constraint('fk_silmatha_regist_robing_after_residence_temple', 'silmatha_regist', type_='foreignkey')
    
    # Refresh inspector after dropping constraints
    inspector = inspect(bind)
    existing_fks = {fk['name'] for fk in inspector.get_foreign_keys('silmatha_regist')}
    
    # Add new foreign keys to aramadata
    if 'fk_silmatha_regist_robing_tutor_residence' not in existing_fks:
        op.create_foreign_key(
            'fk_silmatha_regist_robing_tutor_residence',
            'silmatha_regist', 'aramadata',
            ['sil_robing_tutor_residence'], ['ar_trn'],
            ondelete='SET NULL'
        )
    
    if 'fk_silmatha_regist_mahanatemple' not in existing_fks:
        op.create_foreign_key(
            'fk_silmatha_regist_mahanatemple',
            'silmatha_regist', 'aramadata',
            ['sil_mahanatemple'], ['ar_trn'],
            ondelete='SET NULL'
        )
    
    if 'fk_silmatha_regist_robing_after_residence_temple' not in existing_fks:
        op.create_foreign_key(
            'fk_silmatha_regist_robing_after_residence_temple',
            'silmatha_regist', 'aramadata',
            ['sil_robing_after_residence_temple'], ['ar_trn'],
            ondelete='SET NULL'
        )


def downgrade() -> None:
    """Revert foreign keys back to vihaddata"""
    
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_fks = {fk['name'] for fk in inspector.get_foreign_keys('silmatha_regist')}
    
    # Drop foreign keys to aramadata
    if 'fk_silmatha_regist_robing_tutor_residence' in existing_fks:
        op.drop_constraint('fk_silmatha_regist_robing_tutor_residence', 'silmatha_regist', type_='foreignkey')
    
    if 'fk_silmatha_regist_mahanatemple' in existing_fks:
        op.drop_constraint('fk_silmatha_regist_mahanatemple', 'silmatha_regist', type_='foreignkey')
    
    if 'fk_silmatha_regist_robing_after_residence_temple' in existing_fks:
        op.drop_constraint('fk_silmatha_regist_robing_after_residence_temple', 'silmatha_regist', type_='foreignkey')
    
    # Clean invalid references - revert to vihaddata
    op.execute("""
        UPDATE silmatha_regist 
        SET sil_robing_tutor_residence = NULL 
        WHERE sil_robing_tutor_residence IS NOT NULL 
        AND sil_robing_tutor_residence NOT IN (SELECT vh_trn FROM vihaddata WHERE vh_is_deleted = false)
    """)
    
    op.execute("""
        UPDATE silmatha_regist 
        SET sil_mahanatemple = NULL 
        WHERE sil_mahanatemple IS NOT NULL 
        AND sil_mahanatemple NOT IN (SELECT vh_trn FROM vihaddata WHERE vh_is_deleted = false)
    """)
    
    op.execute("""
        UPDATE silmatha_regist 
        SET sil_robing_after_residence_temple = NULL 
        WHERE sil_robing_after_residence_temple IS NOT NULL 
        AND sil_robing_after_residence_temple NOT IN (SELECT vh_trn FROM vihaddata WHERE vh_is_deleted = false)
    """)
    
    # Refresh inspector after cleaning data
    inspector = inspect(bind)
    existing_fks = {fk['name'] for fk in inspector.get_foreign_keys('silmatha_regist')}
    
    # Add back foreign keys to vihaddata
    if 'fk_silmatha_regist_robing_tutor_residence' not in existing_fks:
        op.create_foreign_key(
            'fk_silmatha_regist_robing_tutor_residence',
            'silmatha_regist', 'vihaddata',
            ['sil_robing_tutor_residence'], ['vh_trn'],
            ondelete='SET NULL'
        )
    
    if 'fk_silmatha_regist_mahanatemple' not in existing_fks:
        op.create_foreign_key(
            'fk_silmatha_regist_mahanatemple',
            'silmatha_regist', 'vihaddata',
            ['sil_mahanatemple'], ['vh_trn'],
            ondelete='SET NULL'
        )
    
    if 'fk_silmatha_regist_robing_after_residence_temple' not in existing_fks:
        op.create_foreign_key(
            'fk_silmatha_regist_robing_after_residence_temple',
            'silmatha_regist', 'vihaddata',
            ['sil_robing_after_residence_temple'], ['vh_trn'],
            ondelete='SET NULL'
        )
