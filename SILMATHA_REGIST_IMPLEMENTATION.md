# Silmatha Registration CRUD Implementation

## Overview

Complete CRUD implementation for `silmatha_regist` following the same structure as `bhikku_regist`.

## Files Created

### 1. Database Model

**File:** `app/models/silmatha_regist.py`

- Table: `silmatha_regist`
- Auto-generated registration number: `SIL{YEAR}{SEQUENCE}` (e.g., SIL2025000001)
- All fields from your payload specification
- Workflow and audit fields matching bhikku_regist structure

### 2. Pydantic Schemas

**File:** `app/schemas/silmatha_regist.py`

- `SilmathaRegistCreate` - For creating new records
- `SilmathaRegistUpdate` - For updating existing records
- `SilmathaRegistInternal` - Full schema with all fields
- Request/Response wrappers for each action
- Main request schema with action enum

### 3. Repository Layer

**File:** `app/repositories/silmatha_regist_repo.py`

- `SilmathaRegistRepository` class
- CRUD operations
- Auto-registration number generation
- Location-based access control integration
- Search and filtering capabilities

### 4. Service Layer

**File:** `app/services/silmatha_regist_service.py`

- `SilmathaRegistService` class
- Business logic and validations
- Contact field validation (mobile, email)
- Workflow management (approve, reject, mark printed, mark scanned)
- Auto-assignment of province/district from user location

### 5. API Routes

**File:** `app/api/v1/routes/silmatha_regist.py`

- Single unified endpoint: `/api/v1/silmatha-regist/manage`
- Supports all CRUD actions via payload

### 6. Database Migration

**File:** `alembic/versions/20251117000002_create_silmatha_regist_table.py`

- Creates `silmatha_regist` table with all columns
- Indexes on `sil_id`, `sil_regn`, and `sil_workflow_status`
- ✅ **Migration applied successfully**

## API Endpoint

**URL:** `POST /api/v1/silmatha-regist/manage`

**Authentication:** Required (JWT token)

**Permissions:** Requires one of:

- `silmatha:create`
- `silmatha:update`
- `silmatha:delete`
- `silmatha:read`

### Additional Endpoints

**File Upload:**

- `POST /api/v1/silmatha-regist/{sil_regn}/upload-scanned-document`
- Upload scanned document file (PDF, JPG, PNG - max 5MB)
- Requires: `silmatha:update` permission

**Workflow Management:**

- `POST /api/v1/silmatha-regist/workflow`
- Manage complete workflow lifecycle
- Requires: `silmatha:approve` OR `silmatha:update` permission

## Supported Actions

### 1. CREATE

Creates a new silmatha registration record.

**Payload:**

```json
{
  "action": "CREATE",
  "payload": {
    "data": {
      "sil_reqstdate": "2025-10-31",
      "sil_gihiname": "dfsdf",
      "sil_dofb": "2025-10-30",
      "sil_fathrname": "sdfsf",
      "sil_email": "sdfsd@gmail.com",
      "sil_mobile": "0771234567",
      "sil_fathrsaddrs": "Father's Address",
      "sil_fathrsmobile": "0771234567",
      "sil_birthpls": "Colombo General Hospital",
      "sil_province": "WP",
      "sil_district": "DC001",
      "sil_korale": "dfgd",
      "sil_pattu": "gdfg",
      "sil_division": "DV001",
      "sil_vilage": "dfg",
      "sil_gndiv": "GN001",
      "sil_viharadhipathi": "BH2025000001",
      "sil_cat": "CAT01",
      "sil_currstat": "ST01",
      "sil_declaration_date": "2025-10-28",
      "sil_remarks": "sdfsdfdf",
      "sil_mahanadate": "2025-10-30",
      "sil_mahananame": "sdfdf",
      "sil_mahanaacharyacd": "BH2025000001",
      "sil_robing_tutor_residence": "TRN0000008",
      "sil_mahanatemple": "TRN0000008",
      "sil_robing_after_residence_temple": "TRN0000008"
    }
  }
}
```

**Response:**

```json
{
  "success": true,
  "message": "Silmatha record created successfully.",
  "data": {
    "sil_id": 1,
    "sil_regn": "SIL2025000001",
    "sil_workflow_status": "PENDING",
    ...
  }
}
```

### 2. READ_ONE

Retrieves a single silmatha record by registration number.

