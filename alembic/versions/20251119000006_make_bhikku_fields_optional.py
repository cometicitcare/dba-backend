"""make_bhikku_fields_optional

Revision ID: 20251119000006
Revises: 20251119000002
Create Date: 2025-11-19 00:00:06.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20251119000006'
down_revision: Union[str, None] = '20251119000002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make br_gndiv nullable (was previously NOT NULL)
    op.alter_column('bhikku_regist', 'br_gndiv',
                    existing_type=sa.String(10),
                    nullable=True)
    
    # Make br_mahanatemple nullable (was previously NOT NULL)
    op.alter_column('bhikku_regist', 'br_mahanatemple',
                    existing_type=sa.String(10),
                    nullable=True)
    
    # Make br_mahanaacharyacd nullable (was previously NOT NULL)
    op.alter_column('bhikku_regist', 'br_mahanaacharyacd',
                    existing_type=sa.String(12),
                    nullable=True)


def downgrade() -> None:
    # Revert br_mahanaacharyacd back to NOT NULL
    op.alter_column('bhikku_regist', 'br_mahanaacharyacd',
                    existing_type=sa.String(12),
                    nullable=False)
    
    # Revert br_mahanatemple back to NOT NULL
    op.alter_column('bhikku_regist', 'br_mahanatemple',
                    existing_type=sa.String(10),
                    nullable=False)
    
    # Revert br_gndiv back to NOT NULL
    op.alter_column('bhikku_regist', 'br_gndiv',
                    existing_type=sa.String(10),
                    nullable=False)
