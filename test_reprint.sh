#!/bin/bash

# Test script for unified reprint endpoint (/api/v1/reprint)
# Covers Bhikku, Silmatha, and High Bhikku/Upasampada reprint flows.
# Auth and login pattern borrowed from test_bhikku_workflow.sh.

set -euo pipefail

BASE_URL=${BASE_URL:-"http://localhost:8000/api/v1"}
COOKIE_FILE="/tmp/reprint_test_cookies.txt"

# Supply registration numbers via env vars or args:
#   BHIKKU_REGN, SILMATHA_REGN, HIGH_BHIKKU_REGN
# Example:
#   BHIKKU_REGN=BH202500001 SILMATHA_REGN=SIL2025000001 HIGH_BHIKKU_REGN=BHR2025000001 ./test_reprint.sh

if [ $# -ge 1 ]; then
  BASE_URL="$1"
fi

echo "🔗 Using BASE_URL: $BASE_URL"
rm -f "$COOKIE_FILE"

login() {
  echo "[LOGIN] superadmin ..."
  local resp
  resp=$(curl -s -c "$COOKIE_FILE" -X POST "$BASE_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"ua_username":"superadmin","ua_password":"Admin@123"}')

  if echo "$resp" | grep -q '"ua_user_id"'; then
    echo "✅ Login OK"
  else
    echo "❌ Login failed"; echo "$resp"; exit 1
  fi
}

create_reprint() {
  local req_type=$1
  local regn=$2
  local reason=$3
  local amount=$4
  local form_no=$5

  echo "[CREATE] $req_type reprint for $regn"
  curl -s -b "$COOKIE_FILE" -X POST "$BASE_URL/reprint" \
    -H "Content-Type: application/json" \
    -d "{
      \"request_type\": \"$req_type\",
      \"regn\": \"$regn\",
      \"request_reason\": \"$reason\",
      \"amount\": $amount,
      \"form_no\": \"$form_no\",
      \"remarks\": \"Automated test for $req_type\"
    }" | python3 -m json.tool
}

approve_reprint() {
  local id=$1
  echo "[APPROVE] Request $id"
  curl -s -b "$COOKIE_FILE" -X POST "$BASE_URL/reprint/$id/approve" | python3 -m json.tool
}

reject_reprint() {
  local id=$1
  echo "[REJECT] Request $id"
  curl -s -b "$COOKIE_FILE" -X POST "$BASE_URL/reprint/$id/reject" \
    -H "Content-Type: application/json" \
    -d '{"rejection_reason":"Automated rejection"}' | python3 -m json.tool
}

complete_reprint() {
  local id=$1
  echo "[COMPLETE] Request $id (mark-printed -> COMPLETED)"
  curl -s -b "$COOKIE_FILE" -X POST "$BASE_URL/reprint/$id/mark-printed" | python3 -m json.tool
}

extract_id() {
  python3 - <<'PY'
import sys, json
data=json.load(sys.stdin)
print(data.get("data",{}).get("id",""))
PY
}

run_flow() {
  local req_type=$1
  local regn=$2
  local label=$3

  if [ -z "$regn" ]; then
    echo "⚠️  Skipping $label (no regn provided)"
    return
  fi

  create_resp=$(create_reprint "$req_type" "$regn" "Test reprint for $label" 500 "FORM-$label")
  req_id=$(echo "$create_resp" | extract_id)
  if [ -z "$req_id" ]; then
    echo "❌ Failed to create $label reprint"; echo "$create_resp"; return
  fi
  echo "   → request id: $req_id"

  approve_reprint "$req_id"
  complete_reprint "$req_id"
}

login

echo "================================================================"
echo "Running reprint flows (BHIKKU, SILMATHA, HIGH_BHIKKU)..."
echo "================================================================"

run_flow "BHIKKU" "${BHIKKU_REGN:-}" "BHIKKU"
run_flow "SILMATHA" "${SILMATHA_REGN:-}" "SILMATHA"
run_flow "HIGH_BHIKKU" "${HIGH_BHIKKU_REGN:-}" "HIGH_BHIKKU"

echo "================================================================"
echo "[LIST] Pending requests (if any)"
curl -s -b "$COOKIE_FILE" "$BASE_URL/reprint?flow_status=PENDING" | python3 -m json.tool

echo "✅ Done"
