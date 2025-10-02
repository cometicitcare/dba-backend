#!/usr/bin/env bash
set -euo pipefail

: "${PORT:=8080}"
: "${STORAGE_DIR:=/app/storage}"

# Create storage mount path if missing (works with Railway Volume)
mkdir -p "$STORAGE_DIR"

# Run DB migrations
alembic upgrade head

# Start app (adjust import path if your main is different)
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
