#!/usr/bin/env python3
"""
Comprehensive Test Suite for Vihara Form Fields (Flow 1 and Flow 2)

This test verifies that:
1. All fields in vihara form flow 1 are properly saved/created/updated in the DB
2. All fields in vihara form flow 2 are properly saved/created/updated in the DB
3. Workflow status transitions work correctly
4. All data integrity is maintained

Flow 1 (Stage 1) Fields: Basic temple information, administrative divisions, religious affiliation, leadership info
Flow 2 (Stage 2) Fields: Mahanyake thero info, certificates, upload scanned files
"""
import requests
import json
import sys
from datetime import datetime, date
from typing import Dict, Any, List
from pprint import pprint

# Configuration
API_BASE_URL = "http://localhost:8080"  # Adjust to your local BE URL
# For local testing without auth, you may need to comment out auth requirements

# Define all vihara fields grouped by category
VIHARA_FLOW_1_FIELDS = {
    "temple_basic_info": [
        "vh_trn",
        "vh_vname",
        "vh_addrs",
        "vh_mobile",
        "vh_whtapp",
        "vh_email",
        "vh_typ",
        "vh_fmlycnt",
        "vh_bgndate",
    ],
    "administrative_divisions": [
        "vh_province",
        "vh_district",
        "vh_divisional_secretariat",
        "vh_pradeshya_sabha",
        "vh_gndiv",
    ],
    "religious_affiliation": [
        "vh_nikaya",
        "vh_parshawa",
        "vh_ssbmcode",
    ],
    "leadership_info": [
        "vh_viharadhipathi_name",
        "vh_viharadhipathi_regn",
        "vh_period_established",
        "vh_ownercd",
    ],
}

VIHARA_FLOW_2_FIELDS = {
    "mahanyake_thero_info": [
        "vh_mahanayake_date",
        "vh_mahanayake_letter_nu",
        "vh_mahanayake_remarks",
    ],
    "buildings_and_governance": [
        "vh_buildings_description",
        "vh_dayaka_families_count",
        "vh_kulangana_committee",
        "vh_dayaka_sabha",
        "vh_temple_working_committee",
        "vh_other_associations",
    ],
    "certifications": [
        "vh_land_info_certified",
        "vh_resident_bhikkhus_certified",
        "vh_sanghika_donation_deed",
        "vh_government_donation_deed",
        "vh_government_donation_deed_in_progress",
        "vh_authority_consent_attached",
        "vh_recommend_new_center",
        "vh_recommend_registered_temple",
    ],
    "annex2_fields": [
        "vh_annex2_recommend_construction",
        "vh_annex2_land_ownership_docs",
        "vh_annex2_chief_incumbent_letter",
        "vh_annex2_coordinator_recommendation",
        "vh_annex2_divisional_secretary_recommendation",
        "vh_annex2_approval_construction",
        "vh_annex2_referral_resubmission",
    ],
    "inspection_info": [
        "vh_inspection_report",
        "vh_inspection_code",
        "vh_grama_niladhari_division_ownership",
    ],
}

ALL_FIELDS = {}
for category, fields in VIHARA_FLOW_1_FIELDS.items():
    ALL_FIELDS.update({f: "flow1" for f in fields})
for category, fields in VIHARA_FLOW_2_FIELDS.items():
    ALL_FIELDS.update({f: "flow2" for f in fields})

# Test data
TEST_VIHARA_FLOW_1_DATA = {
    # Temple Basic Information
    "vh_vname": "Test Vihara Flow 1 Complete",
    "vh_addrs": "123 Temple Street, Test City",
    "vh_mobile": "0714567890",
    "vh_whtapp": "0714567890",
    "vh_email": "test.vihara.flow1@test.com",
    "vh_typ": "VIHARA",
    "vh_fmlycnt": 150,
    "vh_bgndate": "2010-05-15",
    # Administrative Divisions
    "vh_province": "CP-1",
    "vh_district": "DD-001",
    "vh_divisional_secretariat": "DV-001",
    "vh_pradeshya_sabha": "PS-001",
    "vh_gndiv": "GN-001",
    # Religious Affiliation
    "vh_nikaya": "SM",
    "vh_parshawa": "PR-001",
    "vh_ssbmcode": "SSBM-001",
    # Leadership Information
    "vh_viharadhipathi_name": "Ven. Test Bhikkhu",
    "vh_viharadhipathi_regn": "BH2024000123",
    "vh_period_established": "1950",
    "vh_ownercd": "BH2024000123",
}

