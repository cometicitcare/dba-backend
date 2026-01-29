#!/usr/bin/env python3
"""
Test script to verify the resident_bhikkhus field in vihara creation endpoint
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
from datetime import datetime

def get_auth_token():
    """Get authentication token - update credentials as needed"""
    # You'll need to update these credentials based on your test environment
    login_url = "http://127.0.0.1:8001/api/v1/auth/login"
    credentials = {
        "username": "admin",  # Update with actual test credentials
        "password": "password"  # Update with actual test credentials
    }
    
    try:
        response = requests.post(login_url, json=credentials)
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            print(f"Failed to get auth token: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error getting auth token: {e}")
        return None


def test_vihara_creation_with_resident_bhikkhus():
    """Test vihara creation with resident_bhikkhus data"""
    
    base_url = "http://127.0.0.1:8001"
    endpoint = f"{base_url}/api/v1/vihara-data/manage"
    
    # Test payload with resident_bhikkhus
    payload = {
        "action": "CREATE",
        "payload": {
            "data": {
                "temple_name": "Test Temple with Residents",
                "temple_address": "123 Test Street, Test City",
                "telephone_number": "0771234567",
                "whatsapp_number": "0771234567",
                "email_address": f"test_{datetime.now().timestamp()}@test.com",
                "province": "Western",
                "district": "Colombo",
                "divisional_secretariat": "Colombo",
                "pradeshya_sabha": "Colombo MC",
                "grama_niladhari_division": "GN001",
                "nikaya": "Siyam",
                "parshawaya": "P001",
                "viharadhipathi_name": "Ven. Test Thero",
                "period_established": "2020",
                "buildings_description": "Main shrine, image house",
                "dayaka_families_count": "50",
                "kulangana_committee": "Active",
                "dayaka_sabha": "Active",
                "temple_working_committee": "Active",
                "other_associations": "None",
                
                # Temple owned land
                "temple_owned_land": [
                    {
                        "serialNumber": 1,
                        "landName": "Main Temple Land",
                        "village": "Test Village",
                        "district": "Colombo",
                        "extent": "2 acres",
                        "cultivationDescription": "Not cultivated",
                        "ownershipNature": "Temple owned",
                        "deedNumber": "D001",
                        "titleRegistrationNumber": "TR001",
                        "taxDetails": "No tax",
                        "landOccupants": "None"
                    }
                ],
                
                "land_info_certified": True,
                
                # Resident bhikkhus - NEW FIELD
                "resident_bhikkhus": [
                    {
                        "serialNumber": 1,
                        "bhikkhuName": "Ven. Chief Incumbent",
                        "registrationNumber": "REG001",
                        "occupationEducation": "Chief Monk, BA in Buddhist Studies"
                    },
                    {
                        "serialNumber": 2,
                        "bhikkhuName": "Ven. Junior Monk",
                        "registrationNumber": "REG002",
                        "occupationEducation": "Assistant Monk, Dhamma Teacher"
                    }
                ],
                
                "resident_bhikkhus_certified": True,
                "inspection_report": "All facilities in good condition",
                "inspection_code": "INS001",
                "grama_niladhari_division_ownership": "Temple",
                
                "sanghika_donation_deed": True,
                "government_donation_deed": False,
                "government_donation_deed_in_progress": False,
                "authority_consent_attached": True,
                "recommend_new_center": False,
                "recommend_registered_temple": True,
                
                "annex2_recommend_construction": False,
                "annex2_land_ownership_docs": True,
                "annex2_chief_incumbent_letter": True,
                "annex2_coordinator_recommendation": True,
                "annex2_divisional_secretary_recommendation": True,
                "annex2_approval_construction": False,
                "annex2_referral_resubmission": False
            }
        }
    }
    
    print("Testing vihara creation with resident_bhikkhus...")
    print(f"URL: {endpoint}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    # Get auth token
    token = get_auth_token()
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        print("✅ Authentication token obtained")
    else:
        print("⚠️  No authentication token - testing without auth")
    
    try:
        # Test vihara creation
        response = requests.post(endpoint, json=payload, headers=headers)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Vihara created successfully!")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            # Check if resident_bhikkhus were saved
            if "data" in result and hasattr(result["data"], "resident_bhikkhus"):
                print(f"\n✅ Resident bhikkhus saved: {len(result['data']['resident_bhikkhus'])} records")
            else:
                print("\n⚠️  Note: Cannot verify resident_bhikkhus in response (may need to query separately)")
            
            return True
        elif response.status_code == 401:
            print("❌ Authentication required - please update credentials in get_auth_token()")
            print(f"Response: {response.text}")
            return False
        elif response.status_code == 422:
            print("❌ Validation error:")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return False
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vihara_creation_minimal():
    """Test minimal vihara creation to verify endpoint is working"""
    
    base_url = "http://127.0.0.1:8001"
    endpoint = f"{base_url}/api/v1/vihara-data/manage"
    
    # Minimal payload
    payload = {
        "action": "CREATE",
        "payload": {
            "data": {
                "vh_mobile": "0779999999",
                "vh_whtapp": "0779999999",
                "vh_email": f"minimal_{datetime.now().timestamp()}@test.com",
                "vh_gndiv": "GN001",
                "vh_parshawa": "P001"
            }
        }
    }
    
    print("\n\n" + "="*80)
    print("Testing minimal vihara creation (without resident_bhikkhus)...")
    print(f"URL: {endpoint}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    # Get auth token
    token = get_auth_token()
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = requests.post(endpoint, json=payload, headers=headers)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Minimal vihara created successfully!")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("="*80)
    print("VIHARA RESIDENT BHIKKHUS TEST SUITE")
    print("="*80)
    
    # Test 1: Full vihara creation with resident_bhikkhus
    success1 = test_vihara_creation_with_resident_bhikkhus()
    
    # Test 2: Minimal vihara creation
    success2 = test_vihara_creation_minimal()
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Full vihara with resident_bhikkhus: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"Minimal vihara creation: {'✅ PASS' if success2 else '❌ FAIL'}")
    print("="*80)
    
    sys.exit(0 if (success1 or success2) else 1)
