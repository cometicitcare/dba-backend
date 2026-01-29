# Sasanarakshaka Bala Mandalaya CRUD Implementation

## Overview
A complete CRUD (Create, Read, Update, Delete) implementation for **Sasanarakshaka Bala Mandalaya** based on the `cmm_sasanarbm` table, following the same architecture pattern as `bhikku_regist`.

---

## Database Table Structure

**Table Name:** `cmm_sasanarbm`

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| sr_id | int4 | NO | Primary Key (Auto-increment) |
| sr_ssbmcode | varchar(10) | NO | Sasana Rakshaka Bala Mandalaya Code (Unique) |
| sr_dvcd | varchar(10) | NO | Divisional Secretariat Code (FK to cmm_dvsec.dv_dvcode) |
| sr_ssbname | varchar(200) | YES | Sasana Rakshaka Bala Mandalaya Name |
| sr_sbmnayakahimi | varchar(12) | YES | Nayaka Himi Registration Number (FK to bhikku_regist.br_regn) |
| sr_version | timestamp | NO | Version timestamp |
| sr_is_deleted | bool | YES | Soft delete flag (default: false) |
| sr_created_at | timestamp | YES | Creation timestamp |
| sr_updated_at | timestamp | YES | Last update timestamp |
| sr_created_by | varchar(25) | YES | User who created the record |
| sr_updated_by | varchar(25) | YES | User who last updated the record |
| sr_version_number | int4 | YES | Version number for optimistic locking |

---

## API Endpoints

### Base URL: `/api/v1/sasanarakshaka`

### 1. Create Sasanarakshaka Bala Mandalaya
**POST** `/api/v1/sasanarakshaka`

**Permission Required:** `sasanarakshaka:create`

**Request Body:**
```json
{
  "sr_ssbmcode": "SB001",
  "sr_dvcd": "DV001",
  "sr_ssbname": "Colombo Sasana Rakshaka Bala Mandalaya",
  "sr_sbmnayakahimi": "BH2025000001"
}
```

**Response (201 Created):**
```json
{
  "status": "success",
  "message": "Sasanarakshaka Bala Mandalaya created successfully.",
  "data": {
    "sr_id": 1,
    "sr_ssbmcode": "SB001",
    "sr_dvcd": "DV001",
    "sr_ssbname": "Colombo Sasana Rakshaka Bala Mandalaya",
    "sr_sbmnayakahimi": "BH2025000001",
    "sr_version": "2026-01-15T10:30:00",
    "sr_is_deleted": false,
    "sr_created_at": "2026-01-15T10:30:00",
    "sr_updated_at": "2026-01-15T10:30:00",
    "sr_created_by": "admin",
    "sr_updated_by": "admin",
    "sr_version_number": 1
  }
}
```

---

### 2. Get All Sasanarakshaka Bala Mandalaya (List with Pagination)
**GET** `/api/v1/sasanarakshaka`

**Permission Required:** `sasanarakshaka:read`

**Query Parameters:**
- `page` (optional, default: 1) - Page number
- `limit` (optional, default: 100, max: 1000) - Items per page
- `search_key` (optional) - Search across all text fields
- `sr_dvcd` (optional) - Filter by divisional secretariat code

**Example Request:**
```
GET /api/v1/sasanarakshaka?page=1&limit=10&search_key=Colombo&sr_dvcd=DV001
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Sasanarakshaka Bala Mandalaya list retrieved successfully.",
  "data": [
    {
      "sr_id": 1,
      "sr_ssbmcode": "SB001",
      "sr_dvcd": "DV001",
      "sr_ssbname": "Colombo Sasana Rakshaka Bala Mandalaya",
      "sr_sbmnayakahimi": "BH2025000001",
      "sr_version": "2026-01-15T10:30:00",
      "sr_is_deleted": false,
      "sr_created_at": "2026-01-15T10:30:00",
      "sr_updated_at": "2026-01-15T10:30:00",
      "sr_created_by": "admin",
      "sr_updated_by": "admin",
      "sr_version_number": 1
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 10
}
```

---

### 3. Get Single Sasanarakshaka Bala Mandalaya by ID
**GET** `/api/v1/sasanarakshaka/{sr_id}`

**Permission Required:** `sasanarakshaka:read`

**Example Request:**
```
GET /api/v1/sasanarakshaka/1
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Sasanarakshaka Bala Mandalaya retrieved successfully.",
  "data": {
    "sr_id": 1,
    "sr_ssbmcode": "SB001",
    "sr_dvcd": "DV001",
    "sr_ssbname": "Colombo Sasana Rakshaka Bala Mandalaya",
    "sr_sbmnayakahimi": "BH2025000001",
    "sr_version": "2026-01-15T10:30:00",
    "sr_is_deleted": false,
    "sr_created_at": "2026-01-15T10:30:00",
    "sr_updated_at": "2026-01-15T10:30:00",
    "sr_created_by": "admin",
    "sr_updated_by": "admin",
    "sr_version_number": 1
  }
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Sasanarakshaka Bala Mandalaya with ID 999 not found"
}
```

