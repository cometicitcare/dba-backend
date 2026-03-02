"""merge heads

Revision ID: 23883498cca9
Revises: 20260115000002, 20260129000001
Create Date: 2026-01-29 10:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '23883498cca9'
down_revision = ('20260115000002', '20260129000001')
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Merge heads - no additional changes needed"""
    pass


def downgrade() -> None:
    """Downgrade merge - no changes to revert"""
    pass