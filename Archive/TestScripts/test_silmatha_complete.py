#!/usr/bin/env python3
"""
Direct integration test for Silmatha CRUD - Local/Development version
Simpler approach using direct API calls
"""

import requests
import json
import sys

# ============================================================================
# CONFIGURATION
# ============================================================================
API_BASE = "http://localhost:8000/api/v1"

# Test credentials
TEST_USERNAME = "silmatha_admin"
TEST_PASSWORD = "Silmatha@123"

# ============================================================================
# SIMPLE HTTP CLIENT WITH COOKIE HANDLING
# ============================================================================

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        # Use Session with cookie jar to persist cookies
        self.session = requests.Session()
        self.token = None
        self.headers = {
            "Content-Type": "application/json",
        }
    
    def login(self, username, password):
        """Login and get token from response cookies"""
        print("Authenticating...")
        url = f"{self.base_url}/auth/login"
        payload = {
            "ua_username": username,
            "ua_password": password
        }
        
        try:
            response = self.session.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                # Cookies are automatically stored in session.cookies
                cookies = self.session.cookies.get_dict()
                print(f"  Cookies in jar: {list(cookies.keys())}")
                
                token = cookies.get("access_token")
                if token:
                    self.token = token
                    print(f"✓ Login successful - token obtained from cookies")
                    print(f"  Cookie jar now contains: {list(self.session.cookies.keys())}")
                    return True
                else:
                    print(f"✗ No access_token found in cookies")
                    return False
            else:
                print(f"✗ Login failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Login error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def request(self, method, endpoint, payload=None):
        """Make API request with cookies"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            # Print current cookies before request
            current_cookies = self.session.cookies.get_dict()
            print(f"  Current cookies: {list(current_cookies.keys())}")
            
            if method.upper() == "POST":
                response = self.session.post(url, json=payload, headers=self.headers, timeout=30)
            else:
                response = self.session.get(url, headers=self.headers, timeout=30)
            
            result = response.json()
            return response.status_code, result
        except Exception as e:
            print(f"Request error: {str(e)}")
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
    """Generate test UPDATE payload"""
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
# TEST EXECUTION
# ============================================================================

def main():
    print("\n" + "="*80)
    print("SILMATHA CRUD TEST - Field Preservation Verification")
    print("="*80)
    
    # Initialize API client
    client = APIClient(API_BASE)
    
    # Login
    print("\n🔐 Authentication")
    print("-" * 80)
    if not client.login(TEST_USERNAME, TEST_PASSWORD):
        print("\n✗ Cannot proceed without authentication")
        return False
    
    # Step 1: CREATE
    print("\n\n" + "="*80)
    print("STEP 1: CREATE Silmatha Record")
    print("="*80)
    
    print("\n📤 Creating record with all fields...")
    status, result = client.request("POST", "/silmatha-regist/manage", create_test_payload())
    
    if not result or not result.get("data"):
        print(f"\n✗ CREATE failed!")
        if result:
            print(f"   Error: {result.get('message')}")
            if result.get("errors"):
                for error in result["errors"]:
                    print(f"   - {error.get('message')}")
        return False
    
    created_regn = result["data"]["sil_regn"]
    print(f"✓ Created: {created_regn}")
    
    # Step 2: READ (before update)
    print("\n\n" + "="*80)
    print("STEP 2: READ Record (Before Update)")
    print("="*80)
    
    print(f"\n📤 Reading record {created_regn}...")
    status, result = client.request("POST", "/silmatha-regist/manage", create_read_payload(created_regn))
    
    if not result or not result.get("data"):
        print(f"\n✗ READ failed!")
        return False
    
    before_update = result["data"]
    print(f"✓ Record retrieved")
    
    print(f"\n  BEFORE UPDATE:")
    print(f"    sil_gihiname:                  {before_update.get('sil_gihiname')}")
    print(f"    sil_mahananame:                {before_update.get('sil_mahananame')}")
    print(f"    sil_email:                     {before_update.get('sil_email')}")
    print(f"    sil_mobile:                    {before_update.get('sil_mobile')}")
    print(f"    sil_fathrname:                 {before_update.get('sil_fathrname')}")
    print(f"    sil_fathrsaddrs:               {before_update.get('sil_fathrsaddrs')}")
    print(f"    sil_fathrsmobile:              {before_update.get('sil_fathrsmobile')}")
    print(f"    sil_aramadhipathi:             {before_update.get('sil_aramadhipathi')}")
    print(f"    sil_mahanaacharyacd:           {before_update.get('sil_mahanaacharyacd')}")
    print(f"    sil_robing_tutor_residence:    {before_update.get('sil_robing_tutor_residence')}")
    print(f"    sil_mahanatemple:              {before_update.get('sil_mahanatemple')}")
    print(f"    sil_robing_after_residence_temple: {before_update.get('sil_robing_after_residence_temple')}")
    
    # Step 3: UPDATE (only 2 fields)
    print("\n\n" + "="*80)
    print("STEP 3: UPDATE Record (Only 2 Fields)")
    print("="*80)
    
    print(f"\n  Updating:")
    print(f"    sil_gihiname:   'TestSilmatha123' → 'UpdatedGihi999'")
    print(f"    sil_mahananame: 'Mahana Name'     → 'UpdatedMahana999'")
    print(f"\n  (All other fields should remain unchanged)")
    
    print(f"\n📤 Sending UPDATE request...")
    status, result = client.request("POST", "/silmatha-regist/manage", create_update_payload(created_regn))
    
    if not result or not result.get("data"):
        print(f"\n✗ UPDATE failed!")
        if result:
            print(f"   Error: {result.get('message')}")
            if result.get("errors"):
                for error in result["errors"]:
                    print(f"   - {error.get('message')}")
        return False
    
    after_update = result["data"]
    print(f"✓ Record updated")
    
    print(f"\n  AFTER UPDATE:")
    print(f"    sil_gihiname:   {after_update.get('sil_gihiname')}")
    print(f"    sil_mahananame: {after_update.get('sil_mahananame')}")
    
    # Step 4: Verify Field Preservation
    print("\n\n" + "="*80)
    print("STEP 4: Verify Field Preservation")
    print("="*80)
    
    fields_to_check = [
        ("sil_email", "Email"),
        ("sil_mobile", "Mobile"),
        ("sil_fathrname", "Father Name"),
        ("sil_fathrsaddrs", "Father Address"),
        ("sil_fathrsmobile", "Father Mobile"),
        ("sil_aramadhipathi", "Arama Dhipathi"),
        ("sil_mahanaacharyacd", "Mahanaacharya Code"),
        ("sil_robing_tutor_residence", "Robing Tutor Residence"),
        ("sil_mahanatemple", "Mahana Temple"),
        ("sil_robing_after_residence_temple", "Robing After Residence Temple"),
    ]
    
    all_preserved = True
    
    print("\n📋 Fields NOT updated (should be unchanged):")
    for field_name, field_label in fields_to_check:
        before_val = before_update.get(field_name)
        after_val = after_update.get(field_name)
        
        if before_val == after_val:
            status_icon = "✓"
        else:
            status_icon = "✗"
            all_preserved = False
        
        print(f"  {status_icon} {field_label:40} {field_name}")
        if before_val != after_val:
            print(f"     Before: {before_val}")
            print(f"     After:  {after_val}")
    
    print("\n📝 Fields that WERE updated (should have changed):")
    updated_fields = [
        ("sil_gihiname", "Gihi Name", "UpdatedGihi999"),
        ("sil_mahananame", "Mahana Name", "UpdatedMahana999")
    ]
    
    for field_name, field_label, expected_value in updated_fields:
        actual_value = after_update.get(field_name)
        if actual_value == expected_value:
            status_icon = "✓"
            print(f"  {status_icon} {field_label:40} {field_name}")
            print(f"     Value: {actual_value}")
        else:
            status_icon = "✗"
            all_preserved = False
            print(f"  {status_icon} {field_label:40} {field_name}")
            print(f"     Expected: {expected_value}")
            print(f"     Got:      {actual_value}")
    
    # Final Summary
    print("\n\n" + "="*80)
    print("TEST RESULT")
    print("="*80)
    
    if all_preserved:
        print("\n✓✓✓ ALL TESTS PASSED ✓✓✓\n")
        print(f"✓ Record created:        {created_regn}")
        print(f"✓ Record retrieved:      All fields readable")
        print(f"✓ Record updated:        Partial update successful")
        print(f"✓ Field preservation:    All non-updated fields preserved correctly")
        print(f"\n✓ No data loss detected during UPDATE operations!")
        return True
    else:
        print("\n✗✗✗ TESTS FAILED ✗✗✗\n")
        print(f"✗ Some fields were lost or not updated correctly")
        print(f"✗ See details above")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
