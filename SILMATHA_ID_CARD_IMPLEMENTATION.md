# Silmatha ID Card Implementation

Complete implementation of Silmatha ID Card management system matching the Bhikku ID Card structure.

## Database Table: `silmatha_id_card`

Created with **35 columns** including:

### Core Fields

- `sic_id` - Primary key
- `sic_form_no` - Auto-generated unique form number (Format: SIC2025000001)
- `sic_sil_regn` - Foreign key to silmatha_regist table

### Personal Information

- `sic_divisional_secretariat`, `sic_district`
- `sic_full_silmatha_name` - Full name (Required)
- `sic_title_post` - Title/Position
- `sic_lay_name_full` - Lay name (Required)
- `sic_dob` - Date of birth (Required)
- `sic_birth_place`
- `sic_national_id`

### Ordination Details

- `sic_robing_date`, `sic_robing_place`
- `sic_robing_nikaya`, `sic_robing_parshawaya`
- `sic_samaneri_reg_no` - Samaneri registration number
- `sic_dasa_sil_mata_reg_no` - Dasa Sil Mata registration number
- `sic_higher_ord_date`, `sic_higher_ord_name`
- `sic_perm_residence`

### Stay History (JSON)

- `sic_stay_history` - Array of temple stay records
  ```json
  [
    {
      "temple_name": "Temple Name",
      "temple_address": "Address",
      "from_date": "2020-01-15",
      "to_date": "2022-03-20"
    }
  ]
  ```

### File Uploads

- `sic_left_thumbprint_url` - Left thumbprint image URL
- `sic_applicant_photo_url` - Applicant photo URL

### Workflow Management

- `sic_workflow_status` - Current status (PENDING, APPROVED, REJECTED, PRINTING_COMPLETE, COMPLETED)
- `sic_approved_by`, `sic_approved_at`
- `sic_rejection_reason`, `sic_rejected_by`, `sic_rejected_at`
- `sic_printed_by`, `sic_printed_at`

### Audit Fields

- `sic_created_by`, `sic_created_at`
- `sic_updated_by`, `sic_updated_at`

## API Endpoints

### Base URL: `/api/v1/silmatha-id-card`

### 1. Unified Management Endpoint

**POST** `/manage`

Supports all CRUD operations and workflow actions via `action` parameter:

#### Actions:

- **CREATE** - Create new ID card with optional file uploads
- **READ_ONE** - Get by `sic_id` or `sic_sil_regn`
- **READ_ALL** - List all with filtering and pagination
- **UPDATE** - Update existing card with optional file uploads
- **DELETE** - Delete a card
- **APPROVE** - Approve a pending card
- **REJECT** - Reject a card (requires `rejection_reason`)
- **MARK_PRINTED** - Mark as printing complete

#### Example: CREATE with Files (Postman)

```
Method: POST
URL: {{base_url}}/api/v1/silmatha-id-card/manage
Body: form-data

Fields:
- action: CREATE
- sic_sil_regn: SIL2025000001
- sic_full_silmatha_name: Sister Dharmapriya
- sic_lay_name_full: K.M. Nirmala
- sic_dob: 1988-08-22
- sic_district: Kandy
- sic_national_id: 888242345V
- left_thumbprint: (file) - Select image file
- applicant_photo: (file) - Select image file
- sic_stay_history: [{"temple_name":"Dambulla Viharaya","temple_address":"Dambulla","from_date":"2010-05-15","to_date":null}]
```

#### Example: READ_ALL with Filters

```
Method: POST
URL: {{base_url}}/api/v1/silmatha-id-card/manage
Body: form-data

Fields:
- action: READ_ALL
- skip: 0
- limit: 50
- workflow_status: PENDING
- search_key: Dharma
```

#### Example: UPDATE with Files

```
Method: POST
URL: {{base_url}}/api/v1/silmatha-id-card/manage
Body: form-data

Fields:
- action: UPDATE
- sic_id: 1
- sic_district: Matale
- sic_national_id: 888242345V
- left_thumbprint: (file) - New thumbprint if updating
- applicant_photo: (file) - New photo if updating
```

