"""Use bhikku registration numbers for ID cards.

Revision ID: 1d61d5571d9f
Revises: add_id_card_workflow_02
Create Date: 2025-11-16 10:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = "1d61d5571d9f"
down_revision = "add_id_card_workflow_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()

    # Temporary column to store the textual registration number
    op.add_column(
        "bhikku_id_card",
        sa.Column("bic_regn_text", sa.String(length=20), nullable=True),
    )

    # Copy registration numbers using existing FK (br_id -> br_regn)
    bind.execute(
        text(
            """
            UPDATE bhikku_id_card AS bic
            SET bic_regn_text = br.br_regn
            FROM bhikku_regist AS br
            WHERE br.br_id = bic.bic_regn
            """
        )
    )

    # Remove duplicate cards, keeping the earliest record per bhikku
    bind.execute(
        text(
            """
            WITH ranked AS (
                SELECT bic_id,
                       ROW_NUMBER() OVER (PARTITION BY bic_br_id ORDER BY bic_id) AS rn
                FROM bhikku_id_card
            )
            DELETE FROM bhikku_id_card AS target
            USING ranked
            WHERE ranked.rn > 1 AND ranked.bic_id = target.bic_id
            """
        )
    )

    # Replace integer FK with string FK referencing br_regn
    op.execute(
        "ALTER TABLE bhikku_id_card DROP CONSTRAINT IF EXISTS fk_bhikku_id_card_regn"
    )
    op.execute(
        "ALTER TABLE bhikku_id_card DROP CONSTRAINT IF EXISTS bhikku_id_card_bic_regn_fkey"
    )

    op.execute("DROP INDEX IF EXISTS idx_bhikku_id_card_regn")
    op.execute("DROP INDEX IF EXISTS ix_bhikku_id_card_bic_regn")
    op.drop_column("bhikku_id_card", "bic_regn")

    op.alter_column(
        "bhikku_id_card",
        "bic_regn_text",
        new_column_name="bic_regn",
        existing_type=sa.String(length=20),
        nullable=False,
    )

    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'uq_bhikku_regist_br_regn'
            ) THEN
                ALTER TABLE bhikku_regist
                ADD CONSTRAINT uq_bhikku_regist_br_regn UNIQUE (br_regn);
            END IF;
        END$$;
        """
    )

    op.create_foreign_key(
        "bhikku_id_card_bic_regn_fkey",
        "bhikku_id_card",
        "bhikku_regist",
        ["bic_regn"],
        ["br_regn"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )

    op.create_index(
        "ix_bhikku_id_card_bic_regn",
        "bhikku_id_card",
        ["bic_regn"],
        unique=False,
    )

    op.create_unique_constraint(
        "uq_bhikku_id_card_bic_regn", "bhikku_id_card", ["bic_regn"]
    )
    op.create_unique_constraint(
        "uq_bhikku_id_card_bic_br_id", "bhikku_id_card", ["bic_br_id"]
    )


def downgrade() -> None:
    bind = op.get_bind()

    with op.batch_alter_table("bhikku_id_card") as batch_op:
        batch_op.drop_constraint(
            "uq_bhikku_id_card_bic_regn", type_="unique"
        )
        batch_op.drop_constraint(
            "uq_bhikku_id_card_bic_br_id", type_="unique"
        )

    op.execute(
        "ALTER TABLE bhikku_id_card DROP CONSTRAINT IF EXISTS bhikku_id_card_bic_regn_fkey"
    )

    op.execute("DROP INDEX IF EXISTS ix_bhikku_id_card_bic_regn")

    op.add_column(
        "bhikku_id_card",
        sa.Column("bic_regn_int", sa.Integer(), nullable=True),
    )

    bind.execute(
        text(
            """
            UPDATE bhikku_id_card AS bic
            SET bic_regn_int = br.br_id
            FROM bhikku_regist AS br
            WHERE br.br_regn = bic.bic_regn
            """
        )
    )

    op.drop_column("bhikku_id_card", "bic_regn")

    op.alter_column(
        "bhikku_id_card",
        "bic_regn_int",
        new_column_name="bic_regn",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.create_foreign_key(
        "bhikku_id_card_bic_regn_fkey",
        "bhikku_id_card",
        "bhikku_regist",
        ["bic_regn"],
        ["br_id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )

    op.execute(
        """
        ALTER TABLE bhikku_regist
        DROP CONSTRAINT IF EXISTS uq_bhikku_regist_br_regn
        """
    )

    op.create_index(
        "ix_bhikku_id_card_bic_regn",
        "bhikku_id_card",
        ["bic_regn"],
        unique=False,
    )
