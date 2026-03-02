"""Transfer temporary_bhikku records to bhikku_regist

Revision ID: 20260222000002
Revises: 20260222000001
Create Date: 2026-02-22

This migration:
1. Adds a tb_is_transferred flag column to temporary_bhikku
2. Transfers all temporary_bhikku records into bhikku_regist with column mapping
3. Auto-generates BH registration numbers (BH{YEAR}{SEQUENCE}) for each
4. Marks transferred records with tb_is_transferred = true

Column mapping:
  tb_name           -> br_mahananame   (Bhikku name)
  tb_samanera_name  -> br_gihiname     (Samanera / lay name)
  tb_contact_number -> br_mobile       (truncated to 10 chars)
  tb_address        -> br_fathrsaddrs  (address)
  tb_living_temple  -> br_remarks      (stored as reference text, not FK)
  tb_id_number      -> br_remarks      (stored as reference text)
  tb_created_by     -> br_created_by   (audit)

Required defaults for bhikku_regist NOT NULL columns:
  br_regn         -> auto-generated BH{YEAR}{SEQUENCE}
  br_reqstdate    -> current date
  br_currstat     -> 'ST01'    (Active)
  br_parshawaya   -> 'SYM_P01' (default parshawa)

PRODUCTION SAFE: Runs in a single transaction, fully reversible.
"""
from datetime import date, datetime

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260222000002"
down_revision = "20260222000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # Step 1: Add the transfer flag column to temporary_bhikku
    # ------------------------------------------------------------------
    op.add_column(
        "temporary_bhikku",
        sa.Column(
            "tb_is_transferred",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
            comment="Flag indicating this record has been transferred to bhikku_regist",
        ),
    )

    # ------------------------------------------------------------------
    # Step 2: Transfer records using raw SQL inside the same transaction
    # ------------------------------------------------------------------
    conn = op.get_bind()

    # 2a. Determine the next BH registration sequence
    current_year = datetime.utcnow().year
    prefix = f"BH{current_year}"

    result = conn.execute(
        sa.text(
            """
            SELECT COALESCE(
                MAX(
                    CAST(
                        SUBSTRING(br_regn FROM :prefix_len + 1) AS INTEGER
                    )
                ), 0
            )
            FROM bhikku_regist
            WHERE br_regn LIKE :pattern
            """
        ),
        {"prefix_len": len(prefix), "pattern": f"{prefix}%"},
    )
    current_max_seq = result.scalar() or 0

    # 2b. Fetch all temporary_bhikku records that have NOT yet been transferred
    temp_records = conn.execute(
        sa.text(
            """
            SELECT tb_id, tb_name, tb_id_number, tb_contact_number,
                   tb_samanera_name, tb_address, tb_living_temple,
                   tb_created_by
            FROM temporary_bhikku
            WHERE tb_is_transferred = false
            ORDER BY tb_id ASC
            """
        )
    ).fetchall()

    if not temp_records:
        # Nothing to transfer
        return

    # 2c. Insert each record into bhikku_regist with proper column mapping
    seq_counter = current_max_seq
    transferred_tb_ids = []
    today = date.today()

    for row in temp_records:
        seq_counter += 1
        regn_value = f"{prefix}{seq_counter:06d}"

        # tb_contact_number is String(15), br_mobile is String(10) - truncate safely
        mobile = row.tb_contact_number
        if mobile and len(mobile) > 10:
            mobile = mobile[:10]

        # Build remarks with original temp bhikku data for audit trail
        remarks_parts = ["[TEMP_BHIKKU] Transferred from temporary_bhikku table."]
        if row.tb_id_number:
            remarks_parts.append(f"ID Number: {row.tb_id_number}")
        if row.tb_living_temple:
            remarks_parts.append(f"Living Temple: {row.tb_living_temple}")
        remarks = " | ".join(remarks_parts)

        # Truncate remarks to 500 chars (br_remarks max length)
        if len(remarks) > 500:
            remarks = remarks[:497] + "..."

        conn.execute(
            sa.text(
                """
                INSERT INTO bhikku_regist (
                    br_regn,
                    br_reqstdate,
                    br_mahananame,
                    br_gihiname,
                    br_mobile,
                    br_fathrsaddrs,
                    br_currstat,
                    br_parshawaya,
                    br_cat,
                    br_remarks,
                    br_workflow_status,
                    br_is_deleted,
                    br_version,
                    br_created_at,
                    br_updated_at,
                    br_created_by,
                    br_version_number
                ) VALUES (
                    :regn,
                    :reqstdate,
                    :mahananame,
                    :gihiname,
                    :mobile,
                    :address,
                    'ST01',
                    'SYM_P01',
                    'CAT03',
                    :remarks,
                    'PENDING',
                    false,
                    NOW(),
                    NOW(),
                    NOW(),
                    :created_by,
                    1
                )
                """
            ),
            {
                "regn": regn_value,
                "reqstdate": today,
                "mahananame": row.tb_name,
                "gihiname": row.tb_samanera_name,
                "mobile": mobile,
                "address": row.tb_address,
                "remarks": remarks,
                "created_by": row.tb_created_by,
            },
        )
        transferred_tb_ids.append(row.tb_id)

    # 2d. Mark all transferred records
    if transferred_tb_ids:
        conn.execute(
            sa.text(
                """
                UPDATE temporary_bhikku
                SET tb_is_transferred = true,
                    tb_updated_at = NOW()
                WHERE tb_id = ANY(:ids)
                """
            ),
            {"ids": transferred_tb_ids},
        )


def downgrade() -> None:
    # ------------------------------------------------------------------
    # Reverse: Delete the transferred bhikku_regist rows and remove the flag
    # ------------------------------------------------------------------
    conn = op.get_bind()

    # Delete bhikku_regist rows that were inserted from temporary_bhikku during upgrade.
    # Identify them by matching br_mahananame against tb_name for transferred records,
    # plus br_created_by matching tb_created_by.
    conn.execute(
        sa.text(
            """
            DELETE FROM bhikku_regist
            WHERE br_regn IN (
                SELECT b.br_regn
                FROM bhikku_regist b
                INNER JOIN temporary_bhikku tb
                    ON b.br_mahananame = tb.tb_name
                    AND COALESCE(b.br_created_by, '') = COALESCE(tb.tb_created_by, '')
                WHERE tb.tb_is_transferred = true
                  AND b.br_remarks LIKE '[TEMP_BHIKKU]%%'
            )
            """
        )
    )

    # Reset the flag
    conn.execute(
        sa.text(
            """
            UPDATE temporary_bhikku
            SET tb_is_transferred = false
            """
        )
    )

    # Drop the flag column
    op.drop_column("temporary_bhikku", "tb_is_transferred")
