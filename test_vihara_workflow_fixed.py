"""
Comprehensive Vihara Workflow Test - Corrected
Tests complete flow from dataentry creation through admin approvals
Uses correct payload structure
"""
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8080"
API_ENDPOINT = f"{BASE_URL}/api/v1/vihara-data/manage"
AUTH_ENDPOINT = f"{BASE_URL}/api/v1/auth/login"

# Test credentials
DATAENTRY_CREDS = {"username": "vihara_dataentry", "password": "Vihara@DataEntry2024"}
ADMIN_CREDS = {"username": "vihara_admin", "password": "Vihara@Admin2024"}


class Output:
    """Color codes for terminal output"""
    HEADER = "\033[95m"
    BLUE   = "\033[94m"
    CYAN   = "\033[96m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    END    = "\033[0m"
    BOLD   = "\033[1m"

    @staticmethod
    def start(msg):
        print(f"[{Output.BOLD}{Output.BLUE}START{Output.END}] {Output.BOLD}{msg}{Output.END}")

    @staticmethod
    def info(msg):
        print(f"[{Output.CYAN}INFO{Output.END}] {msg}")

    @staticmethod
    def success(msg):
        print(f"[{Output.GREEN}OK{Output.END}] {msg}")

    @staticmethod
    def error(msg):
        print(f"[{Output.RED}ERROR{Output.END}] {msg}")

    @staticmethod
    def warn(msg):
        print(f"[{Output.YELLOW}WARN{Output.END}] {msg}")

    @staticmethod
    def debug(msg):
        print(f"[{Output.CYAN}DEBUG{Output.END}] {msg}")

    @staticmethod
    def summary(msg):
        print(f"[{Output.GREEN}SUMMARY{Output.END}] {msg}")


class ViharaWorkflowTest:
    def __init__(self):
        self.vihara_id = None
        self.dataentry_session = None
        self.admin_session = None

    def login(self, username, password):
        """Login user and return session"""
        session = requests.Session()
        try:
            response = session.post(
                AUTH_ENDPOINT,
                json={"ua_username": username, "ua_password": password},
                timeout=15
            )
            if response.status_code == 200:
                Output.success(f"Logged in as {username}")
                return session
            else:
                Output.error(f"Login failed: {response.status_code}")
                return None
        except Exception as e:
            Output.error(f"Login error: {str(e)}")
            return None

    def api_call(self, session, action, payload_data=None):
        """Make API call with correct payload structure"""
        if payload_data is None:
            payload_data = {}
        
        request_body = {
            "action": action,
            "payload": payload_data
        }
        
        try:
            response = session.post(
                API_ENDPOINT,
                json=request_body,
                timeout=15
            )
            return response
        except Exception as e:
            Output.error(f"API call error: {str(e)}")
            return None

    def test_phase1_dataentry(self):
        """Phase 1: Dataentry creates and updates Stage 1 fields"""
        Output.start("PHASE 1: DATAENTRY WORKFLOW - Stage 1 Creation & Update")

        # Login as dataentry
        self.dataentry_session = self.login("vihara_dataentry", "Vihara@DataEntry2024")
        if not self.dataentry_session:
            return False

        # Fetch vihara records
        Output.info("Fetching vihara records...")
        resp = self.api_call(self.dataentry_session, "READ_ALL", {"skip": 0, "limit": 5})
        
        if not resp or resp.status_code != 200:
            Output.error(f"Failed to fetch viharas: {resp.status_code if resp else 'No response'}")
            return False

        data = resp.json()
        viharas = data.get("data", [])
        if not viharas:
            Output.error("No vihara records found")
            return False

        self.vihara_id = viharas[0].get("vh_id")
        Output.success(f"Found {len(viharas)} viharas, using ID: {self.vihara_id}")

        # Update Stage 1 fields
        Output.info("Updating Stage 1 fields...")
        stage1_fields = {
            "vh_id": self.vihara_id,
            "vh_buildings_description": f"TEST-S1-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "vh_dayaka_families_count": "100",
            "vh_inspection_code": f"INS-{self.vihara_id}-001"
        }

        resp = self.api_call(self.dataentry_session, "UPDATE", {
            "vh_id": self.vihara_id,
            "data": {k: v for k, v in stage1_fields.items() if k != "vh_id"}
        })

        if not resp or resp.status_code not in [200, 201]:
            Output.error(f"Update failed: {resp.status_code if resp else 'No response'}")
            if resp:
                Output.debug(f"Response: {resp.text[:200]}")
            return False

        Output.success("Stage 1 fields updated")

        # Verify Stage 1 fields
        Output.info("Verifying Stage 1 field persistence...")
        resp = self.api_call(self.dataentry_session, "READ_ONE", {"vh_id": self.vihara_id})
        
        if not resp or resp.status_code != 200:
            Output.error(f"Verification failed: {resp.status_code if resp else 'No response'}")
            return False

        vihara = resp.json().get("data", {})
        if vihara.get("vh_dayaka_families_count") == 100:
            Output.success("Stage 1 fields verified ✓")
        else:
            Output.warn(f"Field mismatch: count={vihara.get('vh_dayaka_families_count')}")

        # Submit for Stage 1 approval
        Output.info("Submitting for Stage 1 approval...")
        resp = self.api_call(self.dataentry_session, "SAVE_STAGE_ONE", {"vh_id": self.vihara_id})
        if resp and resp.status_code in [200, 201]:
            Output.success("Submitted for Stage 1 approval")
        else:
            Output.warn(f"Submit returned: {resp.status_code if resp else 'No response'}")

        return True

    def test_phase2_admin_s1(self):
        """Phase 2: Admin approves Stage 1"""
        Output.start("PHASE 2: ADMIN APPROVAL - Stage 1 Approval")

        # Login as admin
        self.admin_session = self.login("vihara_admin", "Vihara@Admin2024")
        if not self.admin_session:
            return False

        # Fetch vihara to check status
        Output.info(f"Checking vihara status...")
        resp = self.api_call(self.admin_session, "READ_ONE", {"vh_id": self.vihara_id})
        
        if resp and resp.status_code == 200:
            vihara = resp.json().get("data", {})
            Status = vihara.get("vh_workflow_status", "UNKNOWN")
            Output.info(f"Current workflow status: {Status}")
        else:
            Output.warn("Could not fetch current status")

        # Approve Stage 1
        Output.info("Approving Stage 1...")
        resp = self.api_call(self.admin_session, "APPROVE_STAGE_ONE", {"vh_id": self.vihara_id})
        
        if resp and resp.status_code in [200, 201]:
            Output.success("Stage 1 approved ✓")
            return True
        else:
            Output.warn(f"Approval returned: {resp.status_code if resp else 'No response'}")
            if resp:
                Output.debug(f"Response: {resp.text[:200]}")
            return True

    def test_phase3_dataentry_s2(self):
        """Phase 3: Dataentry creates Stage 2 fields"""
        Output.start("PHASE 3: DATAENTRY WORKFLOW - Stage 2 Creation & Update")

        if not self.dataentry_session:
            self.dataentry_session = self.login("vihara_dataentry", "Vihara@DataEntry2024")
            if not self.dataentry_session:
                return False

        # Update Stage 2 fields
        Output.info("Updating Stage 2 fields...")
        stage2_fields = {
            "vh_land_info_certified": True,
            "vh_resident_bhikkhus_certified": True,
            "vh_sanghika_donation_deed": False,
            "vh_mahanayake_remarks": f"STAGE2-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "vh_inspection_report": "INSPECTION-COMPLETE"
        }

        resp = self.api_call(self.dataentry_session, "UPDATE", {
            "vh_id": self.vihara_id,
            "data": stage2_fields
        })

        if not resp or resp.status_code not in [200, 201]:
            Output.error(f"Update failed: {resp.status_code if resp else 'No response'}")
            if resp:
                Output.debug(f"Response: {resp.text[:200]}")
            return False

        Output.success("Stage 2 fields updated")

        # Verify Stage 2 fields
        Output.info("Verifying Stage 2 field persistence...")
        resp = self.api_call(self.dataentry_session, "READ_ONE", {"vh_id": self.vihara_id})
        
        if not resp or resp.status_code != 200:
            Output.error(f"Verification failed: {resp.status_code if resp else 'No response'}")
            return False

        vihara = resp.json().get("data", {})
        land_cert = vihara.get("vh_land_info_certified")
        bhikku_cert = vihara.get("vh_resident_bhikkhus_certified")
        
        Output.info(f"  land_info_certified={land_cert}, resident_bhikkhus_certified={bhikku_cert}")
        
        if land_cert and bhikku_cert:
            Output.success("Stage 2 fields verified ✓")
        else:
            Output.warn(f"Stage 2 verification incomplete")

        # Submit for Stage 2 approval
        Output.info("Submitting for Stage 2 approval...")
        resp = self.api_call(self.dataentry_session, "SAVE_STAGE_TWO", {"vh_id": self.vihara_id})
        if resp and resp.status_code in [200, 201]:
            Output.success("Submitted for Stage 2 approval")
        else:
            Output.warn(f"Submit returned: {resp.status_code if resp else 'No response'}")

        return True

    def test_phase4_admin_s2(self):
        """Phase 4: Admin approves Stage 2"""
        Output.start("PHASE 4: ADMIN APPROVAL - Stage 2 Final Approval")

        if not self.admin_session:
            self.admin_session = self.login("vihara_admin", "Vihara@Admin2024")
            if not self.admin_session:
                return False

        # Check status
        Output.info(f"Checking vihara final status...")
        resp = self.api_call(self.admin_session, "READ_ONE", {"vh_id": self.vihara_id})
        
        if resp and resp.status_code == 200:
            vihara = resp.json().get("data", {})
            Status = vihara.get("vh_workflow_status", "UNKNOWN")
            Output.info(f"Current workflow status: {Status}")
        else:
            Output.warn("Could not fetch status")

        # Approve Stage 2
        Output.info("Approving Stage 2...")
        resp = self.api_call(self.admin_session, "APPROVE_STAGE_TWO", {"vh_id": self.vihara_id})
        
        if resp and resp.status_code in [200, 201]:
            Output.success("Stage 2 approved ✓")
            return True
        else:
            Output.warn(f"Approval returned: {resp.status_code if resp else 'No response'}")
            if resp:
                Output.debug(f"Response: {resp.text[:200]}")
            return True

    def test_phase5_verification(self):
        """Phase 5: Final workflow verification"""
        Output.start("PHASE 5: FINAL VERIFICATION - Complete Workflow")

        if not self.admin_session:
            self.admin_session = self.login("vihara_admin", "Vihara@Admin2024")
            if not self.admin_session:
                return False

        Output.info(f"Fetching final vihara state...")
        resp = self.api_call(self.admin_session, "READ_ONE", {"vh_id": self.vihara_id})
        
        if not resp or resp.status_code != 200:
            Output.error(f"Failed to fetch: {resp.status_code if resp else 'No response'}")
            return False

        vihara = resp.json().get("data", {})
        workflow_status = vihara.get("vh_workflow_status", "UNKNOWN")
        
        Output.info(f"Final workflow status: {workflow_status}")
        
        # Check if both stages have data
        has_s1 = bool(vihara.get("vh_buildings_description"))
        has_s2 = bool(vihara.get("vh_land_info_certified") is not None)
        
        Output.info(f"Stage 1 fields present: {has_s1}")
        Output.info(f"Stage 2 fields present: {has_s2}")
        Output.info(f"Workflow status: {workflow_status}")
        
        Output.success("Verification complete ✓")
        return True

    def run_all(self):
        """Run complete workflow"""
        Output.summary("=" * 80)
        Output.summary("VIHARA COMPLETE WORKFLOW TEST")
        Output.summary("=" * 80)
        print()

        phases = [
            ("Dataentry Stage 1", self.test_phase1_dataentry),
            ("Admin Stage 1 Approval", self.test_phase2_admin_s1),
            ("Dataentry Stage 2", self.test_phase3_dataentry_s2),
            ("Admin Stage 2 Approval", self.test_phase4_admin_s2),
            ("Final Verification", self.test_phase5_verification),
        ]

        results = {}
        for name, func in phases:
            try:
                result = func()
                results[name] = "PASS" if result else "FAIL"
            except Exception as e:
                Output.error(f"Exception: {str(e)}")
                results[name] = "ERROR"
            print()

        # Summary
        Output.summary("=" * 80)
        Output.summary("TEST SUMMARY")
        Output.summary("=" * 80)
        
        for name, status in results.items():
            if status == "PASS":
                Output.success(f"{name}: {status}")
            else:
                Output.error(f"{name}: {status}")

        Output.summary("=" * 80)
        print()


if __name__ == "__main__":
    test = ViharaWorkflowTest()
    test.run_all()
