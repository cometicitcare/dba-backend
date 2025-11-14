#!/usr/bin/env bash
set -euo pipefail

: "${PORT:=8080}"
: "${STORAGE_DIR:=/home/appuser/storage}"
: "${APP_USER:=appuser}"

# When running as root (e.g., in Railway), fix storage perms then drop to APP_USER
if [ "$(id -u)" -eq 0 ]; then
    mkdir -p "$STORAGE_DIR" || true
    chown -R "$APP_USER":"$APP_USER" "$STORAGE_DIR" || true
    exec gosu "$APP_USER" "$0" "$@"
fi

# Ensure storage directory exists (works with or without a mounted volume)
mkdir -p "$STORAGE_DIR" || true

# Run DB migrations (requires DATABASE_URL to be set by Railway Postgres plugin)
alembic upgrade head

# Start FastAPI app
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