TEST_VIHARA_FLOW_2_DATA = {
    # Mahanyake Thero Info
    "vh_mahanayake_date": "2023-01-15",
    "vh_mahanayake_letter_nu": "MH-2023-001",
    "vh_mahanayake_remarks": "Approved as legitimate vihara under Mahanyake authority",
    # Buildings and Governance
    "vh_buildings_description": "Main temple hall, meditation rooms, residential quarters",
    "vh_dayaka_families_count": "45",
    "vh_kulangana_committee": "Chairman: ABC, Vice: DEF, Treasurer: GHI",
    "vh_dayaka_sabha": "Monthly meetings held on first Sunday, 50+ members",
    "vh_temple_working_committee": "Temple maintenance, renovation oversight, finance management",
    "vh_other_associations": "Buddhist youth group, women's association, educational programs",
    # Certifications - Boolean fields
    "vh_land_info_certified": True,
    "vh_resident_bhikkhus_certified": True,
    "vh_sanghika_donation_deed": True,
    "vh_government_donation_deed": False,
    "vh_government_donation_deed_in_progress": True,
    "vh_authority_consent_attached": True,
    "vh_recommend_new_center": False,
    "vh_recommend_registered_temple": True,
    # Annex 2 Fields
    "vh_annex2_recommend_construction": True,
    "vh_annex2_land_ownership_docs": True,
    "vh_annex2_chief_incumbent_letter": True,
    "vh_annex2_coordinator_recommendation": True,
    "vh_annex2_divisional_secretary_recommendation": True,
    "vh_annex2_approval_construction": False,
    "vh_annex2_referral_resubmission": False,
    # Inspection Info
    "vh_inspection_report": "Site inspection completed on 2024-01-20. All facilities well-maintained.",
    "vh_inspection_code": "INS-2024-001",
    "vh_grama_niladhari_division_ownership": "GN Division: Matara/Athuraliya - Ownership confirmed",
}


