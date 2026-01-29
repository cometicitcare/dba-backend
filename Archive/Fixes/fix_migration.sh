#!/usr/bin/env bash
# This script fixes the Alembic migration history mismatch
# Use this ONCE to fix the production database

set -euo pipefail

echo "Fixing Alembic migration history..."

# Get the latest revision
LATEST_REVISION="20251115160000"

echo "Stamping database with revision: $LATEST_REVISION"

# Check if DATABASE_URL is set
if [ -z "${DATABASE_URL:-}" ]; then
    echo "ERROR: DATABASE_URL environment variable is not set"
    echo "Please set it first: export DATABASE_URL='your_database_url'"
    exit 1
fi

echo "Using DATABASE_URL: ${DATABASE_URL%%@*}@***" # Hide password in output

# Option 1: Try using psql if available
if command -v psql &> /dev/null; then
    echo "Using psql to fix database..."
    psql "$DATABASE_URL" -c "DELETE FROM alembic_version;"
    psql "$DATABASE_URL" -c "INSERT INTO alembic_version (version_num) VALUES ('$LATEST_REVISION');"
    echo "✓ Database fixed using psql"
else
    # Option 2: Use Python
    echo "Using Python to fix database..."
    python3 <<EOF
from sqlalchemy import create_engine, text
import os

db_url = os.environ.get('DATABASE_URL')
engine = create_engine(db_url)
with engine.connect() as conn:
    conn.execute(text("DELETE FROM alembic_version"))
    conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('$LATEST_REVISION')"))
    conn.commit()
print("✓ Database fixed using Python")
EOF
fi

echo ""
echo "Migration history fixed!"
echo "The database is now marked as being at revision: $LATEST_REVISION"
echo ""
echo "You can now run: alembic upgrade head"
