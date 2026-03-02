"""add vh_viharadhipathi_regn field to vihara

Revision ID: 20251226000001
Revises: 20251214000002
Create Date: 2025-12-26 00:00:01
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20251226000001"
down_revision: Union[str, None] = "20251214000002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add vh_viharadhipathi_regn column to vihaddata table
    op.add_column('vihaddata', sa.Column('vh_viharadhipathi_regn', sa.String(length=50), nullable=True))


def downgrade() -> None:
    # Remove vh_viharadhipathi_regn column from vihaddata table
    op.drop_column('vihaddata', 'vh_viharadhipathi_regn')
