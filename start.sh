#!/usr/bin/env bash
set -eo pipefail

: "${PORT:=8080}"
: "${STORAGE_DIR:=/home/appuser/storage}"

# Ensure storage directory exists (works with or without a mounted volume)
mkdir -p "$STORAGE_DIR" || true

# Run DB migrations (requires DATABASE_URL to be set by Railway Postgres plugin)
echo "Running database migrations..."

# Capture the output to check for specific errors
MIGRATION_OUTPUT=$(alembic upgrade head 2>&1) || MIGRATION_EXIT_CODE=$?

if [ -z "${MIGRATION_EXIT_CODE}" ]; then
    echo "✓ Migrations completed successfully"
else
    echo "⚠ Migration failed - checking for revision mismatch..."
    
    # Check if the error is related to missing revision
    if echo "$MIGRATION_OUTPUT" | grep -q "Can't locate revision"; then
        echo "⚠ Found missing revision in database history"
        echo "⚠ Clearing alembic_version table and stamping with head..."
        
        # Get the current head revision
        HEAD_REVISION=$(alembic heads | grep -oE '[a-f0-9]{12}' | head -1)
        
        if [ -z "$HEAD_REVISION" ]; then
            # Fallback to hardcoded latest revision
            HEAD_REVISION="20251115160000"
        fi
        
        echo "⚠ Using revision: $HEAD_REVISION"
        
        # Directly update the database to clear the bad revision
        # This uses psql if available, otherwise falls back to Python
        if command -v psql &> /dev/null && [ -n "$DATABASE_URL" ]; then
            echo "⚠ Using psql to fix database..."
            psql "$DATABASE_URL" -c "DELETE FROM alembic_version;" || true
            psql "$DATABASE_URL" -c "INSERT INTO alembic_version (version_num) VALUES ('$HEAD_REVISION');"
        else
            # Use Python to fix the database
            echo "⚠ Using Python to fix database..."
            python3 <<EOF
import os
from sqlalchemy import create_engine, text

db_url = os.environ.get('DATABASE_URL')
if db_url:
    # Use psycopg2 instead of asyncpg for sync operations
    if db_url.startswith('postgresql+asyncpg://'):
        db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
    engine = create_engine(db_url)
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM alembic_version"))
        conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('$HEAD_REVISION')"))
    print("✓ Database fixed using Python")
else:
    print("✗ DATABASE_URL not set")
    exit(1)
EOF
        fi
        
        echo "✓ Database stamped successfully"
        echo "Running migrations again..."
        alembic upgrade head
        echo "✓ Migrations completed after fix"
    else
        echo "✗ Migration failed for unknown reason:"
        echo "$MIGRATION_OUTPUT"
        exit 1
    fi
fi

echo "Starting FastAPI application..."
# Start FastAPI app
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
