# Temporary Entities - Developer Quick Reference

## 📋 Quick Navigation

| Entity | Endpoint | ID | Key Fields | Docs |
|--------|----------|----|-----------|----|
| **Silmatha** | `POST /temporary-silmatha/manage` | `ts_id` | ts_name, ts_nic, ts_contact_number, ts_arama_name | [Full Spec](TEMPORARY_ENTITIES_ENDPOINT_SPECIFICATIONS.md#temporary-silmatha) |
| **Bhikku** | `POST /temporary-bhikku/manage` | `tb_id` | tb_name, tb_id_number, tb_contact_number, tb_living_temple | [Full Spec](TEMPORARY_ENTITIES_ENDPOINT_SPECIFICATIONS.md#temporary-bhikku) |
| **Devala** | `POST /temporary-devala/manage` | `td_id` | td_name, td_address, td_contact_number, td_basnayake_nilame_name | [Full Spec](TEMPORARY_ENTITIES_ENDPOINT_SPECIFICATIONS.md#temporary-devala) |
| **Arama** | `POST /temporary-arama/manage` | `ta_id` | ta_name, ta_address, ta_contact_number, ta_aramadhipathi_name | [Full Spec](TEMPORARY_ENTITIES_ENDPOINT_SPECIFICATIONS.md#temporary-arama) |

---

## 🎯 Common Actions (All Entities)

### 1️⃣ CREATE - Add New Record

```bash
curl -X POST "http://localhost:8000/api/v1/temporary-{entity}/manage" \
  -H "Content-Type: application/json" \
  -H "Cookie: session=..." \
  -d '{
    "action": "CREATE",
    "payload": {
      "data": {
        "{entity}_name": "...",
        "{entity}_contact_number": "0771234567"
        // ... other fields
      }
    }
  }'
```

**Response:** Record created with ID
```json
{ "status": "success", "data": { "{entity}_id": 1, ... } }
```

### 2️⃣ READ_ONE - Get Single Record

```bash
curl -X POST "http://localhost:8000/api/v1/temporary-{entity}/manage" \
  -H "Content-Type: application/json" \
  -H "Cookie: session=..." \
  -d '{
    "action": "READ_ONE",
    "payload": {
      "{entity}_id": 1
    }
  }'
```

### 3️⃣ READ_ALL - List Records

```bash
curl -X POST "http://localhost:8000/api/v1/temporary-{entity}/manage" \
  -H "Content-Type: application/json" \
  -H "Cookie: session=..." \
  -d '{
    "action": "READ_ALL",
    "payload": {
      "skip": 0,
      "limit": 10,
      "search": "optional_search_term"
    }
  }'
```

**Response:** Paginated list
```json
{
  "status": "success",
  "data": {
    "records": [...],
    "total": 100,
    "skip": 0,
    "limit": 10
  }
}
```

### 4️⃣ UPDATE - Modify Record

```bash
curl -X POST "http://localhost:8000/api/v1/temporary-{entity}/manage" \
  -H "Content-Type: application/json" \
  -H "Cookie: session=..." \
  -d '{
    "action": "UPDATE",
    "payload": {
      "{entity}_id": 1,
      "updates": {
        "{entity}_contact_number": "0772222222"
        // ... only fields to update
      }
    }
  }'
```

### 5️⃣ DELETE - Remove Record

```bash
curl -X POST "http://localhost:8000/api/v1/temporary-{entity}/manage" \
  -H "Content-Type: application/json" \
  -H "Cookie: session=..." \
  -d '{
    "action": "DELETE",
    "payload": {
      "{entity}_id": 1
    }
  }'
```

---

## 🔑 Key Field Patterns

### Silmatha (ts_*)
```python
ts_id                  # int     | auto-generated ID
ts_name                # str     | required, max 200
ts_nic                 # str     | optional, max 15
ts_contact_number      # str     | optional, max 15
ts_address             # str     | optional, max 500
ts_district            # str     | optional, max 100
ts_province            # str     | optional, max 100
ts_arama_name          # str     | optional, max 200
ts_ordained_date       # date    | optional (YYYY-MM-DD)
ts_created_at          # datetime| server-generated
ts_created_by          # str     | server-generated
```

### Bhikku (tb_*)
```python
tb_id                  # int     | auto-generated ID
tb_name                # str     | required, max 100
tb_id_number           # str     | optional, max 20
tb_contact_number      # str     | optional, max 15
tb_samanera_name       # str     | optional, max 100
tb_address             # str     | optional, max 500
tb_living_temple       # str     | optional, max 200
tb_created_at          # datetime| server-generated
tb_created_by          # str     | server-generated
```

### Devala (td_*)
```python
td_id                  # int     | auto-generated ID
td_name                # str     | required, max 200
td_address             # str     | optional, max 500
td_contact_number      # str     | optional, max 15
td_district            # str     | optional, max 100
td_province            # str     | optional, max 100
td_basnayake_nilame_name # str   | optional, max 200
td_created_at          # datetime| server-generated
td_created_by          # str     | server-generated
```

### Arama (ta_*)
```python
ta_id                  # int     | auto-generated ID
ta_name                # str     | required, max 200
ta_address             # str     | optional, max 500
ta_contact_number      # str     | optional, max 15
ta_district            # str     | optional, max 100
ta_province            # str     | optional, max 100
ta_aramadhipathi_name  # str     | optional, max 200
ta_created_at          # datetime| server-generated
ta_created_by          # str     | server-generated
```

---

## 🛡️ Permissions Required

All temporary entity endpoints require permissions:

| Action | Permission |
|--------|-----------|
| CREATE | `{entity}:create` |
| READ_ONE, READ_ALL | `{entity}:read` |
| UPDATE | `{entity}:update` |
| DELETE | `{entity}:delete` |

**Examples:**
- `silmatha:create`, `silmatha:read`, `silmatha:update`, `silmatha:delete`
- `bhikku:create`, `bhikku:read`, `bhikku:update`, `bhikku:delete`
- `devala:create`, `devala:read`, `devala:update`, `devala:delete`
- `arama:create`, `arama:read`, `arama:update`, `arama:delete`

---

## ❌ Common Errors & Solutions

### 1. Missing Required Field
```json
{
  "status": "error",
  "message": "Validation failed",
  "detail": [{"field": "ts_name", "error": "Field is required"}]
}
```
**Solution:** Include all required fields in CREATE/UPDATE requests

### 2. Invalid Field Length
```json
{
  "status": "error",
  "message": "Validation failed",
  "detail": [{"field": "ts_nic", "error": "Ensure this value has at most 15 characters"}]
}
```
**Solution:** Check field max lengths in [Field Reference](#-key-field-patterns)

### 3. Record Not Found
```json
{
  "status": "error",
  "message": "Record not found",
  "detail": "Temporary silmatha with ID 999 not found"
}
```
**Solution:** Verify ID exists before READ_ONE/UPDATE/DELETE

### 4. Permission Denied
```json
{
  "status": "error",
  "message": "Permission denied",
  "detail": "User does not have 'silmatha:create' permission"
}
```
**Solution:** Request appropriate permissions or use authorized user

### 5. Invalid Date Format
```json
{
  "status": "error",
  "message": "Validation failed",
  "detail": [{"field": "ts_ordained_date", "error": "Invalid date format"}]
}
```
**Solution:** Use ISO 8601 format: `YYYY-MM-DD` (e.g., `2025-01-27`)

---

## 📊 Code Examples

### Python (Requests)
```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"
session = requests.Session()
session.cookies.set('session', '{your_token}')

# CREATE
response = session.post(
    f"{BASE_URL}/temporary-silmatha/manage",
    json={
        "action": "CREATE",
        "payload": {
            "data": {
                "ts_name": "Ven. Ananda",
                "ts_contact_number": "0771234567",
                "ts_district": "CMB",
                "ts_province": "WP"
            }
        }
    }
)
print(response.json())

# READ_ALL with search
response = session.post(
    f"{BASE_URL}/temporary-silmatha/manage",
    json={
        "action": "READ_ALL",
        "payload": {
            "skip": 0,
            "limit": 10,
            "search": "Ananda"
        }
    }
)
records = response.json()["data"]["records"]
```

### JavaScript (Fetch)
```javascript
const BASE_URL = "http://localhost:8000/api/v1";

// CREATE
async function createSilmatha(data) {
  const response = await fetch(
    `${BASE_URL}/temporary-silmatha/manage`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      credentials: "include", // Include cookies
      body: JSON.stringify({
        action: "CREATE",
        payload: { data }
      })
    }
  );
  return response.json();
}

// Usage
const result = await createSilmatha({
  ts_name: "Ven. Ananda",
  ts_contact_number: "0771234567",
  ts_district: "CMB",
  ts_province: "WP"
});
```

### TypeScript Interface
```typescript
interface TemporarySilmatha {
  ts_id?: number;
  ts_name: string;
  ts_nic?: string;
  ts_contact_number?: string;
  ts_address?: string;
  ts_district?: string;
  ts_province?: string;
  ts_arama_name?: string;
  ts_ordained_date?: string; // YYYY-MM-DD
  ts_created_at?: string;
  ts_created_by?: string;
  ts_updated_at?: string | null;
  ts_updated_by?: string | null;
}

interface ApiResponse<T> {
  status: "success" | "error";
  message: string;
  data?: T | T[] | { records: T[]; total: number; skip: number; limit: number };
}
```

---

## 🧪 Testing Checklist

- [ ] CREATE with required fields only
- [ ] CREATE with all optional fields
- [ ] CREATE with invalid field lengths (should fail)
- [ ] READ_ONE with valid ID
- [ ] READ_ONE with invalid ID (should fail)
- [ ] READ_ALL with no filters
- [ ] READ_ALL with search term
- [ ] READ_ALL with pagination (skip/limit)
- [ ] UPDATE single field
- [ ] UPDATE multiple fields
- [ ] UPDATE non-existent record (should fail)
- [ ] DELETE existing record
- [ ] DELETE non-existent record (should fail)
- [ ] Test without authentication (should fail)
- [ ] Test with insufficient permissions (should fail)

---

## 📚 Related Documentation

- **Full Specifications:** [TEMPORARY_ENTITIES_ENDPOINT_SPECIFICATIONS.md](TEMPORARY_ENTITIES_ENDPOINT_SPECIFICATIONS.md)
- **Pagination Reference:** See "Common Patterns" in full spec
- **Response Structure:** [RESPONSE_STRUCTURE_FIX_IMPLEMENTATION.md](RESPONSE_STRUCTURE_FIX_IMPLEMENTATION.md)

---

## 🚀 Implementation Path

1. **Read this guide** to understand the patterns
2. **Review full specifications** for detailed field info
3. **Check code examples** for your language
4. **Run tests** from the checklist
5. **Refer to error section** for troubleshooting

---

## Summary Table

| Aspect | Details |
|--------|---------|
| **Common Endpoint Pattern** | `POST /api/v1/temporary-{entity}/manage` |
| **Common Actions** | CREATE, READ_ONE, READ_ALL, UPDATE, DELETE |
| **Pagination** | skip (offset), limit (1-200), search (optional) |
| **Timestamps** | ISO 8601 format (YYYY-MM-DDTHH:MM:SS) |
| **IDs** | Integer, auto-generated on create |
| **Max String Length** | 500 chars (addresses), 200 (names), 100 (nikaya) |
| **Authentication** | Cookie-based session token |
| **Permissions** | `{entity}:create|read|update|delete` |
| **Response Format** | JSON with status, message, data |

---

For complete endpoint specifications with examples, see [TEMPORARY_ENTITIES_ENDPOINT_SPECIFICATIONS.md](TEMPORARY_ENTITIES_ENDPOINT_SPECIFICATIONS.md)
