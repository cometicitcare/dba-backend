"""add_br_workflow_status_column

Revision ID: 26affe4be069
Revises: add_workflow_status_01
Create Date: 2025-11-14 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '26affe4be069'
down_revision = 'add_workflow_status_01'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # This migration is empty as all workflow changes are in add_workflow_status_01
    pass


def downgrade() -> None:
    # This migration is empty as all workflow changes are in add_workflow_status_01
    pass
