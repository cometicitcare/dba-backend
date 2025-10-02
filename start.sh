#!/usr/bin/env bash
set -euo pipefail

: "${PORT:=8080}"
: "${STORAGE_DIR:=/home/appuser/storage}"

# Ensure storage directory exists (works with or without a mounted volume)
mkdir -p "$STORAGE_DIR" || true

# Run DB migrations (requires DATABASE_URL to be set by Railway Postgres plugin)
alembic upgrade head

# Start FastAPI app
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
