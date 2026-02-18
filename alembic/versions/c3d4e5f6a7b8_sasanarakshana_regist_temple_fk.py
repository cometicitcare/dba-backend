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

revision = 'c3d4e5f6a7b8'
down_revision = 'b2c3d4e5f6a7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Clear existing test data (old rows stored free-text names, not valid TRN codes)
    op.execute("DELETE FROM sasanarakshana_regist")

    # Rename the column
    op.alter_column(
        'sasanarakshana_regist',
        'sar_temple_name',
        new_column_name='sar_temple_trn',
        existing_type=sa.String(255),
        nullable=False,
    )
    # Add FK constraint
    op.create_foreign_key(
        'fk_sasanarakshana_regist_temple_trn',
        'sasanarakshana_regist',
        'vihaddata',
        ['sar_temple_trn'],
        ['vh_trn'],
        ondelete='RESTRICT',
    )


def downgrade() -> None:
    op.drop_constraint(
        'fk_sasanarakshana_regist_temple_trn',
        'sasanarakshana_regist',
        type_='foreignkey',
    )
    op.alter_column(
        'sasanarakshana_regist',
        'sar_temple_trn',
        new_column_name='sar_temple_name',
        existing_type=sa.String(255),
        nullable=False,
    )
