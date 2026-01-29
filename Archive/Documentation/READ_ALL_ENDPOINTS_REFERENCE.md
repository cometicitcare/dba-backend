# READ_ALL Endpoints Reference

This document lists all endpoints with `"action": "READ_ALL"` and their request/response payloads.

---

## 1. Vihara Management

**Endpoint:** `POST /api/v1/viharas/manage`

### Request Payload
```json
{
  "action": "READ_ALL",
  "payload": {
    "page": 1,
    "limit": 100,
    "skip": 0,
    "search_key": "search text",
    "vh_trn": "optional filter",
    "province": "optional province code",
    "district": "optional district code",
    "divisional_secretariat": "optional div sec code",
    "gn_division": "optional GN division",
    "temple": "optional temple name",
    "child_temple": "optional child temple",
    "nikaya": "optional nikaya",
    "parshawaya": "optional parshawaya",
    "category": "optional category",
    "status": "optional status code",
    "vh_typ": "optional vihara type",
    "date_from": "2025-01-01",
    "date_to": "2025-12-31"
  }
}
```

### Response Payload
```json
{
  "status": "success",
  "message": "Viharas retrieved successfully.",
  "data": [
    {
      "vh_id": 1,
      "vh_trn": "TRN001",
      "vh_name": "Main Vihara",
      "vh_address": "Address here",
      "vh_phone": "0712345678",
      "vh_email": "vihara@example.com",
      "vh_province": "Province code",
      "vh_district": "District code",
      "vh_divisional_secretariat": "DS code",
      "vh_gn_division": "GN div code",
      "vh_temple": "Temple ID",
      "vh_child_temple": "Child Temple ID",
      "vh_nikaya": "Nikaya code",
      "vh_parshawaya": "Parshawaya code",
      "vh_category": "Category code",
      "vh_status": "COMPLETED",
      "vh_typ": "PERMANENT",
      "vh_created_at": "2025-01-01T10:00:00",
      "vh_created_by": "user_id",
      "vh_updated_at": "2025-01-27T15:30:00",
      "vh_updated_by": "user_id"
    }
  ],
  "totalRecords": 150,
  "page": 1,
  "limit": 100
}
```

**Filters Available:**
- `search_key`: Search by vihara name, address, or contact
- `vh_trn`: Filter by TRN
- `province`: Province code filter
- `district`: District code filter
- `divisional_secretariat`: Divisional secretariat filter
- `gn_division`: GN division filter
- `temple`: Temple filter
- `child_temple`: Child temple filter
- `nikaya`: Nikaya filter
- `parshawaya`: Parshawaya filter
- `category`: Category code filter
- `status`: Status filter
- `vh_typ`: Vihara type filter
- `date_from`/`date_to`: Date range filter

---

## 2. Temporary Vihara

**Endpoint:** `POST /api/v1/temporary-vihara/manage`

### Request Payload
```json
{
  "action": "READ_ALL",
  "payload": {
    "skip": 0,
    "limit": 100,
    "search": "search text"
  }
}
```

### Response Payload
```json
{
  "status": "success",
  "message": "Retrieved 25 temporary vihara records.",
  "data": {
    "records": [
      {
        "tv_id": 1,
        "tv_name": "Temporary Vihara Name",
        "tv_address": "Address here",
        "tv_contact_number": "0712345678",
        "tv_district": "District",
        "tv_province": "Province",
        "tv_viharadhipathi_name": "Viharadhipathi Name",
        "tv_created_at": "2025-01-01T10:00:00",
        "tv_created_by": "user_id",
        "tv_updated_at": "2025-01-27T15:30:00",
        "tv_updated_by": "user_id"
      }
    ],
    "total": 25,
    "skip": 0,
    "limit": 100
  }
}
```

**Filters Available:**
- `search`: Search by name, address, or contact number

---

## 3. Silmatha Registration

**Endpoint:** `POST /api/v1/silmatha/manage`

### Request Payload
```json
{
  "action": "READ_ALL",
  "payload": {
    "skip": 0,
    "limit": 10,
    "page": 1,
    "search_key": "search text",
    "vh_trn": "optional robing tutor residence TRN",
    "province": "optional province code",
    "district": "optional district code",
    "divisional_secretariat": "optional DS code",
    "gn_division": "optional GN division",
    "temple": "optional robing after residence temple",
    "child_temple": "optional mahana temple",
    "parshawaya": "optional parshawaya",
    "category": "optional category code",
    "status": "optional status code",
    "workflow_status": "optional workflow status",
    "date_from": "2025-01-01",
    "date_to": "2025-12-31"
  }
}
```

### Response Payload
```json
{
  "status": "success",
  "message": "Retrieved X silmatha records.",
  "data": [
    {
      "sil_id": 1,
      "sil_regn": "SIL001",
      "sil_name": "Silmatha Name",
      "sil_gihiname": "Gihi Name",
      "sil_dofb": "2000-01-01",
      "sil_fathrname": "Father Name",
      "sil_email": "email@example.com",
      "sil_mobile": "0712345678",
      "sil_province": "WESTERN",
      "sil_district": "COLOMBO",
      "sil_division": "Division Name",
      "sil_gndiv": "GN Division",
      "sil_currstat": "ACTIVE",
      "sil_cat": "Category Code",
      "sil_viharadhipathi": "Viharadhipathi Name",
      "sil_aramadhipathi": "Aramadhipathi Name",
      "sil_robing_tutor_residence": "Arama TRN",
      "sil_mahanatemple": "Temple TRN",
      "sil_robing_after_residence_temple": "Temple TRN",
      "sil_workflow_status": "PENDING",
      "sil_approval_status": "APPROVED",
      "sil_version_number": 1,
      "sil_created_by_district": "District Code"
    }
  ],
  "totalRecords": 150,
  "page": 1,
  "limit": 10
}
```

**Filters Available:**
- `search_key`: Search across name, registration number
- `vh_trn`: Robing tutor residence TRN filter
- `province`: Province code filter
- `district`: District code filter
- `divisional_secretariat`: DS filter
- `gn_division`: GN division filter
- `temple`: Robing after residence temple filter
- `child_temple`: Mahana temple filter
- `category`: Category code filter
- `status`: Status code filter
- `workflow_status`: Workflow status filter
- `date_from`/`date_to`: Date range filter

---

## 4. Objections

**Endpoint:** `POST /api/v1/objections/manage`

### Request Payload
```json
{
  "action": "READ_ALL",
  "payload": {
    "page": 1,
    "limit": 10,
    "vh_trn": "optional vihara TRN",
    "ar_trn": "optional arama TRN",
    "dv_trn": "optional devala TRN",
    "bh_regn": "optional bhikku registration",
    "sil_regn": "optional silmatha registration",
    "dbh_regn": "optional high bhikku registration",
    "obj_status": "optional objection status",
    "search": "search across TRN/REGN, reason, requester name, form ID"
  }
}
```