**Payload:**

```json
{
  "action": "READ_ONE",
  "payload": {
    "sil_regn": "SIL2025000001"
  }
}
```

### 3. READ_ALL

Retrieves all silmatha records with pagination and filtering.

**Payload:**

```json
{
  "action": "READ_ALL",
  "payload": {
    "skip": 0,
    "limit": 100,
    "search_key": "search term",
    "province": "WP",
    "district": "DC001",
    "workflow_status": "PENDING"
  }
}
```

### 4. UPDATE

Updates an existing silmatha record.

**Payload:**

```json
{
  "action": "UPDATE",
  "payload": {
    "sil_regn": "SIL2025000001",
    "data": {
      "sil_gihiname": "Updated Name",
      "sil_mobile": "0771234568"
    }
  }
}
```

### 5. DELETE

Soft deletes a silmatha record.

**Payload:**

```json
{
  "action": "DELETE",
  "payload": {
    "sil_regn": "SIL2025000001"
  }
}
```

### 6. APPROVE

Approves a pending silmatha registration.

**Payload:**

```json
{
  "action": "APPROVE",
  "payload": {
    "sil_regn": "SIL2025000001"
  }
}
```

### 7. REJECT

Rejects a silmatha registration with a reason.

**Payload:**

```json
{
  "action": "REJECT",
  "payload": {
    "sil_regn": "SIL2025000001",
    "rejection_reason": "Invalid information provided"
  }
}
```

### 8. MARK_PRINTED

Marks a record as printed.

**Payload:**

```json
{
  "action": "MARK_PRINTED",
  "payload": {
    "sil_regn": "SIL2025000001"
  }
}
```

### 9. MARK_SCANNED

Marks a record as scanned with document path.

**Payload:**

```json
{
  "action": "MARK_SCANNED",
  "payload": {
    "sil_regn": "SIL2025000001",
    "scanned_document_path": "/path/to/scanned/document.pdf"
  }
}
```

## Workflow Management

The workflow endpoint (`POST /api/v1/silmatha-regist/workflow`) supports the complete lifecycle of silmatha registrations and reprints.

### Main Workflow Actions

#### APPROVE

Approve a pending silmatha registration.

**Payload:**

```json
{
  "sil_regn": "SIL2025000001",
  "action": "APPROVE"
}
```

#### REJECT

Reject a pending silmatha registration.

**Payload:**

```json
{
  "sil_regn": "SIL2025000001",
  "action": "REJECT",
  "rejection_reason": "Invalid information provided"
}
```

#### MARK_PRINTING

Mark the certificate as in printing process.

**Payload:**

```json
{
  "sil_regn": "SIL2025000001",
  "action": "MARK_PRINTING"
}
```

#### MARK_PRINTED

Mark the certificate as printed.

**Payload:**

```json
{
  "sil_regn": "SIL2025000001",
  "action": "MARK_PRINTED"
}
```

#### MARK_SCANNED

Mark the certificate as scanned (completes workflow).

**Payload:**

```json
{
  "sil_regn": "SIL2025000001",
  "action": "MARK_SCANNED"
}
```

#### RESET_TO_PENDING

Reset workflow to pending state (for corrections).

**Payload:**

```json
{
  "sil_regn": "SIL2025000001",
  "action": "RESET_TO_PENDING"
}
```

### Reprint Workflow Actions

#### REQUEST_REPRINT

Request a certificate reprint.

**Payload:**

```json
{
  "sil_regn": "SIL2025000001",
  "action": "REQUEST_REPRINT",
  "reprint_reason": "Certificate damaged"
}
```

#### ACCEPT_REPRINT

Accept a reprint request.

**Payload:**

```json
{
  "sil_regn": "SIL2025000001",
  "action": "ACCEPT_REPRINT"
}
```

#### REJECT_REPRINT

Reject a reprint request.

**Payload:**

```json
{
  "sil_regn": "SIL2025000001",
  "action": "REJECT_REPRINT",
  "rejection_reason": "No valid reason provided"
}
```

#### COMPLETE_REPRINT

Mark reprint as completed.

**Payload:**

```json
{
  "sil_regn": "SIL2025000001",
  "action": "COMPLETE_REPRINT"
}
```

## File Upload

Upload a scanned document for a silmatha registration.

