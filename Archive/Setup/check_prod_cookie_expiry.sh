#!/usr/bin/env bash

# Check production login cookie expiry for access_token and refresh_token
# Usage: BASE_URL=https://api.dbagovlk.com/api/v1 UA_USERNAME=superadmin UA_PASSWORD=Admin@123 ./check_prod_cookie_expiry.sh

set -euo pipefail

BASE_URL="${BASE_URL:-https://api.dbagovlk.com/api/v1}"
LOGIN_ENDPOINT="${LOGIN_ENDPOINT:-$BASE_URL/auth/login}"
UA_USERNAME="${UA_USERNAME:-superadmin}"
UA_PASSWORD="${UA_PASSWORD:-Admin@123}"

HEADERS_FILE=$(mktemp)
BODY_FILE=$(mktemp)
trap 'rm -f "$HEADERS_FILE" "$BODY_FILE"' EXIT

echo "================================================================================"
echo "Cookie expiry check against: $LOGIN_ENDPOINT"
echo "--------------------------------------------------------------------------------"

# Capture headers for the login call
curl -s -D "$HEADERS_FILE" -o "$BODY_FILE" -X POST "$LOGIN_ENDPOINT" \
  -H "Content-Type: application/json" \
  -d "{\"ua_username\":\"$UA_USERNAME\",\"ua_password\":\"$UA_PASSWORD\"}"

STATUS_LINE=$(head -n 1 "$HEADERS_FILE" | tr -d '\r')
echo "HTTP status: $STATUS_LINE"
echo ""

SET_COOKIES=$(grep -i '^set-cookie:' "$HEADERS_FILE" || true)
if [ -z "$SET_COOKIES" ]; then
  echo "No Set-Cookie headers found. Check credentials or endpoint."
  exit 1
fi

echo "Raw Set-Cookie headers:"
echo "$SET_COOKIES"
echo ""

process_cookie() {
  local cookie_name="$1"
  local header_line
  header_line=$(grep -i "set-cookie: ${cookie_name}" "$HEADERS_FILE" || true)

  echo "[$cookie_name]"
  if [ -z "$header_line" ]; then
    echo "  Not present"
    echo ""
    return
  fi

  local max_age expires
  max_age=$(echo "$header_line" | grep -oE "Max-Age=[0-9]+" | cut -d= -f2 || true)
  expires=$(echo "$header_line" | grep -oE "Expires=[^;]*" | cut -d= -f2- || true)

  if [ -n "$max_age" ]; then
    local minutes hours days
    minutes=$((max_age / 60))
    hours=$((max_age / 3600))
    days=$((max_age / 86400))
    echo "  Max-Age: $max_age seconds (~${minutes}m / ${hours}h / ${days}d)"
  else
    echo "  Max-Age: not found"
  fi

  if [ -n "$expires" ]; then
    EXPIRES_VALUE="$expires" python3 - <<'PY'
import os
import datetime
import email.utils

expires = os.environ["EXPIRES_VALUE"]
print(f"  Expires: {expires}")
try:
    dt = email.utils.parsedate_to_datetime(expires)
    now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    delta = dt - now
    total = int(delta.total_seconds())
    hours = total // 3600
    minutes = (total % 3600) // 60
    days = total // 86400
    print(f"  Time until expiry: {total} seconds (~{hours}h {minutes}m / {days}d)")
except Exception as exc:  # noqa: BLE001
    print(f"  Could not parse Expires header: {exc}")
PY
  else
    echo "  Expires: not found"
  fi

  echo ""
}

process_cookie "access_token"
process_cookie "refresh_token"

echo "Done."
