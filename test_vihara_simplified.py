#!/usr/bin/env python3
"""
Simplified Vihara Field Test - Direct API Testing
Tests all vihara fields without session complexity
"""
import requests
import json
from datetime import datetime

API_BASE_URL = "http://localhost:8080"

# Credentials
DATAENTRY = {"username": "vihara_dataentry", "password": "Vihara@DataEntry2024"}
ADMIN = {"username": "vihara_admin", "password": "Vihara@Admin2024"}

def log(msg, level="INFO"):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{level:6s}] {msg}")

def test_vihara_fields():
    """Test vihara field persistence"""
    
    log("="*80, "START")
    log("Starting Vihara Field Persistence Test")
    log("="*80, "START")
    
    # Create a fresh session for dataentry
    session = requests.Session()
    
    # Login as dataentry
    log("Logging in as dataentry user...", "INFO")
    login_resp = session.post(
        f"{API_BASE_URL}/api/v1/auth/login",
        json={
            "ua_username": DATAENTRY["username"],
            "ua_password": DATAENTRY["password"]
        },
        timeout=15
    )
    
    if login_resp.status_code != 200:
        log(f"Login failed: {login_resp.status_code}", "ERROR")
        log(f"Response: {login_resp.text[:200]}", "ERROR")
        return False
    
    user_data = login_resp.json().get("user", {})
    log(f"OK: Logged in as {user_data.get('ua_username')}", "OK")
    log(f"    Cookies: {list(session.cookies.get_dict().keys())}", "DEBUG")
    
    # Try to fetch vihara records
    log("Fetching vihara records...", "INFO")
    
    # Test with explicit headers and cookies
    cookies = session.cookies
    log(f"Current cookies before request: {session.cookies.get_dict()}", "DEBUG")
    
    fetch_resp = session.post(
        f"{API_BASE_URL}/api/v1/vihara-data/manage",
        json={
            "action": "READ_ALL",
            "payload": {"skip": 0, "limit": 5}
        },
        timeout=15,
        cookies=cookies  # Explicitly pass cookies
    )
    
    log(f"Fetch response status: {fetch_resp.status_code}", "DEBUG")
    
    if fetch_resp.status_code != 200:
        log(f"Fetch failed: {fetch_resp.status_code}", "ERROR")
        log(f"Response: {fetch_resp.text[:300]}", "DEBUG")
        
        # Try without authentication to see if public endpoint
        log("Trying without cookies...", "DEBUG")
        fetch_resp2 = requests.post(
            f"{API_BASE_URL}/api/v1/vihara-data/manage",
            json={
                "action": "READ_ALL",
                "payload": {"skip": 0, "limit": 1}
            },
            timeout=15
        )
        log(f"Response without auth: {fetch_resp2.status_code}", "DEBUG")
        return False
    
    data = fetch_resp.json()
    viharas = data.get("data", [])
    
    if not viharas:
        log("No vihara records found in database", "WARN")
        return False
    

    vihara = viharas[0]
    vh_id = vihara.get("vh_id")
    log(f"OK: Found {len(viharas)} vihara records", "OK")
    log(f"     Using vihara ID {vh_id} for testing", "INFO")
    
    # Test Flow 1 Fields
    log("\n" + "="*80, "START")
    log("FLOW 1 FIELD TEST (Stage 1)", "START")
    log("="*80, "START")
    
    flow1_data = {
        "vh_buildings_description": f"TEST-B1-{vh_id}",
        "vh_dayaka_families_count": "150",
        "vh_inspection_code": f"INS-{vh_id}-001"
    }
    
    log(f"Updating {len(flow1_data)} FLow 1 fields...", "INFO")
    update_resp = session.post(
        f"{API_BASE_URL}/api/v1/vihara-data/manage",
        json={
            "action": "UPDATE",
            "payload": {
                "vh_id": vh_id,
                "data": flow1_data
            }
        },
        timeout=15
    )
    
    if update_resp.status_code not in [200, 201]:
        log(f"Update failed: {update_resp.status_code}", "ERROR")
        log(f"Response: {update_resp.text[:200]}", "DEBUG")
        return False
    
    log("OK: Flow 1 fields updated", "OK")
    
    # Verify Flow 1
    log("Verifying Flow 1 fields...", "INFO")
    import time
    time.sleep(0.3)
    
    read_resp = session.post(
        f"{API_BASE_URL}/api/v1/vihara-data/manage",
        json={
            "action": "READ_ONE",
            "payload": {"vh_id": vh_id}
        },
        timeout=15
    )
    
    if read_resp.status_code != 200:
        log(f"Read failed: {read_resp.status_code}", "ERROR")
        return False
    
    updated_vihara = read_resp.json().get("data", {})
    
    all_pass = True
    for field, expected_val in flow1_data.items():
        actual_val = updated_vihara.get(field)
        if str(actual_val) == str(expected_val):
            log(f"  [OK] {field}: {actual_val}", "OK")
        else:
            log(f"  [FAIL] {field}: expected '{expected_val}', got '{actual_val}'", "FAIL")
            all_pass = False
    
    # Test Flow 2 Fields
    log("\n" + "="*80, "START")
    log("FLOW 2 FIELD TEST (Stage 2)", "START")
    log("="*80, "START")
    
    flow2_data = {
        "vh_land_info_certified": True,
        "vh_resident_bhikkhus_certified": True,
        "vh_sanghika_donation_deed": False,
        "vh_mahanayake_remarks": f"TEST-REMARKS-{vh_id}",
        "vh_inspection_report": f"TEST-REPORT-{vh_id}"
    }
    
    log(f"Updating {len(flow2_data)} Flow 2 fields...", "INFO")
    update_resp2 = session.post(
        f"{API_BASE_URL}/api/v1/vihara-data/manage",
        json={
            "action": "UPDATE",
            "payload": {
                "vh_id": vh_id,
                "data": flow2_data
            }
        },
        timeout=15
    )
    
    if update_resp2.status_code not in [200, 201]:
        log(f"Update failed: {update_resp2.status_code}", "ERROR")
        log(f"Response: {update_resp2.text[:200]}", "DEBUG")
        return False
    
    log("OK: Flow 2 fields updated", "OK")
    
    # Verify Flow 2
    log("Verifying Flow 2 fields...", "INFO")
    time.sleep(0.3)
    
    read_resp2 = session.post(
        f"{API_BASE_URL}/api/v1/vihara-data/manage",
        json={
            "action": "READ_ONE",
            "payload": {"vh_id": vh_id}
        },
        timeout=15
    )
    
    if read_resp2.status_code != 200:
        log(f"Read failed: {read_resp2.status_code}", "ERROR")
        return False
    
    updated_vihara2 = read_resp2.json().get("data", {})
    
    for field, expected_val in flow2_data.items():
        actual_val = updated_vihara2.get(field)
        if type(expected_val).__name__ == "bool":
            if actual_val is expected_val:
                log(f"  [OK] {field}: {actual_val}", "OK")
            else:
                log(f"  [FAIL] {field}: expected {expected_val}, got {actual_val}", "FAIL")
                all_pass = False
        else:
            if str(actual_val) == str(expected_val):
                log(f"  [OK] {field}: {actual_val}", "OK")
            else:
                log(f"  [FAIL] {field}: expected '{expected_val}', got '{actual_val}'", "FAIL")
                all_pass = False
    
    # Summary
    log("\n" + "="*80, "SUMMARY")
    if all_pass:
        log("SUCCESS: All fields persisted correctly!", "SUCCESS")
    else:
        log("FAILURE: Some fields did not persist correctly", "FAILURE")
    log("="*80, "SUMMARY")
    
    return all_pass


if __name__ == "__main__":
    try:
        success = test_vihara_fields()
        exit(0 if success else 1)
    except Exception as e:
        log(f"Exception: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        exit(1)
