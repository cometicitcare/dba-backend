# Objection System Implementation

## Overview
The objection system allows administrators to restrict the addition of resident bhikkus/silmathas to specific viharas, aramas, or devalas. Once an objection is approved, no new resident bhikkus can be added to that entity.

## Database Schema

### Table: `objections`

| Column | Type | Description |
|--------|------|-------------|
| `obj_id` | Integer (PK) | Primary key |
| `obj_entity_type` | Enum | Type of entity (VIHARA, ARAMA, DEVALA) |
| `obj_entity_trn` | String(50) | TRN of the entity |
| `obj_entity_name` | String(200) | Name of entity (auto-populated) |
| `obj_reason` | String(1000) | Reason for restriction |
| `obj_status` | Enum | PENDING, APPROVED, REJECTED, CANCELLED |
| `obj_submitted_by` | String(25) | Username who submitted |
| `obj_submitted_at` | Timestamp | Submission time |
| `obj_approved_by` | String(25) | Username who approved |
| `obj_approved_at` | Timestamp | Approval time |
| `obj_rejected_by` | String(25) | Username who rejected |
| `obj_rejected_at` | Timestamp | Rejection time |
| `obj_rejection_reason` | String(500) | Reason for rejection |
| `obj_cancelled_by` | String(25) | Username who cancelled |
| `obj_cancelled_at` | Timestamp | Cancellation time |
| `obj_cancellation_reason` | String(500) | Reason for cancellation |
| `obj_is_deleted` | Boolean | Soft delete flag |
| `obj_created_at` | Timestamp | Creation time |
| `obj_updated_at` | Timestamp | Last update time |
| `obj_updated_by` | String(25) | Last updater |

## API Endpoints

### 1. Manage Objections
**Endpoint:** `POST /api/v1/objections/manage`  
**Permission:** `objection:create`, `objection:update`, or `objection:delete`

#### Actions

##### CREATE - Submit New Objection
```json
{
  "action": "CREATE",
  "payload": {
    "data": {
      "obj_entity_type": "VIHARA",
      "obj_entity_trn": "TRN0000001",
      "obj_entity_name": "Temple Name",
      "obj_reason": "Cannot add more resident bhikkus due to capacity constraints"
    }
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Objection submitted successfully. Status: PENDING",
  "data": {
    "obj_id": 1,
    "obj_entity_type": "VIHARA",
    "obj_entity_trn": "TRN0000001",
    "obj_status": "PENDING",
    ...
  }
}
```

##### READ_ONE - Get Specific Objection
```json
{
  "action": "READ_ONE",
  "payload": {
    "obj_id": 1
  }
}
```

##### READ_ALL - List Objections
```json
{
  "action": "READ_ALL",
  "payload": {
    "obj_entity_type": "VIHARA",
    "obj_status": "APPROVED",
    "page": 1,
    "limit": 10
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Retrieved 5 objections.",
  "data": [...],
  "totalRecords": 5,
  "page": 1,
  "limit": 10
}
```

##### APPROVE - Approve Objection
```json
{
  "action": "APPROVE",
  "payload": {
    "obj_id": 1
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Objection approved. Resident additions are now restricted for this entity.",
  "data": {...}
}
```

##### REJECT - Reject Objection
```json
{
  "action": "REJECT",
  "payload": {
    "obj_id": 1,
    "rejection_reason": "Reason does not justify restriction"
  }
}
```

##### CANCEL - Cancel Objection
```json
{
  "action": "CANCEL",
  "payload": {
    "obj_id": 1,
    "cancellation_reason": "Capacity issue resolved"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Objection cancelled. Resident additions are now allowed for this entity.",
  "data": {...}
}
```

### 2. Check Objection Status
**Endpoint:** `GET /api/v1/objections/check/{entity_type}/{entity_trn}`  
**Permission:** Authenticated user

**Example:** `GET /api/v1/objections/check/VIHARA/TRN0000001`

**Response (with active objection):**
```json
{
  "has_active_objection": true,
  "objection": {
    "obj_id": 1,
    "obj_entity_type": "VIHARA",
    "obj_entity_trn": "TRN0000001",
    "obj_status": "APPROVED",
    "obj_reason": "Cannot add more resident bhikkus due to capacity",
    ...
  },
  "message": "Active objection exists. Cannot add resident bhikkus/silmathas to this VIHARA."
}
```

**Response (no active objection):**
```json
{
  "has_active_objection": false,
  "objection": null,
  "message": "No active objection. Can add resident bhikkus/silmathas to this VIHARA."
}
```

## Workflow

### Objection Lifecycle

