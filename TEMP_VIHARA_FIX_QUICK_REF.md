# Quick Reference: Temp-Vihara Format Fix

## What Was Fixed
When temp-viharas are returned in the `/api/v1/vihara-data/manage` READ_ALL endpoint, they now have the **same response format** as regular viharas.

## Files Modified
- `app/api/v1/routes/vihara_data.py` - Added helper function and updated 3 locations

## Before vs After

### Before
```json
{
  "vh_id": -1,
  "vh_trn": "TEMP-1",
  "vh_vname": "Temple Name",
  "vh_addrs": "Address",
  "vh_mobile": "0771234567",
  "vh_whtapp": "0771234567",
  "vh_email": "temp1@temporary.local",
  "vh_typ": "TEMP",
  "vh_gndiv": "TEMP",
  "vh_ownercd": "TEMP",
  "vh_parshawa": "TEMP",
  "vh_province": "Province",
  "vh_district": "District",
  "vh_viharadhipathi_name": "Viharadhipathi",
  "vh_workflow_status": "TEMPORARY",
  "vh_created_at": "2025-01-27T10:00:00",
  "vh_created_by": "user123",
  "vh_updated_at": "2025-01-27T10:00:00",
  "vh_updated_by": "user123",
  "vh_is_deleted": false,
  "vh_version_number": 1,
  "temple_lands": [],
  "resident_bhikkhus": []
}
```

### After (Complete Format)
```json
{
  "vh_id": -1,
  "vh_trn": "TEMP-1",
  "vh_vname": "Temple Name",
  "vh_addrs": "Address",
  "vh_mobile": "0771234567",
  "vh_whtapp": "0771234567",
  "vh_email": "temp1@temporary.local",
  "vh_typ": "TEMP",
  "vh_gndiv": "TEMP",
  "vh_ownercd": "TEMP",
  "vh_parshawa": "TEMP",
  "vh_province": "Province",
  "vh_district": "District",
  "vh_divisional_secretariat": null,
  "vh_pradeshya_sabha": null,
  "vh_viharadhipathi_name": "Viharadhipathi",
  "vh_viharadhipathi_regn": null,
  "vh_workflow_status": "TEMPORARY",
  "vh_is_deleted": false,
  "vh_version_number": 1,
  "vh_created_at": "2025-01-27T10:00:00",
  "vh_created_by": "user123",
  "vh_updated_at": "2025-01-27T10:00:00",
  "vh_updated_by": "user123",
  "temple_lands": [],
  "resident_bhikkhus": [],
  "province_info": null,
  "district_info": null,
  "divisional_secretariat_info": null,
  "gn_division_info": null,
  "nikaya_info": null,
  "viharanga_list": [],
  "owner_temp_vihara_info": null,
  "viharadhipathi_temp_bhikku_info": null,
  "vh_ssbmcode": null,
  "vh_syojakarmakrs": null,
  "vh_landownrship": null,
  "vh_pralename": null,
  "vh_bacgrecmn": null,
  "vh_minissecrmrks": null,
  "vh_mahanayake_letter_nu": null,
  "vh_mahanayake_remarks": null,
  "vh_nikaya": null,
  "vh_period_established": null,
  "vh_bgndate": null,
  "vh_mahanayake_date": null,
  "vh_buildings_description": null,
  "vh_building_plan_attached": null,
  "vh_extent": null,
  "vh_extent_unit": null,
  "vh_land_boundary": null,
  "vh_land_ownership_docs": null,
  "vh_sanghika_donation_deed": null,
  "vh_government_donation_deed": null,
  "vh_government_donation_deed_in_progress": null,
  "vh_authority_consent_attached": null,
  "vh_recommend_new_center": null,
  "vh_recommend_registered_temple": null,
  "vh_annex2_recommend_construction": null,
  "vh_annex2_land_ownership_docs": null,
  "vh_annex2_chief_incumbent_letter": null,
  "vh_annex2_coordinator_recommendation": null,
  "vh_annex2_divisional_secretary_recommendation": null,
  "vh_annex2_approval_construction": null,
  "vh_annex2_referral_resubmission": null,
  "vh_form_id": null,
  "vh_stage1_document_path": null,
  "vh_stage2_document_path": null,
  "vh_s1_printed_at": null,
  "vh_s1_printed_by": null,
  "vh_s1_scanned_at": null,
  "vh_s1_scanned_by": null,
  "vh_s1_approved_by": null,
  "vh_s1_approved_at": null,
  "vh_s1_rejected_by": null,
  "vh_s1_rejected_at": null,
  "vh_s1_rejection_reason": null,
  "vh_s2_scanned_at": null,
  "vh_s2_scanned_by": null,
  "vh_s2_approved_by": null,
  "vh_s2_approved_at": null,
  "vh_s2_rejected_by": null,
  "vh_s2_rejected_at": null,
  "vh_s2_rejection_reason": null,
  "vh_approved_by": null,
  "vh_approved_at": null,
  "vh_rejected_by": null,
  "vh_rejected_at": null,
  "vh_rejection_reason": null,
  "vh_printed_at": null,
  "vh_printed_by": null,
  "vh_scanned_at": null,
  "vh_scanned_by": null
}
```

## Helper Function Location
**File**: `app/api/v1/routes/vihara_data.py`  
**Lines**: 31-143  
**Function**: `_build_temp_vihara_dict(temp_vihara) -> dict`

## Usage Points
The function is called in 3 locations in the READ_ALL action:
1. **Line 666** - vihara_admin users, past all regular records
2. **Line 680** - vihara_admin users, filling remaining slots
3. **Line 692** - non-vihara_admin users

## Expected Behavior
✅ All temp-vihara records have the same field structure as regular viharas  
✅ Frontend can treat both temp and regular viharas uniformly  
✅ No "field not found" errors when accessing properties on temp-viharas  
✅ Response format is consistent across all vihara types  

## Testing
Run `python3 test_temp_vihara_format.py` to verify the fix (requires server running on port 8001)
