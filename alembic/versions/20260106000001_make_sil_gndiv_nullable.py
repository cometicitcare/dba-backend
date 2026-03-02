"""make sil_gndiv nullable

Revision ID: 20260106000001
Revises: 20251229000001
Create Date: 2026-01-06 00:00:01
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260106000001"
down_revision: Union[str, None] = "20251229000001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make sil_gndiv nullable (was previously NOT NULL)
    op.alter_column('silmatha_regist', 'sil_gndiv',
                    existing_type=sa.String(10),
                    nullable=True)


def downgrade() -> None:
    # Revert sil_gndiv back to NOT NULL
    op.alter_column('silmatha_regist', 'sil_gndiv',
                    existing_type=sa.String(10),
                    nullable=False)