### 2. Workflow Endpoint

**POST** `/workflow`

Handle workflow actions with JSON body:

```json
{
  "action": "APPROVE",
  "sic_form_no": "SIC2025000001"
}
```

Available actions:

- `APPROVE` - Approve the ID card
- `REJECT` - Reject (requires `rejection_reason`)
- `MARK_PRINTED` - Mark as printing complete

### 3. File Upload Endpoints

**POST** `/{sic_id}/upload-thumbprint`

- Upload left thumbprint image separately
- Body: multipart/form-data with `file` field

**POST** `/{sic_id}/upload-photo`

- Upload applicant photo separately
- Body: multipart/form-data with `file` field

### 4. Retrieval Endpoints

**GET** `/{sic_id}`

- Get ID card by ID

**GET** `/by-regn/{sil_regn}`

- Get ID card by Silmatha registration number

## Features

### 1. Auto-Generated Form Numbers

- Format: `SIC{YEAR}{SEQUENCE}`
- Example: SIC2025000001, SIC2025000002
- Automatically increments per year

### 2. Foreign Key Validation

- Validates that `sic_sil_regn` exists in `silmatha_regist` table
- Prevents orphaned ID card records
- One ID card per Silmatha registration

### 3. File Upload Management

- Supports thumbprint and photo uploads
- Files stored via FileStorage service
- Can upload during CREATE or UPDATE
- Separate endpoints available for file-only uploads

### 4. Workflow Status Management

```
PENDING → APPROVED → PRINTING_COMPLETE → COMPLETED
           ↓
        REJECTED
```

### 5. Stay History (JSON)

- Array of temple residence records
- Supports open-ended stays (to_date = null)
- Pydantic validation via `StayHistoryItem` schema

### 6. Search & Filtering

- Search by: name, registration number, form number, national ID, lay name
- Filter by: workflow status
- Pagination support (skip/limit)

## Implementation Files

### 1. Model

- `app/models/silmatha_id_card.py`
- SQLAlchemy ORM model with all fields
- Foreign key relationship to `silmatha_regist`

### 2. Schemas

- `app/schemas/silmatha_id_card.py`
- Pydantic validation schemas
- Enums: `SilmathaIDCardAction`, `SilmathaIDCardWorkflowStatus`, `SilmathaIDCardWorkflowActionType`
- Schemas: `Create`, `Update`, `Response`, `ManageResponse`, `WorkflowRequest`, `WorkflowResponse`
- `StayHistoryItem` for JSON validation

### 3. Repository

- `app/repositories/silmatha_id_card_repo.py`
- Database operations (CRUD)
- Form number generation
- Workflow state updates
- File URL updates

### 4. Service

- `app/services/silmatha_id_card_service.py`
- Business logic layer
- Validation (registration exists, no duplicate ID card)
- File upload orchestration
- Workflow validations

### 5. Routes

- `app/api/v1/routes/silmatha_id_card.py`
- FastAPI endpoints
- Multipart form-data handling
- Authentication & authorization

### 6. Migration

- `alembic/versions/20251117000003_enhance_silmatha_id_card_table.py`
- Creates `silmatha_id_card` table with all 35 columns
- Indexes on: `sic_id`, `sic_form_no` (unique), `sic_sil_regn` (unique)
- Foreign key constraint to `silmatha_regist`

## Usage Examples

### Create ID Card with Files (Python)

```python
import requests

url = "http://localhost:8000/api/v1/silmatha-id-card/manage"
headers = {"Authorization": "Bearer YOUR_TOKEN"}

files = {
    'left_thumbprint': open('thumbprint.jpg', 'rb'),
    'applicant_photo': open('photo.jpg', 'rb')
}

data = {
    'action': 'CREATE',
    'sic_sil_regn': 'SIL2025000001',
    'sic_full_silmatha_name': 'Sister Dharmapriya',
    'sic_lay_name_full': 'K.M. Nirmala',
    'sic_dob': '1988-08-22',
    'sic_district': 'Kandy',
    'sic_stay_history': '[{"temple_name":"Dambulla Viharaya","temple_address":"Dambulla","from_date":"2010-05-15","to_date":null}]'
}

response = requests.post(url, headers=headers, files=files, data=data)
print(response.json())
```

