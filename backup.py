#!/usr/bin/env python3
"""
Database Backup Script
======================
Creates a full backup (dump) of the PostgreSQL database.
Downloads it to the current directory with a timestamp.

Usage:
    python backup.py [database_name]
    
Examples:
    python backup.py                    # Backs up dbahrms-new (default)
    python backup.py dbahrms-production # Backs up dbahrms-production
"""

import os
import sys
import subprocess
from datetime import datetime

# Database configuration
POSTGRES_HOST = "gondola.proxy.rlwy.net"
POSTGRES_PORT = "22000"
POSTGRES_USER = "app_admin"
POSTGRES_PASSWORD = "rX2SWDbFuM%Qe3kBRzqnQ&Ia"
DEFAULT_DB = "dbahrms-new"


def backup_database(database_name=DEFAULT_DB):
    """
    Creates a full backup dump of the specified PostgreSQL database.
    
    Args:
        database_name (str): Name of the database to backup
        
    Returns:
        bool: True if backup successful, False otherwise
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"backup_{database_name}_{timestamp}.dump"
    
    print(f"Starting backup of database: {database_name}")
    print(f"Output file: {backup_filename}")
    print("-" * 60)
    
    # Build pg_dump command
    cmd = [
        "pg_dump",
        "-h", POSTGRES_HOST,
        "-p", POSTGRES_PORT,
        "-U", POSTGRES_USER,
        "-F", "c",  # Custom format (compressed)
        "-v",  # Verbose
        "-f", backup_filename,
        database_name
    ]
    
    # Set environment variable for password
    env = os.environ.copy()
    env["PGPASSWORD"] = POSTGRES_PASSWORD
    
    try:
        result = subprocess.run(cmd, env=env, capture_output=False, text=True)
        
        if result.returncode == 0:
            # Get file size
            file_size = os.path.getsize(backup_filename)
            size_mb = file_size / (1024 * 1024)
            
            print("-" * 60)
            print(f"✓ Backup completed successfully!")
            print(f"✓ File: {backup_filename}")
            print(f"✓ Size: {size_mb:.2f} MB")
            return True
        else:
            print(f"✗ Backup failed with return code: {result.returncode}")
            return False
            
    except FileNotFoundError:
        print("✗ Error: pg_dump not found. Please install PostgreSQL client tools.")
        print("  On macOS: brew install libpq")
        print("  On Ubuntu/Debian: sudo apt-get install postgresql-client")
        return False
    except Exception as e:
        print(f"✗ Error during backup: {e}")
        return False


def restore_database(backup_file, target_db=DEFAULT_DB):
    """
    Restores a database from a backup dump file.
    
    Args:
        backup_file (str): Path to the backup dump file
        target_db (str): Target database name to restore to
        
    Returns:
        bool: True if restore successful, False otherwise
    """
    if not os.path.exists(backup_file):
        print(f"✗ Error: Backup file not found: {backup_file}")
        return False
    
    print(f"Starting restore from: {backup_file}")
    print(f"Target database: {target_db}")
    print("-" * 60)
    
    # Build pg_restore command
    cmd = [
        "pg_restore",
        "-h", POSTGRES_HOST,
        "-p", POSTGRES_PORT,
        "-U", POSTGRES_USER,
        "-d", target_db,
        "-v",
        backup_file
    ]
    
    # Set environment variable for password
    env = os.environ.copy()
    env["PGPASSWORD"] = POSTGRES_PASSWORD
    
    try:
        result = subprocess.run(cmd, env=env, capture_output=False, text=True)
        
        if result.returncode == 0:
            print("-" * 60)
            print(f"✓ Restore completed successfully!")
            print(f"✓ Database: {target_db}")
            return True
        else:
            print(f"✗ Restore failed with return code: {result.returncode}")
            return False
            
    except FileNotFoundError:
        print("✗ Error: pg_restore not found. Please install PostgreSQL client tools.")
        return False
    except Exception as e:
        print(f"✗ Error during restore: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        print(__doc__)
        sys.exit(0)
    
    # Get database name from command line or use default
    db_name = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DB
    
    # Run backup
    success = backup_database(db_name)
    sys.exit(0 if success else 1)
