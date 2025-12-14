"""increase length for karmacharya and upaddhyaya names

Revision ID: 20251214000002
Revises: 20251214000001
Create Date: 2025-12-14 00:00:02
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20251214000002"
down_revision: Union[str, None] = "20251214000001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Increase length for karmacharya and upaddhyaya name fields"""
    op.alter_column('direct_bhikku_high', 'dbh_karmacharya_name',
                    existing_type=sa.String(length=12),
                    type_=sa.String(length=100),
                    existing_nullable=True)
    
    op.alter_column('direct_bhikku_high', 'dbh_upaddhyaya_name',
                    existing_type=sa.String(length=12),
                    type_=sa.String(length=100),
                    existing_nullable=True)


def downgrade() -> None:
    """Revert length changes"""
    op.alter_column('direct_bhikku_high', 'dbh_karmacharya_name',
                    existing_type=sa.String(length=100),
                    type_=sa.String(length=12),
                    existing_nullable=True)
    
    op.alter_column('direct_bhikku_high', 'dbh_upaddhyaya_name',
                    existing_type=sa.String(length=100),
                    type_=sa.String(length=12),
                    existing_nullable=True)
