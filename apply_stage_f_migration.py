"""
Safe manual migration script for Stage F:
- Checks which columns already exist
- Adds only missing columns (idempotent — safe to re-run)
- Updates alembic_version to 20260223000001
- Verifies all expected columns are present after
"""
import sys
import psycopg2

DB_HOST = "gondola.proxy.rlwy.net"
DB_PORT = 22000
DB_NAME = "dbahrms-new"
DB_USER = "app_admin"
DB_PASS = "rX2SWDbFuM%Qe3kBRzqnQ&Ia"

MIGRATION_ID = "20260223000001"
PREV_MIGRATION = "20260219000001"

# All columns this migration should add
EXPECTED_COLUMNS = {
    # Boolean bypass toggles
    "vh_bypass_no_detail":    "BOOLEAN DEFAULT FALSE",
    "vh_bypass_no_chief":     "BOOLEAN DEFAULT FALSE",
    "vh_bypass_ltr_cert":     "BOOLEAN DEFAULT FALSE",
    # Bypass audit
    "vh_bypass_no_detail_by": "VARCHAR(25)",
    "vh_bypass_no_detail_at": "TIMESTAMP",
    "vh_bypass_no_chief_by":  "VARCHAR(25)",
    "vh_bypass_no_chief_at":  "TIMESTAMP",
    "vh_bypass_ltr_cert_by":  "VARCHAR(25)",
    "vh_bypass_ltr_cert_at":  "TIMESTAMP",
    "vh_bypass_unlocked_by":  "VARCHAR(25)",
    "vh_bypass_unlocked_at":  "TIMESTAMP",
    # Historical period
    "vh_period_era":          "VARCHAR(50)",
    "vh_period_year":         "VARCHAR(10)",
    "vh_period_month":        "VARCHAR(2)",
    "vh_period_day":          "VARCHAR(2)",
    "vh_period_notes":        "VARCHAR(500)",
    # Viharadhipathi date
    "viharadhipathi_date":    "DATE",
}

def get_existing_columns(cur):
    cur.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'vihaddata'
    """)
    return {row[0] for row in cur.fetchall()}

def get_alembic_version(cur):
    try:
        cur.execute("SELECT version_num FROM alembic_version")
        rows = cur.fetchall()
        return [r[0] for r in rows]
    except Exception:
        return []

def main():
    print("=" * 60)
    print("Stage F Migration — Safe Apply Script")
    print("=" * 60)

    try:
        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
            user=DB_USER, password=DB_PASS,
            connect_timeout=15, sslmode="require"
        )
        conn.autocommit = False
        cur = conn.cursor()
        print(f"✅ Connected to {DB_HOST}:{DB_PORT}/{DB_NAME}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)

    # Check alembic version
    versions = get_alembic_version(cur)
    print(f"\n📍 Current alembic_version(s): {versions}")
    migration_already_recorded = MIGRATION_ID in versions

    # Check existing columns
    existing = get_existing_columns(cur)
    missing = {col: ddl for col, ddl in EXPECTED_COLUMNS.items() if col not in existing}
    already_have = {col for col in EXPECTED_COLUMNS if col in existing}

    print(f"\n📊 Column status for vihaddata:")
    print(f"   Already present ({len(already_have)}): {sorted(already_have)}")
    print(f"   Missing         ({len(missing)}): {sorted(missing.keys())}")

    if not missing and migration_already_recorded:
        print("\n✅ Nothing to do — all columns present and migration already recorded.")
        conn.close()
        return

    changes_made = False

    # Add missing columns
    if missing:
        print(f"\n⚙️  Adding {len(missing)} missing column(s)…")
        for col, ddl in missing.items():
            sql = f'ALTER TABLE vihaddata ADD COLUMN IF NOT EXISTS "{col}" {ddl}'
            print(f"   ► {sql}")
            try:
                cur.execute(sql)
                print(f"     ✅ Added {col}")
                changes_made = True
            except Exception as e:
                print(f"     ❌ Failed: {e}")
                conn.rollback()
                conn.close()
                sys.exit(1)

    # Update alembic_version
    if not migration_already_recorded:
        print(f"\n🔖 Updating alembic_version to {MIGRATION_ID}…")
        try:
            if versions:
                cur.execute("UPDATE alembic_version SET version_num = %s", (MIGRATION_ID,))
            else:
                cur.execute("INSERT INTO alembic_version (version_num) VALUES (%s)", (MIGRATION_ID,))
            print(f"   ✅ alembic_version = {MIGRATION_ID}")
            changes_made = True
        except Exception as e:
            print(f"   ❌ Failed to update alembic_version: {e}")
            conn.rollback()
            conn.close()
            sys.exit(1)

    if changes_made:
        conn.commit()
        print("\n✅ All changes committed.")

    # Final verification
    print("\n🔍 Final verification…")
    final_existing = get_existing_columns(cur)
    final_versions = get_alembic_version(cur)
    all_ok = True
    for col in EXPECTED_COLUMNS:
        status = "✅" if col in final_existing else "❌ MISSING"
        print(f"   {status}  {col}")
        if col not in final_existing:
            all_ok = False

    print(f"\n📍 alembic_version: {final_versions}")
    print("\n" + ("✅ MIGRATION COMPLETE — all columns verified!" if all_ok else "❌ Some columns still missing!"))
    conn.close()

if __name__ == "__main__":
    main()
