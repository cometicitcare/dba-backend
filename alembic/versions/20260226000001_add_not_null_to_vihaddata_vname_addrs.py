"""add_not_null_to_vihaddata_vname_addrs

Revision ID: 20260226000001
Revises: 20260223000002
Create Date: 2026-02-26

Adds NOT NULL constraints to vh_vname and vh_addrs in vihaddata.

IMPORTANT: Do NOT run this migration until cleanup_vihara_nulls.py has been
executed in LIVE mode (DRY_RUN = False) and confirmed zero NULL rows remain.
The migration will refuse to apply if any NULL rows still exist.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers
revision = '20260226000001'
down_revision = '20260223000002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # Safety check — refuse to proceed if any NULL rows still exist in active records
    result = conn.execute(text("""
        SELECT COUNT(*)
        FROM vihaddata
        WHERE (vh_vname IS NULL OR vh_addrs IS NULL)
          AND vh_is_deleted = FALSE
    """))
    null_count = result.scalar()
    if null_count and null_count > 0:
        raise RuntimeError(
            f"Migration aborted: {null_count} active rows still have NULL vh_vname or vh_addrs. "
            "Run cleanup_vihara_nulls.py first (DRY_RUN = False) to resolve them, "
            "then retry this migration."
        )

    # Also check soft-deleted rows — fill them with placeholders so the constraint applies
    # to the whole table (PostgreSQL NOT NULL applies to ALL rows, deleted or not)
    conn.execute(text("""
        UPDATE vihaddata
        SET vh_vname = COALESCE(NULLIF(TRIM(vh_vname), ''), '(Name not recorded)'),
            vh_addrs = COALESCE(NULLIF(TRIM(vh_addrs), ''), '(Address not recorded)')
        WHERE vh_is_deleted = TRUE
          AND (vh_vname IS NULL OR TRIM(vh_vname) = ''
               OR vh_addrs IS NULL OR TRIM(vh_addrs) = '')
    """))

    # Add NOT NULL constraints
    op.alter_column(
        'vihaddata', 'vh_vname',
        existing_type=sa.VARCHAR(length=200),
        nullable=False,
    )
    op.alter_column(
        'vihaddata', 'vh_addrs',
        existing_type=sa.VARCHAR(length=200),
        nullable=False,
    )


def downgrade() -> None:
    # Revert to nullable (in case rollback is needed)
    op.alter_column(
        'vihaddata', 'vh_vname',
        existing_type=sa.VARCHAR(length=200),
        nullable=True,
    )
    op.alter_column(
        'vihaddata', 'vh_addrs',
        existing_type=sa.VARCHAR(length=200),
        nullable=True,
    )
