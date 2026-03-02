#!/usr/bin/env python3
"""Verify if migration 20260223000001 was properly applied to the database."""

import os
from sqlalchemy import create_engine, inspect, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL not set in .env")
    exit(1)

# Fix asyncpg URL if needed
if DATABASE_URL.startswith("postgresql+asyncpg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

print(f"📊 Connecting to database...")
try:
    engine = create_engine(DATABASE_URL)
    connection = engine.connect()
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    exit(1)

print("✅ Database connected!\n")

# Columns that the migration should have added
EXPECTED_COLUMNS = {
    # Bypass toggle fields
    "vh_bypass_no_detail": "Boolean",
    "vh_bypass_no_chief": "Boolean",
    "vh_bypass_ltr_cert": "Boolean",
    
    # Bypass audit columns
    "vh_bypass_no_detail_by": "String",
    "vh_bypass_no_detail_at": "DateTime",
    "vh_bypass_no_chief_by": "String",
    "vh_bypass_no_chief_at": "DateTime",
    "vh_bypass_ltr_cert_by": "String",
    "vh_bypass_ltr_cert_at": "DateTime",
    "vh_bypass_unlocked_by": "String",
    "vh_bypass_unlocked_at": "DateTime",
    
    # Historical period fields
    "vh_period_era": "String",
    "vh_period_year": "String",
    "vh_period_month": "String",
    "vh_period_day": "String",
    "vh_period_notes": "String",
    
    # Viharadhipathi date
    "viharadhipathi_date": "Date",
}

# Get table inspector
inspector = inspect(engine)

print("🔍 Checking vihaddata table columns...\n")

# Get existing columns
if "vihaddata" not in inspector.get_table_names():
    print("❌ vihaddata table does not exist!")
    exit(1)

existing_columns = {col["name"]: col for col in inspector.get_columns("vihaddata")}

# Check each expected column
missing_columns = []
found_columns = []

print("Migration Columns Status:")
print("-" * 70)
for col_name, expected_type in EXPECTED_COLUMNS.items():
    if col_name in existing_columns:
        col_info = existing_columns[col_name]
        found_columns.append(col_name)
        print(f"✅ {col_name:<35} {str(col_info['type']):<20}")
    else:
        missing_columns.append(col_name)
        print(f"❌ {col_name:<35} MISSING")

print("-" * 70)
print(f"\n📈 Summary:")
print(f"   Found: {len(found_columns)}/{len(EXPECTED_COLUMNS)} columns")
print(f"   Missing: {len(missing_columns)} columns\n")

# Check alembic_version table
print("🔎 Checking alembic_version table...\n")
try:
    result = connection.execute(text("SELECT version_num FROM alembic_version ORDER BY version_num DESC LIMIT 5;"))
    versions = [row[0] for row in result.fetchall()]
    
    print("Recent Alembic Versions:")
    for v in versions:
        status = "✅" if v == "20260223000001" else "  "
        print(f"{status} {v}")
    
    if "20260223000001" in versions:
        print(f"\n✅ Migration 20260223000001 IS recorded in alembic_version table")
    else:
        print(f"\n❌ Migration 20260223000001 NOT found in alembic_version table")
        print("    (Migration may not have been applied!)")
        
except Exception as e:
    print(f"❌ Failed to check alembic_version: {e}")

# Determine overall status
print("\n" + "=" * 70)
if len(missing_columns) == 0:
    print("✅ MIGRATION SUCCESSFULLY APPLIED")
    print("   All 17 columns are present in the database.")
    print("\n   ✓ Safe to add to git and push")
else:
    print(f"⚠️  MIGRATION INCOMPLETE OR NOT APPLIED")
    print(f"   {len(missing_columns)} columns are missing:")
    for col in missing_columns:
        print(f"     - {col}")
    print("\n   ⚠️  DO NOT add to git yet")
    print("   Action needed: Re-run migration in production database")

print("=" * 70)

connection.close()
