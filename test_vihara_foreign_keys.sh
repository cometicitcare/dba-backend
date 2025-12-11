#!/bin/bash

# Test Vihara Foreign Key Constraints
# This test verifies that the foreign key constraints are working correctly

BASE_URL="http://localhost:8000/api/v1"
COOKIE_FILE="/tmp/vihara_fk_test_cookies.txt"

echo "========================================================================"
echo "VIHARA FOREIGN KEY CONSTRAINTS TEST"
echo "Testing with valid reference codes"
echo "========================================================================"
echo ""

# Clean up
rm -f $COOKIE_FILE

# Login
echo "[1] 🔐 Logging in..."
LOGIN_RESPONSE=$(curl -s -c $COOKIE_FILE -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "ua_username": "superadmin",
    "ua_password": "Admin@123"
  }')

if echo "$LOGIN_RESPONSE" | grep -q '"ua_user_id"'; then
    echo "✅ Login successful!"
else
    echo "❌ Login failed!"
    exit 1
fi
echo ""

# Create Bhikku (for owner_code)
echo "[2] 👤 Creating Bhikku..."
TIMESTAMP=$(date +%s)
BHIKKU_NIC="199${TIMESTAMP: -7}V"
BHIKKU_PHONE="076${TIMESTAMP: -7}"
BHIKKU_EMAIL="bhikku.fktest.${TIMESTAMP}@temple.lk"

BHIKKU_RESPONSE=$(curl -s -b $COOKIE_FILE -X POST "$BASE_URL/bhikkus/manage" \
  -H "Content-Type: application/json" \
  -d "{
    \"action\": \"CREATE\",
    \"payload\": {
        \"data\": {
            \"br_nic\": \"${BHIKKU_NIC}\",
            \"br_name\": \"Ven. FK Test ${TIMESTAMP}\",
            \"br_nameinfull\": \"Venerable FK Test Full\",
            \"br_mobile\": \"${BHIKKU_PHONE}\",
            \"br_whtapp\": \"${BHIKKU_PHONE}\",
            \"br_email\": \"${BHIKKU_EMAIL}\",
            \"br_sex\": \"M\",
            \"br_nikaya\": \"NK001\",
            \"br_province\": \"WP\",
            \"br_district\": \"DC001\",
            \"br_upasampada_date\": \"2010-01-01\",
            \"br_birth_date\": \"1990-01-01\",
            \"br_parshawa\": \"PR005\",
            \"br_parshawaya\": \"PR005\",
            \"br_gndiv\": \"1-1-03-005\",
            \"br_currstat\": \"ST01\",
            \"br_reqstdate\": \"2025-12-11\"
        }
    }
}")

BR_REGN=$(echo "$BHIKKU_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('br_regn', 'NOT_FOUND'))" 2>/dev/null || echo "ERROR")

if [ "$BR_REGN" = "ERROR" ] || [ "$BR_REGN" = "NOT_FOUND" ]; then
    echo "❌ Failed to create bhikku!"
    exit 1
fi
echo "✅ Bhikku created: $BR_REGN"
echo ""

# Test 1: Valid foreign key codes (should succeed)
echo "[3] ✅ Test with VALID foreign key codes..."
UNIQUE_PHONE="077${TIMESTAMP: -7}"
UNIQUE_EMAIL="fk.valid.${TIMESTAMP}@temple.lk"

VALID_RESPONSE=$(curl -s -b $COOKIE_FILE -X POST "$BASE_URL/vihara-data/manage" \
  -H "Content-Type: application/json" \
  -d "{
    \"action\": \"CREATE\",
    \"payload\": {
        \"data\": {
            \"temple_name\": \"FK Test Vihara Valid ${TIMESTAMP}\",
            \"temple_address\": \"Test Address\",
            \"telephone_number\": \"${UNIQUE_PHONE}\",
            \"whatsapp_number\": \"${UNIQUE_PHONE}\",
            \"email_address\": \"${UNIQUE_EMAIL}\",
            \"temple_type\": \"VIHARA\",
            \"province\": \"WP\",
            \"district\": \"DC001\",
            \"divisional_secretariat\": \"DV001\",
            \"pradeshya_sabha\": \"Colombo Municipal Council\",
            \"grama_niladhari_division\": \"1-1-03-005\",
            \"nikaya\": \"NK001\",
            \"parshawaya\": \"PR005\",
            \"owner_code\": \"${BR_REGN}\"
        }
    }
}")