### Response Payload
```json
{
  "status": "success",
  "message": "Retrieved X objections.",
  "data": [
    {
      "obj_id": 1,
      "vh_trn": "TRN001",
      "ar_trn": null,
      "dv_trn": null,
      "bh_regn": null,
      "sil_regn": null,
      "dbh_regn": null,
      "ot_code": "RESIDENCY_RESTRICTION",
      "obj_reason": "Objection reason text",
      "form_id": "FORM001",
      "obj_requester_name": "Requester Name",
      "obj_requester_contact": "0712345678",
      "obj_requester_id_num": "NIC123456789",
      "obj_valid_from": "2025-01-01T00:00:00",
      "obj_valid_until": null,
      "obj_status": "PENDING",
      "obj_submitted_by": "user_id",
      "obj_submitted_at": "2025-01-01T10:00:00",
      "obj_approved_by": null,
      "obj_approved_at": null,
      "obj_rejected_by": null,
      "obj_rejected_at": null,
      "obj_rejection_reason": null,
      "obj_cancelled_by": null,
      "obj_cancelled_at": null,
      "obj_cancellation_reason": null,
      "obj_is_deleted": false,
      "obj_created_at": "2025-01-01T10:00:00",
      "obj_updated_at": "2025-01-27T15:30:00",
      "obj_updated_by": "user_id"
    }
  ],
  "totalRecords": 50,
  "page": 1,
  "limit": 10
}
```

**Filters Available:**
- `vh_trn`: Filter by vihara TRN
- `ar_trn`: Filter by arama TRN
- `dv_trn`: Filter by devala TRN
- `bh_regn`: Filter by bhikku registration
- `sil_regn`: Filter by silmatha registration
- `dbh_regn`: Filter by high bhikku registration
- `obj_status`: Filter by objection status (PENDING, APPROVED, REJECTED, CANCELLED)
- `search`: Global search across multiple fields

---

## 5. District

**Endpoint:** `POST /api/v1/districts/manage`

### Request Payload
```json
{
  "action": "READ_ALL",
  "payload": {
    "page": 1,
    "limit": 100,
    "skip": 0,
    "search_key": "search text",
    "dd_prcode": "optional province code"
  }
}
```

### Response Payload
```json
{
  "status": "success",
  "message": "Districts retrieved successfully.",
  "data": [
    {
      "dd_id": 1,
      "dd_dcode": "COLOMBO",
      "dd_dname": "Colombo",
      "dd_prcode": "WESTERN",
      "dd_created_by": "user_id",
      "dd_updated_by": "user_id"
    }
  ],
  "totalRecords": 25,
  "page": 1,
  "limit": 100
}
```

**Filters Available:**
- `search_key`: Search by district name or code
- `dd_prcode`: Filter by province code

---

## 6. Status (Status Codes)

**Endpoint:** `POST /api/v1/status/manage`

### Request Payload
```json
{
  "action": "READ_ALL",
  "payload": {
    "page": 1,
    "limit": 100,
    "skip": 0,
    "search_key": "search text"
  }
}
```

### Response Payload
```json
{
  "status": "success",
  "message": "Status records retrieved successfully.",
  "data": [
    {
      "st_id": 1,
      "st_statcd": "ACTIVE",
      "st_statdesc": "Active Status",
      "st_created_by": "user_id",
      "st_updated_by": "user_id"
    }
  ],
  "totalRecords": 15,
  "page": 1,
  "limit": 100
}
```

**Filters Available:**
- `search_key`: Search by status code or description

---

## 7. Roles

**Endpoint:** `POST /api/v1/roles/manage`

### Request Payload
```json
{
  "action": "READ_ALL",
  "payload": {
    "page": 1,
    "limit": 100,
    "skip": 0,
    "search_key": "search text",
    "include_deleted": false
  }
}
```

### Response Payload
```json
{
  "status": "success",
  "message": "Roles retrieved successfully.",
  "data": [
    {
      "ro_role_id": "ADMIN",
      "ro_role_name": "Administrator",
      "ro_description": "System Administrator Role",
      "ro_is_deleted": false,
      "ro_created_by": "user_id",
      "ro_updated_by": "user_id"
    }
  ],
  "totalRecords": 10,
  "page": 1,
  "limit": 100
}
```

**Filters Available:**
- `search_key`: Search by role ID or role name
- `include_deleted`: Include deleted roles in results (default: false)

---

## 8. Religion

**Endpoint:** `POST /api/v1/religion/manage`

### Request Payload
```json
{
  "action": "READ_ALL",
  "payload": {
    "page": 1,
    "limit": 100,
    "skip": 0,
    "search_key": "search text"
  }
}
```

### Response Payload
```json
{
  "status": "success",
  "message": "Religions retrieved successfully.",
  "data": [
    {
      "rel_id": 1,
      "rel_name": "Buddhism",
      "rel_code": "BUD"
    }
  ],
  "totalRecords": 10,
  "page": 1,
  "limit": 100
}
```

**Filters Available:**
- `search_key`: Search by religion name or code

---

## 9. Province

**Endpoint:** `POST /api/v1/provinces/manage`

### Request Payload
```json
{
  "action": "READ_ALL",
  "payload": {
    "page": 1,
    "limit": 100,
    "skip": 0,
    "search_key": "search text"
  }
}
```

### Response Payload
```json
{
  "status": "success",
  "message": "Provinces retrieved successfully.",
  "data": [
    {
      "pv_id": 1,
      "pv_prcode": "WESTERN",
      "pv_prname": "Western Province"
    }
  ],
  "totalRecords": 9,
  "page": 1,
  "limit": 100
}
```

**Filters Available:**
- `search_key`: Search by province code or name

---

## 10. Temporary Silmatha

**Endpoint:** `POST /api/v1/temporary-silmatha/manage`

### Request Payload
```json
{
  "action": "READ_ALL",
  "payload": {
    "skip": 0,
    "limit": 100,
    "search": "search text"
  }
}
```

### Response Payload
```json
{
  "status": "success",
  "message": "Retrieved X temporary silmatha records.",
  "data": {
    "records": [
      {
        "ts_id": 1,
        "ts_name": "Silmatha Name",
        "ts_address": "Address",
        "ts_contact_number": "0712345678",
        "ts_created_at": "2025-01-01T10:00:00"
      }
    ],
    "total": 25,
    "skip": 0,
    "limit": 100
  }
}
```

**Filters Available:**
- `search`: Search by name, address, or contact

---

## 11. Temporary Arama

**Endpoint:** `POST /api/v1/temporary-arama/manage`

