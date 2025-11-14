"""enhanced_rbac_structure_with_temporal_access

Revision ID: a4090ddd5179
Revises: 8b0c7f02d60c
Create Date: 2025-11-14 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a4090ddd5179'
down_revision = '8b0c7f02d60c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop old RBAC tables if they exist (fresh start as per client request)
    op.execute("DROP TABLE IF EXISTS user_permissions CASCADE")
    op.execute("DROP TABLE IF EXISTS role_permissions CASCADE")
    op.execute("DROP TABLE IF EXISTS user_roles CASCADE")
    op.execute("DROP TABLE IF EXISTS user_groups CASCADE")
    op.execute("DROP TABLE IF EXISTS permissions CASCADE")
    op.execute("DROP TABLE IF EXISTS roles CASCADE")
    op.execute("DROP TABLE IF EXISTS groups CASCADE")
    op.execute("DROP TABLE IF EXISTS user_accounts CASCADE")
    op.execute("DROP TABLE IF EXISTS login_history CASCADE")
    
    # Create Groups table (Departments)
    op.create_table(
        'groups',
        sa.Column('group_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('group_name', sa.String(length=100), nullable=False),
        sa.Column('group_type', sa.String(length=50), nullable=False),
        sa.Column('group_description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_by', sa.String(length=50), nullable=True),
        sa.Column('updated_by', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('group_id')
    )
    op.create_index('ix_groups_name', 'groups', ['group_name'], unique=True)
    op.create_index('ix_groups_type', 'groups', ['group_type'])
    op.create_index('ix_groups_active', 'groups', ['is_active'])
    
    # Create Roles table
    op.create_table(
        'roles',
        sa.Column('ro_role_id', sa.String(length=10), nullable=False),
        sa.Column('ro_role_name', sa.String(length=50), nullable=False),
        sa.Column('ro_description', sa.String(length=200), nullable=True),
        sa.Column('ro_level', sa.String(length=20), server_default='DATA_ENTRY', nullable=False),
        sa.Column('ro_department_id', sa.Integer(), nullable=True),
        sa.Column('ro_is_system_role', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('ro_is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.PrimaryKeyConstraint('ro_role_id'),
        sa.ForeignKeyConstraint(['ro_department_id'], ['groups.group_id'], ondelete='SET NULL'),
    )
    op.create_index('ix_roles_role_name', 'roles', ['ro_role_name'], unique=True)
    op.create_index('ix_roles_department', 'roles', ['ro_department_id'])
    op.create_index('ix_roles_level', 'roles', ['ro_level'])
    
    # Create Permissions table
    op.create_table(
        'permissions',
        sa.Column('pe_permission_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('pe_name', sa.String(length=100), nullable=False),
        sa.Column('pe_resource', sa.String(length=50), nullable=False),
        sa.Column('pe_action', sa.String(length=50), nullable=False),
        sa.Column('pe_description', sa.Text(), nullable=True),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('pe_created_by', sa.String(length=50), nullable=True),
        sa.Column('pe_updated_by', sa.String(length=50), nullable=True),
        sa.Column('pe_created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('pe_updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('pe_permission_id'),
        sa.ForeignKeyConstraint(['group_id'], ['groups.group_id'], ondelete='CASCADE'),
    )
    op.create_index('ix_permissions_name', 'permissions', ['pe_name'], unique=True)
    op.create_index('ix_permissions_resource_action', 'permissions', ['pe_resource', 'pe_action'])
    
    # Create UserAccount table
    op.create_table(
        'user_accounts',
        sa.Column('ua_user_id', sa.String(length=10), nullable=False),
        sa.Column('ua_username', sa.String(length=50), nullable=False),
        sa.Column('ua_email', sa.String(length=100), nullable=False),
        sa.Column('ua_password_hash', sa.String(length=255), nullable=False),
        sa.Column('ua_salt', sa.String(length=100), nullable=False),
        sa.Column('ua_first_name', sa.String(length=50), nullable=True),
        sa.Column('ua_last_name', sa.String(length=50), nullable=True),
        sa.Column('ua_phone', sa.String(length=15), nullable=True),
        sa.Column('ua_status', sa.String(length=20), server_default='active', nullable=True),
        sa.Column('ua_last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ua_login_attempts', sa.Integer(), server_default='0', nullable=False),
        sa.Column('ua_locked_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ua_password_expires', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ua_must_change_password', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('ua_two_factor_enabled', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('ua_two_factor_secret', sa.String(length=100), nullable=True),
        sa.Column('ua_is_deleted', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('ua_created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('ua_updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('ua_created_by', sa.String(length=50), nullable=True),
        sa.Column('ua_updated_by', sa.String(length=50), nullable=True),
        sa.Column('ua_version_number', sa.Integer(), server_default='1', nullable=False),
        sa.PrimaryKeyConstraint('ua_user_id')
    )
    op.create_index('ix_user_accounts_username', 'user_accounts', ['ua_username'], unique=True)
    op.create_index('ix_user_accounts_email', 'user_accounts', ['ua_email'], unique=True)
    op.create_index('ix_user_accounts_status', 'user_accounts', ['ua_status'])
    
    # Create UserRole table (many-to-many with temporal)
    op.create_table(
        'user_roles',
        sa.Column('ur_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('ur_user_id', sa.String(length=10), nullable=False),
        sa.Column('ur_role_id', sa.String(length=10), nullable=False),
        sa.Column('ur_assigned_date', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('ur_expires_date', sa.TIMESTAMP(), nullable=True),
        sa.Column('ur_is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('ur_assigned_by', sa.String(length=10), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('ur_id'),
        sa.ForeignKeyConstraint(['ur_user_id'], ['user_accounts.ua_user_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ur_role_id'], ['roles.ro_role_id'], ondelete='CASCADE'),
    )
    op.create_index('ix_user_roles_user_role', 'user_roles', ['ur_user_id', 'ur_role_id'], unique=True)
    op.create_index('ix_user_roles_user_id', 'user_roles', ['ur_user_id'])
    op.create_index('ix_user_roles_role_id', 'user_roles', ['ur_role_id'])
    op.create_index('ix_user_roles_active', 'user_roles', ['ur_is_active'])
    op.create_index('ix_user_roles_expires', 'user_roles', ['ur_expires_date'])
    
    # Create UserGroup table (many-to-many with temporal)
    op.create_table(
        'user_groups',
        sa.Column('ug_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.String(length=10), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('assigned_date', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_date', sa.TIMESTAMP(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('assigned_by', sa.String(length=10), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('ug_id'),
        sa.ForeignKeyConstraint(['user_id'], ['user_accounts.ua_user_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['group_id'], ['groups.group_id'], ondelete='CASCADE'),
    )
    op.create_index('ix_user_groups_user_group', 'user_groups', ['user_id', 'group_id'], unique=True)
    op.create_index('ix_user_groups_user_id', 'user_groups', ['user_id'])
    op.create_index('ix_user_groups_group_id', 'user_groups', ['group_id'])
    op.create_index('ix_user_groups_active', 'user_groups', ['is_active'])
    op.create_index('ix_user_groups_expires', 'user_groups', ['expires_date'])
    
    # Create RolePermission table
    op.create_table(
        'role_permissions',
        sa.Column('rp_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('rp_role_id', sa.String(length=10), nullable=False),
        sa.Column('rp_permission_id', sa.Integer(), nullable=False),
        sa.Column('rp_granted', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('rp_id'),
        sa.ForeignKeyConstraint(['rp_role_id'], ['roles.ro_role_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['rp_permission_id'], ['permissions.pe_permission_id'], ondelete='CASCADE'),
    )
    op.create_index('ix_role_permissions_role_perm', 'role_permissions', ['rp_role_id', 'rp_permission_id'], unique=True)
    op.create_index('ix_role_permissions_role_id', 'role_permissions', ['rp_role_id'])
    op.create_index('ix_role_permissions_permission_id', 'role_permissions', ['rp_permission_id'])
    
    # Create UserPermission table (NEW - user-level overrides)
    op.create_table(
        'user_permissions',
        sa.Column('up_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('up_user_id', sa.String(length=10), nullable=False),
        sa.Column('up_permission_id', sa.Integer(), nullable=False),
        sa.Column('up_granted', sa.Boolean(), nullable=False),
        sa.Column('up_assigned_date', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('up_expires_date', sa.TIMESTAMP(), nullable=True),
        sa.Column('up_is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('up_assigned_by', sa.String(length=10), nullable=True),
        sa.Column('up_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('up_id'),
        sa.ForeignKeyConstraint(['up_user_id'], ['user_accounts.ua_user_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['up_permission_id'], ['permissions.pe_permission_id'], ondelete='CASCADE'),
    )
    op.create_index('ix_user_permissions_user_perm', 'user_permissions', ['up_user_id', 'up_permission_id'], unique=True)
    op.create_index('ix_user_permissions_user_id', 'user_permissions', ['up_user_id'])
    op.create_index('ix_user_permissions_permission_id', 'user_permissions', ['up_permission_id'])
    op.create_index('ix_user_permissions_active', 'user_permissions', ['up_is_active'])
    op.create_index('ix_user_permissions_expires', 'user_permissions', ['up_expires_date'])
    
    # Create LoginHistory table
    op.create_table(
        'login_history',
        sa.Column('lh_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('lh_user_id', sa.String(length=20), nullable=False),
        sa.Column('lh_session_id', sa.String(length=255), nullable=False),
        sa.Column('lh_ip_address', sa.String(length=50), nullable=True),
        sa.Column('lh_user_agent', sa.Text(), nullable=True),
        sa.Column('lh_login_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('lh_logout_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('lh_success', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('lh_id'),
        sa.ForeignKeyConstraint(['lh_user_id'], ['user_accounts.ua_user_id'], ondelete='CASCADE'),
    )
    op.create_index('ix_login_history_user_id', 'login_history', ['lh_user_id'])
    op.create_index('ix_login_history_session_id', 'login_history', ['lh_session_id'], unique=True)
    

def downgrade() -> None:
    # Drop all RBAC tables in reverse order
    op.drop_table('login_history')
    op.drop_table('user_permissions')
    op.drop_table('role_permissions')
    op.drop_table('user_groups')
    op.drop_table('user_roles')
    op.drop_table('user_accounts')
    op.drop_table('permissions')
    op.drop_table('roles')
    op.drop_table('groups')
