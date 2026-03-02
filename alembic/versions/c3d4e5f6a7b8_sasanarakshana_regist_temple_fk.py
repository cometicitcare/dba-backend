"""sasanarakshana_regist: rename temple_name to temple_trn FK

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-02-18 00:00:00.000000

Changes:
- Rename column `sar_temple_name` -> `sar_temple_trn`
- Alter type from VARCHAR(255) to VARCHAR(10)
- Add foreign key constraint referencing vihaddata.vh_trn
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

revision = 'c3d4e5f6a7b8'
down_revision = 'b2c3d4e5f6a7'
branch_labels = None
depends_on = None


def _column_exists(conn, table: str, column: str) -> bool:
    return conn.execute(text(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_name=:t AND column_name=:c"
    ), {"t": table, "c": column}).fetchone() is not None


def _constraint_exists(conn, constraint: str) -> bool:
    return conn.execute(text(
        "SELECT 1 FROM information_schema.table_constraints "
        "WHERE constraint_name=:n"
    ), {"n": constraint}).fetchone() is not None


def upgrade() -> None:
    conn = op.get_bind()

    # Clear existing test data (old rows stored free-text names, not valid TRN codes)
    op.execute("DELETE FROM sasanarakshana_regist")

    # Rename the column only if the old name still exists
    if _column_exists(conn, 'sasanarakshana_regist', 'sar_temple_name'):
        op.alter_column(
            'sasanarakshana_regist',
            'sar_temple_name',
            new_column_name='sar_temple_trn',
            existing_type=sa.String(255),
            nullable=False,
        )

    # Add FK constraint only if it doesn't already exist
    if not _constraint_exists(conn, 'fk_sasanarakshana_regist_temple_trn'):
        op.create_foreign_key(
            'fk_sasanarakshana_regist_temple_trn',
            'sasanarakshana_regist',
            'vihaddata',
            ['sar_temple_trn'],
            ['vh_trn'],
            ondelete='RESTRICT',
        )


def downgrade() -> None:
    conn = op.get_bind()

    if _constraint_exists(conn, 'fk_sasanarakshana_regist_temple_trn'):
        op.drop_constraint(
            'fk_sasanarakshana_regist_temple_trn',
            'sasanarakshana_regist',
            type_='foreignkey',
        )

    if _column_exists(conn, 'sasanarakshana_regist', 'sar_temple_trn'):
        op.alter_column(
            'sasanarakshana_regist',
            'sar_temple_trn',
            new_column_name='sar_temple_name',
            existing_type=sa.String(255),
            nullable=False,
        )
