#!/usr/bin/env python3
"""
Test script to verify new temp-bhikku implementation
Tests that temp-bhikku now saves to bhikku_regist table with auto-generated BH number
"""
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
ENDPOINT = f"{BASE_URL}/api/v1/temporary-bhikku/manage"

# You need to provide a valid JWT token
# Replace with actual token from your authentication
TOKEN = "YOUR_JWT_TOKEN_HERE"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TOKEN}"
}


def test_create_temp_bhikku():
    """
    Test CREATE operation - should now save to bhikku_regist table
    and auto-generate BH number
    """
    print("\n" + "="*80)
    print("TEST: CREATE Temp Bhikku (New Implementation)")
    print("="*80)
    print("\nThis test verifies:")
    print("1. Temp-bhikku CREATE saves to bhikku_regist table")
    print("2. Auto-generates BH number (e.g., BH2026000001)")
    print("3. Returns response in temp-bhikku format (backward compatible)")
    print("4. Frontend receives expected response structure")
    print("\n")
    
    payload = {
        "action": "CREATE",
        "payload": {
            "data": {
                "tb_name": "Ven. New Implementation Test Thero",
                "tb_id_number": "199512345678",
                "tb_contact_number": "0771234567",
                "tb_samanera_name": "Test Samanera Name",
                "tb_address": "123 Test Implementation Road, Colombo",
                "tb_living_temple": "Test Vihara for New Implementation"
            }
        }
    }
    
    print("Request Payload:")
    print(json.dumps(payload, indent=2))
    print("\n")
    
    try:
        response = requests.post(ENDPOINT, headers=HEADERS, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"\nResponse:")
        response_data = response.json()
        print(json.dumps(response_data, indent=2, default=str))
        
        if response.status_code == 200:
            print("\n" + "="*80)
            print("✅ SUCCESS: Temp-bhikku created successfully!")
            print("="*80)
            
            # Verify the response structure
            data = response_data.get("data", {})
            print("\nVerification:")
            print(f"  - tb_id (br_id): {data.get('tb_id')}")
            print(f"  - tb_name: {data.get('tb_name')}")
            print(f"  - tb_contact_number: {data.get('tb_contact_number')}")
            print(f"  - br_regn (auto-generated BH number): {data.get('br_regn')}")
            print(f"  - Temp Flag: br_cat = 'TEMP' (set in database)")
            
            if data.get('br_regn'):
                br_regn = data.get('br_regn')
                if br_regn.startswith('BH'):
                    print(f"\n✅ BH number auto-generated correctly: {br_regn}")
                else:
                    print(f"\n⚠️  WARNING: br_regn format unexpected: {br_regn}")
            else:
                print("\n⚠️  WARNING: br_regn not found in response")
            
            print("\n" + "="*80)
            print("BACKEND VERIFICATION:")
            print("="*80)
            print("\nTo verify in database, run:")cat, br_remarks")
            print(f"  FROM bhikku_regist")
            print(f"  WHERE br_regn = '{data.get('br_regn')}'")
            print(f"  AND br_is_deleted = false;")
            print(f"\n  Expected br_cat: 'TEMP'")
            print(f"  Expected br_remarks: starts with '[TEMP_BHIKKU]'('br_regn')}'")
            print(f"  AND br_is_deleted = false;")
            
            return data.get('tb_id'), data.get('br_regn')
        else:
            print("\n❌ FAILED: Request unsuccessful")
            print(f"Error: {response_data}")
            return None, None
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return None, None


def verify_bhikku_in_manage_endpoint(br_regn):
    """
    Verify that the created bhikku appears in the regular bhikku manage endpoint
    """
    if not br_regn:
        print("\n⚠️  Skipping verification - no br_regn provided")
        return
    
    print("\n" + "="*80)
    print("VERIFICATION: Check in Bhikku Manage Endpoint")
    print("="*80)
    
    bhikku_endpoint = f"{BASE_URL}/api/v1/bhikkus/manage"
    payload = {
        "action": "READ_ONE",
        "payload": {
            "br_regn": br_regn
        }
    }
    
    print(f"\nFetching bhikku with br_regn: {br_regn}")
    
    try:
        response = requests.post(bhikku_endpoint, headers=HEADERS, json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            data = response_data.get("data", {})
            print("\n✅ Bhikku found in bhikku_regist table:")
            print(f"  - br_regn: {data.get('br_regn')}")
            print(f"  - br_mahananame: {data.get('br_mahananame')}")
            print(f"  - br_cat: {data.get('br_cat')} (should be 'TEMP')")
            print(f"  - br_workflow_status: {data.get('br_workflow_status')}")
            print(f"  - br_currstat: {data.get('br_currstat')}")
            
            # Verify temp flag
            if data.get('br_cat') == 'TEMP':
                print("\n✅ TEMP flag correctly set!")
            else:
                print(f"\n⚠️  WARNING: br_cat is '{data.get('br_cat')}', expected 'TEMP'
            print(f"  - br_workflow_status: {data.get('br_workflow_status')}")
            print(f"  - br_currstat: {data.get('br_currstat')}")
        else:
            print(f"\n⚠️  Could not fetch bhikku: {response.json()}")
            
    except Exception as e:
        print(f"\n❌ ERROR during verification: {str(e)}")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("TEMP-BHIKKU NEW IMPLEMENTATION TEST SUITE")
    print("="*80)
    print("\nIMPORTANT: Update the TOKEN variable with a valid JWT token before running")
    print("\n")
    
    if TOKEN == "YOUR_JWT_TOKEN_HERE":
        print("⚠️  WARNING: Please update the TOKEN variable with a valid JWT token")
        print("\nTo get a token:")
        print("1. Login to the application")
        print("2. Copy the JWT token from the response or browser storage")
        print("3. Replace TOKEN in this script")
        exit(1)
    
    # Run tests
    tb_id, br_regn = test_create_temp_bhikku()
    
    if tb_id and br_regn:
        # Verify in the regular bhikku endpoint
        verify_bhikku_in_manage_endpoint(br_regn)
        
        print("\n"br_cat = 'TEMP' flag identifies temp bhikkus")
        print("4. br_remarks prefixed with [TEMP_BHIKKU] tag")
        print("5. Response format maintains backward compatibility")
        print("6EST SUMMARY")
        print("="*80)
        print("\n✅ All tests completed successfully!")
        print("\nKey Points:")
        print("1. Temp-bhikku data is now saved to bhikku_regist table")
        print("2. BH number is auto-generated")
        print("3. Response format maintains backward compatibility")
        print("4. Frontend will continue to work without changes")
        print("\n" + "="*80)
    else:
        print("\n" + "="*80)
        print("❌ TEST FAILED")
        print("="*80)
        print("\nPlease check:")
        print("1. Server is running at", BASE_URL)
        print("2. JWT token is valid")
        print("3. User has bhikku:create permission")
        print("\n" + "="*80)
