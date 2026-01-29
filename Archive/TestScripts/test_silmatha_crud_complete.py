#!/usr/bin/env python3
"""
Complete test for Silmatha CREATE, READ, and UPDATE operations
Tests field preservation during updates to ensure no data loss
"""

import requests
import json
from datetime import datetime, date

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
AUTH_TOKEN = "your_token_here"  # Replace with actual token

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {AUTH_TOKEN}"
}

# ============================================================================
# TEST PAYLOADS
# ============================================================================

# Initial CREATE payload with all fields
CREATE_PAYLOAD = {
    "action": "CREATE",
    "payload": {
        "data": {
            "sil_reqstdate": "2025-12-31",
            "sil_form_id": "0005",
            "sil_gihiname": "testGihi",
            "sil_dofb": "1999-12-29",
            "sil_fathrname": "jayathilaka",
            "sil_email": "test@example.com",
            "sil_mobile": "0712345678",
            "sil_fathrsaddrs": "123 Main Street, Colombo",
            "sil_fathrsmobile": "0987654321",
            "sil_birthpls": "colombo",
            "sil_province": "CP",
            "sil_district": "DC006",
            "sil_division": "",
            "sil_gndiv": "",
            "sil_korale": "",
            "sil_pattu": "",
            "sil_vilage": "",
            "sil_aramadhipathi": "TEMP-11",
            "sil_mahananame": "siridhamma",
            "sil_mahanadate": "2020-01-07",
            "sil_mahanaacharyacd": "TEMP-12",
            "sil_robing_tutor_residence": "ARN0000002",
            "sil_mahanatemple": "ARN0000001",
            "sil_robing_after_residence_temple": "ARN0000001",
            "sil_declaration_date": "2025-12-31",
            "sil_remarks": "NA",
            "sil_currstat": "ST01",
            "sil_cat": "CAT01",
            "sil_student_signature": True,
            "sil_acharya_signature": True,
            "sil_aramadhipathi_signature": True,
            "sil_district_secretary_signature": True
        }
    }
}

# UPDATE payload - only update some fields, others should remain unchanged
UPDATE_PAYLOAD_PARTIAL = {
    "action": "UPDATE",
    "payload": {
        "sil_regn": "WILL_BE_SET",  # Will be updated with the created record's regn
        "data": {
            "sil_gihiname": "updatedGihi",  # CHANGED
            "sil_mahananame": "updatedMahananame",  # CHANGED
            # NOTE: NOT updating sil_email, sil_mobile, sil_fathrname - should remain unchanged
        }
    }
}

# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def test_create_silmatha():
    """Test CREATE operation"""
    print("\n" + "="*80)
    print("TEST 1: CREATE Silmatha Record")
    print("="*80)
    
    try:
        response = requests.post(
            f"{BASE_URL}/silmatha-regist/manage",
            json=CREATE_PAYLOAD,
            headers=HEADERS
        )
        
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2, default=str)}")
        
        if response.status_code in [200, 201]:
            created_regn = result.get("data", {}).get("sil_regn")
            print(f"\n✓ CREATE successful!")
            print(f"  Created record with sil_regn: {created_regn}")
            return created_regn
        else:
            print(f"\n✗ CREATE failed!")
            return None
            
    except Exception as e:
        print(f"\n✗ Error during CREATE: {str(e)}")
        return None


def test_read_silmatha(sil_regn):
    """Test READ operation to verify created record"""
    print("\n" + "="*80)
    print(f"TEST 2: READ Silmatha Record ({sil_regn})")
    print("="*80)
    
    try:
        payload = {
            "action": "READ_ONE",
            "payload": {
                "sil_regn": sil_regn
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/silmatha-regist/manage",
            json=payload,
            headers=HEADERS
        )
        
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2, default=str)}")
        
        if response.status_code == 200:
            data = result.get("data", {})
            print(f"\n✓ READ successful!")
            print(f"  sil_gihiname: {data.get('sil_gihiname')}")
            print(f"  sil_email: {data.get('sil_email')}")
            print(f"  sil_mobile: {data.get('sil_mobile')}")
            print(f"  sil_mahananame: {data.get('sil_mahananame')}")
            print(f"  sil_fathrname: {data.get('sil_fathrname')}")
            print(f"  sil_fathrsaddrs: {data.get('sil_fathrsaddrs')}")
            return data
        else:
            print(f"\n✗ READ failed!")
            return None
            
    except Exception as e:
        print(f"\n✗ Error during READ: {str(e)}")
        return None


