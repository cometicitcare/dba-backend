"""Add bikkudtls_mahanayakalist view.

Revision ID: 8b0c7f02d60c
Revises: 
Create Date: 2024-10-07 00:00:00.000000
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "8b0c7f02d60c"
down_revision = "202410101300"
branch_labels = None
depends_on = None


VIEW_NAME = "bikkudtls_mahanayakalist"

VIEW_SQL = f"""
CREATE OR REPLACE VIEW {VIEW_NAME} AS
SELECT
    br.br_regn AS regn,
    br.br_mahananame AS mahananame,
    br.br_currstat AS currstat,
    vd.vh_vname AS vname,
    vd.vh_addrs AS addrs
FROM bhikku_regist br
JOIN vihaddata vd ON br.br_livtemple::text = vd.vh_trn::text
WHERE br.br_currstat::text = 'ST01'::text
  AND br.br_is_deleted = FALSE
  AND vd.vh_is_deleted = FALSE;
"""


def upgrade() -> None:
    op.execute(VIEW_SQL)


def downgrade() -> None:
    op.execute(f"DROP VIEW IF EXISTS {VIEW_NAME};")