**Endpoint:** `POST /api/v1/silmatha-regist/{sil_regn}/upload-scanned-document`

**Method:** Multipart form data

**Parameters:**

- `file`: Scanned document file (max 5MB)

**Allowed formats:** PDF, JPG, JPEG, PNG

**Example (cURL):**

```bash
curl -X POST \
  "http://localhost:8000/api/v1/silmatha-regist/SIL2025000001/upload-scanned-document" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/document.pdf"
```

**Response:**

```json
{
  "success": true,
  "message": "Scanned document uploaded successfully.",
  "data": {
    "sil_id": 1,
    "sil_regn": "SIL2025000001",
    "sil_scanned_document_path": "silmatha_update/2025/11/17/SIL2025000001/scanned_document_abc123.pdf",
    ...
  }
}
```

## Features

✅ **Auto-generated Registration Numbers** - Format: SIL{YEAR}{6-digit sequence}
✅ **Location-Based Access Control** - Integrated with existing LBAC system
✅ **Complete Workflow Management** - PENDING → APPROVED → PRINTING → PRINTED → SCANNED → COMPLETED
✅ **Reprint Workflow** - REQUEST_REPRINT → ACCEPT_REPRINT → COMPLETE_REPRINT
✅ **File Upload** - Upload scanned documents (PDF, JPG, PNG - max 5MB)
✅ **Audit Trail** - Tracks created_by, updated_by, timestamps, version numbers
✅ **Soft Delete** - Records are marked as deleted, not physically removed
✅ **Contact Validation** - Email and mobile number format validation
✅ **Unique Constraints** - Prevents duplicate mobile/email
✅ **Search & Filtering** - Search across multiple fields, filter by province, district, status, etc.
✅ **Workflow State Transitions** - Enforced workflow rules and validations
✅ **Reset to Pending** - Allow corrections by resetting workflow to pending state

## Workflow States

**Main Workflow:**

1. **PENDING** - Initial state after creation
2. **APPROVED** - After approval
3. **PRINTING** - Certificate being printed
4. **PRINTED** - Certificate printed
5. **SCANNED** - Certificate scanned and uploaded
6. **COMPLETED** - Final state
7. **REJECTED** - Registration rejected

**Reprint Workflow:**

1. **REPRINT_PENDING** - Reprint requested
2. **REPRINT_ACCEPTED** - Reprint approved
3. **REPRINT_REJECTED** - Reprint denied
4. **REPRINT_COMPLETED** - Reprint completed

## Workflow Actions Available

### Via `/manage` Endpoint:

- CREATE, READ_ONE, READ_ALL, UPDATE, DELETE
- APPROVE, REJECT, MARK_PRINTED, MARK_SCANNED

### Via `/workflow` Endpoint (Extended):

- APPROVE, REJECT
- MARK_PRINTING, MARK_PRINTED, MARK_SCANNED
- RESET_TO_PENDING
- REQUEST_REPRINT, ACCEPT_REPRINT, REJECT_REPRINT, COMPLETE_REPRINT

### Via File Upload Endpoint:

- Upload scanned documents to `sil_scanned_document_path`

## Database Table Structure

**Table Name:** `silmatha_regist`

**Key Fields:**

- `sil_id` - Primary key (auto-increment)
- `sil_regn` - Unique registration number (auto-generated)
- `sil_workflow_status` - Current workflow state
- All fields from your payload
- Complete workflow tracking fields
- Audit fields (created_at, updated_at, created_by, updated_by, etc.)

## Router Integration

Added to `app/api/v1/router.py` under "Silmatha Management" section:

```python
api_router.include_router(
    silmatha_regist.router,
    prefix="/silmatha-regist",
    tags=["🕉️ Silmatha Management"]
)
```

## Testing

A test script has been created: `test_silmatha_regist_api.py`

## Next Steps

1. **Add Permissions**: Create the following permissions in your RBAC system:

   - `silmatha:create`
   - `silmatha:read`
   - `silmatha:update`
   - `silmatha:delete`

2. **Test the API**: Use the test script or Postman to test all actions

3. **Frontend Integration**: Update frontend to use the new endpoint

## Notes

- The implementation follows the exact same pattern as `bhikku_regist`
- All validation and business logic from bhikku is replicated
- Registration number format is `SIL` instead of `BH`
- The field prefix is `sil_` instead of `br_`
