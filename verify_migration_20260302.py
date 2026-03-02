#!/usr/bin/env python3
"""Verify if migration 20260302000001 registration status is applied."""

import os
from sqlalchemy import create_engine, inspect, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL not set in .env")
    exit(1)

if DATABASE_URL.startswith("postgresql+asyncpg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

print(f"📊 Connecting to database...\n")
try:
    engine = create_engine(DATABASE_URL)
    connection = engine.connect()
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    exit(1)

inspector = inspect(engine)

print("🔍 Checking vihaddata registration status columns...\n")

columns_to_check = {
    "vh_is_registered": "BOOLEAN",
    "vh_unregistered_reason": "VARCHAR(500)"
}

print("Column Status:")
print("-" * 70)

all_correct = True
for col_name, expected_type in columns_to_check.items():
    col_info = None
    for col in inspector.get_columns("vihaddata"):
        if col["name"] == col_name:
            col_info = col
            break
    
    if col_info:
        col_type = str(col_info['type'])
        nullable = col_info['nullable']
        nullable_text = "NULLABLE" if nullable else "NOT NULL"
        
        status = "✅"
        print(f"{status} {col_name:<25} {col_type:<20} {nullable_text}")
    else:
        print(f"❌ {col_name:<25} COLUMN NOT FOUND")
        all_correct = False

print("-" * 70)

# Check alembic version
print("\n🔎 Checking alembic_version table...\n")
try:
    result = connection.execute(text("SELECT version_num FROM alembic_version ORDER BY version_num DESC LIMIT 5;"))
    versions = [row[0] for row in result.fetchall()]
    
    print("Recent Alembic Versions:")
    for v in versions:
        if v in ["20260302000001", "20260228000001", "20260226000001"]:
            status = "✅"
        else:
            status = "  "
        print(f"{status} {v}")
    
    if "20260302000001" in versions:
        print(f"\n✅ Migration 20260302000001 IS recorded")
    else:
        print(f"\n⚠️ Migration 20260302000001 NOT found")
        
except Exception as e:
    print(f"❌ Failed to check alembic_version: {e}")

print("\n" + "=" * 70)
if all_correct:
    print("✅ MIGRATION SUCCESSFULLY APPLIED")
    print("   vh_is_registered and vh_unregistered_reason present")
    print("\n   ✓ Safe to add to git and push")
else:
    print("❌ MIGRATION NOT FULLY APPLIED")
print("=" * 70)

connection.close()
