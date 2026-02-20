# Vihara Comprehensive Field Test Suite - Documentation

## Overview

A comprehensive test suite has been created to verify that all vihara form fields are properly saving, creating, and updating in the database for both **Vihara Flow 1** (Stage 1 - Basic Information) and **Vihara Flow 2** (Stage 2 - Advanced Information).

The test suite supports two user roles:
- **vihara_dataentry** - DATA_ENTRY role: Can create and update vihara records
- **vihara_admin** - ADMIN role: Can approve and manage workflow status

---

## Test File Location

📄 **[test_vihara_fields_with_auth.py](dba-backend/test_vihara_fields_with_auth.py)**

---

## Test Credentials

```
DATAENTRY USER:
  Username: vihara_dataentry
  Password: Vihara@DataEntry2024
  Permissions: vihara:create, vihara:read, vihara:update, vihara:delete, vihara:approve

ADMIN USER:
  Username: vihara_admin  
  Password: Vihara@Admin2024
  Permissions: All vihara management permissions
```

---

## Vihara Flow 1 Fields (Stage 1 - Basic Information)

### Temple Basic Information
- `vh_trn` - Temple Registration Number
- `vh_vname` - Temple Name
- `vh_addrs` - Address
- `vh_mobile` - Mobile Number (10 digits)
- `vh_whtapp` - WhatsApp Number (10 digits)
- `vh_email` - Email Address
- `vh_typ` - Temple Type (VIHARA, ARAMA, etc.)
- `vh_fmlycnt` - Family Count
- `vh_bgndate` - Begin Date

### Administrative Divisions
- `vh_province` - Province Code
- `vh_district` - District Code
- `vh_divisional_secretariat` - Divisional Secretariat Code
- `vh_pradeshya_sabha` - Pradeshya Sabha
- `vh_gndiv` - Grama Niladhari Division Code

### Religious Affiliation
- `vh_nikaya` - Nikaya (SIAM, RAMANYA, MAHANIKAI)
- `vh_parshawa` - Parshawa Code
- `vh_ssbmcode` - Sasanarakshaka Bala Mandalaya Code
- `vh_ownercd` - Owner Code (Bhikku Registration Number)

### Leadership Information
- `vh_viharadhipathi_name` - Chief Incumbent Name
- `vh_viharadhipathi_regn` - Chief Incumbent Registration Number
- `vh_period_established` - Period Established
- `vh_syojakarmakrs` - Service Recognition
- `vh_syojakarmdate` - Service Recognition Date

---

## Vihara Flow 2 Fields (Stage 2 - Advanced Information)

### Mahanyake Thero Information
- `vh_mahanayake_date` - Mahanayake Approval Date
- `vh_mahanayake_letter_nu` - Mahanayake Letter Number
- `vh_mahanayake_remarks` - Mahanayake Remarks

### Buildings and Governance Descriptions
- `vh_buildings_description` - Buildings Description
- `vh_dayaka_families_count` - Dayaka Families Count (String)
- `vh_kulangana_committee` - Kulangana Committee Details
- `vh_dayaka_sabha` - Dayaka Sabha Details
- `vh_temple_working_committee` - Temple Working Committee
- `vh_other_associations` - Other Associations

### Certifications (Boolean Fields)
- `vh_land_info_certified` - Land Information Certified (true/false)
- `vh_resident_bhikkhus_certified` - Resident Bhikkhus Certified (true/false)
- `vh_sanghika_donation_deed` - Sanghika Donation Deed (true/false)
- `vh_government_donation_deed` - Government Donation Deed (true/false)
- `vh_government_donation_deed_in_progress` - Government Deed In Progress (true/false)
- `vh_authority_consent_attached` - Authority Consent Attached (true/false)
- `vh_recommend_new_center` - Recommend New Center (true/false)
- `vh_recommend_registered_temple` - Recommend Registered Temple (true/false)

