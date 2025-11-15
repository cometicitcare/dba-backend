"""add scanned document path to bhikku

Revision ID: c970c05314d5
Revises: 14f4a3921216
Create Date: 2025-11-16 00:26:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c970c05314d5'
down_revision = '14f4a3921216'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add scanned document path field to bhikku_regist table
    op.add_column('bhikku_regist', sa.Column('br_scanned_document_path', sa.String(length=500), nullable=True, comment='Path to uploaded scanned document file'))


def downgrade() -> None:
    # Remove scanned document path field from bhikku_regist table
    op.drop_column('bhikku_regist', 'br_scanned_document_path')
