#!/usr/bin/env python3
"""
Script to analyze, backup, and replace cmm_gndata with refined_cmm_gndata
"""
import os
import asyncio
import pandas as pd
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import asyncpg
from sqlalchemy import text, create_engine
import psycopg2
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"DATABASE_URL: {DATABASE_URL}")

# Parse PostgreSQL URL for psycopg2
from urllib.parse import unquote
parsed = urlparse(DATABASE_URL)
db_config = {
    'host': parsed.hostname,
    'port': parsed.port,
    'database': parsed.path.lstrip('/'),
    'user': parsed.username,
    'password': unquote(parsed.password),  # Decode URL-encoded password
}

print(f"\n{'='*80}")
print("DATABASE CONNECTION TEST")
print(f"{'='*80}")
print(f"Host: {db_config['host']}")
print(f"Port: {db_config['port']}")
print(f"Database: {db_config['database']}")
print(f"User: {db_config['user']}")

async def analyze_tables():
    """Analyze both tables"""
    try:
        # Use psycopg2 for synchronous operations
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        print(f"\n{'='*80}")
        print("TABLE STRUCTURE & ROW COUNT")
        print(f"{'='*80}\n")
        
        # Get cmm_gndata info
        print("1. Checking cmm_gndata:")
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'cmm_gndata'
            ORDER BY ordinal_position
        """)
        cmm_columns = cursor.fetchall()
        print(f"   Columns: {cmm_columns}")
        
        cursor.execute("SELECT COUNT(*) FROM cmm_gndata")
        cmm_count = cursor.fetchone()[0]
        print(f"   Row count: {cmm_count}")
        
        # Get refined_cmm_gndata info
        print("\n2. Checking refined_cmm_gndata:")
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'refined_cmm_gndata'
            ORDER BY ordinal_position
        """)
        refined_columns = cursor.fetchall()
        print(f"   Columns: {refined_columns}")
        
        cursor.execute("SELECT COUNT(*) FROM refined_cmm_gndata")
        refined_count = cursor.fetchone()[0]
        print(f"   Row count: {refined_count}")
        
        # Compare structure
        print(f"\n{'='*80}")
        print("STRUCTURE COMPARISON")
        print(f"{'='*80}")
        print(f"Columns match: {cmm_columns == refined_columns}")
        if cmm_columns != refined_columns:
            print("WARNING: Column definitions differ!")
            print(f"  cmm_gndata: {cmm_columns}")
            print(f"  refined_cmm_gndata: {refined_columns}")
        
        print(f"\nRow count difference: {refined_count - cmm_count} rows")
        print(f"  cmm_gndata: {cmm_count} rows")
        print(f"  refined_cmm_gndata: {refined_count} rows")
        
        # Sample data comparison
        print(f"\n{'='*80}")
        print("SAMPLE DATA (First 5 rows)")
        print(f"{'='*80}\n")
        
        cursor.execute("SELECT * FROM cmm_gndata LIMIT 5")
        print("cmm_gndata sample:")
        print(cursor.fetchall())
        
        cursor.execute("SELECT * FROM refined_cmm_gndata LIMIT 5")
        print("\nrefined_cmm_gndata sample:")
        print(cursor.fetchall())
        
        # Get primary key info
        print(f"\n{'='*80}")
        print("PRIMARY KEY & CONSTRAINTS")
        print(f"{'='*80}\n")
        
        cursor.execute("""
            SELECT constraint_name, constraint_type
            FROM information_schema.table_constraints
            WHERE table_name IN ('cmm_gndata', 'refined_cmm_gndata')
        """)
        constraints = cursor.fetchall()
        print(f"Constraints: {constraints}")
        
        cursor.close()
        conn.close()
        
        return {
            'cmm_count': cmm_count,
            'refined_count': refined_count,
            'columns_match': cmm_columns == refined_columns,
            'cmm_columns': cmm_columns,
            'refined_columns': refined_columns
        }
        
    except Exception as e:
        print(f"ERROR: {e}")
        return None


def backup_cmm_gndata():
    """Backup cmm_gndata to CSV"""
    try:
        print(f"\n{'='*80}")
        print("CREATING BACKUP CSV")
        print(f"{'='*80}\n")
        
        # Create backup directory if it doesn't exist
        backup_dir = Path("./data_backups")
        backup_dir.mkdir(exist_ok=True)
        
        # Create connection string for SQLAlchemy (for pandas)
        conn = psycopg2.connect(**db_config)
        
        # Read cmm_gndata into pandas
        query = "SELECT * FROM cmm_gndata"
        df = pd.read_sql_query(query, conn)
        
        # Save to CSV with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"cmm_gndata_backup_{timestamp}.csv"
        
        df.to_csv(backup_file, index=False)
        
        print(f"✓ Backup created: {backup_file}")
        print(f"  Rows: {len(df)}")
        print(f"  Columns: {list(df.columns)}")
        
        conn.close()
        return str(backup_file)
        
    except Exception as e:
        print(f"ERROR during backup: {e}")
        return None


def replace_cmm_gndata():
    """Replace cmm_gndata with data from refined_cmm_gndata"""
    try:
        print(f"\n{'='*80}")
        print("REPLACING DATA")
        print(f"{'='*80}\n")
        
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Disable foreign key constraints temporarily
        print("1. Disabling foreign key constraints...")
        cursor.execute("ALTER TABLE cmm_gndata DISABLE TRIGGER ALL")
        
        # Clear cmm_gndata
        print("2. Clearing cmm_gndata...")
        cursor.execute("DELETE FROM cmm_gndata")
        
        # Copy data from refined_cmm_gndata
        print("3. Copying data from refined_cmm_gndata...")
        cursor.execute("""
            INSERT INTO cmm_gndata 
            SELECT * FROM refined_cmm_gndata
        """)
        
        # Re-enable constraints
        print("4. Re-enabling foreign key constraints...")
        cursor.execute("ALTER TABLE cmm_gndata ENABLE TRIGGER ALL")
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM cmm_gndata")
        new_count = cursor.fetchone()[0]
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"\n✓ Data replacement successful!")
        print(f"  New row count in cmm_gndata: {new_count}")
        
        return new_count
        
    except Exception as e:
        print(f"ERROR during replacement: {e}")
        return None


async def main():
    print("\n" + "="*80)
    print("CMM_GNDATA SYNC UTILITY")
    print("="*80)
    
    # Step 1: Analyze tables
    analysis = await analyze_tables()
    
    if not analysis:
        print("\nFailed to analyze tables. Exiting.")
        return
    
    # Step 2: Confirm before proceeding
    print(f"\n{'='*80}")
    print("SUMMARY & CONFIRMATION")
    print(f"{'='*80}")
    print(f"\nCurrent cmm_gndata: {analysis['cmm_count']} rows")
    print(f"refined_cmm_gndata: {analysis['refined_count']} rows")
    print(f"Change: {analysis['refined_count'] - analysis['cmm_count']} rows")
    
    response = input("\nProceed with backup and replacement? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("Operation cancelled.")
        return
    
    # Step 3: Create backup
    backup_file = backup_cmm_gndata()
    
    if not backup_file:
        print("\nBackup failed. Aborting replacement.")
        return
    
    # Step 4: Replace data
    new_count = replace_cmm_gndata()
    
    if new_count is not None:
        print(f"\n{'='*80}")
        print("✓ OPERATION COMPLETE")
        print(f"{'='*80}")
        print(f"Backup: {backup_file}")
        print(f"New cmm_gndata count: {new_count}")
    else:
        print("\nReplacement failed.")


if __name__ == "__main__":
    asyncio.run(main())
