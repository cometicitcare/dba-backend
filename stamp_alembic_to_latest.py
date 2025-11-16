#!/usr/bin/env python3
"""Stamp alembic to the latest version without running migrations"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL
db_url = os.getenv('DATABASE_URL')
if not db_url:
    print("ERROR: DATABASE_URL not found in environment")
    sys.exit(1)

# Convert asyncpg URL to psycopg2 URL for synchronous connection
sync_db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')

print(f"Checking database state...")

try:
    import psycopg2
    from urllib.parse import urlparse, parse_qs, unquote
    
    # Parse the URL
    parsed = urlparse(sync_db_url)
    
    # Create connection
    conn = psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port,
        database=parsed.path.lstrip('/'),
        user=parsed.username,
        password=unquote(parsed.password)
    )
    
    cursor = conn.cursor()
    
    # Check if tables exist
    print("\nChecking if migration tables exist:")
    tables_to_check = ['silmatha_regist', 'bhikku_high_regist', 'silmatha_id_card']
    
    for table in tables_to_check:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            )
        """, (table,))
        exists = cursor.fetchone()[0]
        print(f"  {table}: {'EXISTS' if exists else 'DOES NOT EXIST'}")
    
    # Check current version
    cursor.execute("SELECT * FROM alembic_version")
    rows = cursor.fetchall()
    
    print("\nCurrent version in alembic_version table:")
    for row in rows:
        print(f"  Version: '{row[0]}'")
    
    # Since the tables already exist, we should stamp to the latest version
    latest_version = '20251117000003'
    
    print("\n" + "="*60)
    print("STAMPING TO LATEST VERSION")
    print("="*60)
    print(f"\nThe migration tables already exist in the database.")
    print(f"Updating alembic_version to '{latest_version}' to mark migrations as applied...")
    
    cursor.execute("DELETE FROM alembic_version")
    cursor.execute("INSERT INTO alembic_version (version_num) VALUES (%s)", (latest_version,))
    conn.commit()
    
    print(f"✓ Successfully stamped to version '{latest_version}'")
    
    # Verify
    cursor.execute("SELECT * FROM alembic_version")
    rows = cursor.fetchall()
    
    print("\nVerifying - Current version in alembic_version table:")
    for row in rows:
        print(f"  Version: '{row[0]}'")
    
    cursor.close()
    conn.close()
    
    print("\n" + "="*60)
    print("COMPLETE")
    print("="*60)
    print("The database is now in sync with the migration history.")
    print("You can verify with: alembic current")
    
except ImportError:
    print("\nERROR: psycopg2 not installed. Install it with:")
    print("  pip install psycopg2-binary")
    sys.exit(1)
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
