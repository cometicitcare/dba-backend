"""
Test script for Silmatha Registration CRUD API

This script tests the silmatha_regist endpoint with the CREATE action.
"""

import requests
import json

# Base URL - adjust if needed
BASE_URL = "http://localhost:8000/api/v1"
ENDPOINT = f"{BASE_URL}/silmatha-regist/manage"

# Test payload from user requirements
test_payload = {
    "action": "CREATE",
    "payload": {
        "data": {
            "sil_reqstdate": "2025-10-31",
            "sil_gihiname": "dfsdf",
            "sil_dofb": "2025-10-30",
            "sil_fathrname": "sdfsf",
            "sil_email": "sdfsd@gmail.com",
            "sil_mobile": "0771234567",
            "sil_fathrsaddrs": "Father's Address",
            "sil_fathrsmobile": "0771234567",
            "sil_birthpls": "Colombo General Hospital",
            "sil_province": "WP",
            "sil_district": "DC001",
            "sil_korale": "dfgd",
            "sil_pattu": "gdfg",
            "sil_division": "DV001",
            "sil_vilage": "dfg",
            "sil_gndiv": "GN001",
            "sil_viharadhipathi": "BH2025000001",
            "sil_cat": "CAT01",
            "sil_currstat": "ST01",
            "sil_declaration_date": "2025-10-28",
            "sil_remarks": "sdfsdfdf",
            "sil_mahanadate": "2025-10-30",
            "sil_mahananame": "sdfdf",
            "sil_mahanaacharyacd": "BH2025000001",
            "sil_robing_tutor_residence": "TRN0000008",
            "sil_mahanatemple": "TRN0000008",
            "sil_robing_after_residence_temple": "TRN0000008"
        }
    }
}

def test_create_silmatha():
    """Test creating a new silmatha registration"""
    print("Testing CREATE action...")
    print(f"Endpoint: {ENDPOINT}")
    print(f"Payload: {json.dumps(test_payload, indent=2)}")
    
    # Note: This will require authentication token in real usage
    # headers = {"Authorization": "Bearer YOUR_TOKEN_HERE"}
    
    try:
        response = requests.post(ENDPOINT, json=test_payload)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("\n✅ SUCCESS: Silmatha record created successfully!")
        else:
            print(f"\n❌ FAILED: {response.json()}")
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    print("=" * 80)
    print("SILMATHA REGISTRATION API TEST")
    print("=" * 80)
    test_create_silmatha()
    print("=" * 80)
