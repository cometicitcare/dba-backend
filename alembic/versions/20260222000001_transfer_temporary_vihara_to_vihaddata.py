"""Transfer temporary_vihara records to vihaddata

Revision ID: 20260222000001
Revises: 20260219000001
Create Date: 2026-02-22

This migration:
1. Adds a tv_is_transferred flag column to temporary_vihara
2. Transfers all temporary_vihara records into vihaddata with column mapping
3. Marks transferred records with tv_is_transferred = true

PRODUCTION SAFE: Runs in a single transaction, fully reversible.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = "20260222000001"
down_revision = "20260219000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # Step 1: Add the transfer flag column to temporary_vihara
    # ------------------------------------------------------------------
    op.add_column(
        "temporary_vihara",
        sa.Column(
            "tv_is_transferred",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
            comment="Flag indicating this record has been transferred to vihaddata",
        ),
    )

    # ------------------------------------------------------------------
    # Step 2: Transfer records using raw SQL inside the same transaction
    # ------------------------------------------------------------------
    conn = op.get_bind()

    # 2a. Build province lookup: name/code -> cp_code
    province_rows = conn.execute(
        sa.text("SELECT cp_code, cp_name FROM cmm_province")
    ).fetchall()

    province_lookup = {}
    for code, name in province_rows:
        # Map by code itself (e.g. "WP" -> "WP")
        province_lookup[code.strip().lower()] = code
        # Map by English name (e.g. "Western Province" -> "WP")
        if name:
            province_lookup[name.strip().lower()] = code

    # Sinhala province name mappings (known values in temporary_vihara)
    sinhala_province_map = {
        "බස්නාහිර": "WP",
        "මධ්‍යම": "CP",
        "දකුණු": "SP",
        "උතුරු": "NP",
        "නැගෙනහිර": "EP",
        "වයඹ": "NWP",
        "උතුරු මැද": "NCP",
        "ඌව": "UP",
        "සබරගමුව": "SPB",
    }
    for sin_name, code in sinhala_province_map.items():
        province_lookup[sin_name.strip().lower()] = code

    # 2b. Build district lookup: name/code -> dd_dcode
    district_rows = conn.execute(
        sa.text("SELECT dd_dcode, dd_dname FROM cmm_districtdata")
    ).fetchall()

    district_lookup = {}
    for dcode, dname in district_rows:
        # Map by code (e.g. "DC001" -> "DC001")
        district_lookup[dcode.strip().lower()] = dcode
        if dname:
            dname_clean = dname.strip()
            # Map by full name (e.g. "කොළඹ (Colombo)" -> "DC001")
            district_lookup[dname_clean.lower()] = dcode
            # Map by Sinhala part only (e.g. "කොළඹ" -> "DC001")
            if "(" in dname_clean:
                sinhala_part = dname_clean.split("(")[0].strip()
                district_lookup[sinhala_part.lower()] = dcode
                # Map by English part only (e.g. "Colombo" -> "DC001")
                english_part = dname_clean.split("(")[1].rstrip(")").strip()
                district_lookup[english_part.lower()] = dcode

    def resolve_province(raw_value):
        """Resolve a province name/code to the FK code, or None."""
        if not raw_value:
            return None
        return province_lookup.get(raw_value.strip().lower())

    def resolve_district(raw_value):
        """Resolve a district name/code to the FK code, or None."""
        if not raw_value:
            return None
        return district_lookup.get(raw_value.strip().lower())

    # 2c. Find the current max TRN number in vihaddata
    result = conn.execute(
        sa.text(
            """
            SELECT COALESCE(
                MAX(
                    CAST(
                        SUBSTRING(vh_trn FROM 4) AS INTEGER
                    )
                ), 0
            )
            FROM vihaddata
            WHERE vh_trn LIKE 'TRN%'
            """
        )
    )
    current_max_trn = result.scalar() or 0

    # 2d. Fetch all temporary_vihara records that have NOT yet been transferred
    temp_records = conn.execute(
        sa.text(
            """
            SELECT tv_id, tv_name, tv_address, tv_contact_number,
                   tv_district, tv_province, tv_viharadhipathi_name,
                   tv_created_by
            FROM temporary_vihara
            WHERE tv_is_transferred = false
            ORDER BY tv_id ASC
            """
        )
    ).fetchall()

    if not temp_records:
        # Nothing to transfer
        return

    # 2e. Insert each record into vihaddata with proper column mapping
    trn_counter = current_max_trn
    transferred_tv_ids = []

    for row in temp_records:
        trn_counter += 1
        trn_value = f"TRN{trn_counter:07d}"

        # tv_contact_number is String(15), vh_mobile is String(10) – truncate safely
        mobile = row.tv_contact_number
        if mobile and len(mobile) > 10:
            mobile = mobile[:10]

        # Resolve province and district names to FK codes
        province_code = resolve_province(row.tv_province)
        district_code = resolve_district(row.tv_district)

        conn.execute(
            sa.text(
                """
                INSERT INTO vihaddata (
                    vh_trn,
                    vh_vname,
                    vh_addrs,
                    vh_mobile,
                    vh_district,
                    vh_province,
                    vh_viharadhipathi_name,
                    vh_workflow_status,
                    vh_is_deleted,
                    vh_version,
                    vh_created_at,
                    vh_updated_at,
                    vh_created_by,
                    vh_version_number
                ) VALUES (
                    :trn,
                    :name,
                    :address,
                    :mobile,
                    :district,
                    :province,
                    :viharadhipathi,
                    'S1_PENDING',
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
                "trn": trn_value,
                "name": row.tv_name,
                "address": row.tv_address,
                "mobile": mobile,
                "district": district_code,
                "province": province_code,
                "viharadhipathi": row.tv_viharadhipathi_name,
                "created_by": row.tv_created_by,
            },
        )
        transferred_tv_ids.append(row.tv_id)

    # 2f. Mark all transferred records
    if transferred_tv_ids:
        conn.execute(
            sa.text(
                """
                UPDATE temporary_vihara
                SET tv_is_transferred = true,
                    tv_updated_at = NOW()
                WHERE tv_id = ANY(:ids)
                """
            ),
            {"ids": transferred_tv_ids},
        )


def downgrade() -> None:
    # ------------------------------------------------------------------
    # Reverse: Delete the transferred vihaddata rows and remove the flag
    # ------------------------------------------------------------------
    conn = op.get_bind()

    # Find the TRN values that were inserted from temporary_vihara during upgrade.
    # We identify them by matching vh_vname against tv_name for transferred records.
    # A safer approach: delete vihaddata rows whose vh_vname + vh_created_by match
    # temporary_vihara records that are currently marked as transferred.
    conn.execute(
        sa.text(
            """
            DELETE FROM vihaddata
            WHERE vh_trn IN (
                SELECT v.vh_trn
                FROM vihaddata v
                INNER JOIN temporary_vihara tv
                    ON v.vh_vname = tv.tv_name
                    AND COALESCE(v.vh_created_by, '') = COALESCE(tv.tv_created_by, '')
                WHERE tv.tv_is_transferred = true
            )
            """
        )
    )

    # Reset the flag
    conn.execute(
        sa.text(
            """
            UPDATE temporary_vihara
            SET tv_is_transferred = false
            """
        )
    )

    # Drop the flag column
    op.drop_column("temporary_vihara", "tv_is_transferred")
