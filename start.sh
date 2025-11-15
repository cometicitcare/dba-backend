#!/usr/bin/env bash
set -eo pipefail

: "${PORT:=8080}"
: "${STORAGE_DIR:=/home/appuser/storage}"

# Ensure storage directory exists (works with or without a mounted volume)
mkdir -p "$STORAGE_DIR" || true

# Run DB migrations (requires DATABASE_URL to be set by Railway Postgres plugin)
# If migration fails due to missing revision, stamp the database with the latest revision
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
        echo "⚠ Stamping database with current head to fix..."
        
        # Stamp the database with the current head to fix migration history issues
        alembic stamp head --purge
        
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
