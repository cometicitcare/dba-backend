"""add stage f bypass and period fields to vihaddata

Revision ID: 20260223000002
Revises: 20260223000001
Create Date: 2026-02-23

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260223000002"
down_revision = "20260223000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add bypass toggle fields (Boolean)
    op.add_column("vihaddata", sa.Column("vh_bypass_no_detail", sa.Boolean(), nullable=True, server_default=sa.false()))
    op.add_column("vihaddata", sa.Column("vh_bypass_no_chief", sa.Boolean(), nullable=True, server_default=sa.false()))
    op.add_column("vihaddata", sa.Column("vh_bypass_ltr_cert", sa.Boolean(), nullable=True, server_default=sa.false()))
    
    # Stage B: Bypass audit columns (_by = user id, _at = timestamp)
    op.add_column("vihaddata", sa.Column("vh_bypass_no_detail_by", sa.String(25), nullable=True))
    op.add_column("vihaddata", sa.Column("vh_bypass_no_detail_at", sa.DateTime(), nullable=True))
    op.add_column("vihaddata", sa.Column("vh_bypass_no_chief_by", sa.String(25), nullable=True))
    op.add_column("vihaddata", sa.Column("vh_bypass_no_chief_at", sa.DateTime(), nullable=True))
    op.add_column("vihaddata", sa.Column("vh_bypass_ltr_cert_by", sa.String(25), nullable=True))
    op.add_column("vihaddata", sa.Column("vh_bypass_ltr_cert_at", sa.DateTime(), nullable=True))
    op.add_column("vihaddata", sa.Column("vh_bypass_unlocked_by", sa.String(25), nullable=True))
    op.add_column("vihaddata", sa.Column("vh_bypass_unlocked_at", sa.DateTime(), nullable=True))

    # Add historical period fields
    op.add_column("vihaddata", sa.Column("vh_period_era", sa.String(50), nullable=True))
    op.add_column("vihaddata", sa.Column("vh_period_year", sa.String(10), nullable=True))  # free text (e.g. ~600)
    op.add_column("vihaddata", sa.Column("vh_period_month", sa.String(2), nullable=True))
    op.add_column("vihaddata", sa.Column("vh_period_day", sa.String(2), nullable=True))
    op.add_column("vihaddata", sa.Column("vh_period_notes", sa.String(500), nullable=True))
    
    # Add viharadhipathi appointment date
    op.add_column("vihaddata", sa.Column("viharadhipathi_date", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("vihaddata", "viharadhipathi_date")
    op.drop_column("vihaddata", "vh_period_notes")
    op.drop_column("vihaddata", "vh_period_day")
    op.drop_column("vihaddata", "vh_period_month")
    op.drop_column("vihaddata", "vh_period_year")
    op.drop_column("vihaddata", "vh_period_era")
    op.drop_column("vihaddata", "vh_bypass_unlocked_at")
    op.drop_column("vihaddata", "vh_bypass_unlocked_by")
    op.drop_column("vihaddata", "vh_bypass_ltr_cert_at")
    op.drop_column("vihaddata", "vh_bypass_ltr_cert_by")
    op.drop_column("vihaddata", "vh_bypass_no_chief_at")
    op.drop_column("vihaddata", "vh_bypass_no_chief_by")
    op.drop_column("vihaddata", "vh_bypass_no_detail_at")
    op.drop_column("vihaddata", "vh_bypass_no_detail_by")
    op.drop_column("vihaddata", "vh_bypass_ltr_cert")
    op.drop_column("vihaddata", "vh_bypass_no_chief")
    op.drop_column("vihaddata", "vh_bypass_no_detail")
