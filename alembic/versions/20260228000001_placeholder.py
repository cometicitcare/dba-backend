"""placeholder for revision applied directly to production database

This migration was applied to the production database but the file was
not committed to the repository. This placeholder re-establishes the
revision chain without making any schema changes.

Revision ID: 20260228000001
Revises: 20260226000001
Create Date: 2026-02-28

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260228000001"
down_revision = "20260226000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass  # No schema changes — placeholder only


def downgrade() -> None:
    pass  # No schema changes — placeholder only
