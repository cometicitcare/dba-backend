"""add registration status fields to vihaddata

Adds vh_is_registered (Boolean, default TRUE) and vh_unregistered_reason (String)
to the vihaddata table to capture whether a vihara is formally registered with
the Department of Buddhist Affairs, and if not, the reason for absence of registration.

Revision ID: 20260302000001
Revises: 20260228000001
Create Date: 2026-03-02

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260302000001"
down_revision = "20260228000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add registration status flag (default TRUE = registered)
    op.add_column(
        "vihaddata",
        sa.Column(
            "vh_is_registered",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )
    # Add reason for not being registered (only relevant when vh_is_registered = FALSE)
    op.add_column(
        "vihaddata",
        sa.Column(
            "vh_unregistered_reason",
            sa.String(500),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("vihaddata", "vh_unregistered_reason")
    op.drop_column("vihaddata", "vh_is_registered")