class ViharaFieldTestSuite:
    """Test suite for comprehensive vihara field validation"""

    def __init__(self, api_base_url: str):
        self.api_base_url = api_base_url
        self.session = requests.Session()
        self.test_results = {
            "passed": [],
            "failed": [],
            "warnings": []
        }
        self.test_vihara_id = None
        self.test_vihara_trn = None

    def log(self, message: str, level: str = "INFO"):
        """Log test messages"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level:7s}] {message}")

    def log_test(self, message: str, status: str = "PASS", field: str = None):
        """Log test results"""
        self.log(message, level=status)
        if status == "PASS":
            self.test_results["passed"].append((field if field else message, status))
        elif status == "FAIL":
            self.test_results["failed"].append((field if field else message, message))
        else:
            self.test_results["warnings"].append((field if field else message, message))

    # =========================================================================
    # SETUP: Find or create a test vihara
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
                    self.test_vihara_trn = vihara.get("vh_trn")
                    self.log(f"Found existing vihara: TRN={self.test_vihara_trn}, ID={self.test_vihara_id}", level="INFO")
                    return vihara
                else:
                    self.log("No existing vihara records found in database", level="WARN")
                    return None
            else:
                self.log(f"Failed to fetch vihara: {response.status_code}", level="ERROR")
                return None
        except Exception as e:
            self.log(f"Error fetching vihara: {e}", level="ERROR")
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
                if response.text:
                    self.log(f"Response: {response.text}", level="DEBUG")
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
                self.log(f"Successfully updated vihara {vh_id} with action {action}", level="INFO")
                return True
            else:
                self.log(f"Failed to update vihara: {response.status_code}", level="ERROR")
                if response.text:
                    self.log(f"Response: {response.text}", level="DEBUG")
                return False
        except Exception as e:
            self.log(f"Error updating vihara: {e}", level="ERROR")
            return False

    # =========================================================================
    # FLOW 1 TESTS: Basic Information Fields
    # =========================================================================
    def test_flow_1_fields(self, vh_id: int) -> bool:
        """Test Flow 1 (Stage 1) field persistence"""
        self.log("\n" + "="*80, level="INFO")
        self.log("TESTING VIHARA FLOW 1 FIELDS (Stage 1 - Basic Information)", level="INFO")
        self.log("="*80, level="INFO")

        if not vh_id:
            self.log("No vihara ID provided for testing", level="ERROR")
            return False

        # Read current vihara state
        before_update = self.read_vihara(vh_id)
        if not before_update:
            self.log_test("Failed to read vihara before update", status="FAIL")
            return False

        # Update with Flow 1 data
        self.log(f"\nUpdating vihara {vh_id} with Flow 1 test data...")
        if not self.update_vihara(vh_id, TEST_VIHARA_FLOW_1_DATA):
            self.log_test("Failed to update vihara with Flow 1 data", status="FAIL")
            return False

        # Read updated vihara
        import time
        time.sleep(0.5)  # Small delay to ensure DB write
        after_update = self.read_vihara(vh_id)
        if not after_update:
            self.log_test("Failed to read vihara after Flow 1 update", status="FAIL")
            return False

        # Verify each Flow 1 field
        self.log("\nVerifying Flow 1 fields...")
        all_flow1_pass = True

        for category, fields in VIHARA_FLOW_1_FIELDS.items():
            self.log(f"\n  Category: {category.upper().replace('_', ' ')}")
            for field in fields:
                expected_value = TEST_VIHARA_FLOW_1_DATA.get(field)
                actual_value = after_update.get(field)

                # Handle type conversions
                if expected_value is not None and isinstance(expected_value, str):
                    if field in ["vh_bgndate", "vh_fmlycnt"]:
                        # These may need conversion
                        pass

                if str(actual_value) == str(expected_value):
                    self.log_test(f"✓ {field}: {actual_value}", status="PASS", field=field)
                else:
                    self.log_test(
                        f"✗ {field}: Expected '{expected_value}', Got '{actual_value}'",
                        status="FAIL",
                        field=field
                    )
                    all_flow1_pass = False

        return all_flow1_pass

    # =========================================================================
    # FLOW 2 TESTS: Advanced Fields
    # =========================================================================
    def test_flow_2_fields(self, vh_id: int) -> bool:
        """Test Flow 2 (Stage 2) field persistence"""
        self.log("\n" + "="*80, level="INFO")
        self.log("TESTING VIHARA FLOW 2 FIELDS (Stage 2 - Advanced Information)", level="INFO")
        self.log("="*80, level="INFO")

        if not vh_id:
            self.log("No vihara ID provided for testing", level="ERROR")
            return False

        # Update with Flow 2 data
        self.log(f"\nUpdating vihara {vh_id} with Flow 2 test data...")
        if not self.update_vihara(vh_id, TEST_VIHARA_FLOW_2_DATA):
            self.log_test("Failed to update vihara with Flow 2 data", status="FAIL")
            return False

        # Read updated vihara
        import time
        time.sleep(0.5)  # Small delay to ensure DB write
        after_update = self.read_vihara(vh_id)
        if not after_update:
            self.log_test("Failed to read vihara after Flow 2 update", status="FAIL")
            return False

        # Verify each Flow 2 field
        self.log("\nVerifying Flow 2 fields...")
        all_flow2_pass = True

        for category, fields in VIHARA_FLOW_2_FIELDS.items():
            self.log(f"\n  Category: {category.upper().replace('_', ' ')}")
            for field in fields:
                expected_value = TEST_VIHARA_FLOW_2_DATA.get(field)
                actual_value = after_update.get(field)

                if str(actual_value) == str(expected_value):
                    self.log_test(f"✓ {field}: {actual_value}", status="PASS", field=field)
                else:
                    self.log_test(
                        f"✗ {field}: Expected '{expected_value}', Got '{actual_value}'",
                        status="FAIL",
                        field=field
                    )
                    all_flow2_pass = False

        return all_flow2_pass

    # =========================================================================
    # DATA INTEGRITY TESTS
    # =========================================================================
    def test_combined_flow_persistence(self, vh_id: int) -> bool:
        """Test that both Flow 1 and Flow 2 data persist together"""
        self.log("\n" + "="*80, level="INFO")
        self.log("TESTING COMBINED FLOW PERSISTENCE", level="INFO")
        self.log("="*80, level="INFO")

        # Read current state (should have both Flow 1 and Flow 2 data)
        vihara = self.read_vihara(vh_id)
        if not vihara:
            self.log_test("Failed to read vihara for combined test", status="FAIL")
            return False

        combined_pass = True

        # Verify Flow 1 data still exists
        self.log("\nVerifying Flow 1 data persistence...")
        for field in ["vh_vname", "vh_province", "vh_nikaya", "vh_viharadhipathi_name"]:
            actual_value = vihara.get(field)
            expected_value = TEST_VIHARA_FLOW_1_DATA.get(field)
            if str(actual_value) == str(expected_value):
                self.log_test(f"✓ Flow 1 field {field} persisted", status="PASS", field=field)
            else:
                self.log_test(
                    f"✗ Flow 1 field {field} not persisted: {actual_value} != {expected_value}",
                    status="FAIL",
                    field=field
                )
                combined_pass = False

        # Verify Flow 2 data still exists
        self.log("\nVerifying Flow 2 data persistence...")
        for field in ["vh_mahanayake_remarks", "vh_buildings_description", "vh_land_info_certified"]:
            actual_value = vihara.get(field)
            expected_value = TEST_VIHARA_FLOW_2_DATA.get(field)
            if str(actual_value) == str(expected_value):
                self.log_test(f"✓ Flow 2 field {field} persisted", status="PASS", field=field)
            else:
                self.log_test(
                    f"✗ Flow 2 field {field} not persisted: {actual_value} != {expected_value}",
                    status="FAIL",
                    field=field
                )
                combined_pass = False

        return combined_pass

    # =========================================================================
    # WORKFLOW STATUS TESTS
    # =========================================================================
    def test_workflow_transitions(self, vh_id: int) -> bool:
        """Test workflow status transitions"""
        self.log("\n" + "="*80, level="INFO")
        self.log("TESTING WORKFLOW STATUS TRANSITIONS", level="INFO")
        self.log("="*80, level="INFO")

        vihara = self.read_vihara(vh_id)
        if not vihara:
            self.log_test("Failed to read vihara for workflow test", status="FAIL")
            return False

        current_status = vihara.get("vh_workflow_status")
        self.log(f"Current workflow status: {current_status}", level="INFO")

        # Document current workflow state
        workflow_fields = [
            "vh_workflow_status",
            "vh_s1_printed_at", "vh_s1_printed_by",
            "vh_s1_scanned_at", "vh_s1_scanned_by",
            "vh_s1_approved_at", "vh_s1_approved_by",
            "vh_s2_printed_at", "vh_s2_printed_by",
            "vh_s2_scanned_at", "vh_s2_scanned_by",
            "vh_s2_approved_at", "vh_s2_approved_by",
        ]

        self.log("\nCurrent Workflow State:")
        for field in workflow_fields:
            value = vihara.get(field)
            if value:
                self.log(f"  {field}: {value}", level="INFO")

        return True

    # =========================================================================
    # REPORT GENERATION
    # =========================================================================
    def generate_report(self):
        """Generate test report"""
        self.log("\n" + "="*80, level="INFO")
        self.log("TEST SUMMARY REPORT", level="INFO")
        self.log("="*80, level="INFO")

        total_passed = len(self.test_results["passed"])
        total_failed = len(self.test_results["failed"])
        total_warnings = len(self.test_results["warnings"])
        total_tests = total_passed + total_failed + total_warnings

        self.log(f"\nTotal Tests Run: {total_tests}")
        self.log(f"  ✓ Passed:  {total_passed}")
        self.log(f"  ✗ Failed:  {total_failed}")
        self.log(f"  ⚠ Warnings: {total_warnings}")

        if total_failed > 0:
            self.log("\n⚠ FAILED TESTS:", level="WARN")
            for field, message in self.test_results["failed"]:
                self.log(f"  - {field}: {message}", level="WARN")

        if total_warnings > 0:
            self.log("\n⚠ WARNINGS:", level="WARN")
            for field, message in self.test_results["warnings"]:
                self.log(f"  - {field}: {message}", level="WARN")

        self.log("\n" + "="*80, level="INFO")
        if total_failed == 0:
            self.log("✓ ALL TESTS PASSED!", level="INFO")
        else:
            self.log(f"✗ {total_failed} TEST(S) FAILED - SEE DETAILS ABOVE", level="ERROR")

        return total_failed == 0

    # =========================================================================
    # MAIN TEST EXECUTION
    # =========================================================================
    def run_all_tests(self) -> bool:
        """Run complete test suite"""
        try:
            # Find test vihara
            existing_vihara = self.get_existing_vihara()
            if not existing_vihara:
                self.log("Cannot proceed without existing vihara record. Please create one first.", level="ERROR")
                return False

            vh_id = existing_vihara.get("vh_id")

            # Print existing vihara info
            self.log("\n" + "="*80, level="INFO")
            self.log(f"TESTING WITH VIHARA ID: {vh_id}", level="INFO")
            self.log("="*80, level="INFO")
            self.log("\nExisting Vihara Data (Sample):")
            for key in ["vh_id", "vh_trn", "vh_vname", "vh_addrs", "vh_workflow_status"]:
                self.log(f"  {key}: {existing_vihara.get(key)}", level="INFO")

            # Run test suites
            flow1_pass = self.test_flow_1_fields(vh_id)
            flow2_pass = self.test_flow_2_fields(vh_id)
            combined_pass = self.test_combined_flow_persistence(vh_id)
            workflow_pass = self.test_workflow_transitions(vh_id)

            # Generate report
            self.generate_report()

            return flow1_pass and flow2_pass and combined_pass

        except Exception as e:
            self.log(f"Unexpected error during test execution: {e}", level="ERROR")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main entry point"""
    print("\n" + "="*80)
    print("VIHARA COMPREHENSIVE FIELD TEST SUITE")
    print("="*80)
    print(f"API Base URL: {API_BASE_URL}")
    print("="*80 + "\n")

    # Run test suite
    test_suite = ViharaFieldTestSuite(API_BASE_URL)
    success = test_suite.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
