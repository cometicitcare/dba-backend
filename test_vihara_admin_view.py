#!/usr/bin/env python3
"""
Test script to verify vihara_admin can see all vihara records 
with pending approval records at the top
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json

def load_cookies(cookie_file="cookies.txt"):
    """Load cookies from file"""
    try:
        with open(cookie_file, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"❌ Cookie file {cookie_file} not found")
        return None

def test_vihara_admin_view():
    """Test that vihara_admin sees all records with pending approvals at the top"""
    
    base_url = "http://127.0.0.1:8001"
    endpoint = f"{base_url}/api/v1/vihara-data/manage"
    
    # Load vihara_admin cookies (assuming you have a vihara admin logged in)
    cookie_str = load_cookies("cookies.txt")
    if not cookie_str:
        print("⚠️  No cookies found. Please login as vihara_admin first.")
        return False
    
    # Parse cookies
    headers = {
        "Content-Type": "application/json",
        "Cookie": cookie_str
    }
    
    # Test READ_ALL action
    payload = {
        "action": "READ_ALL",
        "payload": {
            "page": 1,
            "limit": 20,
            "skip": 0
        }
    }
    
    print("=" * 80)
    print("Testing vihara_admin READ_ALL endpoint...")
    print("=" * 80)
    print(f"URL: {endpoint}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print()
    
    try:
        response = requests.post(endpoint, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Response: {response.text}")
            return False
        
        result = response.json()
        
        if result.get("status") != "success":
            print(f"❌ Request failed: {result.get('message', 'Unknown error')}")
            return False
        
        data = result.get("data", [])
        total = result.get("totalRecords", 0)
        
        print(f"\n✅ Request successful!")
        print(f"Total Records: {total}")
        print(f"Records Retrieved: {len(data)}")
        print()
        
        # Analyze the records
        pending_approval_count = 0
        other_status_count = 0
        first_non_pending_index = None
        
        print("=" * 80)
        print("Record Order Analysis:")
        print("=" * 80)
        
        for idx, record in enumerate(data):
            vh_id = record.get("vh_id")
            vh_trn = record.get("vh_trn")
            vh_vname = record.get("vh_vname", "N/A")
            workflow_status = record.get("vh_workflow_status", "N/A")
            
            is_pending = workflow_status in ["S1_PEND_APPROVAL", "S2_PEND_APPROVAL"]
            
            status_marker = "🔴" if is_pending else "🟢"
            
            print(f"{idx + 1}. {status_marker} ID: {vh_id}, TRN: {vh_trn}, Status: {workflow_status}")
            
            if is_pending:
                pending_approval_count += 1
                if first_non_pending_index is not None:
                    print(f"   ⚠️  WARNING: Pending approval record found after non-pending record!")
            else:
                other_status_count += 1
                if first_non_pending_index is None:
                    first_non_pending_index = idx
        
        print()
        print("=" * 80)
        print("Summary:")
        print("=" * 80)
        print(f"Records with PENDING APPROVAL status: {pending_approval_count}")
        print(f"Records with OTHER status: {other_status_count}")
        
        # Verify ordering
        if first_non_pending_index is not None:
            # Check if all pending approvals come before other statuses
            all_pending_first = True
            for idx in range(first_non_pending_index):
                if data[idx].get("vh_workflow_status") not in ["S1_PEND_APPROVAL", "S2_PEND_APPROVAL"]:
                    all_pending_first = False
                    break
            
            if all_pending_first:
                print("\n✅ CORRECT: All pending approval records appear at the top!")
            else:
                print("\n❌ ERROR: Pending approval records are NOT at the top!")
                return False
        elif pending_approval_count == 0:
            print("\n⚠️  No pending approval records found in the result set")
        else:
            print("\n✅ CORRECT: All records are pending approval")
        
        # Check ascending order for pending approvals
        if pending_approval_count > 1:
            pending_ids = [r.get("vh_id") for r in data[:pending_approval_count]]
            is_ascending = all(pending_ids[i] <= pending_ids[i+1] for i in range(len(pending_ids)-1))
            
            if is_ascending:
                print("✅ CORRECT: Pending approval records are in ascending order")
            else:
                print("❌ ERROR: Pending approval records are NOT in ascending order")
                return False
        
        print()
        print("=" * 80)
        print("🎉 All checks passed! vihara_admin can see all records correctly.")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("VIHARA ADMIN VIEW TEST")
    print("=" * 80)
    print()
    
    success = test_vihara_admin_view()
    
    if success:
        print("\n✅ Test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Test failed!")
        sys.exit(1)
