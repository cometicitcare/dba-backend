"""make_bhikku_high_fields_nullable

Revision ID: 20251121000002
Revises: 20251121000001
Create Date: 2025-11-21 00:00:02.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20251121000002'
down_revision: Union[str, None] = '20251121000001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Make fields nullable in bhikku_high_regist table"""
    
    # Make bhr_reqstdate nullable
    op.alter_column('bhikku_high_regist', 'bhr_reqstdate',
                    existing_type=sa.Date(),
                    nullable=True)
    
    # Make bhr_currstat nullable
    op.alter_column('bhikku_high_regist', 'bhr_currstat',
                    existing_type=sa.String(5),
                    nullable=True)
    
    # Make bhr_parshawaya nullable
    op.alter_column('bhikku_high_regist', 'bhr_parshawaya',
                    existing_type=sa.String(10),
                    nullable=True)
    
    # Make bhr_livtemple nullable
    op.alter_column('bhikku_high_regist', 'bhr_livtemple',
                    existing_type=sa.String(10),
                    nullable=True)


def downgrade() -> None:
    """Revert fields to NOT NULL in bhikku_high_regist table"""
    
    # Make bhr_livtemple NOT NULL
    op.alter_column('bhikku_high_regist', 'bhr_livtemple',
                    existing_type=sa.String(10),
                    nullable=False)
    
    # Make bhr_parshawaya NOT NULL
    op.alter_column('bhikku_high_regist', 'bhr_parshawaya',
                    existing_type=sa.String(10),
                    nullable=False)
    
    # Make bhr_currstat NOT NULL
    op.alter_column('bhikku_high_regist', 'bhr_currstat',
                    existing_type=sa.String(5),
                    nullable=False)
    
    # Make bhr_reqstdate NOT NULL
    op.alter_column('bhikku_high_regist', 'bhr_reqstdate',
                    existing_type=sa.Date(),
                    nullable=False)
