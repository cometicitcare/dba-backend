# DBA HRMS API - Complete Endpoint Reference

**Last Updated:** January 27, 2026
**Version:** 1.0

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication & Authorization](#authentication--authorization)
3. [Main Entity CRUD Operations](#main-entity-crud-operations)
   - [Vihara](#vihara-crud-operations)
   - [Silmatha](#silmatha-crud-operations)
   - [Bhikku](#bhikku-crud-operations)
   - [Arama](#arama-crud-operations)
4. [Temporary Record CRUD Operations](#temporary-record-crud-operations)
   - [Temporary Vihara](#temporary-vihara-crud-operations)
   - [Temporary Silmatha](#temporary-silmatha-crud-operations)
   - [Temporary Arama](#temporary-arama-crud-operations)
   - [Temporary Bhikku](#temporary-bhikku-crud-operations)
   - [Temporary Devala](#temporary-devala-crud-operations)
5. [READ_ALL List Endpoints](#read_all-list-endpoints)
6. [Search Endpoints](#search-endpoints)
7. [Response Structure Comparison](#response-structure-comparison)
8. [Error Handling](#error-handling)
9. [Examples](#examples)

---

## Overview

This API provides comprehensive CRUD operations for Buddhist religious administrative database management. All endpoints support JSON request/response format with role-based access control.

### Key Features:
- ✅ RESTful API design with POST-based CRUD operations
- ✅ Role-based access control (RBAC)
- ✅ Pagination support (page-based and offset-based)
- ✅ Advanced filtering and search
- ✅ Workflow management (approval, rejection)
- ✅ Audit trail for all operations
- ✅ Foreign key resolution with enriched data

---

## Authentication & Authorization

### Required Headers
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

### Permission Model
Each operation requires specific permissions:
- `entity:create` - Create new records
- `entity:read` - Read/list records
- `entity:update` - Update existing records
- `entity:delete` - Delete records

Where `entity` can be: `vihara`, `silmatha`, `bhikku`, `arama`, `devala`, `system`, etc.

### Error Responses

**401 Unauthorized:**
```json
{
  "status": "error",
  "message": "Unauthorized"
}
```

**403 Forbidden:**
```json
{
  "status": "error",
  "message": "Permission denied. Required permission: entity:create"
}
```

---

# MAIN ENTITY CRUD OPERATIONS

These are the primary registration endpoints with full workflow management, enriched response data, and foreign key resolution.

---

## Vihara CRUD Operations

**Endpoint:** `POST /api/v1/viharas/manage`
**Permission:** `vihara:create`, `vihara:read`, `vihara:update`, `vihara:delete`

### CREATE Action

**Request:**
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
      "vh_nikaya": "SIAM"
    }
  }
}
```

**Response (Success):**
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
    "vh_nikaya": {
      "nk_code": "SIAM",
      "nk_name": "Siam Nikaya"
    },
    "vh_workflow_status": "S1_PENDING",
    "vh_approval_status": null,
    "vh_created_at": "2025-01-27T10:00:00",
    "vh_created_by": "user_id"
  }
}
```

### READ_ONE Action

**Request:**
```json
{
  "action": "READ_ONE",
  "payload": {
    "vh_id": 1
  }
}
```

Or by TRN:
```json
{
  "action": "READ_ONE",
  "payload": {
    "vh_trn": "TRN001"
  }
}
```

**Response:** Same as CREATE response

### READ_ALL Action

**Request:**
```json
{
  "action": "READ_ALL",
  "payload": {
    "page": 1,
    "limit": 100,
    "search_key": "search text",
    "province": "WESTERN",
    "district": "COLOMBO",
    "vh_typ": "PERMANENT"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Viharas retrieved successfully.",
  "data": [
    {
      "vh_id": 1,
      "vh_trn": "TRN001",
      "vh_name": "Temple Name",
      "vh_province": { "cp_code": "WESTERN", "cp_name": "Western Province" },
      "vh_district": { "dd_dcode": "COLOMBO", "dd_dname": "Colombo" },
      "vh_workflow_status": "COMPLETED"
    }
  ],
  "totalRecords": 150,
  "page": 1,
  "limit": 100
}
```

**Available Filters:**
- `search_key`: Search by name, address, contact
- `province`, `district`, `divisional_secretariat`, `gn_division`
- `temple`, `child_temple`, `nikaya`, `parshawaya`, `category`
- `status`, `vh_typ`
- `date_from`, `date_to`: Date range filter

### UPDATE Action

**Request:**
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

**Response:**
```json
{
  "status": "success",
  "message": "Vihara updated successfully.",
  "data": {
    "vh_id": 1,
    "vh_name": "Updated Temple Name",
    "vh_email": "newemail@example.com",
    "vh_updated_at": "2025-01-27T16:00:00",
    "vh_updated_by": "user_id"
  }
}
```

### DELETE Action

**Request:**
```json
{
  "action": "DELETE",
  "payload": {
    "vh_id": 1
  }
}
```

**Response:**
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
**Permission:** `silmatha:create`, `silmatha:read`, `silmatha:update`, `silmatha:delete`

### CREATE Action

**Request:**
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
      "sil_currstat": "ACTIVE"
    }
  }
}
```

**Response:**
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
    "sil_province": {
      "cp_code": "WESTERN",
      "cp_name": "Western Province"
    },
    "sil_cat": {
      "cg_code": "CAT001",
      "cg_desc": "Category Description"
    },
    "sil_currstat": {
      "st_code": "ACTIVE",
      "st_desc": "Active Status"
    },
    "sil_workflow_status": "PENDING",
    "sil_version_number": 1,
    "sil_created_at": "2025-01-27T10:00:00",
    "sil_created_by": "user_id"
  }
}
```

### READ_ONE Action

**Request:**
```json
{
  "action": "READ_ONE",
  "payload": {
    "sil_regn": "SIL001"
  }
}
```

**Response:** Same as CREATE response

### READ_ALL Action

**Request:**
```json
{
  "action": "READ_ALL",
  "payload": {
    "page": 1,
    "limit": 10,
    "search_key": "name",
    "province": "WESTERN",
    "status": "ACTIVE"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Retrieved X silmatha records.",
  "data": [
    {
      "sil_id": 1,
      "sil_regn": "SIL001",
      "sil_name": "Ordained Name",
      "sil_province": { "cp_code": "WESTERN" },
      "sil_workflow_status": "COMPLETED"
    }
  ],
  "totalRecords": 150,
  "page": 1,
  "limit": 10
}
```

**Available Filters:**
- `search_key`: Search by name, registration number
- `province`, `district`, `divisional_secretariat`, `gn_division`
- `temple`, `child_temple`, `parshawaya`, `category`, `status`
- `workflow_status`
- `date_from`, `date_to`: Date range filter

### UPDATE Action

**Request:**
```json
{
  "action": "UPDATE",
  "payload": {
    "sil_id": 1,
    "data": {
      "sil_name": "Updated Name",
      "sil_currstat": "INACTIVE"
    }
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Silmatha record updated successfully.",
  "data": {
    "sil_id": 1,
    "sil_regn": "SIL001",
    "sil_name": "Updated Name",
    "sil_updated_at": "2025-01-27T16:00:00",
    "sil_updated_by": "user_id"
  }
}
```

### DELETE Action

**Request:**
```json
{
  "action": "DELETE",
  "payload": {
    "sil_id": 1
  }
}
```

**Response:**
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
**Permission:** `bhikku:create`, `bhikku:read`, `bhikku:update`, `bhikku:delete`

### CREATE Action

**Request:**
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
      "br_cat": "CAT001",
      "br_currstat": "ACTIVE",
      "br_nikaya": "SIAM",
      "br_livtemple": "TRN001"
    }
  }
}
```

**Response:**
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
    "br_province": {
      "cp_code": "WESTERN",
      "cp_name": "Western Province"
    },
    "br_nikaya": {
      "nk_code": "SIAM",
      "nk_name": "Siam Nikaya"
    },
    "br_livtemple": {
      "vh_trn": "TRN001",
      "vh_name": "Temple Name"
    },
    "br_workflow_status": "PENDING",
    "br_version_number": 1,
    "br_created_at": "2025-01-27T10:00:00",
    "br_created_by": "user_id"
  }
}
```

### READ_ONE Action

**Request:**
```json
{
  "action": "READ_ONE",
  "payload": {
    "br_regn": "BH002025"
  }
}
```

**Response:** Same as CREATE response

### READ_ALL Action

**Request:**
```json
{
  "action": "READ_ALL",
  "payload": {
    "page": 1,
    "limit": 50,
    "search_key": "name",
    "province": "WESTERN",
    "vh_trn": "TRN001"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Retrieved X bhikku records.",
  "data": [
    {
      "br_id": 1,
      "br_regn": "BH002025",
      "br_name": "Ordained Name",
      "br_province": { "cp_code": "WESTERN" },
      "br_livtemple": { "vh_trn": "TRN001" },
      "br_workflow_status": "COMPLETED"
    }
  ],
  "totalRecords": 1500,
  "page": 1,
  "limit": 50
}
```

**Available Filters:**
- `search_key`: Search by name, registration number
- `province`, `district`, `divisional_secretariat`, `gn_division`
- `temple`, `child_temple`, `parshawaya`, `category`, `status`
- `workflow_status`, `vh_trn`

### UPDATE Action

**Request:**
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

**Response:**
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

**Request:**
```json
{
  "action": "DELETE",
  "payload": {
    "br_id": 1
  }
}
```

**Response:**
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
**Permission:** `arama:create`, `arama:read`, `arama:update`, `arama:delete`

### CREATE Action

**Request:**
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
      "ar_nikaya": "SIAM"
    }
  }
}
```

**Response:**
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
    "ar_province": {
      "cp_code": "WESTERN",
      "cp_name": "Western Province"
    },
    "ar_nikaya": {
      "nk_code": "SIAM",
      "nk_name": "Siam Nikaya"
    },
    "ar_workflow_status": "COMPLETED",
    "ar_approval_status": "APPROVED",
    "ar_created_at": "2025-01-27T10:00:00",
    "ar_created_by": "user_id",
    "ar_approved_at": "2025-01-27T15:30:00",
    "ar_approved_by": "approver_id"
  }
}
```

### READ_ONE Action

**Request:**
```json
{
  "action": "READ_ONE",
  "payload": {
    "ar_id": 1
  }
}
```

**Response:** Same as CREATE response

### READ_ALL Action

**Request:**
```json
{
  "action": "READ_ALL",
  "payload": {
    "page": 1,
    "limit": 100,
    "search_key": "arama",
    "province": "WESTERN"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Arama records retrieved successfully.",
  "data": [
    {
      "ar_id": 1,
      "ar_trn": "ARN001",
      "ar_name": "Arama Name",
      "ar_province": { "cp_code": "WESTERN" },
      "ar_workflow_status": "COMPLETED"
    }
  ],
  "totalRecords": 250,
  "page": 1,
  "limit": 100
}
```

**Available Filters:**
- `search_key`: Search by name, address, contact
- `province`, `district`, `divisional_secretariat`, `gn_division`
- `temple`, `child_temple`, `nikaya`, `parshawaya`, `category`
- `status`, `ar_typ`, `date_from`, `date_to`

### UPDATE Action

**Request:**
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

**Response:**
```json
{
  "status": "success",
  "message": "Arama updated successfully.",
  "data": {
    "ar_id": 1,
    "ar_trn": "ARN001",
    "ar_name": "Updated Arama Name",
    "ar_updated_at": "2025-01-27T16:00:00",
    "ar_updated_by": "user_id"
  }
}
```

### DELETE Action

**Request:**
```json
{
  "action": "DELETE",
  "payload": {
    "ar_id": 1
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Arama deleted successfully.",
  "data": null
}
```

---

# TEMPORARY RECORD CRUD OPERATIONS

Temporary records are lightweight, simplified versions used for storing incomplete or draft information. They support basic CRUD operations without workflow management.

---

## Temporary Vihara CRUD Operations

**Endpoint:** `POST /api/v1/temporary-vihara/manage`

### CREATE Action

**Request:**
```json
{
  "action": "CREATE",
  "payload": {
    "data": {
      "tv_name": "Vihara Name",
      "tv_address": "Temple Address",
      "tv_contact_number": "0712345678",
      "tv_district": "COLOMBO",
      "tv_province": "WESTERN"
    }
  }
}
```

**Response:**
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
    "tv_created_at": "2025-01-27T10:00:00",
    "tv_created_by": "user_id"
  }
}
```

### READ_ONE Action

**Request:**
```json
{
  "action": "READ_ONE",
  "payload": {
    "tv_id": 1
  }
}
```

**Response:** Same as CREATE response

### READ_ALL Action

**Request:**
```json
{
  "action": "READ_ALL",
  "payload": {
    "skip": 0,
    "limit": 100,
    "search": "vihara name"
  }
}
```

**Response:**
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
        "tv_contact_number": "0712345678"
      }
    ],
    "total": 25,
    "skip": 0,
    "limit": 100
  }
}
```

### UPDATE Action

**Request:**
```json
{
  "action": "UPDATE",
  "payload": {
    "tv_id": 1,
    "updates": {
      "tv_name": "Updated Name",
      "tv_contact_number": "0787654321"
    }
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Temporary vihara record updated successfully.",
  "data": {
    "tv_id": 1,
    "tv_name": "Updated Name",
    "tv_contact_number": "0787654321",
    "tv_updated_at": "2025-01-27T15:30:00",
    "tv_updated_by": "user_id"
  }
}
```

### DELETE Action

**Request:**
```json
{
  "action": "DELETE",
  "payload": {
    "tv_id": 1
  }
}
```

**Response:**
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

### CREATE/READ_ONE/UPDATE/DELETE

Follow the same pattern as Temporary Vihara with fields:
- `ts_id`, `ts_name`, `ts_gihiname`, `ts_contact_number`, `ts_address`, `ts_province`, `ts_district`

---

## Temporary Arama CRUD Operations

**Endpoint:** `POST /api/v1/temporary-arama/manage`

### CREATE/READ_ONE/UPDATE/DELETE

Follow the same pattern as Temporary Vihara with fields:
- `ta_id`, `ta_name`, `ta_address`, `ta_contact_number`, `ta_province`, `ta_district`

---

## Temporary Bhikku CRUD Operations

**Endpoint:** `POST /api/v1/temporary-bhikku/manage`

### CREATE/READ_ONE/UPDATE/DELETE

Follow the same pattern as Temporary Vihara with fields:
- `tb_id`, `tb_name`, `tb_gihiname`, `tb_contact_number`, `tb_address`, `tb_province`, `tb_district`

---

## Temporary Devala CRUD Operations

**Endpoint:** `POST /api/v1/temporary-devala/manage`

### CREATE/READ_ONE/UPDATE/DELETE

Follow the same pattern as Temporary Vihara with fields:
- `td_id`, `td_name`, `td_address`, `td_contact_number`, `td_province`, `td_district`

---

# READ_ALL LIST ENDPOINTS

Simple read-only endpoints for listing reference data and system codes.

---

## 1. Vihara READ_ALL

**Endpoint:** `POST /api/v1/viharas/manage`

**Request:**
```json
{
  "action": "READ_ALL",
  "payload": {
    "page": 1,
    "limit": 100,
    "search_key": "temple"
  }
}
```

**Response:** Returns list of viharas with enriched data (see Vihara CRUD above)

---

## 2. Silmatha READ_ALL

**Endpoint:** `POST /api/v1/silmatha/manage`

**Request:**
```json
{
  "action": "READ_ALL",
  "payload": {
    "page": 1,
    "limit": 10,
    "search_key": "name"
  }
}
```

**Response:** Returns list of silmathas

---

## 3. Bhikku READ_ALL

**Endpoint:** `POST /api/v1/bhikkus/manage`

**Request:**
```json
{
  "action": "READ_ALL",
  "payload": {
    "page": 1,
    "limit": 50
  }
}
```

**Response:** Returns list of bhikkus

---

## 4. Arama READ_ALL

**Endpoint:** `POST /api/v1/arama/manage`

**Request:**
```json
{
  "action": "READ_ALL",
  "payload": {
    "page": 1,
    "limit": 100
  }
}
```

**Response:** Returns list of aramas

---

## 5. District READ_ALL

**Endpoint:** `POST /api/v1/districts/manage`

**Request:**
```json
{
  "action": "READ_ALL",
  "payload": {
    "page": 1,
    "limit": 100,
    "search_key": "colombo",
    "dd_prcode": "WESTERN"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Districts retrieved successfully.",
  "data": [
    {
      "dd_id": 1,
      "dd_dcode": "COLOMBO",
      "dd_dname": "Colombo",
      "dd_prcode": "WESTERN"
    }
  ],
  "totalRecords": 25,
  "page": 1,
  "limit": 100
}
```

---

## 6. Province READ_ALL

**Endpoint:** `POST /api/v1/provinces/manage`

**Response:**
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
  "totalRecords": 9
}
```

---

## 7. Status READ_ALL

**Endpoint:** `POST /api/v1/status/manage`

**Response:**
```json
{
  "status": "success",
  "message": "Status records retrieved successfully.",
  "data": [
    {
      "st_id": 1,
      "st_statcd": "ACTIVE",
      "st_statdesc": "Active Status"
    }
  ]
}
```

---

## 8. Roles READ_ALL

**Endpoint:** `POST /api/v1/roles/manage`

**Response:**
```json
{
  "status": "success",
  "message": "Roles retrieved successfully.",
  "data": [
    {
      "ro_role_id": "ADMIN",
      "ro_role_name": "Administrator",
      "ro_description": "System Admin Role"
    }
  ]
}
```

---

## 9. Religion READ_ALL

**Endpoint:** `POST /api/v1/religion/manage`

**Response:**
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
  ]
}
```

---

## 10. Payment Methods READ_ALL

**Endpoint:** `POST /api/v1/payment-methods/manage`

**Response:**
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
  ]
}
```

---

## 11. Divisional Secretariat READ_ALL

**Endpoint:** `POST /api/v1/divisional-secretariat/manage`

**Response:**
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
  ]
}
```

