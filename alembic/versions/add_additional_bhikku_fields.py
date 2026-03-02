"""add_additional_bhikku_fields

Revision ID: c6d9f5e3b2c2
Revises: b5c8e3f4d2a1
Create Date: 2025-11-15 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'c6d9f5e3b2c2'
down_revision = 'b5c8e3f4d2a1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add additional religious and administrative fields to bhikku_regist table"""
    
    # Check and add columns only if they don't exist
    conn = op.get_bind()
    
    # Helper function to check if column exists
    def column_exists(table_name, column_name):
        result = conn.execute(sa.text(
            f"SELECT column_name FROM information_schema.columns "
            f"WHERE table_name='{table_name}' AND column_name='{column_name}'"
        ))
        return result.fetchone() is not None
    
    # Add viharadhipathi field
    if not column_exists('bhikku_regist', 'br_viharadhipathi'):
        op.add_column('bhikku_regist', 
            sa.Column('br_viharadhipathi', sa.String(20), nullable=True)
        )
    
    # Add nikaya field
    if not column_exists('bhikku_regist', 'br_nikaya'):
        op.add_column('bhikku_regist', 
            sa.Column('br_nikaya', sa.String(10), nullable=True)
        )
    
    # Add mahanayaka name field (Sinhala/Tamil support)
    if not column_exists('bhikku_regist', 'br_mahanayaka_name'):
        op.add_column('bhikku_regist', 
            sa.Column('br_mahanayaka_name', sa.String(200), nullable=True)
        )
    
    # Add mahanayaka address field
    if not column_exists('bhikku_regist', 'br_mahanayaka_address'):
        op.add_column('bhikku_regist', 
            sa.Column('br_mahanayaka_address', sa.String(500), nullable=True)
        )
    
    # Add residence at declaration field
    if not column_exists('bhikku_regist', 'br_residence_at_declaration'):
        op.add_column('bhikku_regist', 
            sa.Column('br_residence_at_declaration', sa.String(500), nullable=True)
        )
    
    # Add declaration date field
    if not column_exists('bhikku_regist', 'br_declaration_date'):
        op.add_column('bhikku_regist', 
            sa.Column('br_declaration_date', sa.Date(), nullable=True)
        )
    
    # Add robing tutor residence field
    if not column_exists('bhikku_regist', 'br_robing_tutor_residence'):
        op.add_column('bhikku_regist', 
            sa.Column('br_robing_tutor_residence', sa.String(20), nullable=True)
        )
    
    # Add robing after residence temple field
    if not column_exists('bhikku_regist', 'br_robing_after_residence_temple'):
        op.add_column('bhikku_regist', 
            sa.Column('br_robing_after_residence_temple', sa.String(20), nullable=True)
        )


def downgrade() -> None:
    """Remove additional religious and administrative fields from bhikku_regist table"""
    
    op.drop_column('bhikku_regist', 'br_robing_after_residence_temple')
    op.drop_column('bhikku_regist', 'br_robing_tutor_residence')
    op.drop_column('bhikku_regist', 'br_declaration_date')
    op.drop_column('bhikku_regist', 'br_residence_at_declaration')
    op.drop_column('bhikku_regist', 'br_mahanayaka_address')
    op.drop_column('bhikku_regist', 'br_mahanayaka_name')
    op.drop_column('bhikku_regist', 'br_nikaya')
    op.drop_column('bhikku_regist', 'br_viharadhipathi')
