"""Create main_bhikkus table

Stores the authoritative list of Nikaya Mahanayaka and
Parshawaya Mahanayaka bhikku assignments with correct foreign keys.

Revision ID: 20260302000004
Revises: 20260302000003
Create Date: 2026-03-02

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260302000004"
down_revision = "20260302000003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "main_bhikkus",
        sa.Column("mb_id", sa.Integer, primary_key=True, autoincrement=True),
        # Type: 'NIKAYA_MAHANAYAKA' or 'PARSHAWA_MAHANAYAKA'
        sa.Column("mb_type", sa.String(30), nullable=False, index=True),
        # Nikaya reference
        sa.Column(
            "mb_nikaya_cd",
            sa.String(10),
            sa.ForeignKey("cmm_nikayadata.nk_nkn"),
            nullable=False,
            index=True,
        ),
        # Parshawaya reference (NULL for nikaya-level appointments)
        sa.Column(
            "mb_parshawa_cd",
            sa.String(20),
            sa.ForeignKey("cmm_parshawadata.pr_prn"),
            nullable=True,
            index=True,
        ),
        # The appointed bhikku
        sa.Column(
            "mb_bhikku_regn",
            sa.String(20),
            sa.ForeignKey("bhikku_regist.br_regn"),
            nullable=False,
            index=True,
        ),
        sa.Column("mb_start_date", sa.Date, nullable=True),
        sa.Column("mb_end_date", sa.Date, nullable=True),
        sa.Column("mb_remarks", sa.String(500), nullable=True),
        sa.Column("mb_is_active", sa.Boolean, server_default=sa.text("true"), nullable=False),
        # Audit columns
        sa.Column("mb_is_deleted", sa.Boolean, server_default=sa.text("false"), nullable=False),
        sa.Column("mb_created_at", sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column("mb_updated_at", sa.TIMESTAMP, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("mb_created_by", sa.String(25), nullable=True),
        sa.Column("mb_updated_by", sa.String(25), nullable=True),
        sa.Column("mb_version_number", sa.Integer, server_default=sa.text("1"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("main_bhikkus")
