"""create_cmm_gov_officers

Revision ID: 20260228000001
Revises: 20260226000001
Create Date: 2026-02-28

Creates the cmm_gov_officers table for storing government officer contact information.
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '20260228000001'
down_revision = '20260226000001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'cmm_gov_officers',
        sa.Column('go_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('go_title', sa.String(length=100), nullable=False, comment='Title (e.g. Mr., Mrs., Dr.)'),
        sa.Column('go_first_name', sa.String(length=100), nullable=False, comment='First name'),
        sa.Column('go_last_name', sa.String(length=100), nullable=False, comment='Last name'),
        sa.Column('go_contact_number', sa.String(length=20), nullable=False, comment='Contact phone number'),
        sa.Column('go_email', sa.String(length=255), nullable=True, comment='Email address (optional)'),
        sa.Column('go_address', sa.String(length=500), nullable=False, comment='Address'),
        sa.Column('go_id_number', sa.String(length=50), nullable=True, comment='National ID / NIC number (optional)'),
        # audit columns
        sa.Column('go_is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('go_created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('go_updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('go_created_by', sa.String(length=100), nullable=True),
        sa.Column('go_updated_by', sa.String(length=100), nullable=True),
        sa.Column('go_version_number', sa.Integer(), server_default=sa.text('1'), nullable=False),
        sa.PrimaryKeyConstraint('go_id'),
    )
    op.create_index(
        op.f('ix_cmm_gov_officers_go_id'),
        'cmm_gov_officers',
        ['go_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_cmm_gov_officers_go_id'), table_name='cmm_gov_officers')
    op.drop_table('cmm_gov_officers')
