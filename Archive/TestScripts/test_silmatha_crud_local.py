#!/usr/bin/env python3
"""
Direct integration test for Silmatha CRUD - Local/Development version
Handles authentication and runs complete test flow
"""

import requests
import json
import sys
import os

# ============================================================================
# CONFIGURATION
# ============================================================================
API_BASE = "http://localhost:8000/api/v1"

# Use provided test credentials
TEST_USERNAME = "silmatha_admin"
TEST_PASSWORD = "Silmatha@123"

# ============================================================================
# AUTHENTICATION
# ============================================================================

def get_auth_token():
    """Get authentication token"""
    print("Attempting to get auth token...")
    
    # Try to login
    login_url = f"{API_BASE}/auth/login"
    login_payload = {
        "ua_username": TEST_USERNAME,
        "ua_password": TEST_PASSWORD
    }
    
    try:
        # Use cookies to maintain session
        session = requests.Session()
        response = session.post(login_url, json=login_payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            # Check if we got user data (successful auth)
            if result.get("user"):
                # Extract token from cookies
                cookies = session.cookies.get_dict()
                token = cookies.get("access_token")
                
                if token:
                    print(f"✓ Auth token obtained from cookies")
                    return token, session
                else:
                    # Token might be in response
                    token = result.get("access_token") or result.get("token")
                    if token:
                        print(f"✓ Auth token obtained from response")
                        return token, session
                    else:
                        print(f"✓ Auth successful, using session with cookies")
                        return None, session  # Return session for cookie-based auth
        
        print(f"✗ Auth failed with status {response.status_code}")
        print(f"  Response: {response.text[:200]}")
        return None, None
        
    except Exception as e:
        print(f"✗ Auth error: {str(e)}")
        return None, None

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

def call_api(endpoint, payload, auth_token, session=None):
    """Make API call and return response"""
    url = f"{API_BASE}{endpoint}"
    headers = {
        "Content-Type": "application/json",
    }
    
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    # Use session if provided (for cookie-based auth)
    requester = session if session else requests
    
    try:
        print(f"\n📤 POST {endpoint}")
        print(f"   Payload keys: {list(payload.get('payload', {}).get('data', payload.get('payload', {})).keys()) if 'data' in payload.get('payload', {}) else list(payload.get('payload', {}).keys())}")
        
        response = requester.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"   Status: {response.status_code}")
        
        result = response.json()
        
        if result.get("success") == False:
            print(f"   ✗ Error: {result.get('message')}")
            if result.get("errors"):
                for error in result["errors"]:
                    print(f"     - {error.get('message')}")
            return response.status_code, result
        
        return response.status_code, result
        
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
        return None, None

# ============================================================================
# TEST EXECUTION
# ============================================================================

def main():
    print("\n" + "="*80)
    print("SILMATHA CRUD TEST - Complete Field Preservation Check")
    print("="*80)
    
    # Get auth token
    print("\n🔐 Authentication")
    print("-" * 80)
    auth_token, session = get_auth_token()
    
    if not auth_token and not session:
        print("\n✗ Cannot proceed without auth token")
        print("  Make sure the server is running and credentials are correct")
        return False
    
    # Step 1: CREATE
    print("\n\n" + "="*80)
    print("STEP 1: CREATE Silmatha Record")
    print("="*80)
    
    status, result = call_api("/silmatha-regist/manage", create_test_payload(), auth_token, session)
    
    if not result or not result.get("data"):
        print(f"\n✗ CREATE failed!")
        if result:
            print(f"   Full response: {json.dumps(result, indent=2, default=str)}")
        return False
    
    created_regn = result["data"]["sil_regn"]
    print(f"\n✓ Created record: {created_regn}")
    
    # Save original data for comparison
    original_data = result["data"]
    
    # Step 2: READ (before update)
    print("\n\n" + "="*80)
    print("STEP 2: READ Record (Before Update)")
    print("="*80)
    
    status, result = call_api("/silmatha-regist/manage", create_read_payload(created_regn), auth_token, session)
    
    if not result or not result.get("data"):
        print(f"\n✗ READ failed!")
        return False
    
    before_update = result["data"]
    print(f"\n✓ Record retrieved")
    print(f"\n  Key values BEFORE update:")
    print(f"    sil_gihiname: {before_update.get('sil_gihiname')}")
    print(f"    sil_mahananame: {before_update.get('sil_mahananame')}")
    print(f"    sil_email: {before_update.get('sil_email')}")
    print(f"    sil_mobile: {before_update.get('sil_mobile')}")
    print(f"    sil_fathrname: {before_update.get('sil_fathrname')}")
    print(f"    sil_fathrsaddrs: {before_update.get('sil_fathrsaddrs')}")
    
    # Step 3: UPDATE (only gihiname and mahananame)
    print("\n\n" + "="*80)
    print("STEP 3: UPDATE Record (Only 2 fields)")
    print("="*80)
    print(f"\nUpdating only:")
    print(f"  - sil_gihiname: 'TestSilmatha123' → 'UpdatedGihi999'")
    print(f"  - sil_mahananame: 'Mahana Name' → 'UpdatedMahana999'")
    print(f"\nAll other fields should remain unchanged...")
    
    status, result = call_api("/silmatha-regist/manage", create_update_payload(created_regn), auth_token, session)
    
    if not result or not result.get("data"):
        print(f"\n✗ UPDATE failed!")
        if result:
            print(f"   Full response: {json.dumps(result, indent=2, default=str)}")
        return False
    
    after_update = result["data"]
    print(f"\n✓ Record updated successfully")
    print(f"\n  Key values AFTER update:")
    print(f"    sil_gihiname: {after_update.get('sil_gihiname')}")
    print(f"    sil_mahananame: {after_update.get('sil_mahananame')}")
    
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
        "sil_robing_tutor_residence",
        "sil_mahanatemple",
        "sil_robing_after_residence_temple"
    ]
    
    all_preserved = True
    print("\n📋 Fields NOT updated (should be unchanged):")
    for field in fields_to_check:
        before_val = before_update.get(field)
        after_val = after_update.get(field)
        
        if before_val == after_val:
            status_icon = "✓"
        else:
            status_icon = "✗"
            all_preserved = False
        
        print(f"  {status_icon} {field}")
        if before_val != after_val:
            print(f"     Before: {before_val}")
            print(f"     After:  {after_val}")
    
    print("\n📝 Fields UPDATED (should have changed):")
    updated_fields = {
        "sil_gihiname": "UpdatedGihi999",
        "sil_mahananame": "UpdatedMahana999"
    }
    
    for field, expected_value in updated_fields.items():
        actual_value = after_update.get(field)
        if actual_value == expected_value:
            print(f"  ✓ {field}: '{expected_value}'")
        else:
            print(f"  ✗ {field}: Expected '{expected_value}', got '{actual_value}'")
            all_preserved = False
    
    # Final Summary
    print("\n\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    if all_preserved:
        print("\n✓✓✓ ALL TESTS PASSED ✓✓✓")
        print(f"\n✓ Record created: {created_regn}")
        print(f"✓ Record retrieved before update")
        print(f"✓ Record updated with partial fields")
        print(f"✓ All fields properly preserved during update")
        print(f"\nNo data loss detected! Fields work correctly.")
        return True
    else:
        print("\n✗✗✗ TESTS FAILED ✗✗✗")
        print(f"\nSome fields were lost or not updated correctly.")
        print(f"See details above for which fields have issues.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
