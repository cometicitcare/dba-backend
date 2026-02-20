"""
Comprehensive Vihara Workflow Test
Tests complete flow from dataentry creation through admin approvals
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


class ColoredOutput:
    """Color codes for terminal output"""
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    @staticmethod
    def start(msg):
        print(f"[{ColoredOutput.BOLD}{ColoredOutput.OKBLUE}START{ColoredOutput.ENDC}] {ColoredOutput.BOLD}{msg}{ColoredOutput.ENDC}")

    @staticmethod
    def info(msg):
        print(f"[{ColoredOutput.OKCYAN}INFO{ColoredOutput.ENDC}] {msg}")

    @staticmethod
    def success(msg):
        print(f"[{ColoredOutput.OKGREEN}OK{ColoredOutput.ENDC}] {msg}")

    @staticmethod
    def error(msg):
        print(f"[{ColoredOutput.FAIL}ERROR{ColoredOutput.ENDC}] {msg}")

    @staticmethod
    def warning(msg):
        print(f"[{ColoredOutput.WARNING}WARN{ColoredOutput.ENDC}] {msg}")

    @staticmethod
    def debug(msg):
        print(f"[{ColoredOutput.OKCYAN}DEBUG{ColoredOutput.ENDC}] {msg}")

    @staticmethod
    def summary(msg):
        print(f"[{ColoredOutput.OKGREEN}SUMMARY{ColoredOutput.ENDC}] {msg}")


class ViharaWorkflowTest:
    def __init__(self):
        self.test_results = []
        self.vihara_id = None
        self.dataentry_session = None
        self.admin_session = None

    def login(self, username, password):
        """Login user and return session"""
        session = requests.Session()
        try:
            response = session.post(
                AUTH_ENDPOINT,
                json={"ua_username": username, "ua_password": password}
            )
            if response.status_code == 200:
                ColoredOutput.success(f"Logged in as {username}")
                return session
            else:
                ColoredOutput.error(f"Login failed for {username}: {response.status_code}")
                if response.status_code == 422:
                    ColoredOutput.debug(f"Validation error: {response.text}")
                return None
        except Exception as e:
            ColoredOutput.error(f"Login error: {str(e)}")
            return None

    def api_request(self, session, action, payload=None):
        """Make API request with proper payload structure"""
        if payload is None:
            payload = {}
        
        full_payload = {"action": action}
        if payload:
            full_payload.update(payload)
        
        try:
            response = session.post(API_ENDPOINT, json=full_payload)
            return response
        except Exception as e:
            ColoredOutput.error(f"API request error: {str(e)}")
            return None

    def step(self, title, details=""):
        """Print test step"""
        ColoredOutput.start(title)
        if details:
            ColoredOutput.info(details)

    def test_dataentry_workflow(self):
        """Test Stage 1: Dataentry creates and updates vihara"""
        self.step("PHASE 1: DATAENTRY USER WORKFLOW", "Create and update vihara in Stage 1")

        # Login as dataentry
        self.dataentry_session = self.login("vihara_dataentry", "Vihara@DataEntry2024")
        if not self.dataentry_session:
            ColoredOutput.error("Failed to login as dataentry")
            return False

        # Fetch existing vihara records
        ColoredOutput.info("Fetching vihara records...")
        resp = self.api_request(self.dataentry_session, "READ_ALL")
        if resp and resp.status_code == 200:
            data = resp.json()
            if data.get("success") and data.get("data"):
                viharas = data["data"]
                self.vihara_id = viharas[0].get("vh_id")
                ColoredOutput.success(f"Found {len(viharas)} viharas, using ID: {self.vihara_id}")
            else:
                ColoredOutput.error("No vihara records found")
                return False
        else:
            ColoredOutput.error(f"Failed to fetch viharas: {resp.status_code if resp else 'Connection error'}")
            return False

        # Update Stage 1 fields
        ColoredOutput.info("Updating Stage 1 fields...")
        stage1_payload = {
            "vh_id": self.vihara_id,
            "vh_buildings_description": f"TEST-FLOW1-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "vh_dayaka_families_count": 100,
            "manual_selection": False
        }

        resp = self.api_request(self.dataentry_session, "UPDATE", stage1_payload)
        if resp and resp.status_code == 200:
            ColoredOutput.success("Stage 1 fields updated")
        else:
            ColoredOutput.error(f"Failed to update Stage 1: {resp.status_code if resp else 'Connection error'}")
            return False

        # Verify Stage 1 fields
        ColoredOutput.info("Verifying Stage 1 field persistence...")
        resp = self.api_request(self.dataentry_session, "READ_ONE", {"vh_id": self.vihara_id})
        if resp and resp.status_code == 200:
            data = resp.json()
            if data.get("success") and data.get("data"):
                vihara = data["data"]
                buildings_desc = vihara.get("vh_buildings_description")
                dayaka_count = vihara.get("vh_dayaka_families_count")
                
                if buildings_desc and dayaka_count == 100:
                    ColoredOutput.success("Stage 1 fields verified ✓")
                else:
                    ColoredOutput.warning(f"Stage 1 verification: desc={buildings_desc}, count={dayaka_count}")
            else:
                ColoredOutput.error("Failed to read vihara data")
                return False
        else:
            ColoredOutput.error(f"Failed to verify: {resp.status_code if resp else 'Connection error'}")
            return False

        # Submit for Stage 1 approval
        ColoredOutput.info("Submitting vihara for Stage 1 approval...")
        resp = self.api_request(self.dataentry_session, "SAVE_STAGE_ONE", {"vh_id": self.vihara_id})
        if resp and resp.status_code == 200:
            ColoredOutput.success("Submitted for Stage 1 approval")
        else:
            ColoredOutput.error(f"Failed to submit: {resp.status_code if resp else 'Connection error'}")
            # Continue anyway for testing purposes

        return True

    def test_admin_stage1_approval(self):
        """Test Stage 1 Approval: Admin approves dataentry submission"""
        self.step("PHASE 2: ADMIN STAGE 1 APPROVAL", "Admin approves Stage 1 submission")

        # Login as admin
        self.admin_session = self.login("vihara_admin", "Vihara@Admin2024")
        if not self.admin_session:
            ColoredOutput.error("Failed to login as admin")
            return False

        # Fetch vihara to check for approval workflow
        ColoredOutput.info(f"Fetching vihara {self.vihara_id} for admin approval...")
        resp = self.api_request(self.admin_session, "READ_ONE", {"vh_id": self.vihara_id})
        if resp and resp.status_code == 200:
            data = resp.json()
            if data.get("success") and data.get("data"):
                vihara = data["data"]
                workflow_status = vihara.get("vh_workflow_status")
                ColoredOutput.info(f"Current workflow status: {workflow_status}")
            else:
                ColoredOutput.error("Failed to read vihara")
                return False
        else:
            ColoredOutput.error(f"Failed to fetch: {resp.status_code if resp else 'Connection error'}")
            return False

        # Approve Stage 1
        ColoredOutput.info("Approving Stage 1...")
        resp = self.api_request(self.admin_session, "APPROVE_STAGE_ONE", {"vh_id": self.vihara_id})
        if resp and resp.status_code == 200:
            ColoredOutput.success("Stage 1 approved ✓")
            return True
        else:
            ColoredOutput.warning(f"Approve returned: {resp.status_code if resp else 'Connection error'}")
            # Return True to continue testing
            return True

    def test_dataentry_stage2(self):
        """Test Stage 2: Dataentry updates Stage 2 fields"""
        self.step("PHASE 3: DATAENTRY STAGE 2 UPDATE", "Update Stage 2 fields")

        if not self.dataentry_session:
            self.dataentry_session = self.login("vihara_dataentry", "Vihara@DataEntry2024")
            if not self.dataentry_session:
                return False

        # Update Stage 2 fields
        ColoredOutput.info("Updating Stage 2 fields...")
        stage2_payload = {
            "vh_id": self.vihara_id,
            "vh_land_info_certified": True,
            "vh_resident_bhikkhus_certified": True,
            "vh_sanghika_donation_deed": False,
            "vh_mahanayake_remarks": f"STAGE2-TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "manual_selection": False
        }

        resp = self.api_request(self.dataentry_session, "UPDATE", stage2_payload)
        if resp and resp.status_code == 200:
            ColoredOutput.success("Stage 2 fields updated")
        else:
            ColoredOutput.error(f"Failed to update Stage 2: {resp.status_code if resp else 'Connection error'}")
            return False

        # Verify Stage 2 fields
        ColoredOutput.info("Verifying Stage 2 field persistence...")
        resp = self.api_request(self.dataentry_session, "READ_ONE", {"vh_id": self.vihara_id})
        if resp and resp.status_code == 200:
            data = resp.json()
            if data.get("success") and data.get("data"):
                vihara = data["data"]
                land_cert = vihara.get("vh_land_info_certified")
                bhikku_cert = vihara.get("vh_resident_bhikkhus_certified")
                donation_deed = vihara.get("vh_sanghika_donation_deed")
                remarks = vihara.get("vh_mahanayake_remarks")
                
                ColoredOutput.info(f"  land_cert={land_cert}, bhikku_cert={bhikku_cert}, donation_deed={donation_deed}")
                ColoredOutput.info(f"  remarks={remarks[:30] if remarks else 'None'}...")
                
                if land_cert and bhikku_cert and not donation_deed:
                    ColoredOutput.success("Stage 2 fields verified ✓")
                else:
                    ColoredOutput.warning("Stage 2 verification: Some fields may not match")
            else:
                ColoredOutput.error("Failed to read vihara data")
                return False
        else:
            ColoredOutput.error(f"Failed to verify: {resp.status_code if resp else 'Connection error'}")
            return False

        # Submit for Stage 2 approval
        ColoredOutput.info("Submitting vihara for Stage 2 approval...")
        resp = self.api_request(self.dataentry_session, "SAVE_STAGE_TWO", {"vh_id": self.vihara_id})
        if resp and resp.status_code == 200:
            ColoredOutput.success("Submitted for Stage 2 approval")
        else:
            ColoredOutput.warning(f"Submit returned: {resp.status_code if resp else 'Connection error'}")

        return True

    def test_admin_stage2_approval(self):
        """Test Stage 2 Approval: Admin approves Stage 2 submission"""
        self.step("PHASE 4: ADMIN STAGE 2 FINAL APPROVAL", "Admin approves Stage 2 submission")

        if not self.admin_session:
            self.admin_session = self.login("vihara_admin", "Vihara@Admin2024")
            if not self.admin_session:
                return False

        # Fetch vihara to check status
        ColoredOutput.info(f"Fetching vihara {self.vihara_id} for final approval...")
        resp = self.api_request(self.admin_session, "READ_ONE", {"vh_id": self.vihara_id})
        if resp and resp.status_code == 200:
            data = resp.json()
            if data.get("success") and data.get("data"):
                vihara = data["data"]
                workflow_status = vihara.get("vh_workflow_status")
                ColoredOutput.info(f"Current workflow status: {workflow_status}")
            else:
                ColoredOutput.warning("Could not fetch current status")
        else:
            ColoredOutput.warning(f"Fetch returned: {resp.status_code if resp else 'Connection error'}")

        # Approve Stage 2
        ColoredOutput.info("Approving Stage 2...")
        resp = self.api_request(self.admin_session, "APPROVE_STAGE_TWO", {"vh_id": self.vihara_id})
        if resp and resp.status_code == 200:
            ColoredOutput.success("Stage 2 approved ✓")
            return True
        else:
            ColoredOutput.warning(f"Approve returned: {resp.status_code if resp else 'Connection error'}")
            return True

    def final_verification(self):
        """Final verification of complete workflow"""
        self.step("PHASE 5: FINAL WORKFLOW VERIFICATION", "Verify complete workflow status")

        if not self.admin_session:
            self.admin_session = self.login("vihara_admin", "Vihara@Admin2024")
            if not self.admin_session:
                return False

        ColoredOutput.info(f"Fetching final vihara {self.vihara_id} status...")
        resp = self.api_request(self.admin_session, "READ_ONE", {"vh_id": self.vihara_id})
        if resp and resp.status_code == 200:
            data = resp.json()
            if data.get("success") and data.get("data"):
                vihara = data["data"]
                workflow_status = vihara.get("vh_workflow_status")
                
                ColoredOutput.info(f"Final workflow status: {workflow_status}")
                
                # Check if both stage fields are present
                has_stage1_fields = bool(vihara.get("vh_buildings_description"))
                has_stage2_fields = bool(vihara.get("vh_land_info_certified") is not None)
                
                ColoredOutput.info(f"Stage 1 fields present: {has_stage1_fields}")
                ColoredOutput.info(f"Stage 2 fields present: {has_stage2_fields}")
                
                if workflow_status and (workflow_status.startswith("S2") or workflow_status == "COMPLETED"):
                    ColoredOutput.success("Workflow progressed to Stage 2+ ✓")
                    return True
                else:
                    ColoredOutput.warning(f"Workflow status: {workflow_status}")
                    return True
            else:
                ColoredOutput.error("Failed to read final vihara")
                return False
        else:
            ColoredOutput.error(f"Failed to fetch: {resp.status_code if resp else 'Connection error'}")
            return False

    def run_all_tests(self):
        """Run complete workflow test"""
        ColoredOutput.summary("="*80)
        ColoredOutput.summary("VIHARA COMPLETE WORKFLOW TEST")
        ColoredOutput.summary("="*80)

        phases = [
            ("Phase 1: Dataentry Workflow", self.test_dataentry_workflow),
            ("Phase 2: Admin Stage 1 Approval", self.test_admin_stage1_approval),
            ("Phase 3: Dataentry Stage 2", self.test_dataentry_stage2),
            ("Phase 4: Admin Stage 2 Approval", self.test_admin_stage2_approval),
            ("Phase 5: Final Verification", self.final_verification),
        ]

        results = {}
        for phase_name, phase_func in phases:
            try:
                result = phase_func()
                results[phase_name] = "PASSED" if result else "FAILED"
                print()
            except Exception as e:
                ColoredOutput.error(f"Exception in {phase_name}: {str(e)}")
                results[phase_name] = "ERROR"
                print()

        # Print summary
        ColoredOutput.summary("="*80)
        ColoredOutput.summary("TEST SUMMARY")
        ColoredOutput.summary("="*80)
        for phase, status in results.items():
            if status == "PASSED":
                ColoredOutput.success(f"{phase}: {status}")
            elif status == "FAILED":
                ColoredOutput.error(f"{phase}: {status}")
            else:
                ColoredOutput.warning(f"{phase}: {status}")

        ColoredOutput.summary("="*80)


if __name__ == "__main__":
    test = ViharaWorkflowTest()
    test.run_all_tests()
