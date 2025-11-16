#!/usr/bin/env python3
"""Check and fix alembic version in database"""
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
    
    cursor.close()
    conn.close()
    
except ImportError:
    print("\nERROR: psycopg2 not installed. Install it with:")
    print("  pip install psycopg2-binary")
    sys.exit(1)
except Exception as e:
    print(f"\nERROR: {e}")
    sys.exit(1)