### Request Payload
```json
{
  "action": "READ_ALL",
  "payload": {
    "skip": 0,
    "limit": 100,
    "search": "search text"
  }
}
```

### Response Payload
```json
{
  "status": "success",
  "message": "Retrieved X temporary arama records.",
  "data": {
    "records": [
      {
        "ta_id": 1,
        "ta_name": "Arama Name",
        "ta_address": "Address",
        "ta_contact_number": "0712345678",
        "ta_created_at": "2025-01-01T10:00:00"
      }
    ],
    "total": 25,
    "skip": 0,
    "limit": 100
  }
}
```

**Filters Available:**
- `search`: Search by name, address, or contact

---

## 12. Temporary Bhikku

**Endpoint:** `POST /api/v1/temporary-bhikku/manage`

### Request Payload
```json
{
  "action": "READ_ALL",
  "payload": {
    "skip": 0,
    "limit": 100,
    "search": "search text"
  }
}
```

### Response Payload
```json
{
  "status": "success",
  "message": "Retrieved X temporary bhikku records.",
  "data": {
    "records": [
      {
        "tb_id": 1,
        "tb_name": "Bhikku Name",
        "tb_address": "Address",
        "tb_contact_number": "0712345678",
        "tb_created_at": "2025-01-01T10:00:00"
      }
    ],
    "total": 25,
    "skip": 0,
    "limit": 100
  }
}
```

**Filters Available:**
- `search`: Search by name, address, or contact

---

## 13. Temporary Devala

**Endpoint:** `POST /api/v1/temporary-devala/manage`

### Request Payload
```json
{
  "action": "READ_ALL",
  "payload": {
    "skip": 0,
    "limit": 100,
    "search": "search text"
  }
}
```

### Response Payload
```json
{
  "status": "success",
  "message": "Retrieved X temporary devala records.",
  "data": {
    "records": [
      {
        "td_id": 1,
        "td_name": "Devala Name",
        "td_address": "Address",
        "td_contact_number": "0712345678",
        "td_created_at": "2025-01-01T10:00:00"
      }
    ],
    "total": 25,
    "skip": 0,
    "limit": 100
  }
}
```

**Filters Available:**
- `search`: Search by name, address, or contact

---

## 14. Divisional Secretariat

**Endpoint:** `POST /api/v1/divisional-secretariat/manage`

### Request Payload
```json
{
  "action": "READ_ALL",
  "payload": {
    "page": 1,
    "limit": 100,
    "skip": 0,
    "search_key": "search text",
    "dv_dcode": "optional district code"
  }
}
```

### Response Payload
```json
{
  "status": "success",
  "message": "Divisional Secretariats retrieved successfully.",
  "data": [
    {
      "dv_id": 1,
      "dv_dvcode": "DS001",
      "dv_dvname": "Divisional Secretariat Name",
      "dv_dcode": "COLOMBO"
    }
  ],
  "totalRecords": 100,
  "page": 1,
  "limit": 100
}
```

**Filters Available:**
- `search_key`: Search by name or code
- `dv_dcode`: Filter by district code

---

## 15. Payment Methods

**Endpoint:** `POST /api/v1/payment-methods/manage`

### Request Payload
```json
{
  "action": "READ_ALL",
  "payload": {
    "page": 1,
    "limit": 100,
    "skip": 0,
    "search_key": "search text"
  }
}
```

### Response Payload
```json
{
  "status": "success",
  "message": "Payment methods retrieved successfully.",
  "data": [
    {
      "pm_id": 1,
      "pm_pmcode": "CASH",
      "pm_pmdesc": "Cash Payment"
    }
  ],
  "totalRecords": 10,
  "page": 1,
  "limit": 100
}
```

**Filters Available:**
- `search_key`: Search by method code or description

---

## 16. Nilame

**Endpoint:** `POST /api/v1/nilame/manage`

### Request Payload
```json
{
  "action": "READ_ALL",
  "payload": {
    "page": 1,
    "limit": 100,
    "skip": 0,
    "search_key": "search text"
  }
}
```

### Response Payload
```json
{
  "status": "success",
  "message": "Nilame records retrieved successfully.",
  "data": [
    {
      "nlm_id": 1,
      "nlm_code": "NIL001",
      "nlm_description": "Nilame Type"
    }
  ],
  "totalRecords": 20,
  "page": 1,
  "limit": 100
}
```

**Filters Available:**
- `search_key`: Search by code or description

---

## 17. Gramasewaka

**Endpoint:** `POST /api/v1/gramasewaka/manage`

### Request Payload
```json
{
  "action": "READ_ALL",
  "payload": {
    "page": 1,
    "limit": 100,
    "skip": 0,
    "search_key": "search text"
  }
}
```

### Response Payload
```json
{
  "status": "success",
  "message": "Gramasewaka records retrieved successfully.",
  "data": [
    {
      "gs_id": 1,
      "gs_name": "Gramasewaka Name",
      "gs_district": "COLOMBO",
      "gs_gn_division": "GN001"
    }
  ],
  "totalRecords": 50,
  "page": 1,
  "limit": 100
}
```

**Filters Available:**
- `search_key`: Search by name, district, or GN division

---

## Common Pagination Parameters

All READ_ALL endpoints support pagination using one of two methods:

### Method 1: Page-based Pagination
```json
{
  "page": 1,
  "limit": 100
}
```

### Method 2: Offset-based Pagination
```json
{
  "skip": 0,
  "limit": 100
}
```

**Parameters:**
- `page`: Page number (1-indexed). If both `page` and `skip` provided, `page` takes precedence
- `skip`: Number of records to skip (0-indexed)
- `limit`: Maximum number of records to return (default: 10-100, max: 200)

---

## Common Response Structure

All READ_ALL responses follow this structure:

```json
{
  "status": "success",
  "message": "X records retrieved successfully.",
  "data": [
    { /* record object */ }
  ],
  "totalRecords": 150,
  "page": 1,
  "limit": 100
}
```

**Fields:**
- `status`: Response status ("success" or "error")
- `message`: Human-readable message
- `data`: Array of records or single object (depending on endpoint)
- `totalRecords`: Total number of matching records
- `page`: Current page number
- `limit`: Records per page

---

## Error Handling

Common error responses:

```json
{
  "status": "error",
  "message": "Validation error or server error message"
}
```

HTTP Status Codes:
- `200`: Success
- `400`: Validation error (missing required fields, invalid pagination params)
- `401`: Unauthorized
- `403`: Forbidden (insufficient permissions)
- `404`: Resource not found
- `500`: Server error

---

## Authentication & Authorization

All READ_ALL endpoints require:
- **Authentication**: Valid JWT token in `Authorization` header
- **Permissions**: User must have at least one of the required permissions (varies by endpoint)

Example Authorization Header:
```
Authorization: Bearer <your_jwt_token>
```