---

## 12. Nilame READ_ALL

**Endpoint:** `POST /api/v1/nilame/manage`

**Response:**
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
  ]
}
```

---

## 13. Gramasewaka READ_ALL

**Endpoint:** `POST /api/v1/gramasewaka/manage`

**Response:**
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
  ]
}
```

---

## 14. Objections READ_ALL

**Endpoint:** `POST /api/v1/objections/manage`

**Request:**
```json
{
  "action": "READ_ALL",
  "payload": {
    "page": 1,
    "limit": 10,
    "vh_trn": "TRN001",
    "obj_status": "PENDING"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Retrieved X objections.",
  "data": [
    {
      "obj_id": 1,
      "vh_trn": "TRN001",
      "ot_code": "RESIDENCY_RESTRICTION",
      "obj_reason": "Reason text",
      "obj_status": "PENDING",
      "obj_submitted_by": "user_id"
    }
  ],
  "totalRecords": 50,
  "page": 1,
  "limit": 10
}
```

---

# SEARCH ENDPOINTS

Unified search endpoints across all entity types.

---

## 1. Advance Search - All Records

**Endpoint:** `GET /api/v1/advance-search` or `POST /api/v1/advance-search`

### GET Request

```
GET /api/v1/advance-search?registration_number=BH&name=John&entity_type=bhikku&skip=0&limit=50
```

