#!/usr/bin/env python3
"""
Simple test to check what the vihara API returns for reading existing records
"""
import requests
import json
from pprint import pprint

# Configure these based on your setup
API_BASE_URL = "http://localhost:8000"  # or your actual BE URL
AUTH_TOKEN = ""  # Add your token if needed

def test_vihara_read():
    """Test reading a vihara record to see what fields are returned"""
    
    # Try reading a vihara with ID 1 (adjust as needed)
    url = f"{API_BASE_URL}/api/v1/vihara/manage"
    
    payload = {
        "action": "READ_ONE",
        "payload": {
            "vh_id": 1
        }
    }
    
    headers = {
        "Content-Type": "application/json",
    }
    
    if AUTH_TOKEN:
        headers["Authorization"] = f"Bearer {AUTH_TOKEN}"
    
    print("=" * 80)
    print("Testing Vihara Read API")
    print("=" * 80)
    print(f"Endpoint: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("-" * 80)
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("\nResponse Data:")
            pprint(data, width=120)
            
            # Extract and show critical fields
            if "data" in data:
                vihara_data = data["data"]
                print("\n" + "=" * 80)
                print("CRITICAL FIELDS FOR FRONTEND MAPPING:")
                print("=" * 80)
                critical_fields = [
                    "vh_province",
                    "vh_district",
                    "vh_divisional_secretariat",
                    "vh_pradeshya_sabha",
                    "vh_gndiv",
                ]
                for field in critical_fields:
                    value = vihara_data.get(field)
                    print(f"  {field}: {value} (type: {type(value).__name__})")
        else:
            print(f"\nError Response:")
            pprint(response.json() if response.text else "No response body", width=120)
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API. Make sure the backend is running.")
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_vihara_read()
