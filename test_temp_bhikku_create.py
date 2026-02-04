#!/usr/bin/env python3
"""
Test script for temporary bhikku CREATE endpoint
Tests that data is saved to bhikku_regist table with auto-generated BH number
and returns enriched response with nested objects
"""
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
ENDPOINT = "/api/v1/temporary-bhikku/manage"

# Read token from cookies.txt
with open("cookies.txt", "r") as f:
    token = f.read().strip()

# Headers
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Test payload - using the format from the user
test_payload = {
    "action": "CREATE",
    "payload": {
        "data": {
            "tb_bname": "Test009",
            "tb_name": "Test009",
            "tb_address": "Test009",
            "tb_district": "කොළඹ",
            "tb_province": "North Central Province",
            "tb_vihara_name": "Test009"
        }
    }
}

print("=" * 80)
print("Testing Temporary Bhikku CREATE Endpoint")
print("=" * 80)
print(f"\nEndpoint: {BASE_URL}{ENDPOINT}")
print(f"\nPayload:")
print(json.dumps(test_payload, indent=2, ensure_ascii=False))
print("\n" + "=" * 80)

# Make request
try:
    response = requests.post(
        f"{BASE_URL}{ENDPOINT}",
        headers=headers,
        json=test_payload,
        timeout=10
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print("\nResponse:")
    
    if response.status_code == 200:
        response_data = response.json()
        print(json.dumps(response_data, indent=2, ensure_ascii=False))
        
        # Validate response structure
        print("\n" + "=" * 80)
        print("Validation Results:")
        print("=" * 80)
        
        if response_data.get("status") == "success":
            print("✓ Status: success")
        else:
            print("✗ Status: NOT success")
        
        data = response_data.get("data", {})
        
        # Check for BH number
        br_regn = data.get("br_regn", "")
        if br_regn and br_regn.startswith("BH"):
            print(f"✓ Auto-generated BH number: {br_regn}")
        else:
            print(f"✗ BH number not generated or invalid: {br_regn}")
        
        # Check for nested objects (foreign keys)
        nested_checks = {
            "br_province": "Province",
            "br_district": "District",
            "br_currstat": "Current Status",
            "br_parshawaya": "Parshawa",
            "br_cat": "Category"
        }
        
        print("\nNested Object Checks:")
        for field, label in nested_checks.items():
            value = data.get(field)
            if isinstance(value, dict):
                print(f"  ✓ {label} ({field}): {value}")
            elif value:
                print(f"  ✗ {label} ({field}): Plain value, not nested object - {value}")
            else:
                print(f"  - {label} ({field}): Not present or null")
        
        # Check basic fields
        print("\nBasic Field Checks:")
        if data.get("br_mahananame") == "Test009":
            print(f"  ✓ br_mahananame: {data.get('br_mahananame')}")
        else:
            print(f"  ✗ br_mahananame: Expected 'Test009', got '{data.get('br_mahananame')}'")
        
        if data.get("br_fathrsaddrs") == "Test009":
            print(f"  ✓ br_fathrsaddrs: {data.get('br_fathrsaddrs')}")
        else:
            print(f"  ✗ br_fathrsaddrs: Expected 'Test009', got '{data.get('br_fathrsaddrs')}'")
        
        print("\n" + "=" * 80)
        print("Test completed successfully!")
        print("=" * 80)
        
    else:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        print(f"\n✗ Request failed with status code: {response.status_code}")

except requests.exceptions.RequestException as e:
    print(f"\n✗ Request error: {e}")
except json.JSONDecodeError as e:
    print(f"\n✗ JSON decode error: {e}")
    print(f"Response text: {response.text}")
except Exception as e:
    print(f"\n✗ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
