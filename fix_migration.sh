#!/usr/bin/env bash
# This script fixes the Alembic migration history mismatch
# Use this ONCE to fix the production database

set -euo pipefail

echo "Fixing Alembic migration history..."

# First, clear the alembic_version table and stamp it with the latest revision
# This tells Alembic to consider the database at the latest state without running migrations

# Get the latest revision
LATEST_REVISION="20251115160000"

echo "Stamping database with revision: $LATEST_REVISION"

# Option 1: If you have direct database access
# psql $DATABASE_URL -c "DELETE FROM alembic_version;"
# alembic stamp $LATEST_REVISION

# Option 2: Use alembic stamp with --purge to clear and set
alembic stamp --purge head

echo "Migration history fixed!"
echo "The database is now marked as being at the latest revision."
