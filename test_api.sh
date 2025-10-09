#!/bin/bash

BASE_URL="http://localhost:8000/api/v1"

echo "1. Health Check..."
curl -s $BASE_URL/health | jq

echo -e "\n2. Get Roles..."
curl -s $BASE_URL/auth/roles | jq

echo -e "\n3. Register User..."
REGISTER_RESPONSE=$(curl -s -X POST $BASE_URL/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "ua_username": "testuser1",
    "ua_password": "Test123!",
    "ua_email": "test1@example.com",
    "ua_first_name": "Test",
    "ua_last_name": "User",
    "ro_role_id": "ADMIN"
  }')
echo $REGISTER_RESPONSE | jq

echo -e "\n4. Login..."
LOGIN_RESPONSE=$(curl -s -X POST $BASE_URL/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "ua_username": "testuser1",
    "ua_password": "Test123!"
  }')
echo $LOGIN_RESPONSE | jq

SESSION_ID=$(echo $LOGIN_RESPONSE | jq -r '.session_id')
echo -e "\nSession ID: $SESSION_ID"

echo -e "\n5. Create Bhikku..."
curl -s -X POST $BASE_URL/bhikkus/manage \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $SESSION_ID" \
  -d '{
    "action": "CREATE",
    "payload": {
      "data": {
        "br_regn": "TEST001",
        "br_reqstdate": "2024-01-15",
        "br_gndiv": "GN001",
        "br_currstat": "ACT",
        "br_parshawaya": "PS001",
        "br_livtemple": "TM001",
        "br_mahanatemple": "MT001",
        "br_mahanaacharyacd": "MA001"
      }
    }
  }' | jq

echo -e "\n✅ Tests completed!"