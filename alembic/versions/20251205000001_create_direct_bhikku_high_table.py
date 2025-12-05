"""create direct_bhikku_high table

Revision ID: 20251205000001
Revises: 20251204000002
Create Date: 2025-12-05 00:00:01
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20251205000001"
down_revision: Union[str, None] = "20251204000002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create direct_bhikku_high table combining bhikku_regist and bhikku_high_regist fields"""
    op.create_table(
        'direct_bhikku_high',
        # Primary Key
        sa.Column('dbh_id', sa.Integer(), nullable=False),
        sa.Column('dbh_regn', sa.String(length=20), nullable=False),
        sa.Column('dbh_reqstdate', sa.Date(), nullable=False),
        
        # ==================== BHIKKU REGIST FIELDS ====================
        # Geographic/Birth Information
        sa.Column('dbh_birthpls', sa.String(length=50), nullable=True),
        sa.Column('dbh_province', sa.String(length=50), nullable=True),
        sa.Column('dbh_district', sa.String(length=50), nullable=True),
        sa.Column('dbh_korale', sa.String(length=50), nullable=True),
        sa.Column('dbh_pattu', sa.String(length=50), nullable=True),
        sa.Column('dbh_division', sa.String(length=50), nullable=True),
        sa.Column('dbh_vilage', sa.String(length=50), nullable=True),
        sa.Column('dbh_gndiv', sa.String(length=10), nullable=True),
        
        # Personal Information
        sa.Column('dbh_gihiname', sa.String(length=50), nullable=True),
        sa.Column('dbh_dofb', sa.Date(), nullable=True),
        sa.Column('dbh_fathrname', sa.String(length=50), nullable=True),
        sa.Column('dbh_remarks', sa.String(length=100), nullable=True),
        
        # Status Information
        sa.Column('dbh_currstat', sa.String(length=5), nullable=False),
        sa.Column('dbh_effctdate', sa.Date(), nullable=True),
        
        # Temple/Religious Information
        sa.Column('dbh_parshawaya', sa.String(length=10), nullable=False),
        sa.Column('dbh_livtemple', sa.String(length=10), nullable=True),
        sa.Column('dbh_mahanatemple', sa.String(length=10), nullable=True),
        sa.Column('dbh_mahanaacharyacd', sa.String(length=12), nullable=True),
        sa.Column('dbh_multi_mahanaacharyacd', sa.String(length=200), nullable=True),
        sa.Column('dbh_mahananame', sa.String(length=50), nullable=True),
        sa.Column('dbh_mahanadate', sa.Date(), nullable=True),
        sa.Column('dbh_cat', sa.String(length=5), nullable=True),
        
        # Additional Religious/Administrative Fields
        sa.Column('dbh_viharadhipathi', sa.String(length=20), nullable=True),
        sa.Column('dbh_nikaya', sa.String(length=10), nullable=True),
        sa.Column('dbh_mahanayaka_name', sa.String(length=200), nullable=True),
        sa.Column('dbh_mahanayaka_address', sa.String(length=500), nullable=True),
        sa.Column('dbh_residence_at_declaration', sa.String(length=500), nullable=True),
        sa.Column('dbh_declaration_date', sa.Date(), nullable=True),
        sa.Column('dbh_robing_tutor_residence', sa.String(length=20), nullable=True),
        sa.Column('dbh_robing_after_residence_temple', sa.String(length=20), nullable=True),
        
        # Contact Information
        sa.Column('dbh_mobile', sa.String(length=10), nullable=True),
        sa.Column('dbh_email', sa.String(length=50), nullable=True),
        sa.Column('dbh_fathrsaddrs', sa.String(length=200), nullable=True),
        sa.Column('dbh_fathrsmobile', sa.String(length=10), nullable=True),
        
        # Serial Number
        sa.Column('dbh_upasampada_serial_no', sa.String(length=20), nullable=True),
        
        # ==================== BHIKKU HIGH REGIST FIELDS ====================
        # High Bhikku Specific Fields
        sa.Column('dbh_samanera_serial_no', sa.String(length=20), nullable=True),
        sa.Column('dbh_cc_code', sa.String(length=5), nullable=True),
        sa.Column('dbh_higher_ordination_place', sa.String(length=50), nullable=True),
        sa.Column('dbh_higher_ordination_date', sa.Date(), nullable=True),
        sa.Column('dbh_karmacharya_name', sa.String(length=12), nullable=True),
        sa.Column('dbh_upaddhyaya_name', sa.String(length=12), nullable=True),
        sa.Column('dbh_assumed_name', sa.String(length=50), nullable=True),
        sa.Column('dbh_residence_higher_ordination_trn', sa.String(length=50), nullable=True),
        sa.Column('dbh_residence_permanent_trn', sa.String(length=50), nullable=True),
        sa.Column('dbh_declaration_residence_address', sa.String(length=200), nullable=True),
        sa.Column('dbh_tutors_tutor_regn', sa.String(length=200), nullable=True),
        sa.Column('dbh_presiding_bhikshu_regn', sa.String(length=200), nullable=True),
        
        # ==================== WORKFLOW FIELDS ====================
        # Document Storage
        sa.Column('dbh_scanned_document_path', sa.String(length=500), nullable=True),
        
        # Workflow Status
        sa.Column('dbh_workflow_status', sa.String(length=20), server_default=sa.text("'PENDING'"), nullable=False),
        sa.Column('dbh_approval_status', sa.String(length=20), nullable=True),
        
        # Approval Tracking
        sa.Column('dbh_approved_by', sa.String(length=25), nullable=True),
        sa.Column('dbh_approved_at', sa.TIMESTAMP(), nullable=True),
        
        # Rejection Tracking
        sa.Column('dbh_rejected_by', sa.String(length=25), nullable=True),
        sa.Column('dbh_rejected_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('dbh_rejection_reason', sa.String(length=500), nullable=True),
        
        # Printing Tracking
        sa.Column('dbh_printed_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('dbh_printed_by', sa.String(length=25), nullable=True),
        
        # Scanning Tracking
        sa.Column('dbh_scanned_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('dbh_scanned_by', sa.String(length=25), nullable=True),
        
        # ==================== AUDIT FIELDS ====================
        sa.Column('dbh_version', sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False),
        sa.Column('dbh_is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=True),
        sa.Column('dbh_created_at', sa.TIMESTAMP(), server_default=sa.func.now(), nullable=True),
        sa.Column('dbh_updated_at', sa.TIMESTAMP(), server_default=sa.func.now(), nullable=True),
        sa.Column('dbh_created_by', sa.String(length=25), nullable=True),
        sa.Column('dbh_updated_by', sa.String(length=25), nullable=True),
        sa.Column('dbh_version_number', sa.Integer(), server_default=sa.text('1'), nullable=True),
        
        # Location-based access control
        sa.Column('dbh_created_by_district', sa.String(length=10), nullable=True),
        
        # Constraints
        sa.PrimaryKeyConstraint('dbh_id'),
        sa.UniqueConstraint('dbh_regn')
    )
    
    # Create indexes for better query performance
    op.create_index('ix_direct_bhikku_high_dbh_id', 'direct_bhikku_high', ['dbh_id'])
    op.create_index('ix_direct_bhikku_high_dbh_regn', 'direct_bhikku_high', ['dbh_regn'], unique=True)
    op.create_index('ix_direct_bhikku_high_dbh_workflow_status', 'direct_bhikku_high', ['dbh_workflow_status'])
    op.create_index('ix_direct_bhikku_high_dbh_created_by_district', 'direct_bhikku_high', ['dbh_created_by_district'])
    
    # Create sequence for ID generation
    op.execute("""
        CREATE SEQUENCE IF NOT EXISTS direct_bhikku_high_dbh_id_seq
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE
        CACHE 1;
    """)
    
    # Set sequence ownership
    op.execute("""
        ALTER SEQUENCE direct_bhikku_high_dbh_id_seq OWNED BY direct_bhikku_high.dbh_id;
    """)
    
    # Set default value for dbh_id
    op.execute("""
        ALTER TABLE direct_bhikku_high 
        ALTER COLUMN dbh_id SET DEFAULT nextval('direct_bhikku_high_dbh_id_seq'::regclass);
    """)


def downgrade() -> None:
    """Drop direct_bhikku_high table and related objects"""
    # Drop indexes
    op.drop_index('ix_direct_bhikku_high_dbh_created_by_district', 'direct_bhikku_high')
    op.drop_index('ix_direct_bhikku_high_dbh_workflow_status', 'direct_bhikku_high')
    op.drop_index('ix_direct_bhikku_high_dbh_regn', 'direct_bhikku_high')
    op.drop_index('ix_direct_bhikku_high_dbh_id', 'direct_bhikku_high')
    
    # Drop table
    op.drop_table('direct_bhikku_high')
    
    # Drop sequence
    op.execute("DROP SEQUENCE IF EXISTS direct_bhikku_high_dbh_id_seq;")
