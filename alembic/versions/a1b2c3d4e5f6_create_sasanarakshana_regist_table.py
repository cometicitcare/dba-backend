"""create sasanarakshana_regist table

Revision ID: a1b2c3d4e5f6
Revises: fdb5dc86afe3
Create Date: 2026-02-18 00:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '20260209000001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the cmm_sasanarakshana_regist table."""
    conn = op.get_bind()
    table_exists = conn.execute(text(
        "SELECT 1 FROM information_schema.tables "
        "WHERE table_name='sasanarakshana_regist'"
    )).fetchone()

    if table_exists:
        return

    op.create_table(
        'sasanarakshana_regist',
        sa.Column('sar_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('sar_temple_name', sa.String(255), nullable=False, comment='Temple Name'),
        sa.Column('sar_temple_address', sa.String(500), nullable=True, comment='Temple Address'),
        sa.Column('sar_mandala_name', sa.String(255), nullable=True, comment='Mandala Name'),
        sa.Column('sar_bank_name', sa.String(255), nullable=True, comment='Bank Name'),
        sa.Column('sar_account_number', sa.String(100), nullable=True, comment='Bank Account Number'),
        sa.Column('sar_president_name', sa.String(255), nullable=True, comment='President Name'),
        sa.Column('sar_deputy_president_name', sa.String(255), nullable=True, comment='Deputy President Name'),
        sa.Column('sar_vice_president_1_name', sa.String(255), nullable=True, comment='Vice President 1 Name'),
        sa.Column('sar_vice_president_2_name', sa.String(255), nullable=True, comment='Vice President 2 Name'),
        sa.Column('sar_general_secretary_name', sa.String(255), nullable=True, comment='General Secretary Name'),
        sa.Column('sar_deputy_secretary_name', sa.String(255), nullable=True, comment='Deputy Secretary Name'),
        sa.Column('sar_treasurer_name', sa.String(255), nullable=True, comment='Treasurer Name'),
        sa.Column('sar_committee_member_1', sa.String(255), nullable=True, comment='Committee Member 1'),
        sa.Column('sar_committee_member_2', sa.String(255), nullable=True, comment='Committee Member 2'),
        sa.Column('sar_committee_member_3', sa.String(255), nullable=True, comment='Committee Member 3'),
        sa.Column('sar_committee_member_4', sa.String(255), nullable=True, comment='Committee Member 4'),
        sa.Column('sar_committee_member_5', sa.String(255), nullable=True, comment='Committee Member 5'),
        sa.Column('sar_committee_member_6', sa.String(255), nullable=True, comment='Committee Member 6'),
        sa.Column('sar_committee_member_7', sa.String(255), nullable=True, comment='Committee Member 7'),
        sa.Column('sar_committee_member_8', sa.String(255), nullable=True, comment='Committee Member 8'),
        sa.Column('sar_chief_organizer_name', sa.String(255), nullable=True, comment='Chief Organizer Name'),
        sa.Column('sar_is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=True, comment='Soft delete flag'),
        sa.Column('sar_created_at', sa.TIMESTAMP(), server_default=sa.func.now(), nullable=True, comment='Creation timestamp'),
        sa.Column('sar_updated_at', sa.TIMESTAMP(), server_default=sa.func.now(), nullable=True, comment='Last update timestamp'),
        sa.Column('sar_created_by', sa.String(25), nullable=True, comment='User who created the record'),
        sa.Column('sar_updated_by', sa.String(25), nullable=True, comment='User who last updated the record'),
        sa.Column('sar_version_number', sa.Integer(), server_default=sa.text('1'), nullable=True, comment='Version number for optimistic locking'),
        sa.PrimaryKeyConstraint('sar_id'),
    )
    op.create_index('ix_sasanarakshana_regist_sar_id', 'sasanarakshana_regist', ['sar_id'], unique=False)


def downgrade() -> None:
    """Drop the cmm_sasanarakshana_regist table."""
    op.drop_index('ix_sasanarakshana_regist_sar_id', table_name='sasanarakshana_regist')
    op.drop_table('sasanarakshana_regist')