---

# MAIN ENTITY CRUD OPERATIONS (VIHARA, SILMATHA, BHIKKU, ARAMA)

These are the primary registration endpoints with full workflow management, enriched response data, and foreign key resolution.

---

## Vihara CRUD Operations

**Endpoint:** `POST /api/v1/viharas/manage`

### CREATE Action

#### Request
```json
{
  "action": "CREATE",
  "payload": {
    "data": {
      "vh_name": "Temple Name",
      "vh_address": "Temple Address",
      "vh_phone": "0712345678",
      "vh_email": "temple@example.com",
      "vh_province": "WESTERN",
      "vh_district": "COLOMBO",
      "vh_type": "PERMANENT",
      "vh_nikaya": "SIAM",
      "vh_viharadhipathi": "High Monk Name"
    }
  }
}
```

#### Response
```json
{
  "status": "success",
  "message": "Vihara created successfully.",
  "data": {
    "vh_id": 1,
    "vh_trn": "TRN001",
    "vh_name": "Temple Name",
    "vh_address": "Temple Address",
    "vh_phone": "0712345678",
    "vh_email": "temple@example.com",
    "vh_province": {
      "cp_code": "WESTERN",
      "cp_name": "Western Province"
    },
    "vh_district": {
      "dd_dcode": "COLOMBO",
      "dd_dname": "Colombo District"
    },
    "vh_type": "PERMANENT",
    "vh_nikaya": {
      "nk_code": "SIAM",
      "nk_name": "Siam Nikaya"
    },
    "vh_status": "COMPLETED",
    "vh_workflow_status": "COMPLETED",
    "vh_approval_status": "APPROVED",
    "vh_created_at": "2025-01-27T10:00:00",
    "vh_created_by": "user_id",
    "vh_approved_at": "2025-01-27T15:30:00",
    "vh_approved_by": "approver_id",
    "temple_lands": [],
    "resident_bhikkhus": []
  }
}
```

### READ_ONE Action

#### Request
```json
{
  "action": "READ_ONE",
  "payload": {
    "vh_id": 1
  }
}
```

Or search by TRN:
```json
{
  "action": "READ_ONE",
  "payload": {
    "vh_trn": "TRN001"
  }
}
```

#### Response (Same as CREATE)

### READ_ALL Action (Already documented above)

### UPDATE Action

#### Request
```json
{
  "action": "UPDATE",
  "payload": {
    "vh_id": 1,
    "data": {
      "vh_name": "Updated Temple Name",
      "vh_email": "newemail@example.com"
    }
  }
}
```

#### Response
```json
{
  "status": "success",
  "message": "Vihara updated successfully.",
  "data": {
    "vh_id": 1,
    "vh_trn": "TRN001",
    "vh_name": "Updated Temple Name",
    "vh_email": "newemail@example.com",
    "vh_updated_at": "2025-01-27T16:00:00",
    "vh_updated_by": "user_id"
  }
}
```

### DELETE Action

#### Request
```json
{
  "action": "DELETE",
  "payload": {
    "vh_id": 1
  }
}
```

#### Response
```json
{
  "status": "success",
  "message": "Vihara deleted successfully.",
  "data": null
}
```

---

## Silmatha CRUD Operations

**Endpoint:** `POST /api/v1/silmatha/manage`

### CREATE Action

#### Request
```json
{
  "action": "CREATE",
  "payload": {
    "data": {
      "sil_name": "Ordained Name",
      "sil_gihiname": "Birth Name",
      "sil_dofb": "1995-05-15",
      "sil_email": "silmatha@example.com",
      "sil_mobile": "0712345678",
      "sil_province": "WESTERN",
      "sil_district": "COLOMBO",
      "sil_cat": "CAT001",
      "sil_currstat": "ACTIVE",
      "sil_viharadhipathi": "Acharya Name"
    }
  }
}
```

#### Response
```json
{
  "status": "success",
  "message": "Silmatha record created successfully.",
  "data": {
    "sil_id": 1,
    "sil_regn": "SIL001",
    "sil_name": "Ordained Name",
    "sil_gihiname": "Birth Name",
    "sil_dofb": "1995-05-15",
    "sil_email": "silmatha@example.com",
    "sil_mobile": "0712345678",
    "sil_province": {
      "cp_code": "WESTERN",
      "cp_name": "Western Province"
    },
    "sil_district": {
      "dd_dcode": "COLOMBO",
      "dd_dname": "Colombo District"
    },
    "sil_cat": {
      "cg_code": "CAT001",
      "cg_desc": "Category Description"
    },
    "sil_currstat": {
      "st_code": "ACTIVE",
      "st_desc": "Active Status"
    },
    "sil_viharadhipathi": {
      "sil_regn": "SIL_ACHARYA",
      "sil_name": "Acharya Name"
    },
    "sil_workflow_status": "PENDING",
    "sil_approval_status": null,
    "sil_version_number": 1,
    "sil_created_at": "2025-01-27T10:00:00",
    "sil_created_by": "user_id"
  }
}
```

### READ_ONE Action

#### Request
```json
{
  "action": "READ_ONE",
  "payload": {
    "sil_regn": "SIL001"
  }
}
```

#### Response (Same as CREATE)

### UPDATE Action

#### Request
```json
{
  "action": "UPDATE",
  "payload": {
    "sil_id": 1,
    "data": {
      "sil_name": "Updated Ordained Name",
      "sil_currstat": "INACTIVE"
    }
  }
}
```

#### Response
```json
{
  "status": "success",
  "message": "Silmatha record updated successfully.",
  "data": {
    "sil_id": 1,
    "sil_regn": "SIL001",
    "sil_name": "Updated Ordained Name",
    "sil_currstat": "INACTIVE",
    "sil_updated_at": "2025-01-27T16:00:00",
    "sil_updated_by": "user_id"
  }
}
```

### DELETE Action

#### Request
```json
{
  "action": "DELETE",
  "payload": {
    "sil_id": 1
  }
}
```

#### Response
```json
{
  "status": "success",
  "message": "Silmatha record deleted successfully.",
  "data": null
}
```

---

## Bhikku CRUD Operations

**Endpoint:** `POST /api/v1/bhikkus/manage`

### CREATE Action

#### Request
```json
{
  "action": "CREATE",
  "payload": {
    "data": {
      "br_name": "Ordained Name",
      "br_gihiname": "Birth Name",
      "br_dofb": "1990-01-15",
      "br_email": "bhikku@example.com",
      "br_mobile": "0712345678",
      "br_province": "WESTERN",
      "br_district": "COLOMBO",
      "br_cat": "CAT001",
      "br_currstat": "ACTIVE",
      "br_nikaya": "SIAM",
      "br_livtemple": "TRN001",
      "br_mahananame": "Mahanayaka Name"
    }
  }
}
```

