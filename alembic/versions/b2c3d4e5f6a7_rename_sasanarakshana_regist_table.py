"""rename cmm_sasanarakshana_regist to sasanarakshana_regist

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-18 00:01:00

"""
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def _table_exists(conn, table: str) -> bool:
    return conn.execute(text(
        "SELECT 1 FROM information_schema.tables WHERE table_name=:t"
    ), {"t": table}).fetchone() is not None


def _index_exists(conn, index: str) -> bool:
    return conn.execute(text(
        "SELECT 1 FROM pg_indexes WHERE indexname=:i"
    ), {"i": index}).fetchone() is not None


def upgrade() -> None:
    """Rename table from cmm_sasanarakshana_regist to sasanarakshana_regist."""
    conn = op.get_bind()

    # Only rename if the old table still exists (skip if already renamed or created correctly)
    if _table_exists(conn, 'cmm_sasanarakshana_regist'):
        op.rename_table('cmm_sasanarakshana_regist', 'sasanarakshana_regist')

    # Only rename the index if the old index name still exists
    if _index_exists(conn, 'ix_cmm_sasanarakshana_regist_sar_id'):
        op.execute('ALTER INDEX ix_cmm_sasanarakshana_regist_sar_id RENAME TO ix_sasanarakshana_regist_sar_id')


def downgrade() -> None:
    """Rename table back to cmm_sasanarakshana_regist."""
    conn = op.get_bind()
    if _index_exists(conn, 'ix_sasanarakshana_regist_sar_id'):
        op.execute('ALTER INDEX ix_sasanarakshana_regist_sar_id RENAME TO ix_cmm_sasanarakshana_regist_sar_id')
    if _table_exists(conn, 'sasanarakshana_regist'):
        op.rename_table('sasanarakshana_regist', 'cmm_sasanarakshana_regist')
