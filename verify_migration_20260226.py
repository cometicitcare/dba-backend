#!/usr/bin/env python3
"""Verify if migration 20260226000001 NOT NULL constraints are applied."""

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

# Get table inspector
inspector = inspect(engine)

print("🔍 Checking vihaddata NOT NULL constraints...\n")

# Get column info for vh_vname and vh_addrs
columns_to_check = {
    "vh_vname": "VARCHAR(200)",
    "vh_addrs": "VARCHAR(500)"
}

print("Column Nullable Status:")
print("-" * 70)

all_correct = True
for col_name, expected_type in columns_to_check.items():
    col_info = None
    for col in inspector.get_columns("vihaddata"):
        if col["name"] == col_name:
            col_info = col
            break
    
    if col_info:
        nullable = col_info['nullable']
        col_type = str(col_info['type'])
        
        status = "✅" if not nullable else "❌"
        nullable_text = "NOT NULL (OK)" if not nullable else "NULLABLE (ERROR)"
        
        print(f"{status} {col_name:<20} {nullable_text:<25} Type: {col_type}")
        
        if nullable:
            all_correct = False
    else:
        print(f"❌ {col_name:<20} COLUMN NOT FOUND")
        all_correct = False

print("-" * 70)

# Check alembic version
print("\n🔎 Checking alembic_version table...\n")
try:
    result = connection.execute(text("SELECT version_num FROM alembic_version ORDER BY version_num DESC LIMIT 5;"))
    versions = [row[0] for row in result.fetchall()]
    
    print("Recent Alembic Versions:")
    for v in versions:
        status = "✅" if v == "20260226000001" else "  "
        print(f"{status} {v}")
    
    if "20260226000001" in versions:
        print(f"\n✅ Migration 20260226000001 IS recorded in alembic_version table")
    else:
        print(f"\n⚠️ Migration 20260226000001 NOT found in alembic_version table")
        
except Exception as e:
    print(f"❌ Failed to check alembic_version: {e}")

print("\n" + "=" * 70)
if all_correct:
    print("✅ MIGRATION SUCCESSFULLY APPLIED")
    print("   vh_vname and vh_addrs have NOT NULL constraints")
    print("\n   ✓ Safe to add to git and push")
else:
    print("❌ MIGRATION NOT FULLY APPLIED")
    print("   Some columns are still nullable")
print("=" * 70)

connection.close()
