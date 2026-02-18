"""rename cmm_sasanarakshana_regist to sasanarakshana_regist

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-18 00:01:00

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Rename table from cmm_sasanarakshana_regist to sasanarakshana_regist."""
    op.rename_table('cmm_sasanarakshana_regist', 'sasanarakshana_regist')
    # Rename the index accordingly
    op.execute('ALTER INDEX ix_cmm_sasanarakshana_regist_sar_id RENAME TO ix_sasanarakshana_regist_sar_id')


def downgrade() -> None:
    """Rename table back to cmm_sasanarakshana_regist."""
    op.execute('ALTER INDEX ix_sasanarakshana_regist_sar_id RENAME TO ix_cmm_sasanarakshana_regist_sar_id')
    op.rename_table('sasanarakshana_regist', 'cmm_sasanarakshana_regist')