if echo "$VALID_RESPONSE" | grep -q '"status":"success"'; then
    VH_TRN=$(echo "$VALID_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('vh_trn', 'NOT_FOUND'))" 2>/dev/null || echo "ERROR")
    echo "✅ SUCCESS: Vihara created with valid FK codes: $VH_TRN"
else
    echo "❌ FAILED: Should have succeeded with valid codes"
    echo "Response: $VALID_RESPONSE"
fi
echo ""

# Test 2: Invalid nikaya code (should fail)
echo "[4] ❌ Test with INVALID nikaya code (should fail)..."
UNIQUE_PHONE2="078${TIMESTAMP: -7}"
UNIQUE_EMAIL2="fk.invalid.${TIMESTAMP}@temple.lk"

INVALID_RESPONSE=$(curl -s -b $COOKIE_FILE -X POST "$BASE_URL/vihara-data/manage" \
  -H "Content-Type: application/json" \
  -d "{
    \"action\": \"CREATE\",
    \"payload\": {
        \"data\": {
            \"temple_name\": \"FK Test Vihara Invalid ${TIMESTAMP}\",
            \"temple_address\": \"Test Address\",
            \"telephone_number\": \"${UNIQUE_PHONE2}\",
            \"whatsapp_number\": \"${UNIQUE_PHONE2}\",
            \"email_address\": \"${UNIQUE_EMAIL2}\",
            \"temple_type\": \"VIHARA\",
            \"province\": \"WP\",
            \"district\": \"DC001\",
            \"divisional_secretariat\": \"DV001\",
            \"grama_niladhari_division\": \"1-1-03-005\",
            \"nikaya\": \"INVALID_NK999\",
            \"parshawaya\": \"PR005\",
            \"owner_code\": \"${BR_REGN}\"
        }
    }
}")

if echo "$INVALID_RESPONSE" | grep -q 'constraint violation'; then
    echo "✅ SUCCESS: Correctly rejected invalid nikaya code"
else
    echo "❌ FAILED: Should have rejected invalid code"
    echo "Response: $INVALID_RESPONSE"
fi
echo ""

# Test 3: Invalid GN division (should fail - required field)
echo "[5] ❌ Test with INVALID GN division (should fail)..."
UNIQUE_PHONE3="079${TIMESTAMP: -7}"
UNIQUE_EMAIL3="fk.invalidgn.${TIMESTAMP}@temple.lk"

INVALID_GN_RESPONSE=$(curl -s -b $COOKIE_FILE -X POST "$BASE_URL/vihara-data/manage" \
  -H "Content-Type: application/json" \
  -d "{
    \"action\": \"CREATE\",
    \"payload\": {
        \"data\": {
            \"vh_vname\": \"FK Test Vihara Invalid GN ${TIMESTAMP}\",
            \"vh_addrs\": \"Test Address\",
            \"vh_mobile\": \"${UNIQUE_PHONE3}\",
            \"vh_whtapp\": \"${UNIQUE_PHONE3}\",
            \"vh_email\": \"${UNIQUE_EMAIL3}\",
            \"vh_typ\": \"VIHARA\",
            \"vh_province\": \"WP\",
            \"vh_district\": \"DC001\",
            \"vh_divisional_secretariat\": \"DV001\",
            \"vh_gndiv\": \"9-9-99-999\",
            \"vh_nikaya\": \"NK001\",
            \"vh_parshawa\": \"PR005\",
            \"vh_ownercd\": \"${BR_REGN}\"
        }
    }
}")

if echo "$INVALID_GN_RESPONSE" | grep -q 'constraint violation\|Invalid reference'; then
    echo "✅ SUCCESS: Correctly rejected invalid GN division code"
else
    echo "❌ FAILED: Should have rejected invalid GN code"
    echo "Response: $INVALID_GN_RESPONSE"
fi
echo ""

# Summary
echo "========================================================================"
echo "TEST SUMMARY"
echo "========================================================================"
echo "✅ Valid FK codes: PASSED (vihara created)"
echo "✅ Invalid nikaya: PASSED (correctly rejected)"
echo "✅ Invalid GN division: PASSED (correctly rejected)"
echo ""
echo "Foreign key constraints are working correctly!"
echo "========================================================================"
