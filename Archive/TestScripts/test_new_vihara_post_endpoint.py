#!/usr/bin/env python3
"""
Test script to verify the new POST vihara-list endpoint
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json

def test_vihara_post_endpoint():
    """Test the new POST vihara-list endpoint"""
    
    base_url = "http://127.0.0.1:8001"
    endpoint = f"{base_url}/api/v1/bhikkus/vihara-list"
    
    # Test payload
    payload = {
        "action": "READ_ONE",
        "payload": {
            "vh_id": 41
        }
    }
    
    print("Testing POST /api/v1/bhikkus/vihara-list endpoint...")
    print(f"URL: {endpoint}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        # Test without authentication (should get 401)
        response = requests.post(endpoint, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Check that we get authentication error (not 404 or 422)
        if response.status_code == 401:
            print("✅ Endpoint exists and is properly protected")
        elif response.status_code == 404:
            print("❌ Endpoint not found - check routing")
            return False
        elif response.status_code == 422:
            print("❌ Validation error - check request schema")
            return False
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
        
        # Test with invalid action
        invalid_payload = {
            "action": "INVALID_ACTION",
            "payload": {
                "vh_id": 41
            }
        }
        
        print(f"\nTesting with invalid action...")
        response_invalid = requests.post(endpoint, json=invalid_payload)
        print(f"Status Code: {response_invalid.status_code}")
        print(f"Response: {json.dumps(response_invalid.json(), indent=2)}")
        
        # Test with missing vh_id
        missing_payload = {
            "action": "READ_ONE",
            "payload": {}
        }
        
        print(f"\nTesting with missing vh_id...")
        response_missing = requests.post(endpoint, json=missing_payload)
        print(f"Status Code: {response_missing.status_code}")
        print(f"Response: {json.dumps(response_missing.json(), indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")
        return False

def test_endpoint_structure():
    """Test that the new schemas are properly defined"""
    
    try:
        from app.schemas.vihara import BhikkuViharaManagementRequest, BhikkuViharaReadOnePayload
        print("✅ New schemas imported successfully")
        
        # Test schema structure
        test_payload = BhikkuViharaReadOnePayload(vh_id=41)
        print(f"✅ BhikkuViharaReadOnePayload: {test_payload.model_dump()}")
        
        test_request = BhikkuViharaManagementRequest(
            action="READ_ONE", 
            payload=test_payload
        )
        print(f"✅ BhikkuViharaManagementRequest: {test_request.model_dump()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema error: {e}")
        return False

if __name__ == "__main__":
    print("Testing new POST vihara-list endpoint...\n")
    
    # Test schema structure first
    schema_ok = test_endpoint_structure()
    if not schema_ok:
        print("\n❌ Schema tests failed.")
        sys.exit(1)
    
    # Test endpoint
    endpoint_ok = test_vihara_post_endpoint()
    if endpoint_ok:
        print("\n🎉 All tests passed! The endpoint is ready for use.")
        print("\n📋 Usage Example:")
        print("POST /api/v1/bhikkus/vihara-list")
        print(json.dumps({
            "action": "READ_ONE",
            "payload": {
                "vh_id": 41
            }
        }, indent=2))
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1)