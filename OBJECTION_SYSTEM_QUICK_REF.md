# Objection System - Quick Reference

## Overview
Restrict resident bhikku/silmatha additions to vihara/arama/devala entities.

## Quick Start

### 1. Submit Objection
```bash
POST /api/v1/objections/manage
{
  "action": "CREATE",
  "payload": {
    "data": {
      "obj_entity_type": "VIHARA",
      "obj_entity_trn": "TRN0000001",
      "obj_reason": "Cannot add more residents"
    }
  }
}
```

### 2. Approve Objection (Activates Restriction)
```bash
POST /api/v1/objections/manage
{
  "action": "APPROVE",
  "payload": {
    "obj_id": 1
  }
}
```

### 3. Check Status
```bash
GET /api/v1/objections/check/VIHARA/TRN0000001
```

### 4. Cancel Objection (Removes Restriction)
```bash
POST /api/v1/objections/manage
{
  "action": "CANCEL",
  "payload": {
    "obj_id": 1,
    "cancellation_reason": "Issue resolved"
  }
}
```

## All Actions

| Action | Description | Status Flow |
|--------|-------------|-------------|
| `CREATE` | Submit new objection | → PENDING |
| `READ_ONE` | Get specific objection | - |
| `READ_ALL` | List objections with filters | - |
| `APPROVE` | Approve objection | PENDING → APPROVED |
| `REJECT` | Reject objection (with reason) | PENDING → REJECTED |
| `CANCEL` | Cancel objection (with reason) | PENDING/APPROVED → CANCELLED |

## Status Meanings

- **PENDING**: Submitted, awaiting review
- **APPROVED**: Activated - resident additions blocked ❌
- **REJECTED**: Not approved - no restriction ✅
- **CANCELLED**: Was approved but now removed - restriction lifted ✅

## Entity Types

- `VIHARA` - For vihara/temple entities
- `ARAMA` - For arama entities  
- `DEVALA` - For devala entities

## Example Workflows

### Full Workflow (Create → Approve → Cancel)
```bash
# 1. Create objection
curl -X POST /api/v1/objections/manage \
  -H "Authorization: Bearer TOKEN" \
  -d '{"action":"CREATE","payload":{"data":{"obj_entity_type":"VIHARA","obj_entity_trn":"TRN0000001","obj_reason":"Capacity full"}}}'

# 2. Approve (blocks additions)
curl -X POST /api/v1/objections/manage \
  -H "Authorization: Bearer TOKEN" \
  -d '{"action":"APPROVE","payload":{"obj_id":1}}'

# 3. Cancel later (allows additions again)
curl -X POST /api/v1/objections/manage \
  -H "Authorization: Bearer TOKEN" \
  -d '{"action":"CANCEL","payload":{"obj_id":1,"cancellation_reason":"Capacity increased"}}'
```

### Rejection Workflow (Create → Reject)
```bash
# 1. Create objection
curl -X POST /api/v1/objections/manage \
  -H "Authorization: Bearer TOKEN" \
  -d '{"action":"CREATE","payload":{"data":{"obj_entity_type":"ARAMA","obj_entity_trn":"ARN0000001","obj_reason":"Test"}}}'

# 2. Reject (no restriction applied)
curl -X POST /api/v1/objections/manage \
  -H "Authorization: Bearer TOKEN" \
  -d '{"action":"REJECT","payload":{"obj_id":1,"rejection_reason":"Insufficient justification"}}'
```

## List Objections with Filters

```bash
POST /api/v1/objections/manage
{
  "action": "READ_ALL",
  "payload": {
    "obj_entity_type": "VIHARA",     // Optional filter
    "obj_entity_trn": "TRN0000001",  // Optional filter
    "obj_status": "APPROVED",         // Optional filter
    "page": 1,                        // Default: 1
    "limit": 10                       // Default: 10, max: 100
  }
}
```

## Validation Helper (For Developers)

Add this check before allowing resident additions:

```python
from app.utils.objection_validators import validate_no_active_objection
from app.models.objection import EntityType

# Before adding residents
validate_no_active_objection(
    db,
    entity_type=EntityType.VIHARA,
    entity_trn=vihara_trn,
    operation_description="add resident bhikkus"
)
```

## Permissions

- `objection:create` - Submit new objections
- `objection:update` - Approve/reject objections
- `objection:delete` - Cancel objections
- `objection:read` - View objections

## Common Errors

### 403 - Active Objection Exists
```
Cannot add resident bhikkus to this VIHARA. 
An active objection exists (ID: 1). 
Reason: Cannot add more residents due to capacity
```
**Solution:** Cancel the objection or wait for approval decision.

### 404 - Entity Not Found
```
VIHARA with TRN 'TRN9999999' not found
```
**Solution:** Verify the entity TRN exists.

### 400 - Invalid Status Transition
```
Cannot approve objection with status APPROVED. 
Only PENDING objections can be approved.
```
**Solution:** Check current status before attempting transition.

## Database Table

```sql
-- Check objections
SELECT obj_id, obj_entity_type, obj_entity_trn, obj_status, obj_reason 
FROM objections 
WHERE obj_is_deleted = FALSE;

-- Check active objections
SELECT * FROM objections 
WHERE obj_status = 'APPROVED' AND obj_is_deleted = FALSE;
```

## Files

- Model: `app/models/objection.py`
- Schema: `app/schemas/objection.py`
- Repository: `app/repositories/objection_repo.py`
- Service: `app/services/objection_service.py`
- Routes: `app/api/v1/routes/objections.py`
- Validator: `app/utils/objection_validators.py`
- Migration: `alembic/versions/20251210000005_create_objections_table.py`
- Docs: `OBJECTION_SYSTEM_IMPLEMENTATION.md`
