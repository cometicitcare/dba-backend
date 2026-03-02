"""remove mahanaacharyacd foreign key constraint

Revision ID: 20251210000003
Revises: 20251210000002
Create Date: 2025-12-10 00:00:03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '20251210000003'
down_revision = '20251210000002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Remove foreign key constraint from sil_mahanaacharyacd as it can contain comma-separated values"""
    
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_fks = {fk['name'] for fk in inspector.get_foreign_keys('silmatha_regist')}
    
    # Drop the constraint if it exists
    # This field can contain comma-separated sil_regn values, so it cannot have a FK constraint
    if 'fk_silmatha_regist_mahanaacharyacd' in existing_fks:
        op.drop_constraint('fk_silmatha_regist_mahanaacharyacd', 'silmatha_regist', type_='foreignkey')


def downgrade() -> None:
    """Do not recreate the constraint as it's invalid for comma-separated values"""
    # Note: We intentionally do not recreate this constraint in downgrade
    # because sil_mahanaacharyacd can contain comma-separated values
    pass