---

### 4. Get Single Sasanarakshaka Bala Mandalaya by Code
**GET** `/api/v1/sasanarakshaka/code/{sr_ssbmcode}`

**Permission Required:** `sasanarakshaka:read`

**Example Request:**
```
GET /api/v1/sasanarakshaka/code/SB001
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Sasanarakshaka Bala Mandalaya retrieved successfully.",
  "data": {
    "sr_id": 1,
    "sr_ssbmcode": "SB001",
    "sr_dvcd": "DV001",
    "sr_ssbname": "Colombo Sasana Rakshaka Bala Mandalaya",
    "sr_sbmnayakahimi": "BH2025000001",
    ...
  }
}
```

---

### 5. Update Sasanarakshaka Bala Mandalaya
**PUT** `/api/v1/sasanarakshaka/{sr_id}`

**Permission Required:** `sasanarakshaka:update`

**Request Body (all fields optional):**
```json
{
  "sr_ssbname": "Updated Sasana Rakshaka Bala Mandalaya Name",
  "sr_sbmnayakahimi": "BH2025000002"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Sasanarakshaka Bala Mandalaya updated successfully.",
  "data": {
    "sr_id": 1,
    "sr_ssbmcode": "SB001",
    "sr_dvcd": "DV001",
    "sr_ssbname": "Updated Sasana Rakshaka Bala Mandalaya Name",
    "sr_sbmnayakahimi": "BH2025000002",
    "sr_version": "2026-01-15T11:00:00",
    "sr_is_deleted": false,
    "sr_created_at": "2026-01-15T10:30:00",
    "sr_updated_at": "2026-01-15T11:00:00",
    "sr_created_by": "admin",
    "sr_updated_by": "admin",
    "sr_version_number": 2
  }
}
```

---

### 6. Delete Sasanarakshaka Bala Mandalaya (Soft Delete)
**DELETE** `/api/v1/sasanarakshaka/{sr_id}`

**Permission Required:** `sasanarakshaka:delete`

**Example Request:**
```
DELETE /api/v1/sasanarakshaka/1
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Sasanarakshaka Bala Mandalaya deleted successfully.",
  "data": {
    "sr_id": 1
  }
}
```

---

## File Structure

```
app/
├── models/
│   └── sasanarakshaka.py          # SQLAlchemy model for cmm_sasanarbm table
├── schemas/
│   └── sasanarakshaka.py          # Pydantic schemas for request/response validation
├── repositories/
│   └── sasanarakshaka_repo.py     # Data access layer (database operations)
├── services/
│   └── sasanarakshaka_service.py  # Business logic and validation
└── api/
    └── v1/
        ├── router.py              # Main router registration (updated)
        └── routes/
            └── sasanarakshaka.py  # API endpoint definitions
```

---

## Permissions Required

The following permissions need to be created in the RBAC system:

- `sasanarakshaka:create` - Create new Sasanarakshaka Bala Mandalaya records
- `sasanarakshaka:read` - View Sasanarakshaka Bala Mandalaya records
- `sasanarakshaka:update` - Update existing Sasanarakshaka Bala Mandalaya records
- `sasanarakshaka:delete` - Delete Sasanarakshaka Bala Mandalaya records

---

## Validation Rules

1. **Unique Code Validation:**
   - `sr_ssbmcode` must be unique across all non-deleted records

2. **Foreign Key Validation:**
   - `sr_dvcd` must exist in `cmm_dvsec.dv_dvcode` and not be deleted
   - `sr_sbmnayakahimi` (if provided) must exist in `bhikku_regist.br_regn` and not be deleted

3. **Soft Delete:**
   - Records are not physically deleted; `sr_is_deleted` is set to `true`
   - Deleted records are excluded from all read operations

4. **Version Control:**
   - `sr_version_number` increments on each update for optimistic locking

---

## Features

✅ Complete CRUD operations (Create, Read, Update, Delete)
✅ Pagination support with configurable page size
✅ Full-text search across all text fields
✅ Filter by divisional secretariat code
✅ Foreign key validation (divisional secretariat and bhikku registration)
✅ Unique code validation
✅ Soft delete functionality
✅ Version control and optimistic locking
✅ Audit trail (created_by, updated_by, timestamps)
✅ Permission-based access control
✅ Consistent error handling
✅ Follows bhikku_regist architecture pattern

---

## Testing

To test the endpoints, ensure:

1. The server is running: `uvicorn app.main:app --reload --port 8000`
2. You have valid authentication credentials
3. Required permissions are assigned to your user account
4. Foreign key references (divisional secretariat and bhikku registration) exist in the database

---

## Notes

- All endpoints require authentication via JWT token
- Soft delete is used - records are never physically deleted from the database
- The implementation follows the same pattern as `bhikku_regist` for consistency
- All responses follow the standardized format with `status`, `message`, and `data` fields
