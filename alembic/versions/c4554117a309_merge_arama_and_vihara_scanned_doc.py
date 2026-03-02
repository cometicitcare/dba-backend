"""merge arama and vihara scanned doc

Revision ID: c4554117a309
Revises: 2ec29c78a35e, 20251204000001
Create Date: 2025-12-04 00:00:02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4554117a309'
down_revision: Union[str, None] = ('2ec29c78a35e', '20251204000001')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Merge migration - no changes needed"""
    pass


def downgrade() -> None:
    """Merge migration - no changes needed"""
    pass
