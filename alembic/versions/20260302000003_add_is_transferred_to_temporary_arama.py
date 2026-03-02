"""Add is_transferred flag to temporary_arama table

Adds ta_is_transferred (Boolean, default FALSE) to temporary_arama table.

This flag provides consistency across all TEMP tables (temporary_vihara,
temporary_bhikku, temporary_silmatha, and temporary_arama) for tracking
which records have been transferred to their respective main tables.

Revision ID: 20260302000003
Revises: 20260302000002
Create Date: 2026-03-02

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260302000003"
down_revision = "20260302000002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add is_transferred column to temporary_arama
    op.add_column(
        "temporary_arama",
        sa.Column(
            "ta_is_transferred",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
            comment="Flag indicating this record has been transferred to aramadata"
        ),
    )


def downgrade() -> None:
    # Remove is_transferred from temporary_arama
    op.drop_column("temporary_arama", "ta_is_transferred")