#### Response
```json
{
  "status": "success",
  "message": "Bhikku created successfully.",
  "data": {
    "br_id": 1,
    "br_regn": "BH002025",
    "br_name": "Ordained Name",
    "br_gihiname": "Birth Name",
    "br_dofb": "1990-01-15",
    "br_email": "bhikku@example.com",
    "br_mobile": "0712345678",
    "br_province": {
      "cp_code": "WESTERN",
      "cp_name": "Western Province"
    },
    "br_district": {
      "dd_dcode": "COLOMBO",
      "dd_dname": "Colombo District"
    },
    "br_cat": {
      "cg_code": "CAT001",
      "cg_desc": "Category Description"
    },
    "br_currstat": {
      "st_code": "ACTIVE",
      "st_desc": "Active Status"
    },
    "br_nikaya": {
      "nk_code": "SIAM",
      "nk_name": "Siam Nikaya"
    },
    "br_livtemple": {
      "vh_trn": "TRN001",
      "vh_name": "Temple Name"
    },
    "br_mahananame": "Mahanayaka Name",
    "br_workflow_status": "PENDING",
    "br_approval_status": null,
    "br_version_number": 1,
    "br_created_at": "2025-01-27T10:00:00",
    "br_created_by": "user_id"
  }
}
```

### READ_ONE Action

#### Request
```json
{
  "action": "READ_ONE",
  "payload": {
    "br_regn": "BH002025"
  }
}
```

#### Response (Same as CREATE)

### UPDATE Action

#### Request
```json
{
  "action": "UPDATE",
  "payload": {
    "br_id": 1,
    "data": {
      "br_name": "Updated Name",
      "br_livtemple": "TRN002"
    }
  }
}
```

#### Response
```json
{
  "status": "success",
  "message": "Bhikku record updated successfully.",
  "data": {
    "br_id": 1,
    "br_regn": "BH002025",
    "br_name": "Updated Name",
    "br_updated_at": "2025-01-27T16:00:00",
    "br_updated_by": "user_id"
  }
}
```

### DELETE Action

#### Request
```json
{
  "action": "DELETE",
  "payload": {
    "br_id": 1
  }
}
```

#### Response
```json
{
  "status": "success",
  "message": "Bhikku record deleted successfully.",
  "data": null
}
```

---

## Arama CRUD Operations

**Endpoint:** `POST /api/v1/arama/manage`

### CREATE Action

#### Request
```json
{
  "action": "CREATE",
  "payload": {
    "data": {
      "ar_name": "Arama Name",
      "ar_address": "Arama Address",
      "ar_mobile": "0712345678",
      "ar_email": "arama@example.com",
      "ar_province": "WESTERN",
      "ar_district": "COLOMBO",
      "ar_type": "NUNNERY",
      "ar_nikaya": "SIAM",
      "ar_aramadhipathi": "Aramadhipathi Name"
    }
  }
}
```

#### Response
```json
{
  "status": "success",
  "message": "Arama created successfully.",
  "data": {
    "ar_id": 1,
    "ar_trn": "ARN001",
    "ar_name": "Arama Name",
    "ar_address": "Arama Address",
    "ar_mobile": "0712345678",
    "ar_email": "arama@example.com",
    "ar_province": {
      "cp_code": "WESTERN",
      "cp_name": "Western Province"
    },
    "ar_district": {
      "dd_dcode": "COLOMBO",
      "dd_dname": "Colombo District"
    },
    "ar_type": "NUNNERY",
    "ar_nikaya": {
      "nk_code": "SIAM",
      "nk_name": "Siam Nikaya"
    },
    "ar_aramadhipathi": "Aramadhipathi Name",
    "ar_workflow_status": "COMPLETED",
    "ar_approval_status": "APPROVED",
    "ar_status": "COMPLETED",
    "ar_created_at": "2025-01-27T10:00:00",
    "ar_created_by": "user_id",
    "ar_approved_at": "2025-01-27T15:30:00",
    "ar_approved_by": "approver_id",
    "arama_lands": [],
    "resident_silmathas": []
  }
}
```

### READ_ONE Action

#### Request
```json
{
  "action": "READ_ONE",
  "payload": {
    "ar_id": 1
  }
}
```

Or by TRN:
```json
{
  "action": "READ_ONE",
  "payload": {
    "ar_trn": "ARN001"
  }
}
```

#### Response (Same as CREATE)

### UPDATE Action

#### Request
```json
{
  "action": "UPDATE",
  "payload": {
    "ar_id": 1,
    "data": {
      "ar_name": "Updated Arama Name",
      "ar_mobile": "0787654321"
    }
  }
}
```

#### Response
```json
{
  "status": "success",
  "message": "Arama updated successfully.",
  "data": {
    "ar_id": 1,
    "ar_trn": "ARN001",
    "ar_name": "Updated Arama Name",
    "ar_mobile": "0787654321",
    "ar_updated_at": "2025-01-27T16:00:00",
    "ar_updated_by": "user_id"
  }
}
```

### DELETE Action

#### Request
```json
{
  "action": "DELETE",
  "payload": {
    "ar_id": 1
  }
}
```

#### Response
```json
{
  "status": "success",
  "message": "Arama deleted successfully.",
  "data": null
}
```

---

# COMPARISON: NORMAL vs TEMPORARY CRUD RESPONSES

## Response Structure Differences

### Normal Entities (Vihara, Silmatha, Bhikku, Arama)
- ✅ **Enriched Foreign Key Data** - FK references are resolved to full objects with names and descriptions
- ✅ **Workflow Status** - Includes workflow_status, approval_status, and approval metadata
- ✅ **Complex Relations** - May include nested arrays (temple_lands, resident_bhikkhus, arama_lands, etc.)
- ✅ **Version Control** - Includes version_number for optimistic locking
- ✅ **Audit Trail** - created_by, created_at, updated_by, updated_at, approved_by, approved_at
- ✅ **Registration Numbers** - Auto-generated TRN (Vihara/Arama) or registration codes
- ✅ **High Data Richness** - Full entity with all related information

### Temporary Entities (Temporary Vihara, Silmatha, Arama, Bhikku, Devala)
- ❌ **Simple Field Names** - No nested FK objects, just raw codes/IDs
- ❌ **No Workflow** - No workflow_status or approval_status
- ❌ **Flat Structure** - Simple key-value pairs, no nested arrays
- ❌ **No Version Control** - No version_number field
- ❌ **Minimal Metadata** - Only basic audit fields (created_at, created_by)
- ❌ **No Registration Numbers** - Uses simple sequential IDs
- ❌ **Low Data Complexity** - Minimal related data

---

## Field Naming Conventions

