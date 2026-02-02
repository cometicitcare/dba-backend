# Bhikku Management Permission Setup

## Problem
The users `bhikku_admin` and `bhikku_dataentry` cannot access the bhikku management APIs, specifically the endpoint:
```
POST https://api.dbagovlk.com/api/v1/bhikkus-high/manage
```

### Root Cause
The endpoint requires specific permissions that were not assigned to these users:
1. At least one of: `bhikku:create`, `bhikku:update`, or `bhikku:delete`
2. For CREATE action: `CREATE_BHIKKU_HIGH` permission

## Solution
We've created automated setup scripts that will:
1. Create a "Bhikku Department" group
2. Create all necessary permissions for bhikku management
3. Create/update the bhikku_admin and bhikku_dataentry roles
4. Assign appropriate permissions to each role
5. Create or update the users with correct role assignments

## Setup Instructions

### Option 1: Using the Setup Script (Recommended)

Run the automated setup script:

```bash
./setup_bhikku.sh
```

This script will automatically detect if you're using Docker Compose and run the setup accordingly.

### Option 2: Manual Setup via Docker Compose

If you're running the application with Docker Compose:

```bash
# Make sure Docker Compose is running
docker compose up -d

# Run the setup script
docker compose exec api python -m app.utils.setup_bhikku_complete
```

### Option 3: Manual Setup (Local Development)

If you're running locally without Docker:

```bash
# Activate your virtual environment
source .venv/bin/activate  # or your venv path

# Run the setup script
python -m app.utils.setup_bhikku_complete
```

## What Gets Created

### Roles
1. **bhikku_admin** (BHIK_ADM)
   - Role Level: ADMIN
   - Full access to all bhikku management features

2. **bhikku_dataentry** (BHIK_DATA)
   - Role Level: DATA_ENTRY
   - Can create, read, and update bhikku records (no delete)

### Permissions Assigned

**bhikku_admin gets:**
- `bhikku:create` - Create bhikku records
- `bhikku:read` - Read bhikku records
- `bhikku:update` - Update bhikku records
- `bhikku:delete` - Delete bhikku records
- `CREATE_BHIKKU_HIGH` - Create higher ordination records
- `READ_BHIKKU_HIGH` - Read higher ordination records
- `UPDATE_BHIKKU_HIGH` - Update higher ordination records
- `DELETE_BHIKKU_HIGH` - Delete higher ordination records
- `bhikku:manage_id_card` - Manage ID cards
- `bhikku:manage_certificate` - Manage certifications

**bhikku_dataentry gets:**
- `bhikku:create` - Create bhikku records
- `bhikku:read` - Read bhikku records
- `bhikku:update` - Update bhikku records
- `CREATE_BHIKKU_HIGH` - Create higher ordination records
- `READ_BHIKKU_HIGH` - Read higher ordination records
- `UPDATE_BHIKKU_HIGH` - Update higher ordination records
- `bhikku:manage_id_card` - Manage ID cards
- `bhikku:manage_certificate` - Manage certifications

### Users Created

If the users don't exist, they will be created with:

| Username | Password | Role |
|----------|----------|------|
| bhikku_admin | Bhikku@123 | bhikku_admin |
| bhikku_dataentry | Bhikku@123 | bhikku_dataentry |

## Testing the Fix

### 1. Login

```bash
curl -X POST https://api.dbagovlk.com/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -c cookies.txt \
  -d '{
    "ua_username": "bhikku_admin",
    "ua_password": "Bhikku@123"
  }'
```

### 2. Test the Bhikku High Endpoint

Create a test payload file (`test_payload.json`):

```json
{
  "action": "CREATE",
  "payload": {
    "data": {
      "bhr_reqstdate": "2025-11-24",
      "bhr_currstat": "ST01",
      "bhr_parshawaya": "",
      "bhr_livtemple": "VH001",
      "bhr_candidate_regn": "BH2025000001",
      "bhr_cc_code": "CAT02",
      "bhr_samanera_serial_no": "BH2025000001",
      "bhr_higher_ordination_place": "Test Temple",
      "bhr_higher_ordination_date": "2025-10-30",
      "bhr_karmacharya_name": "Test Karmacharya",
      "bhr_upaddhyaya_name": "Test Upaddhyaya",
      "bhr_assumed_name": "Test Name",
      "bhr_residence_higher_ordination_trn": "VH001",
      "bhr_residence_permanent_trn": "VH001",
      "bhr_declaration_residence_address": "Test Address",
      "bhr_tutors_tutor_regn": "BH2025000001",
      "bhr_presiding_bhikshu_regn": "BH2025000001",
      "bhr_declaration_date": "2025-11-01",
      "bhr_remarks": "Test remarks"
    }
  }
}
```

Then make the request:

```bash
curl -X POST https://api.dbagovlk.com/api/v1/bhikkus-high/manage \
  -H 'Content-Type: application/json' \
  -b cookies.txt \
  -d @test_payload.json
```

### 3. Verify Permissions

Check what permissions the user has:

```bash
curl -X GET https://api.dbagovlk.com/api/v1/auth/me/permissions \
  -b cookies.txt
```

## Troubleshooting

### "Permission denied" error
- Make sure you ran the setup script successfully
- Verify the user is logged in (cookies are valid)
- Check that the user has the correct role assigned

### "Role not found" error
- Run the setup script: `./setup_bhikku.sh`
- Verify database connection is working

### Setup script fails
- Ensure DATABASE_URL is correctly set in `.env`
- Make sure the database is running
- For Docker: `docker compose up -d db`

## Files Created

The following utility scripts were created:

1. **`app/utils/setup_bhikku_complete.py`** - Complete setup (recommended)
   - Creates groups, permissions, roles, and users in one go

2. **`app/utils/seed_bhikku_permissions.py`** - Permissions and roles only
   - Creates permissions and assigns them to roles

3. **`app/utils/assign_bhikku_roles.py`** - User setup only
   - Creates users and assigns roles (requires roles to exist)

4. **`setup_bhikku.sh`** - Bash wrapper script
   - Automatically detects environment and runs setup

## Additional Notes

- The setup scripts are **idempotent** - safe to run multiple times
- Existing users/roles/permissions will not be duplicated
- The scripts will update existing records if needed
- All operations are logged to console for transparency

## Support

If you encounter any issues, check:
1. Database connectivity
2. Environment variables in `.env`
3. Docker Compose services are running: `docker compose ps`
4. Application logs: `docker compose logs api`
