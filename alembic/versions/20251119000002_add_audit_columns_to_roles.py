"""add audit columns to roles

Revision ID: 20251119000002
Revises: 20251117000005
Create Date: 2025-11-19 00:00:02.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20251119000002'
down_revision: Union[str, None] = '20251117000005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add audit columns to roles table
    op.add_column('roles', sa.Column('ro_created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.add_column('roles', sa.Column('ro_updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.add_column('roles', sa.Column('ro_created_by', sa.String(length=25), nullable=True))
    op.add_column('roles', sa.Column('ro_updated_by', sa.String(length=25), nullable=True))
    op.add_column('roles', sa.Column('ro_version_number', sa.Integer(), server_default='1', nullable=True))


def downgrade() -> None:
    # Remove audit columns from roles table
    op.drop_column('roles', 'ro_version_number')
    op.drop_column('roles', 'ro_updated_by')
    op.drop_column('roles', 'ro_created_by')
    op.drop_column('roles', 'ro_updated_at')
    op.drop_column('roles', 'ro_created_at')
