"""remove incorrect mahanayaka_name foreign key

Revision ID: 20251116133100
Revises: 20251116000001
Create Date: 2025-11-16 13:31:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20251116133100'
down_revision: Union[str, None] = '20251116000001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


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


def upgrade():
    # Drop the incorrect foreign key constraint on br_mahanayaka_name
    # This field should store a name (text), not a foreign key reference
    if constraint_exists('fk_bhikku_regist_mahanayaka_name', 'bhikku_regist'):
        op.drop_constraint('fk_bhikku_regist_mahanayaka_name', 'bhikku_regist', type_='foreignkey')


def downgrade():
    # Re-create the foreign key constraint (not recommended as it was incorrect)
    # Only included for migration reversibility
    if not constraint_exists('fk_bhikku_regist_mahanayaka_name', 'bhikku_regist'):
        op.create_foreign_key(
            'fk_bhikku_regist_mahanayaka_name',
            'bhikku_regist', 'bhikku_regist',
            ['br_mahanayaka_name'], ['br_regn'],
            ondelete='SET NULL'
        )