### Approve ID Card

```python
url = "http://localhost:8000/api/v1/silmatha-id-card/workflow"
headers = {"Authorization": "Bearer YOUR_TOKEN"}

payload = {
    "action": "APPROVE",
    "sic_form_no": "SIC2025000001"
}

response = requests.post(url, headers=headers, json=payload)
print(response.json())
```

### Search ID Cards

```python
url = "http://localhost:8000/api/v1/silmatha-id-card/manage"
headers = {"Authorization": "Bearer YOUR_TOKEN"}

data = {
    'action': 'READ_ALL',
    'workflow_status': 'PENDING',
    'search_key': 'Dharma',
    'skip': 0,
    'limit': 20
}

response = requests.post(url, headers=headers, data=data)
result = response.json()
print(f"Found {result['total']} ID cards")
for card in result['data']:
    print(f"- {card['sic_form_no']}: {card['sic_full_silmatha_name']}")
```

## Workflow Status Flow

1. **CREATE** → Status: `PENDING`

   - ID card created with basic info
   - Files can be uploaded during creation or later

2. **APPROVE** → Status: `APPROVED`

   - Sets `sic_approved_by` and `sic_approved_at`
   - Clears any previous rejection data

3. **REJECT** → Status: `REJECTED`

   - Requires `rejection_reason`
   - Sets `sic_rejected_by` and `sic_rejected_at`
   - Clears any previous approval data

4. **MARK_PRINTED** → Status: `PRINTING_COMPLETE`
   - Can only be done if status is `APPROVED`
   - Sets `sic_printed_by` and `sic_printed_at`

## Validation Rules

1. **Create ID Card**

   - `sic_sil_regn` must exist in `silmatha_regist` table
   - Only one ID card allowed per registration number
   - Required fields: `sic_full_silmatha_name`, `sic_lay_name_full`, `sic_dob`

2. **Approve ID Card**

   - Cannot approve an already approved card

3. **Mark Printed**

   - Card must be in `APPROVED` status first

4. **File Uploads**
   - Handled by FileStorage service
   - Stored in `silmatha_id_cards/thumbprints/` and `silmatha_id_cards/photos/`

## Comparison with Bhikku ID Card

Both implementations are **identical** in structure:

| Feature                    | Bhikku ID Card         | Silmatha ID Card    |
| -------------------------- | ---------------------- | ------------------- |
| Form Number Format         | FORM-{YEAR}-{SEQUENCE} | SIC{YEAR}{SEQUENCE} |
| Total Columns              | 35                     | 35                  |
| File Uploads               | Thumbprint + Photo     | Thumbprint + Photo  |
| Workflow States            | 5 states               | 5 states            |
| Stay History JSON          | ✅                     | ✅                  |
| Foreign Key                | bhikku_regist          | silmatha_regist     |
| Search & Filter            | ✅                     | ✅                  |
| Unified /manage Endpoint   | ✅                     | ✅                  |
| Separate Workflow Endpoint | ✅                     | ✅                  |

## Router Registration

Added to `app/api/v1/router.py`:

```python
api_router.include_router(
    silmatha_id_card.router,
    prefix="/silmatha-id-card",
    tags=["🕉️ Silmatha Management"]
)
```

## Database Migration Applied

Migration `20251117000003` successfully created the table with:

- 35 columns
- 3 indexes (sic_id, sic_form_no unique, sic_sil_regn unique)
- 1 foreign key constraint to silmatha_regist

## Summary

✅ Complete CRUD implementation
✅ File upload support (thumbprint + photo)
✅ Workflow management (5 states)
✅ Form number auto-generation
✅ Foreign key validation
✅ Stay history JSON support
✅ Search & filtering
✅ Pagination
✅ Database migration applied
✅ Router registered
✅ Matches bhikku_id_card structure exactly
