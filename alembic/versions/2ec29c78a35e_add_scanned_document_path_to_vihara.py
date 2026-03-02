"""add scanned document path to vihara

Revision ID: 2ec29c78a35e
Revises: 80d5302d897a
Create Date: 2025-12-04 00:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "2ec29c78a35e"
down_revision: Union[str, None] = "80d5302d897a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add scanned document path column to vihaddata table"""
    op.add_column('vihaddata', sa.Column('vh_scanned_document_path', sa.String(length=500), nullable=True))


def downgrade() -> None:
    """Remove scanned document path column from vihaddata table"""
    op.drop_column('vihaddata', 'vh_scanned_document_path')
