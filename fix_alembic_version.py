#!/usr/bin/env python3
"""Fix corrupted alembic version in database"""
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

print(f"Connecting to database...")

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
    
    # Check current version
    cursor.execute("SELECT * FROM alembic_version")
    rows = cursor.fetchall()
    
    print("\nCurrent version(s) in alembic_version table:")
    for row in rows:
        print(f"  Version: '{row[0]}'")
    
    # The corrupted version is '202511170000'
    # We need to replace it with the last known good version
    # Based on the migration history, the last migration before the three new ones is '20251116133100'
    
    print("\n" + "="*60)
    print("FIXING CORRUPTED VERSION")
    print("="*60)
    
    correct_version = '20251116133100'
    
    print(f"\nUpdating alembic_version from '202511170000' to '{correct_version}'...")
    
    cursor.execute("DELETE FROM alembic_version")
    cursor.execute("INSERT INTO alembic_version (version_num) VALUES (%s)", (correct_version,))
    conn.commit()
    
    print(f"✓ Successfully updated to version '{correct_version}'")
    
    # Verify
    cursor.execute("SELECT * FROM alembic_version")
    rows = cursor.fetchall()
    
    print("\nVerifying - Current version(s) in alembic_version table:")
    for row in rows:
        print(f"  Version: '{row[0]}'")
    
    cursor.close()
    conn.close()
    
    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    print("Now you can run: alembic upgrade head")
    print("This will apply migrations 20251117000002, 20251117000001, and 20251117000003")
    
except ImportError:
    print("\nERROR: psycopg2 not installed. Install it with:")
    print("  pip install psycopg2-binary")
    sys.exit(1)
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