def test_update_silmatha(sil_regn, original_data):
    """Test UPDATE operation and verify field preservation"""
    print("\n" + "="*80)
    print(f"TEST 3: UPDATE Silmatha Record ({sil_regn})")
    print("="*80)
    
    # Prepare update payload with the regn
    update_payload = UPDATE_PAYLOAD_PARTIAL.copy()
    update_payload["payload"]["sil_regn"] = sil_regn
    
    print(f"Update payload fields: {list(update_payload['payload']['data'].keys())}")
    print(f"  - sil_gihiname: {original_data.get('sil_gihiname')} → {update_payload['payload']['data']['sil_gihiname']}")
    print(f"  - sil_mahananame: {original_data.get('sil_mahananame')} → {update_payload['payload']['data']['sil_mahananame']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/silmatha-regist/manage",
            json=update_payload,
            headers=HEADERS
        )
        
        print(f"\nStatus Code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2, default=str)}")
        
        if response.status_code == 200:
            updated_data = result.get("data", {})
            print(f"\n✓ UPDATE successful!")
            print(f"  Updated sil_gihiname: {updated_data.get('sil_gihiname')}")
            print(f"  Updated sil_mahananame: {updated_data.get('sil_mahananame')}")
            return updated_data
        else:
            print(f"\n✗ UPDATE failed!")
            return None
            
    except Exception as e:
        print(f"\n✗ Error during UPDATE: {str(e)}")
        return None


def test_verify_field_preservation(original_data, updated_data):
    """Verify that fields not in update request remained unchanged"""
    print("\n" + "="*80)
    print("TEST 4: Verify Field Preservation (No Data Loss)")
    print("="*80)
    
    fields_to_check = [
        "sil_email",
        "sil_mobile",
        "sil_fathrname",
        "sil_fathrsaddrs",
        "sil_fathrsmobile",
        "sil_aramadhipathi",
        "sil_mahanaacharyacd",
        "sil_robing_tutor_residence",
        "sil_mahanatemple",
        "sil_robing_after_residence_temple"
    ]
    
    all_preserved = True
    
    print("\nChecking fields that were NOT updated (should be unchanged):")
    for field in fields_to_check:
        original_value = original_data.get(field)
        updated_value = updated_data.get(field)
        
        if original_value == updated_value:
            print(f"  ✓ {field}: {original_value}")
        else:
            print(f"  ✗ {field}: {original_value} → {updated_value} (CHANGED!)")
            all_preserved = False
    
    print("\nChecking fields that WERE updated:")
    updated_fields = ["sil_gihiname", "sil_mahananame"]
    for field in updated_fields:
        original_value = original_data.get(field)
        updated_value = updated_data.get(field)
        
        if original_value != updated_value:
            print(f"  ✓ {field}: {original_value} → {updated_value}")
        else:
            print(f"  ✗ {field}: Should have changed but didn't!")
            all_preserved = False
    
    if all_preserved:
        print(f"\n✓ All fields properly preserved!")
        return True
    else:
        print(f"\n✗ Some fields were lost or not updated correctly!")
        return False


def run_all_tests():
    """Run all tests in sequence"""
    print("\n\n")
    print("#"*80)
    print("# SILMATHA CRUD TESTS - Field Preservation Verification")
    print("#"*80)
    
    # Test 1: CREATE
    created_regn = test_create_silmatha()
    if not created_regn:
        print("\n✗ Test suite aborted - CREATE failed")
        return False
    
    # Test 2: READ (verify initial state)
    original_data = test_read_silmatha(created_regn)
    if not original_data:
        print("\n✗ Test suite aborted - READ failed")
        return False
    
    # Test 3: UPDATE
    updated_data = test_update_silmatha(created_regn, original_data)
    if not updated_data:
        print("\n✗ Test suite aborted - UPDATE failed")
        return False
    
    # Test 4: Verify Field Preservation
    success = test_verify_field_preservation(original_data, updated_data)
    
    # Summary
    print("\n\n")
    print("#"*80)
    print("# TEST SUMMARY")
    print("#"*80)
    if success:
        print("\n✓ ALL TESTS PASSED - No field data loss detected!")
    else:
        print("\n✗ TESTS FAILED - Field data loss detected!")
    
    return success


if __name__ == "__main__":
    print("\nNote: Update BASE_URL, AUTH_TOKEN in this script before running")
    print("Expected BASE_URL: http://localhost:8000/api/v1")
    print("Expected running on: dbagovlk.com or your dev environment")
    print("\nPress Ctrl+C to skip running tests, or continue to run...\n")
    
    try:
        # Uncomment to run tests
        # run_all_tests()
        print("Tests are prepared but commented out. Uncomment line to run.")
        print("Make sure to set BASE_URL and AUTH_TOKEN first!")
    except KeyboardInterrupt:
        print("\n\nTests skipped by user")
