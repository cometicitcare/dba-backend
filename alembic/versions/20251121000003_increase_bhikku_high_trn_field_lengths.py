"""increase_bhikku_high_trn_field_lengths

Revision ID: 20251121000003
Revises: 20251121000002
Create Date: 2025-11-21 00:00:03.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20251121000003'
down_revision: Union[str, None] = '20251121000002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Increase field lengths for temple reference numbers in bhikku_high_regist table"""
    
    # Increase bhr_higher_ordination_place from 10 to 50
    op.alter_column('bhikku_high_regist', 'bhr_higher_ordination_place',
                    existing_type=sa.String(10),
                    type_=sa.String(50),
                    existing_nullable=True)
    
    # Increase bhr_residence_higher_ordination_trn from 10 to 50
    op.alter_column('bhikku_high_regist', 'bhr_residence_higher_ordination_trn',
                    existing_type=sa.String(10),
                    type_=sa.String(50),
                    existing_nullable=True)
    
    # Increase bhr_residence_permanent_trn from 10 to 50
    op.alter_column('bhikku_high_regist', 'bhr_residence_permanent_trn',
                    existing_type=sa.String(10),
                    type_=sa.String(50),
                    existing_nullable=True)
    
    # Increase bhr_declaration_residence_address from 10 to 200
    op.alter_column('bhikku_high_regist', 'bhr_declaration_residence_address',
                    existing_type=sa.String(10),
                    type_=sa.String(200),
                    existing_nullable=True)


def downgrade() -> None:
    """Revert field lengths in bhikku_high_regist table"""
    
    # Revert bhr_declaration_residence_address
    op.alter_column('bhikku_high_regist', 'bhr_declaration_residence_address',
                    existing_type=sa.String(200),
                    type_=sa.String(10),
                    existing_nullable=True)
    
    # Revert bhr_residence_permanent_trn
    op.alter_column('bhikku_high_regist', 'bhr_residence_permanent_trn',
                    existing_type=sa.String(50),
                    type_=sa.String(10),
                    existing_nullable=True)
    
    # Revert bhr_residence_higher_ordination_trn
    op.alter_column('bhikku_high_regist', 'bhr_residence_higher_ordination_trn',
                    existing_type=sa.String(50),
                    type_=sa.String(10),
                    existing_nullable=True)
    
    # Revert bhr_higher_ordination_place
    op.alter_column('bhikku_high_regist', 'bhr_higher_ordination_place',
                    existing_type=sa.String(50),
                    type_=sa.String(10),
                    existing_nullable=True)