### Normal Entities
```
Vihara:     vh_id, vh_trn, vh_name, vh_address, vh_phone, vh_email, ...
Silmatha:   sil_id, sil_regn, sil_name, sil_gihiname, sil_dofb, ...
Bhikku:     br_id, br_regn, br_name, br_gihiname, br_dofb, ...
Arama:      ar_id, ar_trn, ar_name, ar_address, ar_mobile, ...
```

### Temporary Entities
```
Temp Vihara:    tv_id, tv_name, tv_address, tv_contact_number, ...
Temp Silmatha:  ts_id, ts_name, ts_gihiname, ts_contact_number, ...
Temp Bhikku:    tb_id, tb_name, tb_gihiname, tb_contact_number, ...
Temp Arama:     ta_id, ta_name, ta_address, ta_contact_number, ...
Temp Devala:    td_id, td_name, td_address, td_contact_number, ...
```

---

## Pagination Response Format Differences

### Normal Entities (Standard)
```json
{
  "status": "success",
  "message": "X records retrieved successfully.",
  "data": [
    { /* enriched entity object */ }
  ],
  "totalRecords": 150,
  "page": 1,
  "limit": 100
}
```

### Temporary Entities (Metadata Wrapper)
```json
{
  "status": "success",
  "message": "Retrieved X records.",
  "data": {
    "records": [
      { /* simple temporary entity object */ }
    ],
    "total": 25,
    "skip": 0,
    "limit": 100
  }
}
```

---

## When to Use Normal vs Temporary Entities

### Use **Normal Entities** When:
- ✅ Creating permanent registrations
- ✅ Need full workflow management (approval, rejection)
- ✅ Require enriched FK data (resolved names, descriptions)
- ✅ Need version control and audit trail
- ✅ Building final registration records
- ✅ Storing complete entity information
- ✅ Performing bulk operations on complete records

### Use **Temporary Entities** When:
- ✅ Collecting incomplete information
- ✅ Need simple placeholders during data entry
- ✅ Want to save form state without validation
- ✅ Storing partial/draft records
- ✅ Don't need workflow management yet
- ✅ Need lightweight storage for later migration
- ✅ Performing intermediate steps before final registration

---

# TEMPORARY RECORD CRUD OPERATIONS

All temporary record endpoints (`temporary_vihara`, `temporary_silmatha`, `temporary_arama`, `temporary_bhikku`, `temporary_devala`) support the same CRUD operations structure.

---

## Temporary Vihara CRUD Operations

**Endpoint:** `POST /api/v1/temporary-vihara/manage`

### CREATE Action

#### Request
```json
{
  "action": "CREATE",
  "payload": {
    "data": {
      "tv_name": "Vihara Name",
      "tv_address": "Temple Address",
      "tv_contact_number": "0712345678",
      "tv_district": "COLOMBO",
      "tv_province": "WESTERN",
      "tv_viharadhipathi_name": "Viharadhipathi Name"
    }
  }
}
```

#### Response
```json
{
  "status": "success",
  "message": "Temporary vihara record created successfully.",
  "data": {
    "tv_id": 1,
    "tv_name": "Vihara Name",
    "tv_address": "Temple Address",
    "tv_contact_number": "0712345678",
    "tv_district": "COLOMBO",
    "tv_province": "WESTERN",
    "tv_viharadhipathi_name": "Viharadhipathi Name",
    "tv_created_at": "2025-01-27T10:00:00",
    "tv_created_by": "user_id",
    "tv_updated_at": null,
    "tv_updated_by": null
  }
}
```

### READ_ONE Action

#### Request
```json
{
  "action": "READ_ONE",
  "payload": {
    "tv_id": 1
  }
}
```

#### Response
```json
{
  "status": "success",
  "message": "Temporary vihara record retrieved successfully.",
  "data": {
    "tv_id": 1,
    "tv_name": "Vihara Name",
    "tv_address": "Temple Address",
    "tv_contact_number": "0712345678",
    "tv_district": "COLOMBO",
    "tv_province": "WESTERN",
    "tv_viharadhipathi_name": "Viharadhipathi Name",
    "tv_created_at": "2025-01-27T10:00:00",
    "tv_created_by": "user_id",
    "tv_updated_at": null,
    "tv_updated_by": null
  }
}
```

### READ_ALL Action (Already documented above)

#### Request
```json
{
  "action": "READ_ALL",
  "payload": {
    "skip": 0,
    "limit": 100,
    "search": "search text"
  }
}
```

#### Response
```json
{
  "status": "success",
  "message": "Retrieved X temporary vihara records.",
  "data": {
    "records": [
      {
        "tv_id": 1,
        "tv_name": "Vihara Name",
        "tv_address": "Temple Address",
        "tv_contact_number": "0712345678",
        "tv_district": "COLOMBO",
        "tv_province": "WESTERN",
        "tv_viharadhipathi_name": "Viharadhipathi Name",
        "tv_created_at": "2025-01-27T10:00:00",
        "tv_created_by": "user_id"
      }
    ],
    "total": 25,
    "skip": 0,
    "limit": 100
  }
}
```

### UPDATE Action

#### Request
```json
{
  "action": "UPDATE",
  "payload": {
    "tv_id": 1,
    "updates": {
      "tv_name": "Updated Vihara Name",
      "tv_contact_number": "0787654321",
      "tv_address": "New Address"
    }
  }
}
```

#### Response
```json
{
  "status": "success",
  "message": "Temporary vihara record updated successfully.",
  "data": {
    "tv_id": 1,
    "tv_name": "Updated Vihara Name",
    "tv_address": "New Address",
    "tv_contact_number": "0787654321",
    "tv_district": "COLOMBO",
    "tv_province": "WESTERN",
    "tv_viharadhipathi_name": "Viharadhipathi Name",
    "tv_created_at": "2025-01-27T10:00:00",
    "tv_created_by": "user_id",
    "tv_updated_at": "2025-01-27T15:30:00",
    "tv_updated_by": "user_id"
  }
}
```

### DELETE Action

#### Request
```json
{
  "action": "DELETE",
  "payload": {
    "tv_id": 1
  }
}
```

#### Response
```json
{
  "status": "success",
  "message": "Temporary vihara record deleted successfully.",
  "data": null
}
```

---

## Temporary Silmatha CRUD Operations

**Endpoint:** `POST /api/v1/temporary-silmatha/manage`

### CREATE Action

#### Request
```json
{
  "action": "CREATE",
  "payload": {
    "data": {
      "ts_name": "Silmatha Name",
      "ts_gihiname": "Birth Name",
      "ts_contact_number": "0712345678",
      "ts_address": "Address",
      "ts_province": "WESTERN",
      "ts_district": "COLOMBO"
    }
  }
}
```

