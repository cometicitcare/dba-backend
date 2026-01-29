#!/usr/bin/env python3
"""
Test script for the new arama silmathas endpoint.
This script demonstrates how to search for an arama and get all associated silmathas.
"""
import requests
import json
from typing import Optional

# Configuration
BASE_URL = "http://127.0.0.1:8001/api/v1"  # Update this to your server URL
# BASE_URL = "https://api.dbagovlk.com/api/v1"  # For production

def get_auth_token(username: str = "admin", password: str = "password") -> Optional[str]:
    """Get authentication token"""
    login_url = f"{BASE_URL.replace('/api/v1', '')}/api/v1/auth/login"
    credentials = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(login_url, json=credentials)
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"✅ Successfully logged in as {username}")
            return token
        else:
            print(f"❌ Failed to get auth token: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error getting auth token: {e}")
        return None


def get_silmathas_by_arama(ar_trn: str, token: str, skip: int = 0, limit: int = 10):
    """
    Get all silmathas associated with a specific arama/temple.
    
    Args:
        ar_trn: Arama/Temple TRN (e.g., "TRN0000001" or "ARN0000001")
        token: Authentication token
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
    """
    endpoint = f"{BASE_URL}/arama-data/{ar_trn}/silmathas"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    params = {
        "skip": skip,
        "limit": limit
    }
    
    print(f"\n{'='*80}")
    print(f"Testing: GET Silmathas for Arama '{ar_trn}'")
    print(f"{'='*80}")
    print(f"URL: {endpoint}")
    print(f"Params: skip={skip}, limit={limit}")
    
    try:
        response = requests.get(endpoint, headers=headers, params=params)
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ SUCCESS!")
            print(f"\nArama Name: {data.get('arama_name', 'N/A')}")
            print(f"Total Silmathas Found: {data.get('totalRecords', 0)}")
            print(f"Returned Records: {len(data.get('data', []))}")
            
            # Display each silmatha record
            silmathas = data.get('data', [])
            if silmathas:
                print(f"\n{'─'*80}")
                print("Silmatha Records:")
                print(f"{'─'*80}")
                
                for idx, silmatha in enumerate(silmathas, 1):
                    print(f"\n{idx}. Registration Number: {silmatha.get('sil_regn', 'N/A')}")
                    print(f"   Name: {silmatha.get('sil_mahananame', 'N/A')}")
                    print(f"   Lay Name: {silmatha.get('sil_gihiname', 'N/A')}")
                    print(f"   Status: {silmatha.get('sil_workflow_status', 'N/A')}")
                    print(f"   Mobile: {silmatha.get('sil_mobile', 'N/A')}")
                    print(f"   Email: {silmatha.get('sil_email', 'N/A')}")
                    
                    # Show temple associations
                    robing_tutor = silmatha.get('sil_robing_tutor_residence')
                    if isinstance(robing_tutor, dict):
                        print(f"   Robing Tutor Residence: {robing_tutor.get('vh_vname', 'N/A')} ({robing_tutor.get('vh_trn', 'N/A')})")
                    
                    mahana_temple = silmatha.get('sil_mahanatemple')
                    if isinstance(mahana_temple, dict):
                        print(f"   Mahana Temple: {mahana_temple.get('vh_vname', 'N/A')} ({mahana_temple.get('vh_trn', 'N/A')})")
                    
                    robing_after = silmatha.get('sil_robing_after_residence_temple')
                    if isinstance(robing_after, dict):
                        print(f"   Robing After Residence: {robing_after.get('vh_vname', 'N/A')} ({robing_after.get('vh_trn', 'N/A')})")
            else:
                print("\nℹ️  No silmatha records found for this arama.")
            
            # Print full JSON response (optional - uncomment if needed)
            # print(f"\n{'─'*80}")
            # print("Full JSON Response:")
            # print(f"{'─'*80}")
            # print(json.dumps(data, indent=2))
            
        elif response.status_code == 404:
            print(f"\n❌ ERROR: Arama not found")
            print(f"Response: {response.text}")
        elif response.status_code == 403:
            print(f"\n❌ ERROR: Permission denied")
            print(f"Response: {response.text}")
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"\n❌ Exception occurred: {e}")


def main():
    """Main test function"""
    print("="*80)
    print("ARAMA SILMATHAS ENDPOINT TEST")
    print("="*80)
    
    # Step 1: Get authentication token
    print("\n[Step 1] Getting authentication token...")
    token = get_auth_token(username="admin", password="password")
    
    if not token:
        print("\n❌ Cannot proceed without authentication token.")
        print("Please update the credentials in the script.")
        return
    
    # Step 2: Test the endpoint with different arama TRNs
    print("\n[Step 2] Testing silmathas endpoint...")
    
    # Example 1: Search with a specific TRN (update this with actual TRN from your database)
    test_trns = [
        "TRN0000001",  # Update with actual TRN from your database
        "ARN0000001",  # Update with actual ARN from your database
    ]
    
    for ar_trn in test_trns:
        get_silmathas_by_arama(ar_trn, token, skip=0, limit=10)
    
    print("\n" + "="*80)
    print("✅ TEST COMPLETED!")
    print("="*80)
    print("\nNote: Update the test_trns list with actual TRNs from your database.")
    print("You can also modify the skip and limit parameters for pagination testing.")


if __name__ == "__main__":
    main()