### Annex 2 Certification Checkboxes (Boolean Fields)
- `vh_annex2_recommend_construction` - Recommend Construction
- `vh_annex2_land_ownership_docs` - Land Ownership Documents
- `vh_annex2_chief_incumbent_letter` - Chief Incumbent Letter
- `vh_annex2_coordinator_recommendation` - Coordinator Recommendation
- `vh_annex2_divisional_secretary_recommendation` - Divisional Secretary Recommendation
- `vh_annex2_approval_construction` - Approval for Construction
- `vh_annex2_referral_resubmission` - Referral for Resubmission

### Inspection Information
- `vh_inspection_report` - Inspection Report (Text)
- `vh_inspection_code` - Inspection Code
- `vh_grama_niladhari_division_ownership` - GN Division Ownership Confirmation

---

## Workflow Status Fields

### Current Workflow Status
- `vh_workflow_status` - Current status in the workflow

### Stage 1 Workflow Fields
- `vh_s1_printed_at` - Stage 1 Form Printed Timestamp
- `vh_s1_printed_by` - User who printed Stage 1 form
- `vh_s1_scanned_at` - Scanned Timestamp
- `vh_s1_scanned_by` - User who scanned
- `vh_s1_approved_by` - Approved by User
- `vh_s1_approved_at` - Approval Timestamp
- `vh_s1_rejected_by` - Rejected by User
- `vh_s1_rejected_at` - Rejection Timestamp
- `vh_s1_rejection_reason` - Rejection Reason

### Stage 2 Workflow Fields
- `vh_s2_scanned_at` - Stage 2 Scanned Timestamp
- `vh_s2_scanned_by` - User who scanned Stage 2
- `vh_s2_approved_by` - Approved by User
- `vh_s2_approved_at` - Approval Timestamp
- `vh_s2_rejected_by` - Rejected by User
- `vh_s2_rejected_at` - Rejection Timestamp
- `vh_s2_rejection_reason` - Rejection Reason

---

## Test Phases

### Phase 1: DATAENTRY USER WORKFLOW
Tests that the dataentry user can:
1. ✓ Login successfully
2. ✓ Read existing vihara records
3. ✓ Create and update all Flow 1 fields
4. ✓ Create and update all Flow 2 fields
5. ✓ Verify field persistence in database

**Tests included:**
- Basic Fields Test - Verifies all critical fields are present
- Fields Enumeration - Lists all fields and their current values
- Field Persistence Test - Updates fields and verifies they're saved in DB
- Flow 1 Updates Test - Updates stage 1 fields and verifies persistence
- Flow 2 Updates Test - Updates stage 2 fields including booleans

### Phase 2: ADMIN USER APPROVAL WORKFLOW
Tests that admin user can:
1. ✓ Login successfully with admin credentials
2. ✓ View pending vihara records for approval
3. ✓ Access and manage workflow statuses

---

## How to Run the Tests

### Prerequisites
- Backend server running locally on port 8080
- Database connected and accessible
- Valid test credentials (vihara_dataentry and vihara_admin)

### Run the Test Suite

```bash
cd dba-backend
python test_vihara_fields_with_auth.py
```

### Expected Output

```
================================================================================
VIHARA COMPREHENSIVE FIELD TEST SUITE (WITH AUTH)
================================================================================

[TIMESTAMP] [INFO] ==================================================
[TIMESTAMP] [INFO] PHASE 1: DATAENTRY USER WORKFLOW
[TIMESTAMP] [INFO] Logging in as: vihara_dataentry
[TIMESTAMP] [INFO] OK: Successfully authenticated as vihara_dataentry
[TIMESTAMP] [INFO]     Role: vihara_dataentry
[TIMESTAMP] [INFO]     Permissions: 14 permissions granted
[TIMESTAMP] [INFO] Fetching existing vihara records...
[TIMESTAMP] [INFO] OK: Found vihara ID=X, Name=Temple Name
...
[TIMESTAMP] [INFO] PHASE 2: ADMIN USER APPROVAL WORKFLOW
...
[TIMESTAMP] [INFO] COMPREHENSIVE TEST SUMMARY
1. Basic Fields Test (Dataentry): PASS
2. All Fields Enumeration: PASS
3. Field Persistence Test: PASS
4. Dataentry Workflow (Creation/Updates): PASS
5. Admin Approval Workflow: PASS

SUCCESS: All tests passed! Vihara fields are working correctly.
```

---