#### Response
```json
{
  "status": "success",
  "message": "Temporary silmatha record created successfully.",
  "data": {
    "ts_id": 1,
    "ts_name": "Silmatha Name",
    "ts_gihiname": "Birth Name",
    "ts_contact_number": "0712345678",
    "ts_address": "Address",
    "ts_province": "WESTERN",
    "ts_district": "COLOMBO",
    "ts_created_at": "2025-01-27T10:00:00",
    "ts_created_by": "user_id"
  }
}
```

### READ_ONE Action

#### Request
```json
{
  "action": "READ_ONE",
  "payload": {
    "ts_id": 1
  }
}
```

#### Response
```json
{
  "status": "success",
  "message": "Temporary silmatha record retrieved successfully.",
  "data": {
    "ts_id": 1,
    "ts_name": "Silmatha Name",
    "ts_gihiname": "Birth Name",
    "ts_contact_number": "0712345678",
    "ts_address": "Address",
    "ts_province": "WESTERN",
    "ts_district": "COLOMBO",
    "ts_created_at": "2025-01-27T10:00:00",
    "ts_created_by": "user_id"
  }
}
```

### UPDATE Action

#### Request
```json
{
  "action": "UPDATE",
  "payload": {
    "ts_id": 1,
    "updates": {
      "ts_name": "Updated Name",
      "ts_contact_number": "0787654321"
    }
  }
}
```

#### Response
```json
{
  "status": "success",
  "message": "Temporary silmatha record updated successfully.",
  "data": {
    "ts_id": 1,
    "ts_name": "Updated Name",
    "ts_gihiname": "Birth Name",
    "ts_contact_number": "0787654321",
    "ts_address": "Address",
    "ts_province": "WESTERN",
    "ts_district": "COLOMBO",
    "ts_created_at": "2025-01-27T10:00:00",
    "ts_created_by": "user_id",
    "ts_updated_at": "2025-01-27T15:30:00",
    "ts_updated_by": "user_id"
  }
}
```

### DELETE Action

#### Request
```json
{
  "action": "DELETE",
  "payload": {
    "ts_id": 1
  }
}
```

#### Response
```json
{
  "status": "success",
  "message": "Temporary silmatha record deleted successfully.",
  "data": null
}
```

---

## Temporary Arama CRUD Operations

**Endpoint:** `POST /api/v1/temporary-arama/manage`

### CREATE Action

#### Request
```json
{
  "action": "CREATE",
  "payload": {
    "data": {
      "ta_name": "Arama Name",
      "ta_address": "Arama Address",
      "ta_contact_number": "0712345678",
      "ta_province": "WESTERN",
      "ta_district": "COLOMBO"
    }
  }
}
```

#### Response
```json
{
  "status": "success",
  "message": "Temporary arama record created successfully.",
  "data": {
    "ta_id": 1,
    "ta_name": "Arama Name",
    "ta_address": "Arama Address",
    "ta_contact_number": "0712345678",
    "ta_province": "WESTERN",
    "ta_district": "COLOMBO",
    "ta_created_at": "2025-01-27T10:00:00",
    "ta_created_by": "user_id"
  }
}
```

### READ_ONE Action

#### Request
```json
{
  "action": "READ_ONE",
  "payload": {
    "ta_id": 1
  }
}
```

#### Response
```json
{
  "status": "success",
  "message": "Temporary arama record retrieved successfully.",
  "data": {
    "ta_id": 1,
    "ta_name": "Arama Name",
    "ta_address": "Arama Address",
    "ta_contact_number": "0712345678",
    "ta_province": "WESTERN",
    "ta_district": "COLOMBO",
    "ta_created_at": "2025-01-27T10:00:00",
    "ta_created_by": "user_id"
  }
}
```

### UPDATE Action

#### Request
```json
{
  "action": "UPDATE",
  "payload": {
    "ta_id": 1,
    "updates": {
      "ta_name": "Updated Arama Name",
      "ta_contact_number": "0787654321"
    }
  }
}
```

#### Response
```json
{
  "status": "success",
  "message": "Temporary arama record updated successfully.",
  "data": {
    "ta_id": 1,
    "ta_name": "Updated Arama Name",
    "ta_address": "Arama Address",
    "ta_contact_number": "0787654321",
    "ta_province": "WESTERN",
    "ta_district": "COLOMBO",
    "ta_created_at": "2025-01-27T10:00:00",
    "ta_created_by": "user_id",
    "ta_updated_at": "2025-01-27T15:30:00",
    "ta_updated_by": "user_id"
  }
}
```

### DELETE Action

#### Request
```json
{
  "action": "DELETE",
  "payload": {
    "ta_id": 1
  }
}
```

#### Response
```json
{
  "status": "success",
  "message": "Temporary arama record deleted successfully.",
  "data": null
}
```

---

## Temporary Bhikku CRUD Operations

**Endpoint:** `POST /api/v1/temporary-bhikku/manage`

### CREATE Action

#### Request
```json
{
  "action": "CREATE",
  "payload": {
    "data": {
      "tb_name": "Bhikku Name",
      "tb_gihiname": "Birth Name",
      "tb_contact_number": "0712345678",
      "tb_address": "Address",
      "tb_province": "WESTERN",
      "tb_district": "COLOMBO"
    }
  }
}
```

#### Response
```json
{
  "status": "success",
  "message": "Temporary bhikku record created successfully.",
  "data": {
    "tb_id": 1,
    "tb_name": "Bhikku Name",
    "tb_gihiname": "Birth Name",
    "tb_contact_number": "0712345678",
    "tb_address": "Address",
    "tb_province": "WESTERN",
    "tb_district": "COLOMBO",
    "tb_created_at": "2025-01-27T10:00:00",
    "tb_created_by": "user_id"
  }
}
```

### READ_ONE, UPDATE, DELETE Actions

Follow the same pattern as Temporary Vihara/Silmatha/Arama with corresponding field names (`tb_id`, `tb_name`, etc.)

---

## Temporary Devala CRUD Operations

**Endpoint:** `POST /api/v1/temporary-devala/manage`

### CREATE Action

#### Request
```json
{
  "action": "CREATE",
  "payload": {
    "data": {
      "td_name": "Devala Name",
      "td_address": "Devala Address",
      "td_contact_number": "0712345678",
      "td_province": "WESTERN",
      "td_district": "COLOMBO"
    }
  }
}
```

#### Response
```json
{
  "status": "success",
  "message": "Temporary devala record created successfully.",
  "data": {
    "td_id": 1,
    "td_name": "Devala Name",
    "td_address": "Devala Address",
    "td_contact_number": "0712345678",
    "td_province": "WESTERN",
    "td_district": "COLOMBO",
    "td_created_at": "2025-01-27T10:00:00",
    "td_created_by": "user_id"
  }
}
```

