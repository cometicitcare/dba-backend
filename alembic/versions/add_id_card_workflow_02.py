"""Add ID card workflow status and tracking tables.

Revision ID: add_id_card_workflow_02
Revises: 26affe4be069
Create Date: 2025-11-15 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = "add_id_card_workflow_02"
down_revision = "26affe4be069"
branch_labels = None
depends_on = None


def _get_table_names(inspector):
    return set(inspector.get_table_names())


def _get_column_names(inspector, table_name: str):
    try:
        return {col["name"] for col in inspector.get_columns(table_name)}
    except sa.exc.NoSuchTableError:
        return set()


def upgrade() -> None:
    """Add workflow status column to bhikku_id_card and create bhikku_id_card_workflow_flags table."""
    bind = op.get_bind()
    inspector = inspect(bind)

    # Add workflow_status column to bhikku_id_card table if it does not exist
    columns = _get_column_names(inspector, "bhikku_id_card")
    if "bic_workflow_status" not in columns:
        op.add_column(
            "bhikku_id_card",
            sa.Column(
                "bic_workflow_status",
                sa.String(20),
                nullable=False,
                server_default="pending",
            ),
        )

    # Create bhikku_id_card_workflow_flags table if it is missing
    table_names = _get_table_names(inspector)
    if "bhikku_id_card_workflow_flags" not in table_names:
        op.create_table(
            "bhikku_id_card_workflow_flags",
            sa.Column("bicwf_id", sa.Integer(), nullable=False),
            sa.Column("bicwf_bhikku_id_card_id", sa.Integer(), nullable=False),
            sa.Column("bicwf_bhikku_id", sa.Integer(), nullable=False),
            sa.Column(
                "bicwf_current_flag",
                sa.String(20),
                nullable=False,
                server_default="pending",
            ),
            sa.Column("bicwf_pending_date", sa.TIMESTAMP(), nullable=True),
            sa.Column("bicwf_approval_date", sa.TIMESTAMP(), nullable=True),
            sa.Column("bicwf_approval_by", sa.String(25), nullable=True),
            sa.Column("bicwf_approval_notes", sa.String(500), nullable=True),
            sa.Column("bicwf_printing_date", sa.TIMESTAMP(), nullable=True),
            sa.Column("bicwf_print_by", sa.String(25), nullable=True),
            sa.Column("bicwf_scan_date", sa.TIMESTAMP(), nullable=True),
            sa.Column("bicwf_scan_by", sa.String(25), nullable=True),
            sa.Column("bicwf_completion_date", sa.TIMESTAMP(), nullable=True),
            sa.Column("bicwf_completed_by", sa.String(25), nullable=True),
            sa.Column(
                "bicwf_created_at", sa.TIMESTAMP(), server_default=sa.func.now()
            ),
            sa.Column(
                "bicwf_updated_at", sa.TIMESTAMP(), server_default=sa.func.now()
            ),
            sa.Column("bicwf_created_by", sa.String(25), nullable=True),
            sa.Column("bicwf_updated_by", sa.String(25), nullable=True),
            sa.Column("bicwf_is_deleted", sa.Boolean(), server_default="false"),
            sa.Column(
                "bicwf_version_number", sa.Integer(), server_default="1"
            ),
            sa.ForeignKeyConstraint(
                ["bicwf_bhikku_id_card_id"],
                ["bhikku_id_card.bic_id"],
                onupdate="CASCADE",
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(
                ["bicwf_bhikku_id"],
                ["bhikku_regist.br_id"],
                onupdate="CASCADE",
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(
                ["bicwf_created_by"],
                ["user_accounts.ua_user_id"],
                onupdate="CASCADE",
                ondelete="SET NULL",
            ),
            sa.ForeignKeyConstraint(
                ["bicwf_updated_by"],
                ["user_accounts.ua_user_id"],
                onupdate="CASCADE",
                ondelete="SET NULL",
            ),
            sa.PrimaryKeyConstraint("bicwf_id"),
        )
        op.create_index(
            op.f(
                "ix_bhikku_id_card_workflow_flags_bicwf_bhikku_id_card_id"
            ),
            "bhikku_id_card_workflow_flags",
            ["bicwf_bhikku_id_card_id"],
            unique=False,
        )
        op.create_index(
            op.f("ix_bhikku_id_card_workflow_flags_bicwf_bhikku_id"),
            "bhikku_id_card_workflow_flags",
            ["bicwf_bhikku_id"],
            unique=False,
        )
        op.create_index(
            op.f("ix_bhikku_id_card_workflow_flags_bicwf_current_flag"),
            "bhikku_id_card_workflow_flags",
            ["bicwf_current_flag"],
            unique=False,
        )


def downgrade() -> None:
    """Revert ID card workflow status changes."""
    bind = op.get_bind()
    inspector = inspect(bind)

    table_names = _get_table_names(inspector)
    if "bhikku_id_card_workflow_flags" in table_names:
        op.drop_index(
            op.f("ix_bhikku_id_card_workflow_flags_bicwf_current_flag"),
            table_name="bhikku_id_card_workflow_flags",
        )
        op.drop_index(
            op.f("ix_bhikku_id_card_workflow_flags_bicwf_bhikku_id"),
            table_name="bhikku_id_card_workflow_flags",
        )
        op.drop_index(
            op.f("ix_bhikku_id_card_workflow_flags_bicwf_bhikku_id_card_id"),
            table_name="bhikku_id_card_workflow_flags",
        )
        op.drop_table("bhikku_id_card_workflow_flags")

    columns = _get_column_names(inspector, "bhikku_id_card")
    if "bic_workflow_status" in columns:
        op.drop_column("bhikku_id_card", "bic_workflow_status")
