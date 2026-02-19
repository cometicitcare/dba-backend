"""add file_number and vihara_code to vihaddata

Revision ID: 20260219000001
Revises: 20260218000001
Create Date: 2026-02-19

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260219000001"
down_revision = "20260218000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("vihaddata", sa.Column("vh_file_number", sa.String(50), nullable=True))
    op.add_column("vihaddata", sa.Column("vh_vihara_code", sa.String(50), nullable=True))


def downgrade() -> None:
    op.drop_column("vihaddata", "vh_vihara_code")
    op.drop_column("vihaddata", "vh_file_number")
