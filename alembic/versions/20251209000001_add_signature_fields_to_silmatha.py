"""add signature fields to silmatha_regist

Revision ID: 20251209000001
Revises: 20251208000001
Create Date: 2025-12-09 00:00:01

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251209000001'
down_revision = '20251208000001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add signature boolean fields to silmatha_regist table"""
    # Add signature fields as boolean (true/false)
    op.add_column('silmatha_regist', sa.Column('sil_student_signature', sa.Boolean(), nullable=True, comment='ශිෂ්‍ය මෑණියන් වහන්සේගේ අත්සන'))
    op.add_column('silmatha_regist', sa.Column('sil_acharya_signature', sa.Boolean(), nullable=True, comment='ආචාර්ය මෑණියන් වහන්සේගේ අත්සන'))
    op.add_column('silmatha_regist', sa.Column('sil_aramadhipathi_signature', sa.Boolean(), nullable=True, comment='ආරාමාධිපති මෑණියන් වහන්සේගේ අත්සන'))
    op.add_column('silmatha_regist', sa.Column('sil_district_secretary_signature', sa.Boolean(), nullable=True, comment='දිස්ත්‍රික් සිල්මාතා සංගමයේ ලේකම් අත්සන'))


def downgrade() -> None:
    """Remove signature fields from silmatha_regist table"""
    op.drop_column('silmatha_regist', 'sil_district_secretary_signature')
    op.drop_column('silmatha_regist', 'sil_aramadhipathi_signature')
    op.drop_column('silmatha_regist', 'sil_acharya_signature')
    op.drop_column('silmatha_regist', 'sil_student_signature')
