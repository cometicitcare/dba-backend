#!/usr/bin/env python3
"""
Test script for Silmatha Arama List endpoint
Tests the new /api/v1/silmatha-regist/arama-list endpoint
"""

import requests
import json
from typing import Optional

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
# BASE_URL = "https://api.dbagovlk.com/api/v1"

def login(username: str, password: str) -> Optional[requests.Session]:
    """
    Login and return session with authentication cookie
    """
    session = requests.Session()
    login_url = f"{BASE_URL}/auth/login"
    
    payload = {
        "username": username,
        "password": password
    }
    
    print(f"🔐 Logging in as: {username}")
    response = session.post(login_url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Login successful!")
        print(f"   User: {data.get('data', {}).get('ua_user_id', 'N/A')}")
        return session
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None


def test_arama_list(session: requests.Session, page: int = 1, limit: int = 10, search_key: Optional[str] = None):
    """
    Test the arama list endpoint for silmatha users
    """
    endpoint = f"{BASE_URL}/silmatha-regist/arama-list"
    
    payload = {
        "action": "READ_ALL",
        "payload": {
            "page": page,
            "limit": limit,
            "skip": 0
        }
    }
    
    if search_key:
        payload["payload"]["search_key"] = search_key
    
    print(f"\n📋 Testing Arama List Endpoint")
    print(f"   Endpoint: {endpoint}")
    print(f"   Page: {page}, Limit: {limit}")
    if search_key:
        print(f"   Search: {search_key}")
    
    response = session.post(endpoint, json=payload)
    
    print(f"\n📊 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success!")
        print(f"\n   Status: {data.get('status')}")
        print(f"   Message: {data.get('message')}")
        print(f"   Total Records: {data.get('totalRecords')}")
        print(f"   Page: {data.get('page')}")
        print(f"   Limit: {data.get('limit')}")
        print(f"   Records Returned: {len(data.get('data', []))}")
        
        # Display first few records
        aramas = data.get('data', [])
        if aramas:
            print(f"\n   📍 First {min(3, len(aramas))} Aramas:")
            for i, arama in enumerate(aramas[:3], 1):
                print(f"\n   {i}. TRN: {arama.get('ar_trn')}")
                print(f"      Name: {arama.get('ar_vname', 'N/A')}")
                print(f"      Address: {arama.get('ar_addrs', 'N/A')}")
        
        # Verify response structure
        print(f"\n   🔍 Validation:")
        for arama in aramas:
            fields = list(arama.keys())
            if set(fields) != {'ar_trn', 'ar_vname', 'ar_addrs'}:
                print(f"   ⚠️  Warning: Unexpected fields in response: {fields}")
                break
        else:
            print(f"   ✅ All records have correct fields (ar_trn, ar_vname, ar_addrs)")
        
        return data
    else:
        print(f"❌ Request failed!")
        print(f"   Response: {response.text}")
        return None


def test_invalid_action(session: requests.Session):
    """
    Test with invalid action to verify error handling
    """
    endpoint = f"{BASE_URL}/silmatha-regist/arama-list"
    
    payload = {
        "action": "READ_ONE",  # Invalid action
        "payload": {
            "page": 1,
            "limit": 10,
            "skip": 0
        }
    }
    
    print(f"\n🧪 Testing Invalid Action")
    response = session.post(endpoint, json=payload)
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 422:
        print(f"   ✅ Correctly rejected invalid action")
        print(f"   Response: {response.json()}")
    else:
        print(f"   ⚠️  Unexpected response")
        print(f"   Response: {response.text}")


def main():
    """
    Main test function
    """
    print("=" * 80)
    print("SILMATHA ARAMA LIST ENDPOINT TEST")
    print("=" * 80)
    
    # Login credentials - update with actual test user
    username = input("Enter username (with silmatha permissions): ").strip()
    if not username:
        username = "silmatha_user"  # Default
    
    password = input("Enter password: ").strip()
    if not password:
        password = "password123"  # Default
    
    # Login
    session = login(username, password)
    if not session:
        print("\n❌ Cannot proceed without authentication")
        return
    
    # Test 1: Basic list without search
    print("\n" + "=" * 80)
    print("TEST 1: List all aramas (first page)")
    print("=" * 80)
    test_arama_list(session, page=1, limit=10)
    
    # Test 2: With search key
    print("\n" + "=" * 80)
    print("TEST 2: Search aramas")
    print("=" * 80)
    search_term = input("\nEnter search term (or press Enter to skip): ").strip()
    if search_term:
        test_arama_list(session, page=1, limit=10, search_key=search_term)
    
    # Test 3: Pagination
    print("\n" + "=" * 80)
    print("TEST 3: Pagination (page 2)")
    print("=" * 80)
    test_arama_list(session, page=2, limit=5)
    
    # Test 4: Invalid action
    print("\n" + "=" * 80)
    print("TEST 4: Invalid action handling")
    print("=" * 80)
    test_invalid_action(session)
    
    print("\n" + "=" * 80)
    print("TESTS COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()
