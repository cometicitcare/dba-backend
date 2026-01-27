# Temporary Entities - Complete Endpoint Specifications

## Table of Contents
1. [Temporary Silmatha](#temporary-silmatha)
2. [Temporary Bhikku](#temporary-bhikku)
3. [Temporary Devala](#temporary-devala)
4. [Temporary Arama](#temporary-arama)
5. [Field Reference](#field-reference-guide)
6. [Common Patterns](#common-patterns)

---

## Temporary Silmatha

### Endpoint
```
POST /api/v1/temporary-silmatha/manage
```

### Authorization
Required Permissions:
- `silmatha:create` (CREATE)
- `silmatha:read` (READ_ONE, READ_ALL)
- `silmatha:update` (UPDATE)
- `silmatha:delete` (DELETE)

### Field Reference

| Field | Type | Max Length | Required | Description |
|-------|------|-----------|----------|-------------|
| `ts_id` | `int` | - | ✅ (READ_ONE, UPDATE, DELETE only) | Unique silmatha identifier |
| `ts_name` | `string` | 200 | ✅ | Silmatha/Nun name |
| `ts_nic` | `string` | 15 | ❌ | National Identity Card number |
| `ts_contact_number` | `string` | 15 | ❌ | Mobile/contact number |
| `ts_address` | `string` | 500 | ❌ | Residential address |
| `ts_district` | `string` | 100 | ❌ | District code (e.g., "CMB") |
| `ts_province` | `string` | 100 | ❌ | Province code (e.g., "WP") |
| `ts_arama_name` | `string` | 200 | ❌ | Associated arama/hermitage name |
| `ts_ordained_date` | `date` | - | ❌ | Date of monastic ordination (YYYY-MM-DD) |
| `ts_created_at` | `datetime` | - | 🔒 (Response only) | Record creation timestamp |
| `ts_created_by` | `string` | - | 🔒 (Response only) | User who created record |
| `ts_updated_at` | `datetime` | - | 🔒 (Response only) | Last update timestamp |
| `ts_updated_by` | `string` | - | 🔒 (Response only) | User who last updated record |

### Actions

#### CREATE
Creates a new temporary silmatha record.

**Request:**
```json
{
  "action": "CREATE",
  "payload": {
    "data": {
      "ts_name": "Venerable Bhikkhuni",
      "ts_nic": "123456789V",
      "ts_contact_number": "0771234567",
      "ts_address": "Temple Road, Colombo",
      "ts_district": "CMB",
      "ts_province": "WP",
      "ts_arama_name": "Kelaniya Arama",
      "ts_ordained_date": "2020-01-15"
    }
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Temporary silmatha record created successfully.",
  "data": {
    "ts_id": 1,
    "ts_name": "Venerable Bhikkhuni",
    "ts_nic": "123456789V",
    "ts_contact_number": "0771234567",
    "ts_address": "Temple Road, Colombo",
    "ts_district": "CMB",
    "ts_province": "WP",
    "ts_arama_name": "Kelaniya Arama",
    "ts_ordained_date": "2020-01-15",
    "ts_created_at": "2025-01-27T10:30:00",
    "ts_created_by": "user_123",
    "ts_updated_at": null,
    "ts_updated_by": null
  }
}
```

#### READ_ONE
Retrieves a single temporary silmatha record by ID.

**Request:**
```json
{
  "action": "READ_ONE",
  "payload": {
    "ts_id": 1
  }
}
```

**Response:** Same as CREATE response

#### READ_ALL
Retrieves all temporary silmatha records with pagination and search.

**Request:**
```json
{
  "action": "READ_ALL",
  "payload": {
    "skip": 0,
    "limit": 10,
    "search": "Venerable"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Retrieved 5 temporary silmatha records.",
  "data": {
    "records": [
      {
        "ts_id": 1,
        "ts_name": "Venerable Bhikkhuni",
        "ts_nic": "123456789V",
        "ts_contact_number": "0771234567",
        "ts_address": "Temple Road, Colombo",
        "ts_district": "CMB",
        "ts_province": "WP",
        "ts_arama_name": "Kelaniya Arama",
        "ts_ordained_date": "2020-01-15",
        "ts_created_at": "2025-01-27T10:30:00",
        "ts_created_by": "user_123"
      }
    ],
    "total": 5,
    "skip": 0,
    "limit": 10
  }
}
```

#### UPDATE
Updates an existing temporary silmatha record.

**Request:**
```json
{
  "action": "UPDATE",
  "payload": {
    "ts_id": 1,
    "updates": {
      "ts_contact_number": "0772222222",
      "ts_address": "New Temple Road, Colombo"
    }
  }
}
```

**Response:** Same as CREATE response

#### DELETE
Deletes a temporary silmatha record.

**Request:**
```json
{
  "action": "DELETE",
  "payload": {
    "ts_id": 1
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Temporary silmatha record deleted successfully.",
  "data": null
}
```

---

## Temporary Bhikku

### Endpoint
```
POST /api/v1/temporary-bhikku/manage
```

### Authorization
Required Permissions:
- `bhikku:create` (CREATE)
- `bhikku:read` (READ_ONE, READ_ALL)
- `bhikku:update` (UPDATE)
- `bhikku:delete` (DELETE)

### Field Reference

| Field | Type | Max Length | Required | Description |
|-------|------|-----------|----------|-------------|
| `tb_id` | `int` | - | ✅ (READ_ONE, UPDATE, DELETE only) | Unique bhikku identifier |
| `tb_name` | `string` | 100 | ✅ | Bhikku/Monk name |
| `tb_id_number` | `string` | 20 | ❌ | National ID or identification number |
| `tb_contact_number` | `string` | 15 | ❌ | Mobile/contact number |
| `tb_samanera_name` | `string` | 100 | ❌ | Samanera (novice) name before ordination |
| `tb_address` | `string` | 500 | ❌ | Residential address |
| `tb_living_temple` | `string` | 200 | ❌ | Current living temple/vihara |
| `tb_created_at` | `datetime` | - | 🔒 (Response only) | Record creation timestamp |
| `tb_created_by` | `string` | - | 🔒 (Response only) | User who created record |
| `tb_updated_at` | `datetime` | - | 🔒 (Response only) | Last update timestamp |
| `tb_updated_by` | `string` | - | 🔒 (Response only) | User who last updated record |

### Actions

#### CREATE
Creates a new temporary bhikku record.

**Request:**
```json
{
  "action": "CREATE",
  "payload": {
    "data": {
      "tb_name": "Ven. Sumangala",
      "tb_id_number": "198765432V",
      "tb_contact_number": "0779876543",
      "tb_samanera_name": "Amal",
      "tb_address": "Samanera Quarters, Colombo",
      "tb_living_temple": "Kelaniya Rajamaha Vihara"
    }
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Temporary bhikku record created successfully.",
  "data": {
    "tb_id": 1,
    "tb_name": "Ven. Sumangala",
    "tb_id_number": "198765432V",
    "tb_contact_number": "0779876543",
    "tb_samanera_name": "Amal",
    "tb_address": "Samanera Quarters, Colombo",
    "tb_living_temple": "Kelaniya Rajamaha Vihara",
    "tb_created_at": "2025-01-27T11:00:00",
    "tb_created_by": "user_456",
    "tb_updated_at": null,
    "tb_updated_by": null
  }
}
```

#### READ_ONE
Retrieves a single temporary bhikku record by ID.

**Request:**
```json
{
  "action": "READ_ONE",
  "payload": {
    "tb_id": 1
  }
}
```

**Response:** Same as CREATE response

#### READ_ALL
Retrieves all temporary bhikku records with pagination and search.

**Request:**
```json
{
  "action": "READ_ALL",
  "payload": {
    "skip": 0,
    "limit": 20,
    "search": "Sumangala"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Retrieved 3 temporary bhikku records.",
  "data": {
    "records": [
      {
        "tb_id": 1,
        "tb_name": "Ven. Sumangala",
        "tb_id_number": "198765432V",
        "tb_contact_number": "0779876543",
        "tb_samanera_name": "Amal",
        "tb_address": "Samanera Quarters, Colombo",
        "tb_living_temple": "Kelaniya Rajamaha Vihara",
        "tb_created_at": "2025-01-27T11:00:00",
        "tb_created_by": "user_456"
      }
    ],
    "total": 3,
    "skip": 0,
    "limit": 20
  }
}
```

#### UPDATE
Updates an existing temporary bhikku record.

**Request:**
```json
{
  "action": "UPDATE",
  "payload": {
    "tb_id": 1,
    "updates": {
      "tb_contact_number": "0771111111",
      "tb_living_temple": "Colombo Raja Maha Vihara"
    }
  }
}
```

**Response:** Same as CREATE response

#### DELETE
Deletes a temporary bhikku record.

**Request:**
```json
{
  "action": "DELETE",
  "payload": {
    "tb_id": 1
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Temporary bhikku record deleted successfully.",
  "data": null
}
```

---

## Temporary Devala

### Endpoint
```
POST /api/v1/temporary-devala/manage
```

### Authorization
Required Permissions:
- `devala:create` (CREATE)
- `devala:read` (READ_ONE, READ_ALL)
- `devala:update` (UPDATE)
- `devala:delete` (DELETE)

### Field Reference

| Field | Type | Max Length | Required | Description |
|-------|------|-----------|----------|-------------|
| `td_id` | `int` | - | ✅ (READ_ONE, UPDATE, DELETE only) | Unique devala identifier |
| `td_name` | `string` | 200 | ✅ | Devala/Shrine name |
| `td_address` | `string` | 500 | ❌ | Devala address |
| `td_contact_number` | `string` | 15 | ❌ | Mobile/contact number |
| `td_district` | `string` | 100 | ❌ | District code (e.g., "CMB") |
| `td_province` | `string` | 100 | ❌ | Province code (e.g., "WP") |
| `td_basnayake_nilame_name` | `string` | 200 | ❌ | Basnayake Nilame (Chief custodian) name |
| `td_created_at` | `datetime` | - | 🔒 (Response only) | Record creation timestamp |
| `td_created_by` | `string` | - | 🔒 (Response only) | User who created record |
| `td_updated_at` | `datetime` | - | 🔒 (Response only) | Last update timestamp |
| `td_updated_by` | `string` | - | 🔒 (Response only) | User who last updated record |

### Actions

#### CREATE
Creates a new temporary devala record.

**Request:**
```json
{
  "action": "CREATE",
  "payload": {
    "data": {
      "td_name": "Colombo Central Devala",
      "td_address": "Main Street, Colombo",
      "td_contact_number": "0112223333",
      "td_district": "CMB",
      "td_province": "WP",
      "td_basnayake_nilame_name": "Mr. K.D. Silva"
    }
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Temporary devala record created successfully.",
  "data": {
    "td_id": 1,
    "td_name": "Colombo Central Devala",
    "td_address": "Main Street, Colombo",
    "td_contact_number": "0112223333",
    "td_district": "CMB",
    "td_province": "WP",
    "td_basnayake_nilame_name": "Mr. K.D. Silva",
    "td_created_at": "2025-01-27T14:15:00",
    "td_created_by": "user_789",
    "td_updated_at": null,
    "td_updated_by": null
  }
}
```

#### READ_ONE
Retrieves a single temporary devala record by ID.

**Request:**
```json
{
  "action": "READ_ONE",
  "payload": {
    "td_id": 1
  }
}
```

**Response:** Same as CREATE response

#### READ_ALL
Retrieves all temporary devala records with pagination and search.

**Request:**
```json
{
  "action": "READ_ALL",
  "payload": {
    "skip": 0,
    "limit": 15,
    "search": "Colombo"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Retrieved 2 temporary devala records.",
  "data": {
    "records": [
      {
        "td_id": 1,
        "td_name": "Colombo Central Devala",
        "td_address": "Main Street, Colombo",
        "td_contact_number": "0112223333",
        "td_district": "CMB",
        "td_province": "WP",
        "td_basnayake_nilame_name": "Mr. K.D. Silva",
        "td_created_at": "2025-01-27T14:15:00",
        "td_created_by": "user_789"
      }
    ],
    "total": 2,
    "skip": 0,
    "limit": 15
  }
}
```

#### UPDATE
Updates an existing temporary devala record.

**Request:**
```json
{
  "action": "UPDATE",
  "payload": {
    "td_id": 1,
    "updates": {
      "td_contact_number": "0112224444",
      "td_basnayake_nilame_name": "Mr. A.B. Fernando"
    }
  }
}
```

**Response:** Same as CREATE response

#### DELETE
Deletes a temporary devala record.

**Request:**
```json
{
  "action": "DELETE",
  "payload": {
    "td_id": 1
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Temporary devala record deleted successfully.",
  "data": null
}
```

---

## Temporary Arama

### Endpoint
```
POST /api/v1/temporary-arama/manage
```

### Authorization
Required Permissions:
- `arama:create` (CREATE)
- `arama:read` (READ_ONE, READ_ALL)
- `arama:update` (UPDATE)
- `arama:delete` (DELETE)

### Field Reference

| Field | Type | Max Length | Required | Description |
|-------|------|-----------|----------|-------------|
| `ta_id` | `int` | - | ✅ (READ_ONE, UPDATE, DELETE only) | Unique arama identifier |
| `ta_name` | `string` | 200 | ✅ | Arama/Hermitage name |
| `ta_address` | `string` | 500 | ❌ | Arama address |
| `ta_contact_number` | `string` | 15 | ❌ | Mobile/contact number |
| `ta_district` | `string` | 100 | ❌ | District code (e.g., "CMB") |
| `ta_province` | `string` | 100 | ❌ | Province code (e.g., "WP") |
| `ta_aramadhipathi_name` | `string` | 200 | ❌ | Aramadhipathi (Chief incumbent) name |
| `ta_created_at` | `datetime` | - | 🔒 (Response only) | Record creation timestamp |
| `ta_created_by` | `string` | - | 🔒 (Response only) | User who created record |
| `ta_updated_at` | `datetime` | - | 🔒 (Response only) | Last update timestamp |
| `ta_updated_by` | `string` | - | 🔒 (Response only) | User who last updated record |

### Actions

#### CREATE
Creates a new temporary arama record.

**Request:**
```json
{
  "action": "CREATE",
  "payload": {
    "data": {
      "ta_name": "Ananda Arama",
      "ta_address": "Forest Lane, Kandy",
      "ta_contact_number": "0812222222",
      "ta_district": "KDY",
      "ta_province": "CP",
      "ta_aramadhipathi_name": "Ven. Ananda"
    }
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Temporary arama record created successfully.",
  "data": {
    "ta_id": 1,
    "ta_name": "Ananda Arama",
    "ta_address": "Forest Lane, Kandy",
    "ta_contact_number": "0812222222",
    "ta_district": "KDY",
    "ta_province": "CP",
    "ta_aramadhipathi_name": "Ven. Ananda",
    "ta_created_at": "2025-01-27T15:45:00",
    "ta_created_by": "user_101",
    "ta_updated_at": null,
    "ta_updated_by": null
  }
}
```

#### READ_ONE
Retrieves a single temporary arama record by ID.

**Request:**
```json
{
  "action": "READ_ONE",
  "payload": {
    "ta_id": 1
  }
}
```

**Response:** Same as CREATE response

#### READ_ALL
Retrieves all temporary arama records with pagination and search.

**Request:**
```json
{
  "action": "READ_ALL",
  "payload": {
    "skip": 0,
    "limit": 25,
    "search": "Arama"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Retrieved 4 temporary arama records.",
  "data": {
    "records": [
      {
        "ta_id": 1,
        "ta_name": "Ananda Arama",
        "ta_address": "Forest Lane, Kandy",
        "ta_contact_number": "0812222222",
        "ta_district": "KDY",
        "ta_province": "CP",
        "ta_aramadhipathi_name": "Ven. Ananda",
        "ta_created_at": "2025-01-27T15:45:00",
        "ta_created_by": "user_101"
      }
    ],
    "total": 4,
    "skip": 0,
    "limit": 25
  }
}
```

#### UPDATE
Updates an existing temporary arama record.

**Request:**
```json
{
  "action": "UPDATE",
  "payload": {
    "ta_id": 1,
    "updates": {
      "ta_contact_number": "0812333333",
      "ta_aramadhipathi_name": "Ven. Sudeva"
    }
  }
}
```

**Response:** Same as CREATE response

#### DELETE
Deletes a temporary arama record.

**Request:**
```json
{
  "action": "DELETE",
  "payload": {
    "ta_id": 1
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Temporary arama record deleted successfully.",
  "data": null
}
```

---

## Field Reference Guide

### Common Field Patterns

#### ID Fields
- **Format:** `{entity}_{type}_id` or `{entity}_id`
- **Examples:** `ts_id`, `tb_id`, `td_id`, `ta_id`
- **Type:** `int` (auto-generated on creation)
- **Required:** Only in READ_ONE, UPDATE, DELETE actions

#### Timestamp Fields
- **Format:** `{entity}_created_at`, `{entity}_updated_at`
- **Type:** `datetime` (ISO 8601 format)
- **Generated:** Server-side, read-only
- **Example:** `"2025-01-27T10:30:00"`

#### Audit Fields
- **Format:** `{entity}_created_by`, `{entity}_updated_by`
- **Type:** `string` (user ID)
- **Generated:** Server-side, read-only
- **Value:** User ID of person who created/updated record

#### String Fields with Max Lengths
- Names (e.g., `ts_name`): 100-200 characters
- Addresses: 500 characters maximum
- Contact numbers: 15 characters maximum (international format: +94...)
- NIC/ID numbers: 15-20 characters

#### Location Fields
- **District codes:** E.g., "CMB" (Colombo), "KDY" (Kandy)
- **Province codes:** E.g., "WP" (Western), "CP" (Central)
- Support both codes and names

---

## Common Patterns

### Pagination

All READ_ALL actions support pagination:

**Request Parameters:**
```json
{
  "skip": 0,        // Records to skip (0-based)
  "limit": 10,      // Max records to return (1-200)
  "search": "term"  // Optional search filter
}
```

**Response Metadata:**
```json
{
  "records": [...],
  "total": 100,     // Total matching records
  "skip": 0,
  "limit": 10
}
```

### Search Behavior

Search filters apply across multiple fields:

| Entity | Search Fields |
|--------|---------------|
| **Silmatha** | name, NIC, address, contact, arama_name |
| **Bhikku** | name, ID number, address, contact, living_temple |
| **Devala** | name, address, contact, basnayake_nilame_name |
| **Arama** | name, address, contact, aramadhipathi_name |

### Error Responses

**Validation Error:**
```json
{
  "status": "error",
  "message": "Validation failed",
  "detail": [
    {
      "field": "ts_name",
      "error": "Field is required"
    }
  ]
}
```

**Not Found Error:**
```json
{
  "status": "error",
  "message": "Record not found",
  "detail": "Temporary silmatha with ID 999 not found"
}
```

**Permission Error:**
```json
{
  "status": "error",
  "message": "Permission denied",
  "detail": "User does not have 'silmatha:create' permission"
}
```

### Date Format

All dates use ISO 8601 format:
- **Date only:** `YYYY-MM-DD` (e.g., `2025-01-27`)
- **DateTime:** `YYYY-MM-DDTHH:MM:SS` (e.g., `2025-01-27T10:30:00`)
- **With timezone:** `YYYY-MM-DDTHH:MM:SS±HH:MM`

### Request Headers

All requests should include:
```
Content-Type: application/json
Cookie: session={session_token}
```

### Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Action completed |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | Missing authentication |
| 403 | Forbidden | Permission denied |
| 404 | Not Found | Record doesn't exist |
| 500 | Server Error | Internal error |

---

## Implementation Guide

### How to Use These Specifications

1. **For API Consumers:** Use the endpoint, field reference, and action examples
2. **For Backend Developers:** Implement validators, permissions, and business logic based on field constraints
3. **For Frontend Developers:** Build forms and request generators using field specs
4. **For QA/Testing:** Create test cases for each action and field combination

### Testing Checklist

- ✅ CREATE: Test with all required fields, then with optional fields
- ✅ READ_ONE: Test with valid/invalid IDs
- ✅ READ_ALL: Test pagination (skip/limit), search filtering
- ✅ UPDATE: Test partial updates, field validation
- ✅ DELETE: Test deletion of existing/non-existing records
- ✅ Permissions: Test with/without required permissions
- ✅ Input validation: Test max lengths, required fields
- ✅ Error handling: Test all error scenarios

### Code Examples

#### Using cURL

```bash
# CREATE
curl -X POST "http://localhost:8000/api/v1/temporary-silmatha/manage" \
  -H "Content-Type: application/json" \
  -H "Cookie: session={token}" \
  -d '{
    "action": "CREATE",
    "payload": {
      "data": {
        "ts_name": "Ven. Test",
        "ts_contact_number": "0771234567"
      }
    }
  }'

# READ_ALL
curl -X POST "http://localhost:8000/api/v1/temporary-silmatha/manage" \
  -H "Content-Type: application/json" \
  -H "Cookie: session={token}" \
  -d '{
    "action": "READ_ALL",
    "payload": {
      "skip": 0,
      "limit": 10
    }
  }'
```

#### Using Python Requests

```python
import requests

session = requests.Session()
session.cookies.set('session', '{token}')

# CREATE
response = session.post(
    'http://localhost:8000/api/v1/temporary-silmatha/manage',
    json={
        'action': 'CREATE',
        'payload': {
            'data': {
                'ts_name': 'Ven. Test',
                'ts_contact_number': '0771234567'
            }
        }
    }
)
```

---

## Summary

| Entity | Endpoint | ID Field | Key Fields |
|--------|----------|----------|-----------|
| **Silmatha** | `/temporary-silmatha/manage` | `ts_id` | name, NIC, contact, arama_name, ordained_date |
| **Bhikku** | `/temporary-bhikku/manage` | `tb_id` | name, id_number, contact, living_temple |
| **Devala** | `/temporary-devala/manage` | `td_id` | name, address, contact, basnayake_nilame_name |
| **Arama** | `/temporary-arama/manage` | `ta_id` | name, address, contact, aramadhipathi_name |

All entities support the same 5 CRUD actions (CREATE, READ_ONE, READ_ALL, UPDATE, DELETE) with consistent patterns and error handling.
