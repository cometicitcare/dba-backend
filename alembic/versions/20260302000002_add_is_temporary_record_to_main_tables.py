"""Add is_temporary_record flags to bhikku_regist and vihaddata main tables

Adds vh_is_temporary_record (Boolean, default FALSE) to vihaddata table
and br_is_temporary_record (Boolean, default FALSE) to bhikku_regist table.

These flags indicate whether a record was initially created as temporary
in the corresponding temporary_vihara / temporary_bhikku tables before
being transferred to the main table.

Revision ID: 20260302000002
Revises: 20260302000001
Create Date: 2026-03-02

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260302000002"
down_revision = "20260302000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add is_temporary_record column to vihaddata
    op.add_column(
        "vihaddata",
        sa.Column(
            "vh_is_temporary_record",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
            comment="Indicates this record was created as temporary in temporary_vihara first"
        ),
    )

    # Add is_temporary_record column to bhikku_regist
    op.add_column(
        "bhikku_regist",
        sa.Column(
            "br_is_temporary_record",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
            comment="Indicates this record was created as temporary in temporary_bhikku first"
        ),
    )


def downgrade() -> None:
    # Remove is_temporary_record from bhikku_regist
    op.drop_column("bhikku_regist", "br_is_temporary_record")

    # Remove is_temporary_record from vihaddata
    op.drop_column("vihaddata", "vh_is_temporary_record")
