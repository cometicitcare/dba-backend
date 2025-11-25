"""Merge reprint branch and district role rename branch

Revision ID: 20251123000003
Revises: 20251123000002, 20251120010000
Create Date: 2025-11-23 00:00:03
"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20251123000003"
down_revision: Union[str, Sequence[str], None] = (
    "20251123000002",
    "20251120010000",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """No-op merge migration to unify heads."""
    pass


def downgrade() -> None:
    """Downgrade is a no-op; Alembic will handle branch separation."""
    pass