### POST Request

**Request:**
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

**Response:**
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
      "current_status": "ACTIVE"
    }
  ]
}
```

**Query Parameters/Payload Fields:**
- `registration_number`: Partial match search
- `name`: Ordained or birth name search
- `birth_date`: Exact date match (YYYY-MM-DD)
- `entity_type`: bhikku, silmatha, high_bhikku, vihara, arama, devala
- `skip`, `limit`: Pagination (max 100)

---

## 2. Record Details - Single Record

**Endpoint:** `GET /api/v1/advance-search/{entity_type}/{registration_number}`

**Request:**
```
GET /api/v1/advance-search/bhikku/BH002025
```

**Response:**
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
        "label": "Live Location",
        "value": "Main Temple (TRN001)"
      }
    ]
  }
}
```

---

## 3. QR Code Search

**Endpoint:** `POST /api/v1/qr_search`

**Note:** No authentication required

**Request:**
```json
{
  "id": "BH002025",
  "record_type": "bhikku"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Record details retrieved successfully.",
  "data": {
    "ordained_name": "Bhikkhu Name",
    "birth_name": "John Doe",
    "date_of_birth": "1990-01-15",
    "contact_number": "0712345678",
    "live_location": "Main Temple",
    "current_status": "ACTIVE"
  }
}
```

