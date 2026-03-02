"""add location based access control

Revision ID: 20251116000001
Revises: 8e0106445d04
Create Date: 2025-11-16 00:00:01.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20251116000001'
down_revision: Union[str, None] = '8e0106445d04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum type for user location type
    user_location_type = postgresql.ENUM('MAIN_BRANCH', 'PROVINCE_BRANCH', 'DISTRICT_BRANCH', name='userlocationtype')
    user_location_type.create(op.get_bind())
    
    # Create main_branches table
    op.create_table(
        'main_branches',
        sa.Column('mb_id', sa.Integer(), nullable=False),
        sa.Column('mb_code', sa.String(length=10), nullable=False),
        sa.Column('mb_name', sa.String(length=200), nullable=False),
        sa.Column('mb_description', sa.String(length=500), nullable=True),
        sa.Column('mb_is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('mb_created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('mb_updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('mb_created_by', sa.String(length=25), nullable=True),
        sa.Column('mb_updated_by', sa.String(length=25), nullable=True),
        sa.Column('mb_version_number', sa.Integer(), server_default='1', nullable=False),
        sa.PrimaryKeyConstraint('mb_id')
    )
    op.create_index(op.f('ix_main_branches_mb_id'), 'main_branches', ['mb_id'], unique=False)
    op.create_index(op.f('ix_main_branches_mb_code'), 'main_branches', ['mb_code'], unique=True)
    
    # Create province_branches table
    op.create_table(
        'province_branches',
        sa.Column('pb_id', sa.Integer(), nullable=False),
        sa.Column('pb_code', sa.String(length=10), nullable=False),
        sa.Column('pb_name', sa.String(length=200), nullable=False),
        sa.Column('pb_description', sa.String(length=500), nullable=True),
        sa.Column('pb_main_branch_id', sa.Integer(), nullable=False),
        sa.Column('pb_province_code', sa.String(length=10), nullable=True),
        sa.Column('pb_is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('pb_created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('pb_updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('pb_created_by', sa.String(length=25), nullable=True),
        sa.Column('pb_updated_by', sa.String(length=25), nullable=True),
        sa.Column('pb_version_number', sa.Integer(), server_default='1', nullable=False),
        sa.ForeignKeyConstraint(['pb_main_branch_id'], ['main_branches.mb_id'], ),
        sa.PrimaryKeyConstraint('pb_id')
    )
    op.create_index(op.f('ix_province_branches_pb_id'), 'province_branches', ['pb_id'], unique=False)
    op.create_index(op.f('ix_province_branches_pb_code'), 'province_branches', ['pb_code'], unique=True)
    op.create_index(op.f('ix_province_branches_pb_main_branch_id'), 'province_branches', ['pb_main_branch_id'], unique=False)
    op.create_index(op.f('ix_province_branches_pb_province_code'), 'province_branches', ['pb_province_code'], unique=False)
    
    # Create district_branches table
    op.create_table(
        'district_branches',
        sa.Column('db_id', sa.Integer(), nullable=False),
        sa.Column('db_code', sa.String(length=10), nullable=False),
        sa.Column('db_name', sa.String(length=200), nullable=False),
        sa.Column('db_description', sa.String(length=500), nullable=True),
        sa.Column('db_province_branch_id', sa.Integer(), nullable=False),
        sa.Column('db_district_code', sa.String(length=10), nullable=True),
        sa.Column('db_is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('db_created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('db_updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('db_created_by', sa.String(length=25), nullable=True),
        sa.Column('db_updated_by', sa.String(length=25), nullable=True),
        sa.Column('db_version_number', sa.Integer(), server_default='1', nullable=False),
        sa.ForeignKeyConstraint(['db_province_branch_id'], ['province_branches.pb_id'], ),
        sa.PrimaryKeyConstraint('db_id')
    )
    op.create_index(op.f('ix_district_branches_db_id'), 'district_branches', ['db_id'], unique=False)
    op.create_index(op.f('ix_district_branches_db_code'), 'district_branches', ['db_code'], unique=True)
    op.create_index(op.f('ix_district_branches_db_province_branch_id'), 'district_branches', ['db_province_branch_id'], unique=False)
    op.create_index(op.f('ix_district_branches_db_district_code'), 'district_branches', ['db_district_code'], unique=False)
    
    # Add location columns to user_accounts table
    op.add_column('user_accounts', sa.Column('ua_location_type', user_location_type, nullable=True))
    op.add_column('user_accounts', sa.Column('ua_main_branch_id', sa.Integer(), nullable=True))
    op.add_column('user_accounts', sa.Column('ua_province_branch_id', sa.Integer(), nullable=True))
    op.add_column('user_accounts', sa.Column('ua_district_branch_id', sa.Integer(), nullable=True))
    
    # Create indexes on user_accounts location columns
    op.create_index(op.f('ix_user_accounts_ua_location_type'), 'user_accounts', ['ua_location_type'], unique=False)
    op.create_index(op.f('ix_user_accounts_ua_main_branch_id'), 'user_accounts', ['ua_main_branch_id'], unique=False)
    op.create_index(op.f('ix_user_accounts_ua_province_branch_id'), 'user_accounts', ['ua_province_branch_id'], unique=False)
    op.create_index(op.f('ix_user_accounts_ua_district_branch_id'), 'user_accounts', ['ua_district_branch_id'], unique=False)
    
    # Create foreign key constraints on user_accounts
    op.create_foreign_key('fk_user_accounts_main_branch', 'user_accounts', 'main_branches', ['ua_main_branch_id'], ['mb_id'])
    op.create_foreign_key('fk_user_accounts_province_branch', 'user_accounts', 'province_branches', ['ua_province_branch_id'], ['pb_id'])
    op.create_foreign_key('fk_user_accounts_district_branch', 'user_accounts', 'district_branches', ['ua_district_branch_id'], ['db_id'])


def downgrade() -> None:
    # Drop foreign key constraints from user_accounts
    op.drop_constraint('fk_user_accounts_district_branch', 'user_accounts', type_='foreignkey')
    op.drop_constraint('fk_user_accounts_province_branch', 'user_accounts', type_='foreignkey')
    op.drop_constraint('fk_user_accounts_main_branch', 'user_accounts', type_='foreignkey')
    
    # Drop indexes from user_accounts
    op.drop_index(op.f('ix_user_accounts_ua_district_branch_id'), table_name='user_accounts')
    op.drop_index(op.f('ix_user_accounts_ua_province_branch_id'), table_name='user_accounts')
    op.drop_index(op.f('ix_user_accounts_ua_main_branch_id'), table_name='user_accounts')
    op.drop_index(op.f('ix_user_accounts_ua_location_type'), table_name='user_accounts')
    
    # Drop location columns from user_accounts
    op.drop_column('user_accounts', 'ua_district_branch_id')
    op.drop_column('user_accounts', 'ua_province_branch_id')
    op.drop_column('user_accounts', 'ua_main_branch_id')
    op.drop_column('user_accounts', 'ua_location_type')
    
    # Drop district_branches table
    op.drop_index(op.f('ix_district_branches_db_district_code'), table_name='district_branches')
    op.drop_index(op.f('ix_district_branches_db_province_branch_id'), table_name='district_branches')
    op.drop_index(op.f('ix_district_branches_db_code'), table_name='district_branches')
    op.drop_index(op.f('ix_district_branches_db_id'), table_name='district_branches')
    op.drop_table('district_branches')
    
    # Drop province_branches table
    op.drop_index(op.f('ix_province_branches_pb_province_code'), table_name='province_branches')
    op.drop_index(op.f('ix_province_branches_pb_main_branch_id'), table_name='province_branches')
    op.drop_index(op.f('ix_province_branches_pb_code'), table_name='province_branches')
    op.drop_index(op.f('ix_province_branches_pb_id'), table_name='province_branches')
    op.drop_table('province_branches')
    
    # Drop main_branches table
    op.drop_index(op.f('ix_main_branches_mb_code'), table_name='main_branches')
    op.drop_index(op.f('ix_main_branches_mb_id'), table_name='main_branches')
    op.drop_table('main_branches')
    
    # Drop enum type
    user_location_type = postgresql.ENUM('MAIN_BRANCH', 'PROVINCE_BRANCH', 'DISTRICT_BRANCH', name='userlocationtype')
    user_location_type.drop(op.get_bind())