### READ_ONE, UPDATE, DELETE Actions

Follow the same pattern as other temporary entities with corresponding field names (`td_id`, `td_name`, etc.)

---

# SEARCH ENDPOINTS

## 1. Advance Search - Search All Records

**Endpoint:** `GET /api/v1/advance-search` or `POST /api/v1/advance-search`

This unified search endpoint searches across all entity types (Bhikku, Silmatha, High Bhikku, Direct High Bhikku, Vihara, Arama, Devala).

### GET Request (Query Parameters)

```
GET /api/v1/advance-search?registration_number=BH&name=John&birth_date=1990-01-15&entity_type=bhikku&skip=0&limit=50
```

### POST Request

#### Request
```json
{
  "registration_number": "BH2025",
  "name": "John",
  "birth_date": "1990-01-15",
  "entity_type": "bhikku",
  "skip": 0,
  "limit": 50
}
```

### Response
```json
{
  "status": "success",
  "message": "Found 15 matching record(s)",
  "total": 15,
  "data": [
    {
      "entity_type": "bhikku",
      "registration_number": "BH002025",
      "ordained_name": "Bhikkhu Name",
      "birth_name": "John Doe",
      "date_of_birth": "1990-01-15",
      "contact_number": "0712345678",
      "email": "email@example.com",
      "live_location_temple": "TRN001",
      "current_status": "ACTIVE",
      "category": "CAT001",
      "ordination_date": "2015-01-01"
    }
  ]
}
```

**Query/Payload Parameters:**
- `registration_number`: Search by registration number (partial match) - Optional
- `name`: Search by ordained name or birth name (partial match) - Optional
- `birth_date`: Search by exact birth date (YYYY-MM-DD format) - Optional
- `entity_type`: Filter by specific entity type - Optional
  - Valid values: `bhikku`, `silmatha`, `high_bhikku`, `direct_high_bhikku`, `vihara`, `arama`, `devala`
- `skip`: Number of records to skip (default: 0) - Optional
- `limit`: Maximum records to return (default: 50, max: 100) - Optional

---

## 2. Record Details - Get Single Record Details

**Endpoint:** `GET /api/v1/advance-search/{entity_type}/{registration_number}`

Retrieves comprehensive details for a single entity in QR-style format.

### Request
```
GET /api/v1/advance-search/bhikku/BH002025
```

### Response
```json
{
  "status": "success",
  "message": "Record details retrieved successfully.",
  "data": {
    "entity_type": "bhikku",
    "registration_number": "BH002025",
    "fields": [
      {
        "label": "Ordained Name",
        "value": "Bhikkhu Name"
      },
      {
        "label": "Birth Name",
        "value": "John Doe"
      },
      {
        "label": "Date of Birth",
        "value": "1990-01-15"
      },
      {
        "label": "Live Location Temple",
        "value": "Main Temple (TRN001)"
      },
      {
        "label": "Current Status",
        "value": "ACTIVE"
      },
      {
        "label": "Category",
        "value": "Category Description"
      },
      {
        "label": "Ordination Date",
        "value": "2015-01-01"
      },
      {
        "label": "Contact Number",
        "value": "0712345678"
      },
      {
        "label": "Email",
        "value": "email@example.com"
      },
      {
        "label": "Workflow Status",
        "value": "COMPLETED"
      }
    ]
  }
}
```

**Path Parameters:**
- `entity_type`: Type of entity
  - Valid values: `bhikku`, `silmatha`, `high_bhikku`, `direct_high_bhikku`, `vihara`, `arama`, `devala`
- `registration_number`: Registration number or TRN (e.g., `BH002025`, `TRN001`)

---

## 3. QR Code Search

**Endpoint:** `POST /api/v1/qr_search`

Get limited details via QR code search. This endpoint does NOT require authentication.

### Request
```json
{
  "id": "BH002025",
  "record_type": "bhikku"
}
```

### Response
```json
{
  "status": "success",
  "message": "Record details retrieved successfully.",
  "data": {
    "ordained_name": "Bhikkhu Name",
    "birth_name": "John Doe",
    "date_of_birth": "1990-01-15",
    "contact_number": "0712345678",
    "email": "email@example.com",
    "live_location": "Main Temple",
    "current_status": "ACTIVE",
    "category": "Category Name",
    "ordination_date": "2015-01-01"
  }
}
```

**Request Parameters:**
- `id`: Registration ID/Number - Required
- `record_type`: Type of record (optional, auto-detects from ID prefix if not provided)
  - Valid values: `bhikku`, `silmatha`, `high_bhikku`, `vihara`, `arama`, `devala`

**Supported ID Prefixes (auto-detection):**
- `BH*` → bhikku
- `SIL*` → silmatha
- `UPS*` → high_bhikku
- `DBH*` → direct_high_bhikku
- `TRN*` → vihara
- `ARN*` → arama
- `DVL*` → devala

---

# ERROR RESPONSES

All endpoints may return error responses in the following format:

### Validation Error
```json
{
  "status": "error",
  "message": "Validation error",
  "errors": [
    {
      "field": "payload.registration_number",
      "message": "Field is required"
    }
  ]
}
```
**HTTP Status Code:** 400

### Not Found Error
```json
{
  "status": "error",
  "message": "No record found with ID: XX"
}
```
**HTTP Status Code:** 404

### Authentication Error
```json
{
  "status": "error",
  "message": "Unauthorized"
}
```
**HTTP Status Code:** 401

### Permission Error
```json
{
  "status": "error",
  "message": "Permission denied. Required permission: vihara:read"
}
```
**HTTP Status Code:** 403

### Server Error
```json
{
  "status": "error",
  "message": "Error searching records: Internal error details"
}
```
**HTTP Status Code:** 500

---

## Example cURL Request

```bash
curl -X POST "http://localhost:8000/api/v1/viharas/manage" \
  -H "Authorization: Bearer your_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "READ_ALL",
    "payload": {
      "page": 1,
      "limit": 50,
      "search_key": "vihara"
    }
  }'
```

---

## Example Python Request

```python
import requests

url = "http://localhost:8000/api/v1/viharas/manage"
headers = {
    "Authorization": "Bearer your_token_here",
    "Content-Type": "application/json"
}
payload = {
    "action": "READ_ALL",
    "payload": {
        "page": 1,
        "limit": 50,
        "search_key": "vihara"
    }
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
```

---

## Performance Considerations

- **Limit Size**: Maximum limit is 200 records per request
- **Search Index**: Search operations are indexed on commonly used fields
- **Pagination**: Use offset-based pagination for large datasets
- **Filtering**: Combine multiple filters to reduce result set
- **Caching**: Consider implementing client-side caching for frequently accessed READ_ALL results

---

**Last Updated:** January 27, 2026
**Version:** 1.0