**ID Prefix Detection:**
- `BH*` → bhikku
- `SIL*` → silmatha
- `UPS*` / `DBH*` → high_bhikku
- `TRN*` → vihara
- `ARN*` → arama
- `DVL*` → devala

---

# RESPONSE STRUCTURE COMPARISON

## Normal Entities vs Temporary Entities

| Feature | Normal | Temporary |
|---------|--------|-----------|
| Enriched FK Data | ✅ Nested objects | ❌ Simple codes |
| Workflow Status | ✅ Yes | ❌ No |
| Approval Metadata | ✅ Yes | ❌ No |
| Version Control | ✅ Yes | ❌ No |
| Related Arrays | ✅ Yes | ❌ No |
| Auto-Generated IDs | ✅ TRN/Codes | ❌ Sequential |
| Audit Fields | ✅ Complete | ❌ Basic |

### Normal Entity Example
```json
{
  "vh_id": 1,
  "vh_trn": "TRN001",
  "vh_province": {
    "cp_code": "WESTERN",
    "cp_name": "Western Province"
  },
  "vh_workflow_status": "COMPLETED",
  "vh_approval_status": "APPROVED",
  "vh_version_number": 1,
  "vh_created_at": "2025-01-27T10:00:00",
  "vh_created_by": "user_id"
}
```