```
PENDING ──[APPROVE]──> APPROVED (restricts additions)
   │
   └──[REJECT]──> REJECTED (no restriction)

APPROVED ──[CANCEL]──> CANCELLED (removes restriction)
PENDING ──[CANCEL]──> CANCELLED (removes restriction)
```

### Status Transitions

| From Status | Action | To Status | Effect |
|------------|--------|-----------|--------|
| PENDING | APPROVE | APPROVED | Resident additions blocked |
| PENDING | REJECT | REJECTED | No restriction |
| PENDING | CANCEL | CANCELLED | No restriction |
| APPROVED | CANCEL | CANCELLED | Restriction removed |

## Validation Logic

### When Adding Resident Bhikkus/Silmathas

Before allowing addition of resident bhikkus/silmathas, the system should:

1. Check if an APPROVED objection exists for the entity
2. If exists, return error with objection details
3. If not, allow the operation

**Example validation (utility function):**
```python
from app.utils.objection_validators import validate_no_active_objection
from app.models.objection import EntityType

# In vihara/arama/devala update service
validate_no_active_objection(
    db, 
    entity_type=EntityType.VIHARA,
    entity_trn="TRN0000001",
    operation_description="add resident bhikkus"
)
```

## Integration Points

### Vihara Data
- When updating vihara to add resident bhikkhus
- Before creating new resident_bhikkhu records

### Arama Data  
- When updating arama to add resident silmathas
- Before creating new arama_resident_silmatha records

### Devala Data
- When updating devala to add resident data
- Before creating new resident records

## Permissions Required

| Operation | Permission |
|-----------|-----------|
| Create objection | `objection:create` |
| Approve/Reject objection | `objection:update` |
| Cancel objection | `objection:delete` |
| List/Read objections | `objection:read` |
| Check objection status | Any authenticated user |

## Error Responses

### 403 - Active Objection Exists
```json
{
  "detail": "Cannot add resident bhikkus to this VIHARA. An active objection exists (ID: 1). Reason: Cannot add more residents due to capacity"
}
```

### 404 - Entity Not Found
```json
{
  "detail": "VIHARA with TRN 'TRN9999999' not found"
}
```

### 400 - Invalid Status Transition
```json
{
  "detail": "Cannot approve objection with status APPROVED. Only PENDING objections can be approved."
}
```

### 400 - Active Objection Already Exists
```json
{
  "detail": "Active objection already exists for this VIHARA"
}
```

## Files Created

1. **Model:** `app/models/objection.py`
2. **Schema:** `app/schemas/objection.py`
3. **Repository:** `app/repositories/objection_repo.py`
4. **Service:** `app/services/objection_service.py`
5. **Routes:** `app/api/v1/routes/objections.py`
6. **Utilities:** `app/utils/objection_validators.py`
7. **Migration:** `alembic/versions/20251210000001_create_objections_table.py`

## Database Migration

To apply the migration:

```bash
# Run migration
alembic upgrade head

# Verify table created
psql -d your_database -c "\d objections"
```

## Testing

### Manual Testing Steps

1. **Create an objection:**
```bash
curl -X POST http://localhost:8001/api/v1/objections/manage \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "CREATE",
    "payload": {
      "data": {
        "obj_entity_type": "VIHARA",
        "obj_entity_trn": "TRN0000001",
        "obj_reason": "Test objection reason"
      }
    }
  }'
```

2. **Approve the objection:**
```bash
curl -X POST http://localhost:8001/api/v1/objections/manage \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "APPROVE",
    "payload": {
      "obj_id": 1
    }
  }'
```

3. **Check objection status:**
```bash
curl -X GET http://localhost:8001/api/v1/objections/check/VIHARA/TRN0000001 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

4. **Try to add resident bhikkus** (should fail with 403)

5. **Cancel the objection:**
```bash
curl -X POST http://localhost:8001/api/v1/objections/manage \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "CANCEL",
    "payload": {
      "obj_id": 1,
      "cancellation_reason": "Issue resolved"
    }
  }'
```

6. **Try to add resident bhikkus again** (should succeed)

## Notes

- Entity name is auto-populated from the entity's record when creating an objection
- Only PENDING objections can be approved or rejected
- Only PENDING or APPROVED objections can be cancelled
- When an objection is cancelled, resident additions are immediately allowed again
- All actions are tracked with timestamps and user information for audit purposes
- Soft delete is supported (obj_is_deleted flag)

## Future Enhancements

1. Email notifications when objections are approved/rejected/cancelled
2. Bulk objection management
3. Objection history/audit trail view
4. Integration with location-based access control
5. Automatic objection expiry after a certain period
6. Comments/discussion thread for objections
