#!/usr/bin/env python3
"""
Test script to verify temp-vihara response format in READ_ALL endpoint
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json

def test_temp_vihara_format():
    """Test that temp-vihara records have matching response format with regular viharas"""
    
    base_url = "http://127.0.0.1:8001"
    endpoint = f"{base_url}/api/v1/vihara-data/manage"
    
    # Test payload for READ_ALL
    payload = {
        "action": "READ_ALL",
        "payload": {
            "skip": 0,
            "limit": 100
        }
    }
    
    print("=" * 80)
    print("Testing Temp-Vihara Format in READ_ALL Response")
    print("=" * 80)
    print(f"\nEndpoint: {endpoint}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(endpoint, json=payload)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error Response: {json.dumps(response.json(), indent=2)}")
            return False
        
        data = response.json()
        records = data.get("data", [])
        
        if not records:
            print("⚠️  No records found in response")
            return True
        
        # Find a temp-vihara record (should have vh_trn like "TEMP-1", "TEMP-2", etc.)
        temp_viharas = [r for r in records if isinstance(r.get("vh_trn"), str) and r["vh_trn"].startswith("TEMP-")]
        regular_viharas = [r for r in records if not (isinstance(r.get("vh_trn"), str) and r["vh_trn"].startswith("TEMP-"))]
        
        print(f"\n✅ Found {len(regular_viharas)} regular viharas and {len(temp_viharas)} temp viharas")
        
        if not temp_viharas:
            print("⚠️  No temp-vihara records found. Cannot test format comparison.")
            if regular_viharas:
                print(f"📋 Sample regular vihara keys: {sorted(regular_viharas[0].keys())}")
            return True
        
        # Check field consistency
        if regular_viharas and temp_viharas:
            regular_keys = set(regular_viharas[0].keys())
            temp_keys = set(temp_viharas[0].keys())
            
            print(f"\n📊 Regular Vihara: {len(regular_keys)} fields")
            print(f"📊 Temp-Vihara: {len(temp_keys)} fields")
            
            # Check for missing fields in temp-vihara
            missing_in_temp = regular_keys - temp_keys
            extra_in_temp = temp_keys - regular_keys
            
            if missing_in_temp:
                print(f"\n⚠️  Missing fields in temp-vihara: {sorted(missing_in_temp)}")
            else:
                print(f"\n✅ All regular vihara fields present in temp-vihara")
            
            if extra_in_temp:
                print(f"⚠️  Extra fields in temp-vihara: {sorted(extra_in_temp)}")
            else:
                print(f"✅ No extra fields in temp-vihara")
            
            # Print sample temp-vihara
            print(f"\n📋 Sample Temp-Vihara Record:")
            print(json.dumps(temp_viharas[0], indent=2, default=str))
            
            print(f"\n📋 Sample Regular Vihara Record (first 30 fields):")
            sample_regular = {k: regular_viharas[0][k] for k in sorted(regular_viharas[0].keys())[:30]}
            print(json.dumps(sample_regular, indent=2, default=str))
            
            if not missing_in_temp:
                print("\n✅ SUCCESS: Temp-vihara response format matches regular vihara format!")
                return True
            else:
                print(f"\n❌ FAILED: Response format mismatch detected")
                return False
        else:
            print("⚠️  Insufficient data for comparison")
            return True
        
    except Exception as e:
        print(f"\n❌ Error testing endpoint: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing temp-vihara response format...\n")
    
    success = test_temp_vihara_format()
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Tests failed!")
        sys.exit(1)
