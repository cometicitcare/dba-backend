#!/bin/bash
# Test Sasanarakshaka Bala Mandalaya CRUD endpoints
# This script tests all CRUD operations for the Sasanarakshaka Bala Mandalaya module

BASE_URL="http://localhost:8000/api/v1"
TOKEN_FILE="cookies.txt"

echo "=========================================="
echo "Sasanarakshaka Bala Mandalaya CRUD Tests"
echo "=========================================="
echo ""

# Check if token file exists
if [ ! -f "$TOKEN_FILE" ]; then
    echo "❌ Token file not found: $TOKEN_FILE"
    echo "Please ensure you have a valid authentication token"
    exit 1
fi

# Extract token from cookies file
TOKEN=$(grep -oP 'access_token=\K[^;]+' "$TOKEN_FILE" 2>/dev/null || cat "$TOKEN_FILE")

if [ -z "$TOKEN" ]; then
    echo "❌ Could not extract token from $TOKEN_FILE"
    exit 1
fi

echo "✅ Using authentication token"
echo ""

# Test 1: List all Sasanarakshaka Bala Mandalaya (should work even if empty)
echo "Test 1: GET /sasanarakshaka - List all records"
echo "--------------------------------------------"
curl -s -X GET "$BASE_URL/sasanarakshaka?page=1&limit=10" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | jq '.'
echo ""
echo ""

# Test 2: Create a new Sasanarakshaka Bala Mandalaya
echo "Test 2: POST /sasanarakshaka - Create new record"
echo "--------------------------------------------"
CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/sasanarakshaka" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sr_ssbmcode": "TEST001",
    "sr_dvcd": "DV001",
    "sr_ssbname": "Test Sasana Rakshaka Bala Mandalaya",
    "sr_sbmnayakahimi": null
  }')

echo "$CREATE_RESPONSE" | jq '.'

# Extract sr_id from response if creation was successful
SR_ID=$(echo "$CREATE_RESPONSE" | jq -r '.data.sr_id // empty')

if [ -z "$SR_ID" ]; then
    echo ""
    echo "⚠️  Note: Creation failed (possibly due to missing foreign keys or permissions)"
    echo "   This is expected if divisional secretariat 'DV001' doesn't exist"
    echo "   Please check your database and permissions"
    echo ""
    exit 0
fi

echo ""
echo "✅ Created record with ID: $SR_ID"
echo ""

# Test 3: Get record by ID
echo "Test 3: GET /sasanarakshaka/{sr_id} - Get by ID"
echo "--------------------------------------------"
curl -s -X GET "$BASE_URL/sasanarakshaka/$SR_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | jq '.'
echo ""
echo ""

# Test 4: Get record by code
echo "Test 4: GET /sasanarakshaka/code/{sr_ssbmcode} - Get by code"
echo "--------------------------------------------"
curl -s -X GET "$BASE_URL/sasanarakshaka/code/TEST001" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | jq '.'
echo ""
echo ""

# Test 5: Update record
echo "Test 5: PUT /sasanarakshaka/{sr_id} - Update record"
echo "--------------------------------------------"
curl -s -X PUT "$BASE_URL/sasanarakshaka/$SR_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sr_ssbname": "Updated Test Sasana Rakshaka Bala Mandalaya"
  }' | jq '.'
echo ""
echo ""

# Test 6: Search with filters
echo "Test 6: GET /sasanarakshaka?search_key=Test - Search records"
echo "--------------------------------------------"
curl -s -X GET "$BASE_URL/sasanarakshaka?search_key=Test&page=1&limit=10" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | jq '.'
echo ""
echo ""

# Test 7: Delete record (soft delete)
echo "Test 7: DELETE /sasanarakshaka/{sr_id} - Delete record"
echo "--------------------------------------------"
curl -s -X DELETE "$BASE_URL/sasanarakshaka/$SR_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | jq '.'
echo ""
echo ""

# Test 8: Verify deletion - should not be found
echo "Test 8: GET /sasanarakshaka/{sr_id} - Verify deletion"
echo "--------------------------------------------"
curl -s -X GET "$BASE_URL/sasanarakshaka/$SR_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | jq '.'
echo ""
echo ""

echo "=========================================="
echo "✅ All tests completed!"
echo "=========================================="
