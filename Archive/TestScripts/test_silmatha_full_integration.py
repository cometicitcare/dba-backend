#!/usr/bin/env python3
"""
Direct integration test for Silmatha CRUD using requests library
Run this after setting up your auth token
"""

import requests
import json
import sys

# ============================================================================
# CONFIGURATION - UPDATE THESE
# ============================================================================
API_BASE = "https://api.dbagovlk.com/api/v1"  # Change to http://localhost:8000/api/v1 for local
AUTH_TOKEN = "YOUR_AUTH_TOKEN_HERE"  # Get this from logging in

# ============================================================================
# TEST DATA
# ============================================================================

def create_test_payload():
    """Generate test CREATE payload"""
    return {
        "action": "CREATE",
        "payload": {
            "data": {
                "sil_reqstdate": "2025-12-31",
                "sil_form_id": "0005",
                "sil_gihiname": "TestSilmatha123",
                "sil_dofb": "1999-12-29",
                "sil_fathrname": "Father Name",
                "sil_email": "test123@example.com",
                "sil_mobile": "0712345678",
                "sil_fathrsaddrs": "Test Address",
                "sil_fathrsmobile": "0787654321",
                "sil_birthpls": "colombo",
                "sil_province": "CP",
                "sil_district": "DC006",
                "sil_aramadhipathi": "TEMP-11",
                "sil_mahananame": "Mahana Name",
                "sil_mahanadate": "2020-01-07",
                "sil_mahanaacharyacd": "TEMP-12",
                "sil_robing_tutor_residence": "ARN0000002",
                "sil_mahanatemple": "ARN0000001",
                "sil_robing_after_residence_temple": "ARN0000001",
                "sil_declaration_date": "2025-12-31",
                "sil_remarks": "Test record",
                "sil_currstat": "ST01",
                "sil_cat": "CAT01",
                "sil_student_signature": True,
                "sil_acharya_signature": True,
                "sil_aramadhipathi_signature": True,
                "sil_district_secretary_signature": True
            }
        }
    }

def create_update_payload(sil_regn):
    """Generate test UPDATE payload - only update gihiname and mahananame"""
    return {
        "action": "UPDATE",
        "payload": {
            "sil_regn": sil_regn,
            "data": {
                "sil_gihiname": "UpdatedGihi999",
                "sil_mahananame": "UpdatedMahana999"
            }
        }
    }

def create_read_payload(sil_regn):
    """Generate READ payload"""
    return {
        "action": "READ_ONE",
        "payload": {
            "sil_regn": sil_regn
        }
    }

# ============================================================================
# API CALLS
# ============================================================================

def call_api(endpoint, payload):
    """Make API call and return response"""
    url = f"{API_BASE}{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }
    
    try:
        print(f"\nCalling: {url}")
        print(f"Payload: {json.dumps(payload, indent=2, default=str)}")
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"\nStatus: {response.status_code}")
        
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2, default=str)}")
        
        return response.status_code, result
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        return None, None

# ============================================================================
# TEST EXECUTION
# ============================================================================

def main():
    print("\n" + "="*80)
    print("SILMATHA CRUD TEST")
    print("="*80)
    
    if AUTH_TOKEN == "YOUR_AUTH_TOKEN_HERE":
        print("\n✗ Error: Please set AUTH_TOKEN first!")
        print("  Edit this script and set AUTH_TOKEN to your valid auth token")
        sys.exit(1)
    
    # Step 1: CREATE
    print("\n\n" + "="*80)
    print("STEP 1: CREATE Silmatha Record")
    print("="*80)
    
    status, result = call_api("/silmatha-regist/manage", create_test_payload())
    
    if not result or not result.get("data"):
        print("\n✗ CREATE failed!")
        return False
    
    created_regn = result["data"]["sil_regn"]
    print(f"\n✓ Created: {created_regn}")
    
    # Save original data for comparison
    original_data = result["data"]
    
    # Step 2: READ (before update)
    print("\n\n" + "="*80)
    print("STEP 2: READ Record (Before Update)")
    print("="*80)
    
    status, result = call_api("/silmatha-regist/manage", create_read_payload(created_regn))
    
    if not result or not result.get("data"):
        print("\n✗ READ failed!")
        return False
    
    before_update = result["data"]
    print(f"\n✓ Read record before update")
    print(f"  sil_gihiname: {before_update.get('sil_gihiname')}")
    print(f"  sil_mahananame: {before_update.get('sil_mahananame')}")
    print(f"  sil_email: {before_update.get('sil_email')}")
    print(f"  sil_mobile: {before_update.get('sil_mobile')}")
    print(f"  sil_fathrname: {before_update.get('sil_fathrname')}")
    
    # Step 3: UPDATE (only gihiname and mahananame)
    print("\n\n" + "="*80)
    print("STEP 3: UPDATE Record (Only gihiname & mahananame)")
    print("="*80)
    
    status, result = call_api("/silmatha-regist/manage", create_update_payload(created_regn))
    
    if not result or not result.get("data"):
        print("\n✗ UPDATE failed!")
        return False
    
    after_update = result["data"]
    print(f"\n✓ Updated record")
    print(f"  sil_gihiname: {after_update.get('sil_gihiname')}")
    print(f"  sil_mahananame: {after_update.get('sil_mahananame')}")
    
    # Step 4: Verify Field Preservation
    print("\n\n" + "="*80)
    print("STEP 4: Verify Field Preservation (No Data Loss)")
    print("="*80)
    
    fields_to_check = [
        "sil_email",
        "sil_mobile", 
        "sil_fathrname",
        "sil_fathrsaddrs",
        "sil_fathrsmobile",
        "sil_aramadhipathi",
        "sil_mahanaacharyacd",
        "sil_robing_tutor_residence"
    ]
    
    all_preserved = True
    print("\nFields NOT updated (should remain same as before):")
    for field in fields_to_check:
        before_val = before_update.get(field)
        after_val = after_update.get(field)
        
        if before_val == after_val:
            status = "✓"
        else:
            status = "✗"
            all_preserved = False
        
        print(f"  {status} {field}")
        print(f"     Before: {before_val}")
        print(f"     After:  {after_val}")
    
    print("\nFields UPDATED (should have changed):")
    updated_fields = {
        "sil_gihiname": "UpdatedGihi999",
        "sil_mahananame": "UpdatedMahana999"
    }
    
    for field, expected_value in updated_fields.items():
        actual_value = after_update.get(field)
        if actual_value == expected_value:
            print(f"  ✓ {field}: Changed to '{expected_value}'")
        else:
            print(f"  ✗ {field}: Expected '{expected_value}', got '{actual_value}'")
            all_preserved = False
    
    # Final Summary
    print("\n\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    if all_preserved:
        print("\n✓✓✓ ALL TESTS PASSED - Fields properly preserved! ✓✓✓")
        print(f"\nCreated record: {created_regn}")
        return True
    else:
        print("\n✗✗✗ TESTS FAILED - Some fields were lost! ✗✗✗")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
