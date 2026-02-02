"""create reprint_requests table

Revision ID: 20251123000001
Revises: 20251122000001
Create Date: 2025-11-23 00:00:01
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "20251123000001"
down_revision = "20251122000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "reprint_requests",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("request_type", sa.String(length=30), nullable=False, index=True, comment="BHIKKU, HIGH_BHIKKU, UPASAMPADA"),
        sa.Column("bhikku_regn", sa.String(length=12), nullable=True, index=True),
        sa.Column("bhikku_high_regn", sa.String(length=12), nullable=True, index=True),
        sa.Column("upasampada_regn", sa.String(length=20), nullable=True, index=True),
        sa.Column("form_no", sa.String(length=50), nullable=True, index=True),
        sa.Column("request_reason", sa.String(length=500), nullable=True),
        sa.Column("amount", sa.Numeric(10, 2), nullable=True),
        sa.Column("remarks", sa.String(length=500), nullable=True),
        sa.Column("flow_status", sa.String(length=20), nullable=False, server_default=sa.text("'PENDING'"), index=True, comment="PENDING, APPROVED, REJECTED, COMPLETED"),
        sa.Column("requested_by", sa.String(length=25), nullable=True),
        sa.Column("requested_at", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.Column("approved_by", sa.String(length=25), nullable=True),
        sa.Column("approved_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("rejected_by", sa.String(length=25), nullable=True),
        sa.Column("rejected_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("rejection_reason", sa.String(length=500), nullable=True),
        sa.Column("printed_by", sa.String(length=25), nullable=True),
        sa.Column("printed_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("completed_by", sa.String(length=25), nullable=True),
        sa.Column("completed_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("now()"), onupdate=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "(bhikku_regn IS NOT NULL)::int + (bhikku_high_regn IS NOT NULL)::int + (upasampada_regn IS NOT NULL)::int >= 1",
            name="ck_reprint_requests_target_present",
        ),
        sa.ForeignKeyConstraint(["bhikku_regn"], ["bhikku_regist.br_regn"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["bhikku_high_regn"], ["bhikku_high_regist.bhr_regn"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["upasampada_regn"], ["bhikku_high_regist.bhr_regn"], ondelete="CASCADE"),
    )


def downgrade() -> None:
    op.drop_table("reprint_requests")
