"""Transfer temporary_silmatha records to silmatha_regist

Revision ID: 20260223000001
Revises: 20260222000002
Create Date: 2026-02-23

This migration:
1. Adds a ts_is_transferred flag column to temporary_silmatha
2. Transfers all temporary_silmatha records into silmatha_regist with column mapping
3. Auto-generates SIL registration numbers (SIL{YEAR}{SEQUENCE}) for each
4. Marks transferred records with ts_is_transferred = true

Column mapping:
  ts_name           -> sil_gihiname          (Silmatha name)
  ts_contact_number -> sil_mobile            (truncated to 10 chars)
  ts_address        -> sil_fathrsaddrs       (address)
  ts_ordained_date  -> sil_declaration_date  (ordination/declaration date)
  ts_created_by     -> sil_created_by        (audit)

  ts_nic            -> sil_remarks           (stored in remarks - no direct column)
  ts_district       -> sil_remarks           (free text, cannot map to FK)
  ts_province       -> sil_remarks           (free text, cannot map to FK)
  ts_arama_name     -> sil_remarks           (stored in remarks - no direct FK)

Required defaults for silmatha_regist NOT NULL columns:
  sil_regn            -> auto-generated SIL{YEAR}{SEQUENCE}
  sil_reqstdate       -> current date
  sil_currstat        -> 'ST01'    (Active)
  sil_workflow_status -> 'PENDING'

PRODUCTION SAFE: Runs in a single transaction, fully reversible.
"""
from datetime import date, datetime

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260223000001"
down_revision = "20260222000002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # Step 1: Add the transfer flag column to temporary_silmatha
    # ------------------------------------------------------------------
    op.add_column(
        "temporary_silmatha",
        sa.Column(
            "ts_is_transferred",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
            comment="Flag indicating this record has been transferred to silmatha_regist",
        ),
    )

    # ------------------------------------------------------------------
    # Step 2: Transfer records using raw SQL inside the same transaction
    # ------------------------------------------------------------------
    conn = op.get_bind()

    # 2a. Determine the next SIL registration sequence
    current_year = datetime.utcnow().year
    prefix = f"SIL{current_year}"

    result = conn.execute(
        sa.text(
            """
            SELECT COALESCE(
                MAX(
                    CAST(
                        SUBSTRING(sil_regn FROM :prefix_len + 1) AS INTEGER
                    )
                ), 0
            )
            FROM silmatha_regist
            WHERE sil_regn LIKE :pattern
            """
        ),
        {"prefix_len": len(prefix), "pattern": f"{prefix}%"},
    )
    current_max_seq = result.scalar() or 0

    # 2b. Fetch all temporary_silmatha records that have NOT yet been transferred
    temp_records = conn.execute(
        sa.text(
            """
            SELECT ts_id, ts_name, ts_nic, ts_contact_number,
                   ts_address, ts_district, ts_province,
                   ts_arama_name, ts_ordained_date, ts_created_by
            FROM temporary_silmatha
            WHERE ts_is_transferred = false
            ORDER BY ts_id ASC
            """
        )
    ).fetchall()

    if not temp_records:
        # Nothing to transfer
        return

    # 2c. Insert each record into silmatha_regist with proper column mapping
    seq_counter = current_max_seq
    transferred_ts_ids = []
    today = date.today()

    for row in temp_records:
        seq_counter += 1
        regn_value = f"{prefix}{seq_counter:06d}"

        # ts_contact_number is String(15), sil_mobile is String(10) - truncate safely
        mobile = row.ts_contact_number
        if mobile and len(mobile) > 10:
            mobile = mobile[:10]

        # Build remarks with original temp silmatha data for audit trail
        remarks_parts = ["[TEMP_SILMATHA] Transferred from temporary_silmatha table."]
        if row.ts_nic:
            remarks_parts.append(f"NIC: {row.ts_nic}")
        if row.ts_district:
            remarks_parts.append(f"District: {row.ts_district}")
        if row.ts_province:
            remarks_parts.append(f"Province: {row.ts_province}")
        if row.ts_arama_name:
            remarks_parts.append(f"Arama: {row.ts_arama_name}")
        remarks = " | ".join(remarks_parts)

        # Truncate remarks to 100 chars (sil_remarks max length in model is String(100))
        if len(remarks) > 100:
            remarks = remarks[:97] + "..."

        # Truncate address to 200 chars (sil_fathrsaddrs max length)
        address = row.ts_address
        if address and len(address) > 200:
            address = address[:197] + "..."

        # Truncate name to 50 chars (sil_gihiname max length)
        name = row.ts_name
        if name and len(name) > 50:
            name = name[:47] + "..."

        conn.execute(
            sa.text(
                """
                INSERT INTO silmatha_regist (
                    sil_regn,
                    sil_reqstdate,
                    sil_gihiname,
                    sil_mobile,
                    sil_fathrsaddrs,
                    sil_declaration_date,
                    sil_currstat,
                    sil_remarks,
                    sil_workflow_status,
                    sil_is_deleted,
                    sil_is_temporary_record,
                    sil_version,
                    sil_created_at,
                    sil_updated_at,
                    sil_created_by,
                    sil_version_number
                ) VALUES (
                    :regn,
                    :reqstdate,
                    :gihiname,
                    :mobile,
                    :address,
                    :declaration_date,
                    'ST01',
                    :remarks,
                    'PENDING',
                    false,
                    true,
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
                "gihiname": name,
                "mobile": mobile,
                "address": address,
                "declaration_date": row.ts_ordained_date,
                "remarks": remarks,
                "created_by": row.ts_created_by,
            },
        )
        transferred_ts_ids.append(row.ts_id)

    # 2d. Mark all transferred records
    if transferred_ts_ids:
        conn.execute(
            sa.text(
                """
                UPDATE temporary_silmatha
                SET ts_is_transferred = true,
                    ts_updated_at = NOW()
                WHERE ts_id = ANY(:ids)
                """
            ),
            {"ids": transferred_ts_ids},
        )


def downgrade() -> None:
    # ------------------------------------------------------------------
    # Reverse: Delete the transferred silmatha_regist rows and remove the flag
    # ------------------------------------------------------------------
    conn = op.get_bind()

    # Delete silmatha_regist rows that were inserted from temporary_silmatha during upgrade.
    # Identify them by sil_is_temporary_record = true AND sil_remarks starting with [TEMP_SILMATHA]
    # plus matching sil_gihiname against ts_name for transferred records.
    conn.execute(
        sa.text(
            """
            DELETE FROM silmatha_regist
            WHERE sil_regn IN (
                SELECT s.sil_regn
                FROM silmatha_regist s
                INNER JOIN temporary_silmatha ts
                    ON s.sil_gihiname = ts.ts_name
                    AND COALESCE(s.sil_created_by, '') = COALESCE(ts.ts_created_by, '')
                WHERE ts.ts_is_transferred = true
                  AND s.sil_remarks LIKE '[TEMP_SILMATHA]%%'
                  AND s.sil_is_temporary_record = true
            )
            """
        )
    )

    # Reset the flag
    conn.execute(
        sa.text(
            """
            UPDATE temporary_silmatha
            SET ts_is_transferred = false
            """
        )
    )

    # Drop the flag column
    op.drop_column("temporary_silmatha", "ts_is_transferred")
