"""merge multiple heads

Revision ID: 8e0106445d04
Revises: 3015686570d6, c970c05314d5
Create Date: 2025-11-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8e0106445d04'
down_revision = ('3015686570d6', 'c970c05314d5')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
