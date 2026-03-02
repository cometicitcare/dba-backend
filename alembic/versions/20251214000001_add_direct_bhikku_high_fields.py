"""add direct bhikku high fields

Revision ID: 20251214000001
Revises: 20251205000001
Create Date: 2025-12-14 00:00:01
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20251214000001"
down_revision: Union[str, None] = "ec9be833d776"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add new fields to direct_bhikku_high table"""
    # Add form_id field
    op.add_column('direct_bhikku_high', sa.Column('dbh_form_id', sa.String(length=50), nullable=True))
    
    # Add remarks_upasampada field (for higher ordination remarks)
    op.add_column('direct_bhikku_high', sa.Column('dbh_remarks_upasampada', sa.String(length=500), nullable=True))
    
    # Add index for form_id
    op.create_index('ix_direct_bhikku_high_dbh_form_id', 'direct_bhikku_high', ['dbh_form_id'])


def downgrade() -> None:
    """Remove added fields from direct_bhikku_high table"""
    op.drop_index('ix_direct_bhikku_high_dbh_form_id', 'direct_bhikku_high')
    op.drop_column('direct_bhikku_high', 'dbh_remarks_upasampada')
    op.drop_column('direct_bhikku_high', 'dbh_form_id')
