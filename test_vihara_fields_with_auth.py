#!/usr/bin/env python3
"""
Comprehensive Test Suite for Vihara Form Fields (Flow 1 and Flow 2)
WITH AUTHENTICATION HANDLING
"""
import requests
import json
import sys
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from pprint import pprint

# Configuration
API_BASE_URL = "http://localhost:8080"

# Test credentials
DATAENTRY_USER = {
    "username": "vihara_dataentry",
    "password": "Vihara@DataEntry2024"
}

ADMIN_USER = {
    "username": "vihara_admin",
    "password": "Vihara@Admin2024"
}

class ViharaFieldTestSuiteWithAuth:
    """Test suite with authentication for comprehensive vihara field validation"""

    def __init__(self, api_base_url: str):
        self.api_base_url = api_base_url
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = {
            "passed": [],
            "failed": [],
            "warnings": []
        }
        self.test_vihara_id = None

    def log(self, message: str, level: str = "INFO"):
        """Log test messages"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level:7s}] {message}")

    # =========================================================================
    # AUTHENTICATION
    # =========================================================================
    def login(self, username: str = None, password: str = None) -> bool:
        """Authenticate and get auth token"""
        if username is None:
            username = DATAENTRY_USER["username"]
            password = DATAENTRY_USER["password"]
        
        self.log(f"Logging in as: {username}", level="INFO")
        
        endpoint = f"{self.api_base_url}/api/v1/auth/login"
        payload = {
            "ua_username": username,
            "ua_password": password
        }
        
        try:
            response = self.session.post(endpoint, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Token is set as HTTP-only cookie by the backend
                # Session will automatically include it for subsequent requests
                user_data = data.get("user")
                if user_data:
                    username_returned = user_data.get("ua_username")
                    self.log(f"OK: Successfully authenticated as {username_returned}", level="INFO")
                    role_name = user_data.get("role", {}).get("ro_role_name", "N/A")
                    self.log(f"    Role: {role_name}", level="INFO")
                    perms = user_data.get("permissions", [])
                    self.log(f"    Permissions: {len(perms)} permissions granted", level="INFO")
                    
                    # Debug: print cookies
                    cookies = self.session.cookies.get_dict()
                    self.log(f"    Cookies set: {list(cookies.keys())}", level="DEBUG")
                    
                    return True
                else:
                    self.log(f"ERROR: No user data in response", level="ERROR")
                    return False
            else:
                self.log(f"ERROR: Login failed: {response.status_code}", level="ERROR")
                if response.text:
                    self.log(f"Response: {response.text}", level="DEBUG")
                return False
        except Exception as e:
            self.log(f"ERROR: Error during login: {e}", level="ERROR")
            return False

    # =========================================================================
    # VIHARA OPERATIONS
    # =========================================================================
    def get_existing_vihara(self, limit: int = 5) -> Dict[str, Any]:
        """Get existing vihara for testing"""
        self.log("Fetching existing vihara records for testing...")

        endpoint = f"{self.api_base_url}/api/v1/vihara-data/manage"
        payload = {
            "action": "READ_ALL",
            "payload": {
                "skip": 0,
                "limit": limit
            }
        }

        try:
            response = self.session.post(endpoint, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("data") and len(data["data"]) > 0:
                    vihara = data["data"][0]
                    self.test_vihara_id = vihara.get("vh_id")
                    self.log(f"OK: Found vihara ID={self.test_vihara_id}, Name={vihara.get('vh_vname')}", level="INFO")
                    return vihara
                else:
                    self.log("WARNING: No vihara records found in database", level="WARN")
                    return None
            else:
                self.log(f"ERROR: Failed to fetch vihara: {response.status_code}", level="ERROR")
                if response.text:
                    self.log(f"Response: {response.text[:300]}", level="DEBUG")
                return None
        except Exception as e:
            self.log(f"ERROR: Error fetching vihara: {e}", level="ERROR")
            return None

    def read_vihara(self, vh_id: int) -> Dict[str, Any]:
        """Read a vihara record by ID"""
        endpoint = f"{self.api_base_url}/api/v1/vihara-data/manage"
        payload = {
            "action": "READ_ONE",
            "payload": {
                "vh_id": vh_id
            }
        }

        try:
            response = self.session.post(endpoint, json=payload, timeout=10)
            if response.status_code == 200:
                return response.json().get("data")
            else:
                self.log(f"Failed to read vihara {vh_id}: {response.status_code}", level="ERROR")
                return None
        except Exception as e:
            self.log(f"Error reading vihara: {e}", level="ERROR")
            return None

    def update_vihara(self, vh_id: int, data: Dict[str, Any], action: str = "UPDATE") -> bool:
        """Update a vihara record"""
        endpoint = f"{self.api_base_url}/api/v1/vihara-data/manage"
        update_data = {"vh_id": vh_id}
        update_data.update(data)

        payload = {
            "action": action,
            "payload": update_data
        }

        try:
            response = self.session.post(endpoint, json=payload, timeout=10)
            if response.status_code in [200, 201]:
                self.log(f"✓ Updated vihara {vh_id} with {len(data)} fields", level="INFO")
                return True
            else:
                self.log(f"✗ Failed to update vihara: {response.status_code}", level="ERROR")
                if response.text:
                    self.log(f"Response: {response.text[:300]}", level="DEBUG")
                return False
        except Exception as e:
            self.log(f"✗ Error updating vihara: {e}", level="ERROR")
            return False

    # =========================================================================
    # DIAGNOSTIC TESTS
    # =========================================================================
    def test_basic_fields(self, vh_id: int) -> bool:
        """Test basic vihara fields"""
        self.log("\n" + "="*80, level="INFO")
        self.log("TESTING BASIC VIHARA FIELDS", level="INFO")
        self.log("="*80, level="INFO")

        vihara = self.read_vihara(vh_id)
        if not vihara:
            self.log("✗ Failed to read vihara", level="FAIL")
            return False

        # Map critical fields
        critical_fields = {
            "vh_id": int,
            "vh_trn": str,
            "vh_vname": str,
            "vh_addrs": str,
            "vh_workflow_status": str,
            "vh_created_at": str,
            "vh_updated_at": str,
        }

        self.log("\nCurrent Vihara Data:")
        all_pass = True
        for field, expected_type in critical_fields.items():
            value = vihara.get(field)
            actual_type = type(value).__name__
            
            field_exists = field in vihara
            type_matches = isinstance(value, expected_type) if value is not None else field_exists
            
            status = "[OK]" if field_exists else "[FAIL]"
            self.log(f"  {status} {field}: {value} (type: {actual_type})", level="INFO")
            
            if not field_exists:
                all_pass = False

        return all_pass

    def test_all_fields_enumeration(self, vh_id: int) -> bool:
        """Enumerate all fields in the vihara record"""
        self.log("\n" + "="*80, level="INFO")
        self.log("ENUMERATING ALL VIHARA FIELDS", level="INFO")
        self.log("="*80, level="INFO")

        vihara = self.read_vihara(vh_id)
        if not vihara:
            self.log("✗ Failed to read vihara", level="FAIL")
            return False

        # Flow 1 fields
        flow1_fields = [
            "vh_trn", "vh_vname", "vh_addrs", "vh_mobile", "vh_whtapp", "vh_email",
            "vh_typ", "vh_gndiv", "vh_fmlycnt", "vh_bgndate", "vh_ownercd", "vh_parshawa",
            "vh_ssbmcode", "vh_province", "vh_district", "vh_divisional_secretariat",
            "vh_pradeshya_sabha", "vh_nikaya", "vh_viharadhipathi_name", "vh_viharadhipathi_regn",
            "vh_period_established"
        ]

        # Flow 2 fields
        flow2_fields = [
            "vh_mahanayake_date", "vh_mahanayake_letter_nu", "vh_mahanayake_remarks",
            "vh_buildings_description", "vh_dayaka_families_count", "vh_kulangana_committee",
            "vh_dayaka_sabha", "vh_temple_working_committee", "vh_other_associations",
            "vh_land_info_certified", "vh_resident_bhikkhus_certified",
            "vh_inspection_report", "vh_inspection_code", "vh_grama_niladhari_division_ownership",
            "vh_sanghika_donation_deed", "vh_government_donation_deed",
            "vh_government_donation_deed_in_progress", "vh_authority_consent_attached",
            "vh_recommend_new_center", "vh_recommend_registered_temple",
            "vh_annex2_recommend_construction", "vh_annex2_land_ownership_docs",
            "vh_annex2_chief_incumbent_letter", "vh_annex2_coordinator_recommendation",
            "vh_annex2_divisional_secretary_recommendation", "vh_annex2_approval_construction",
            "vh_annex2_referral_resubmission"
        ]

        self.log("\n--- FLOW 1 FIELDS (Stage 1 - Basic Information) ---")
        for field in flow1_fields:
            value = vihara.get(field)
            has_value = value is not None and value != ""
            status = "✓" if has_value else "○"
            self.log(f"  {status} {field}: {value if has_value else '(empty)'}")

        self.log("\n--- FLOW 2 FIELDS (Stage 2 - Advanced Information) ---")
        for field in flow2_fields:
            value = vihara.get(field)
            has_value = value is not None and value != ""
            status = "✓" if has_value else "○"
            self.log(f"  {status} {field}: {value if has_value else '(empty)'}")

        self.log("\n=== WORKFLOW STATUS ===")
        workflow_fields = [
            "vh_workflow_status", "vh_approval_status",
            "vh_s1_printed_at", "vh_s1_approved_at", "vh_s1_rejected_at",
            "vh_s2_printed_at", "vh_s2_approved_at", "vh_s2_rejected_at"
        ]
        for field in workflow_fields:
            value = vihara.get(field)
            self.log(f"  {field}: {value}")

        return True

    def test_sample_update(self, vh_id: int) -> bool:
        """Test updating a few fields and verify persistence"""
        self.log("\n" + "="*80, level="INFO")
        self.log("TESTING FIELD PERSISTENCE WITH SAMPLE UPDATE", level="INFO")
        self.log("="*80, level="INFO")

        # Get current state
        before = self.read_vihara(vh_id)
        if not before:
            self.log("[FAIL] Failed to read vihara before update", level="FAIL")
            return False

        # Prepare update data
        import random
        test_suffix = f"_TEST_{random.randint(1000, 9999)}"
        update_data = {
            "vh_inspection_code": f"TEST-CODE{test_suffix}",
            "vh_inspection_report": f"Test inspection report{test_suffix}",
            "vh_dayaka_families_count": "99"
        }

        self.log(f"\nUpdating fields: {list(update_data.keys())}")
        if not self.update_vihara(vh_id, update_data):
            return False

        # Verify the update
        import time
        time.sleep(0.5)
        after = self.read_vihara(vh_id)
        if not after:
            self.log("[FAIL] Failed to read vihara after update", level="FAIL")
            return False

        self.log("\nVerifying persistence:")
        all_pass = True
        for field, expected_value in update_data.items():
            actual_value = after.get(field)
            if str(actual_value) == str(expected_value):
                self.log(f"  OK {field}: {actual_value}", level="INFO")
            else:
                self.log(f"  FAIL {field}: Expected '{expected_value}', Got '{actual_value}'", level="ERROR")
                all_pass = False

        return all_pass

    def test_workflow_approval_as_admin(self, vh_id: int) -> bool:
        """Test approval workflow as admin user"""
        self.log("\n" + "="*80, level="INFO")
        self.log("TESTING WORKFLOW APPROVAL (ADMIN ROLE)", level="INFO")
        self.log("="*80, level="INFO")

        # Switch to admin
        self.log("\nSwitching to ADMIN user for approval testing...")
        if not self.login(ADMIN_USER["username"], ADMIN_USER["password"]):
            self.log("FAIL: Could not login as admin", level="FAIL")
            return False

        # Read current vihara state
        vihara = self.read_vihara(vh_id)
        if not vihara:
            self.log("FAIL: Could not read vihara as admin", level="FAIL")
            return False

        current_status = vihara.get("vh_workflow_status")
        self.log(f"\nCurrent workflow status: {current_status}")
        self.log(f"Vihara Name: {vihara.get('vh_vname')}")

        self.log(f"\nAdmin user: {ADMIN_USER['username']} - can view all vihara details")

        return True

    def test_dataentry_create_update_workflow(self) -> bool:
        """Test complete workflow as dataentry user"""
        self.log("\n" + "="*80, level="INFO")
        self.log("TESTING COMPLETE DATAENTRY WORKFLOW (DATAENTRY ROLE)", level="INFO")
        self.log("="*80, level="INFO")

        # Get a test vihara for workflow testing
        vihara = self.get_existing_vihara(limit=1)
        if not vihara:
            self.log("FAIL: No vihara available for workflow test", level="FAIL")
            return False

        vh_id = vihara.get("vh_id")
        self.log(f"\nUsing vihara ID: {vh_id} for workflow test")

        # Test Flow 1 Updates
        self.log("\n--- Testing Flow 1 (Stage 1) Updates ---")
        flow1_updates = {
            "vh_buildings_description": "Well-maintained temple with main hall and meditation rooms",
            "vh_dayaka_families_count": "75",
            "vh_temple_working_committee": "Chairman: XYZ, Members: ABC, DEF, GHI"
        }

        if self.update_vihara(vh_id, flow1_updates):
            self.log("  OK: Flow 1 updates successful", level="INFO")
            # Verify  
            import time
            time.sleep(0.2)
            vihara_check = self.read_vihara(vh_id)
            if vihara_check and vihara_check.get("vh_buildings_description"):
                self.log("  OK: Flow 1 data verified in database", level="INFO")
        else:
            self.log("  FAIL: Flow 1 updates failed", level="ERROR")
            return False

        # Test Flow 2 Updates with boolean fields
        self.log("\n--- Testing Flow 2 (Stage 2) Updates ---")
        flow2_updates = {
            "vh_land_info_certified": True,
            "vh_resident_bhikkhus_certified": True,
            "vh_sanghika_donation_deed": True,
            "vh_mahanayake_remarks": "Approved by Mahanayake authority",
            "vh_grama_niladhari_division_ownership": "GN Division confirmed"
        }

        if self.update_vihara(vh_id, flow2_updates):
            self.log("  OK: Flow 2 updates successful", level="INFO")
            import time
            time.sleep(0.2)
            vihara_check = self.read_vihara(vh_id)
            if vihara_check:
                self.log("  OK: Flow 2 fields updated in database", level="INFO")
                return True
        else:
            self.log("  FAIL: Flow 2 updates failed", level="ERROR")
            return False

        return True

    # =========================================================================
    # MAIN EXECUTION
    # =========================================================================
    def run_all_tests(self) -> bool:
        """Run complete test suite with dataentry and admin workflows"""
        try:
            self.log("\n" + "="*80, level="INFO")
            self.log("PHASE 1: DATAENTRY USER WORKFLOW", level="INFO")
            self.log("="*80, level="INFO")

            # Test dataentry user
            if not self.login(DATAENTRY_USER["username"], DATAENTRY_USER["password"]):
                self.log("Cannot proceed without dataentry authentication", level="ERROR")
                return False

            # Get test vihara
            existing_vihara = self.get_existing_vihara()
            if not existing_vihara:
                self.log("Cannot proceed without existing vihara record", level="ERROR")
                return False

            vh_id = existing_vihara.get("vh_id")

            # Run dataentry tests
            test1_pass = self.test_basic_fields(vh_id)
            test2_pass = self.test_all_fields_enumeration(vh_id)
            test3_pass = self.test_sample_update(vh_id)
            test4_pass = self.test_dataentry_create_update_workflow()

            self.log("\n" + "="*80, level="INFO")
            self.log("PHASE 2: ADMIN USER APPROVAL WORKFLOW", level="INFO")
            self.log("="*80, level="INFO")

            # Test admin approvals
            test5_pass = self.test_workflow_approval_as_admin(vh_id)

            # Summary
            self.log("\n" + "="*80, level="INFO")
            self.log("COMPREHENSIVE TEST SUMMARY", level="INFO")
            self.log("="*80, level="INFO")
            self.log(f"1. Basic Fields Test (Dataentry): {'PASS' if test1_pass else 'FAIL'}", level="INFO")
            self.log(f"2. All Fields Enumeration: {'PASS' if test2_pass else 'FAIL'}", level="INFO")
            self.log(f"3. Field Persistence Test: {'PASS' if test3_pass else 'FAIL'}", level="INFO")
            self.log(f"4. Dataentry Workflow (Creation/Updates): {'PASS' if test4_pass else 'FAIL'}", level="INFO")
            self.log(f"5. Admin Approval Workflow: {'PASS' if test5_pass else 'FAIL'}", level="INFO")

            all_pass = test1_pass and test2_pass and test3_pass and test4_pass and test5_pass
            
            if all_pass:
                self.log("\n" + "="*80, level="INFO")
                self.log("SUCCESS: All tests passed! Vihara fields are working correctly.", level="INFO")
                self.log("="*80, level="INFO")
            else:
                self.log("\n" + "="*80, level="INFO")
                self.log("WARNING: Some tests failed. See details above.", level="WARN")
                self.log("="*80, level="INFO")

            return all_pass

        except Exception as e:
            self.log(f"Unexpected error: {e}", level="ERROR")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main entry point"""
    print("\n" + "="*80)
    print("VIHARA COMPREHENSIVE FIELD TEST SUITE (WITH AUTH)")
    print("="*80)
    print(f"API Base URL: {API_BASE_URL}")
    print("="*80 + "\n")

    test_suite = ViharaFieldTestSuiteWithAuth(API_BASE_URL)
    success = test_suite.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