### Temporary Entity Example
```json
{
  "tv_id": 1,
  "tv_name": "Vihara Name",
  "tv_province": "WESTERN",
  "tv_created_at": "2025-01-27T10:00:00",
  "tv_created_by": "user_id"
}
```

---

# ERROR HANDLING

## HTTP Status Codes

| Code | Meaning | Response |
|------|---------|----------|
| 200 | Success | Operation completed successfully |
| 400 | Bad Request | Validation error or missing fields |
| 401 | Unauthorized | Missing or invalid JWT token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 500 | Server Error | Internal error |

## Error Response Format

### Validation Error (400)
```json
{
  "status": "error",
  "message": "Validation error",
  "errors": [
    {
      "field": "payload.vh_name",
      "message": "Field is required"
    }
  ]
}
```

### Not Found (404)
```json
{
  "status": "error",
  "message": "Vihara not found"
}
```

### Permission Error (403)
```json
{
  "status": "error",
  "message": "Permission denied. Required permission: vihara:create"
}
```

---

# EXAMPLES

## Example 1: Create a Vihara

**cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/viharas/manage" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "CREATE",
    "payload": {
      "data": {
        "vh_name": "New Temple",
        "vh_address": "123 Temple Road",
        "vh_phone": "0711234567",
        "vh_province": "WESTERN"
      }
    }
  }'