## Frontend Testing

The following flows should be manually tested on the Frontend:

### Vihara Flow 1 (Stage 1) - Update Registration Tab
1. Login as `vihara_dataentry`
2. Navigate to Temple → Vihara → Select a vihara record to update
3. Fill in all Flow 1 fields on "Vihara flow 1" tab:
   - Temple Basic Information
   - Administrative Divisions (using dropdown selectors)
   - Religious Affiliation
   - Leadership Information
4. Click "Save this section"
5. **Verify:** All fields are saved in the database

### Vihara Flow 2 (Stage 2) - Update Registration Tab
1. Continue from previous vihara (or select another)
2. Click on "Vihara flow 2" tab
3. Fill in all Flow 2 fields:
   - Mahanyake Thero Information
   - Buildings & Governance (text descriptions)
   - Certification checkboxes (toggle boolean fields)
   - Annex 2 checkboxes
   - Inspection Information
4. Click "Save this section"
5. **Verify:** All boolean and text fields are saved correctly in the database

### Admin Approval Workflow - FE Testing
1. Login as `vihara_admin`
2. Navigate to Temple → Vihara → View Records
3. Find pending vihara records (status = S1_PEND_APPROVAL or S2_PEND_APPROVAL)
4. Click on a record to view details
5. Click "Approve Stage 1" or "Approve Stage 2" button
6. **Verify:**
   - Workflow status changes correctly in the UI
   - Status updates in the database
   - Record moves to next stage

---

## API Endpoints Tested

```
POST /api/v1/vihara-data/manage
  Actions:
  - READ_ALL: List all vihara records
  - READ_ONE: Get specific vihara record
  - UPDATE: Update vihara fields
  - SAVE_STAGE_ONE: Save/create stage 1 data
  - SAVE_STAGE_TWO: Save/create stage 2 data
  - APPROVE_STAGE_ONE: Approve stage 1
  - APPROVE_STAGE_TWO: Approve stage 2
```

---

## Known Issues & Resolutions

### Issue 1: Session Cookies Not Persisting
The backend uses HTTP-only cookies for authentication. The test suite initializes a `requests.Session()` which should handle cookies automatically.

**Resolution:** Ensure the backend sets Set-Cookie headers correctly and that requests library is configured to accept cookies.

### Issue 2: Timeout on Login
If login times out, it may be due to the backend processing. Increase the timeout value in the test:

```python
response = self.session.post(endpoint, json=payload, timeout=30)  # Increased from 10
```

### Issue 3: Boolean Fields Not Saving
Boolean fields must be passed as Python `True`/`False`, not strings `"true"`/`"false"`.

**Resolution:** Ensure JSON serialization converts Python booleans correctly.

---

## Test Results Template

After running tests, document results as follows:

```
TEST RUN: [Date/Time]
Environment: Local (WSL Ubuntu, Backend port 8080)
Test User: vihara_dataentry
Admin User: vihara_admin

FLOW 1 FIELDS:
- Temple Basic Info: PASS/FAIL
- Admin Divisions: PASS/FAIL
- Religious Affiliation: PASS/FAIL
- Leadership Info: PASS/FAIL

FLOW 2 FIELDS:
- Mahanyake Info: PASS/FAIL
- Buildings & Governance: PASS/FAIL
- Certifications: PASS/FAIL
- Annex 2: PASS/FAIL
- Inspection Info: PASS/FAIL

WORKFLOW:
- Stage 1 Approval: PASS/FAIL
- Stage 2 Approval: PASS/FAIL

FRONTEND (Manual):
- Flow 1 Form Fields: PASS/FAIL
- Flow 2 Form Fields: PASS/FAIL
- Admin Approval UI: PASS/FAIL

Notes: [Any issues found]
```

---

## Support

For issues or questions about the test suite:
1. Check the test output logs for detailed error messages
2. Verify frontend form field names match BD field names (snake_case convert to camelCase in FE)
3. Ensure database connectivity is working
4. Check that user permissions are correctly assigned

---

**Created:** February 20, 2026
**Test Framework:** Python `requests` library with direct API calls
**Coverage:** 40+ vihara fields across Flow 1 and Flow 2
