# Vihara Endpoint Access Fix

## Problem Summary

The Vihara endpoint (`/api/v1/vihara/manage`) was inaccessible to Super Administrator users because:

1. **Wrong Permissions Required**: The endpoint was checking for `system:create`, `system:update`, `system:delete` permissions
2. **Missing Vihara Permissions**: The user didn't have `vihara:*` permissions in their role

## What Was Fixed

### 1. Updated Endpoint Permissions ✅

**File**: `app/api/v1/routes/vihara_data.py`

**Changed FROM:**
```python
@router.post("/manage", response_model=ViharaManagementResponse, 
    dependencies=[has_any_permission("system:create", "system:update", "system:delete")])
```

**Changed TO:**
```python
@router.post("/manage", response_model=ViharaManagementResponse, 
    dependencies=[has_any_permission("vihara:create", "vihara:read", "vihara:update", "vihara:delete")])
```

This aligns with the RBAC design where permissions follow the `resource:action` pattern (e.g., `bhikku:create`, `silmatha:read`, etc.)

### 2. Created Database Setup Scripts

Two scripts were created to add vihara permissions:

#### Option A: SQL Script
**File**: `add_vihara_permissions.sql`

Run with:
```bash
psql $DATABASE_URL -f add_vihara_permissions.sql
```

#### Option B: Python Script (Recommended)
**File**: `add_vihara_permissions.py`

Run with:
```bash
python add_vihara_permissions.py
```

This script:
- ✅ Creates 6 vihara permissions (`vihara:create`, `read`, `update`, `delete`, `export`, `approve`)
- ✅ Assigns all vihara permissions to Super Administrator role
- ✅ Assigns all vihara permissions to Bhikku Administrator role
- ✅ Assigns `vihara:read` to other admin roles (Silmatha Admin, Damma Admin, etc.)
- ✅ Verifies the setup
- ✅ Shows which users have vihara permissions

## How to Apply the Fix

### Step 1: Run the Permission Setup Script

```bash
cd /Users/shanuka/Desktop/Work\ project/dba-backend
python add_vihara_permissions.py
```

**Expected Output:**
```
============================================================
VIHARA PERMISSIONS SETUP SCRIPT
============================================================

1. Checking System Administration group...
   ✓ System Administration group exists

2. Creating vihara permissions...
   ✓ vihara:approve
   ✓ vihara:create
   ✓ vihara:delete
   ✓ vihara:export
   ✓ vihara:read
   ✓ vihara:update

3. Checking Super Administrator role...
   ✓ Super Administrator role exists

4. Assigning vihara permissions to Super Administrator...
   ✓ 6 vihara permissions assigned to Super Administrator

5. Assigning vihara permissions to Bhikku Administrator...
   ✓ 6 vihara permissions assigned to Bhikku Administrator

6. Assigning vihara:read to other administrator roles...
   ✓ vihara:read assigned to 4 additional roles

7. Verification:

   Total vihara permissions in database: 6
   - vihara:approve: Approve vihara registrations
   - vihara:create: Create new vihara (temple) records
   - vihara:delete: Delete vihara (temple) records
   - vihara:export: Export vihara data
   - vihara:read: View vihara (temple) records
   - vihara:update: Update existing vihara (temple) records

   Roles with vihara permissions:
   - Super Administrator: 6 permissions
   - Bhikku Administrator: 6 permissions
   - Silmatha Administrator: 1 permissions
   ...

✅ Vihara permissions setup complete!
```

### Step 2: Restart the Application

```bash
# If running with uvicorn
uvicorn app.main:app --reload

# Or if using docker
docker-compose restart
```

### Step 3: Test the Endpoint

Use your existing Super Admin token to test:

```bash
curl -X POST "http://localhost:8000/api/v1/vihara/manage" \
  -H "Content-Type: application/json" \
  -H "Cookie: access_token=YOUR_TOKEN" \
  -d '{
    "action": "READ_ALL",
    "payload": {
      "page": 1,
      "limit": 10
    }
  }'
```

## Vihara Permissions Details

The following permissions are now available:

| Permission | Action | Who Has It | Description |
|------------|--------|-----------|-------------|
| `vihara:create` | Create | Super Admin, Bhikku Admin | Create new vihara records |
| `vihara:read` | Read | Super Admin, All Admins | View vihara records |
| `vihara:update` | Update | Super Admin, Bhikku Admin | Update vihara information |
| `vihara:delete` | Delete | Super Admin, Bhikku Admin | Delete vihara records |
| `vihara:export` | Export | Super Admin, Bhikku Admin | Export vihara data |
| `vihara:approve` | Approve | Super Admin, Bhikku Admin | Approve vihara registrations |

## Verification

After applying the fix, your Super Admin user should have the following in their permission list:

```json
{
  "permissions": [
    "vihara:create",
    "vihara:read", 
    "vihara:update",
    "vihara:delete",
    "vihara:export",
    "vihara:approve",
    // ... other permissions
  ],
  "permission_map": {
    "vihara": [
      "create",
      "read",
      "update", 
      "delete",
      "export",
      "approve"
    ],
    // ... other resource mappings
  }
}
```

## Why This Happened

This issue occurred because:

1. **Inconsistent Permission Naming**: The vihara endpoint was using generic `system:*` permissions instead of resource-specific `vihara:*` permissions
2. **Missing Permission Seeds**: The vihara permissions weren't created in the initial RBAC setup migration
3. **Documentation vs Implementation Gap**: The RBAC_GUIDE.md documented `vihara:*` permissions, but they weren't actually in the database

## Prevention

To prevent similar issues in the future:

1. ✅ **Follow the `resource:action` pattern** for all new endpoints
2. ✅ **Document permissions** in RBAC_GUIDE.md when creating new resources
3. ✅ **Create migration scripts** that seed permissions for new resources
4. ✅ **Test with non-super-admin roles** to ensure proper permission checks

## Related Files

- `app/api/v1/routes/vihara_data.py` - Vihara endpoint (UPDATED)
- `add_vihara_permissions.py` - Permission setup script (NEW)
- `add_vihara_permissions.sql` - SQL setup script (NEW)
- `RBAC_GUIDE.md` - RBAC documentation (reference)
- `VIHARA_ACCESS_FIX.md` - This document (NEW)

## Contact

If you encounter any issues after applying this fix:
1. Check the server logs for permission-related errors
2. Verify your user's permissions with: `GET /api/v1/auth/me`
3. Run the verification script: `python add_vihara_permissions.py`

---

**Fixed on**: November 15, 2025  
**Fixed by**: GitHub Copilot  
**Issue**: Vihara endpoint inaccessible to Super Administrator
**Status**: ✅ RESOLVED