```

**Python:**
```python
import requests

url = "http://localhost:8000/api/v1/viharas/manage"
headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Content-Type": "application/json"
}
payload = {
    "action": "CREATE",
    "payload": {
        "data": {
            "vh_name": "New Temple",
            "vh_address": "123 Temple Road",
            "vh_phone": "0711234567",
            "vh_province": "WESTERN"
        }
    }
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
```

## Example 2: Search for Bhikku

**cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/advance-search" \
  -H "Content-Type: application/json" \
  -d '{
    "registration_number": "BH",
    "name": "John",
    "entity_type": "bhikku",
    "limit": 50
  }'
```

## Example 3: List All Viharas with Filters

**cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/viharas/manage" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "READ_ALL",
    "payload": {
      "page": 1,
      "limit": 100,
      "province": "WESTERN",
      "search_key": "temple"
    }
  }'
```

---

## Common Pagination Parameters

### Page-Based Pagination
```json
{
  "page": 1,
  "limit": 50
}
```
- `page`: 1-indexed page number
- `limit`: Records per page (default varies, max 200)

### Offset-Based Pagination
```json
{
  "skip": 0,
  "limit": 50
}
```
- `skip`: Number of records to skip
- `limit`: Records to return

---

**Document Version:** 1.0
**Last Updated:** January 27, 2026
**Maintained By:** DBA System Team
