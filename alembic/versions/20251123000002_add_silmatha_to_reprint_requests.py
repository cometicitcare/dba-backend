"""add silmatha support to reprint_requests

Revision ID: 20251123000002
Revises: 20251123000001
Create Date: 2025-11-23 00:20:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20251123000002"
down_revision = "20251123000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("reprint_requests", sa.Column("silmatha_regn", sa.String(length=20), nullable=True))
    op.create_foreign_key(
        "fk_reprint_requests_silmatha", "reprint_requests", "silmatha_regist", ["silmatha_regn"], ["sil_regn"], ondelete="CASCADE"
    )
    op.create_index("ix_reprint_requests_silmatha_regn", "reprint_requests", ["silmatha_regn"])

    # Replace check constraint to include silmatha_regn
    op.drop_constraint("ck_reprint_requests_target_present", "reprint_requests", type_="check")
    op.create_check_constraint(
        "ck_reprint_requests_target_present",
        "reprint_requests",
        "(bhikku_regn IS NOT NULL)::int + (bhikku_high_regn IS NOT NULL)::int + (upasampada_regn IS NOT NULL)::int + (silmatha_regn IS NOT NULL)::int >= 1",
    )


def downgrade() -> None:
    op.drop_constraint("ck_reprint_requests_target_present", "reprint_requests", type_="check")
    op.create_check_constraint(
        "ck_reprint_requests_target_present",
        "reprint_requests",
        "(bhikku_regn IS NOT NULL)::int + (bhikku_high_regn IS NOT NULL)::int + (upasampada_regn IS NOT NULL)::int >= 1",
    )
    op.drop_index("ix_reprint_requests_silmatha_regn", table_name="reprint_requests")
    op.drop_constraint("fk_reprint_requests_silmatha", "reprint_requests", type_="foreignkey")
    op.drop_column("reprint_requests", "silmatha_regn")
