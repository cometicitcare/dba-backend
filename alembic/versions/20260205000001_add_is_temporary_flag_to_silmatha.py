"""add is_temporary flag to silmatha_regist

Revision ID: 20260205000001
Revises: 23883498cca9
Create Date: 2026-02-05 00:00:01.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = '20260205000001'
down_revision = '23883498cca9'
branch_labels = None
depends_on = None


def upgrade():
    """Add sil_is_temporary_record flag to silmatha_regist table"""
    conn = op.get_bind()
    result = conn.execute(text(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_name='silmatha_regist' AND column_name='sil_is_temporary_record'"
    ))
    if result.fetchone() is None:
        op.add_column('silmatha_regist', sa.Column('sil_is_temporary_record', sa.Boolean(), nullable=True, server_default=sa.text('false'), comment='Flag to identify records created from temporary silmatha endpoint'))


def downgrade():
    """Remove sil_is_temporary_record flag from silmatha_regist table"""
    op.drop_column('silmatha_regist', 'sil_is_temporary_record')
