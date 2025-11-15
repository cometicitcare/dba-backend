#!/usr/bin/env python3
"""
Script to fix Alembic migration history by directly updating the database.
This is useful when you have a missing revision error.

Usage:
    python fix_alembic_db.py

Requirements:
    - DATABASE_URL environment variable must be set
    - sqlalchemy package must be installed
"""

import os
import sys
from sqlalchemy import create_engine, text

# The latest migration revision in your codebase
LATEST_REVISION = "20251115160000"

def main():
    # Get DATABASE_URL from environment
    db_url = os.environ.get('DATABASE_URL')
    
    if not db_url:
        print("❌ ERROR: DATABASE_URL environment variable is not set")
        print("Please set it first:")
        print("  export DATABASE_URL='postgresql://user:pass@host:port/dbname'")
        sys.exit(1)
    
    # Hide password in output
    safe_url = db_url.split('@')[0].split(':')[:-1]
    print(f"🔧 Connecting to database...")
    print(f"   Using: {':'.join(safe_url)}:***@{db_url.split('@')[1]}")
    
    try:
        # Create database engine
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            # Check current version
            print("\n📋 Checking current alembic_version...")
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            current_versions = [row[0] for row in result]
            
            if current_versions:
                print(f"   Current version(s): {', '.join(current_versions)}")
            else:
                print("   No version found in database")
            
            # Clear the alembic_version table
            print(f"\n🗑️  Clearing alembic_version table...")
            conn.execute(text("DELETE FROM alembic_version"))
            
            # Insert the latest revision
            print(f"📌 Stamping database with revision: {LATEST_REVISION}")
            conn.execute(text(f"INSERT INTO alembic_version (version_num) VALUES ('{LATEST_REVISION}')"))
            
            # Commit the changes
            conn.commit()
            
            # Verify
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            new_version = result.fetchone()[0]
            
            print(f"\n✅ Success! Database is now at revision: {new_version}")
            print("\nYou can now run: alembic upgrade head")
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
