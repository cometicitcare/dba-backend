# Temp-Vihara Response Format Fix

## Issue
When adding temp-vihara records, they were not displaying correctly in the vihara-data READ_ALL endpoint. The response format was not matching the regular vihara records format, causing inconsistency in the API response structure.

## Root Cause
The temporary vihara records in the `READ_ALL` action were being manually constructed as dictionaries with only a minimal set of fields. Regular vihara records, on the other hand, were being passed through the `ViharaOut` schema validation which includes all the fields defined in the `ViharaBase` and `ViharaOut` schemas.

The mismatch meant:
- Regular viharas had ~100+ fields in the response
- Temp-viharas had only ~20 fields in the response
- Missing fields: nested info objects, workflow fields, document fields, audit fields, etc.

## Solution
Created a helper function `_build_temp_vihara_dict()` that constructs a complete temporary vihara dictionary matching the full structure of `ViharaOut`:

### Changes Made in [app/api/v1/routes/vihara_data.py](app/api/v1/routes/vihara_data.py)

1. **Added Helper Function** (Lines 31-143):
   - `_build_temp_vihara_dict(temp_vihara)` - Converts temporary vihara records to complete vihara-compatible format
   - Includes all fields from the `ViharaOut` schema
   - Sets appropriate default/null values for fields not applicable to temp viharas
   - Properly formats mobile number and email

2. **Updated Three Locations** where temp-vihara dicts were being created:
   - **Line 666**: For vihara_admin users when past all regular records
   - **Line 680**: For vihara_admin users when partially filling remaining slots
   - **Line 692**: For non-vihara_admin users

3. **Removed Duplicate Code**:
   - Eliminated three duplicated sections of temp-vihara dictionary construction
   - Now all temp-viharas use the single helper function ensuring consistency

## Fields Now Included in Temp-Vihara Response

### Primary Fields (Populated)
- `vh_id`: Negative value of temp vihara ID
- `vh_trn`: "TEMP-{id}" format
- `vh_vname`: Temp vihara name
- `vh_addrs`: Temp vihara address
- `vh_mobile`, `vh_whtapp`: Contact numbers
- `vh_email`: Generated temporary email
- `vh_typ`, `vh_gndiv`, `vh_ownercd`, `vh_parshawa`: Set to "TEMP"
- `vh_province`, `vh_district`: From temp vihara data
- `vh_viharadhipathi_name`: From temp vihara data
- Audit fields: `vh_created_at`, `vh_created_by`, `vh_updated_at`, `vh_updated_by`
- Status fields: `vh_workflow_status="TEMPORARY"`, `vh_is_deleted=False`, `vh_version_number=1`

### Relationship Fields (Empty)
- `temple_lands`: Empty array
- `resident_bhikkhus`: Empty array

### Optional Nested Info Fields (Null)
- `province_info`, `district_info`, `divisional_secretariat_info`
- `gn_division_info`, `nikaya_info`
- `owner_temp_vihara_info`, `viharadhipathi_temp_bhikku_info`
- `viharanga_list`

### Optional Document/Workflow Fields (Null)
- Stage 1 & 2 fields: `vh_stage1_document_path`, `vh_stage2_document_path`, etc.
- Workflow fields: `vh_s1_printed_at`, `vh_s1_scanned_at`, etc.
- Approval/Rejection fields: All set to None
- All other document and certification fields

## Benefits
✅ **Consistent Response Format**: Temp-viharas and regular viharas now have the same field structure  
✅ **Eliminates Type Errors**: Frontend won't encounter unexpected null fields  
✅ **Better API Predictability**: Clients can expect all fields to be present (even if null)  
✅ **Code Maintainability**: Single source of truth for temp-vihara formatting  
✅ **Reduced Duplication**: One helper function vs. three duplicate code blocks  

## Testing
Created `test_temp_vihara_format.py` to verify:
- Temp-vihara records are returned in READ_ALL
- All fields present in regular viharas are also present in temp-viharas
- Response format consistency between regular and temporary viharas

## Notes
- Temp viharas have `vh_id` as negative values (e.g., -1, -2) to distinguish them from regular viharas
- `vh_workflow_status` is set to "TEMPORARY" to identify these records
- All optional fields are properly initialized to None/empty lists to maintain schema consistency
