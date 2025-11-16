# Quick Start Guide: Location-Based Access Control

## Prerequisites

- Database backup created
- Alembic migrations up to date
- Python environment activated

## Step-by-Step Setup

### 1. Apply Database Migration

```bash
# Make sure you're in the project root directory
cd /Users/shanuka/Desktop/Work\ project/dba-backend

# Run the migration
alembic upgrade head
```

This will:

- Create `main_branches` table
- Create `province_branches` table
- Create `district_branches` table
- Add location fields to `user_accounts` table
- Create necessary indexes and foreign keys

### 2. Seed Location Data

```bash
# Run the seed script
python seed_location_branches.py
```

This will populate:

- 3 Main Branches (MB001, MB002, MB003)
- 9 Province Branches (PB001-PB009)
- 25 District Branches (DB001-DB025)

### 3. Verify Setup

#### Check Database Tables

```sql
-- Verify main branches
SELECT mb_id, mb_code, mb_name FROM main_branches WHERE mb_is_deleted = false;

-- Verify province branches
SELECT pb_id, pb_code, pb_name, pb_main_branch_id FROM province_branches WHERE pb_is_deleted = false;

-- Verify district branches
SELECT db_id, db_code, db_name, db_province_branch_id FROM district_branches WHERE db_is_deleted = false;

-- Check user_accounts schema
\d user_accounts
```

#### Test API Endpoints

```bash
# Get all main branches
curl -X GET "http://localhost:8000/api/v1/location-branches/main-branches" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get all province branches
curl -X GET "http://localhost:8000/api/v1/location-branches/province-branches" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get all district branches
curl -X GET "http://localhost:8000/api/v1/location-branches/district-branches" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Create Users with Location Access

#### Example: Create Main Branch User

```json
POST /api/v1/users
{
  "ua_username": "main_admin",
  "ua_email": "main@example.com",
  "ua_password": "SecurePass123!",
  "confirmPassword": "SecurePass123!",
  "ua_first_name": "Main",
  "ua_last_name": "Admin",
  "ro_role_id": "ADMIN",
  "ua_location_type": "MAIN_BRANCH",
  "ua_main_branch_id": 1
}
```

#### Example: Create Province Branch User

```json
POST /api/v1/users
{
  "ua_username": "province_admin",
  "ua_email": "province@example.com",
  "ua_password": "SecurePass123!",
  "confirmPassword": "SecurePass123!",
  "ua_first_name": "Province",
  "ua_last_name": "Admin",
  "ro_role_id": "ADMIN",
  "ua_location_type": "PROVINCE_BRANCH",
  "ua_province_branch_id": 1
}
```

#### Example: Create District Branch User

```json
POST /api/v1/users
{
  "ua_username": "district_admin",
  "ua_email": "district@example.com",
  "ua_password": "SecurePass123!",
  "confirmPassword": "SecurePass123!",
  "ua_first_name": "District",
  "ua_last_name": "Admin",
  "ro_role_id": "ADMIN",
  "ua_location_type": "DISTRICT_BRANCH",
  "ua_district_branch_id": 1
}
```

### 5. Test Access Control

#### Test 1: Main Branch User (Full Access)

```bash
# Login as main branch user
# Make request to get all bhikkus
# Should see ALL bhikku records regardless of location
```

#### Test 2: Province Branch User (Province-Limited)

```bash
# Login as province branch user (e.g., Western Province)
# Make request to get all bhikkus
# Should only see bhikkus from Western Province
```

#### Test 3: District Branch User (District-Limited)

```bash
# Login as district branch user (e.g., Colombo District)
# Make request to get all bhikkus
# Should only see bhikkus from Colombo District
```

## Common Issues and Solutions

### Issue: Migration Fails

```bash
# Check current migration status
alembic current

# View pending migrations
alembic heads

# If there are conflicts, resolve them manually or:
alembic downgrade -1
alembic upgrade head
```

### Issue: Seed Script Fails

**Problem**: Foreign key constraint errors
**Solution**: Ensure migration completed successfully before running seed script

**Problem**: Duplicate code errors
**Solution**: Location branches already seeded. Clear tables if re-seeding is needed:

```sql
DELETE FROM district_branches;
DELETE FROM province_branches;
DELETE FROM main_branches;
```

### Issue: User Creation Validation Errors

**Problem**: "Main branch ID is required for MAIN_BRANCH type users"
**Solution**: Ensure location fields match the location type:

- MAIN_BRANCH → requires `ua_main_branch_id`
- PROVINCE_BRANCH → requires `ua_province_branch_id`
- DISTRICT_BRANCH → requires `ua_district_branch_id`

### Issue: Users See No Data

**Problem**: User has location restriction but no data matches their location
**Solution**:

1. Check bhikku records have correct province/district codes
2. Verify user's location assignment is correct
3. Check that location branch province/district codes match actual data

## Updating Existing Users

If you have existing users that need location assignments:

```sql
-- Update user to be a main branch user
UPDATE user_accounts
SET ua_location_type = 'MAIN_BRANCH',
    ua_main_branch_id = 1
WHERE ua_username = 'existing_user';

-- Update user to be a province branch user
UPDATE user_accounts
SET ua_location_type = 'PROVINCE_BRANCH',
    ua_province_branch_id = 1
WHERE ua_username = 'existing_user';

-- Update user to be a district branch user
UPDATE user_accounts
SET ua_location_type = 'DISTRICT_BRANCH',
    ua_district_branch_id = 1
WHERE ua_username = 'existing_user';
```

## Rollback (if needed)

If you need to rollback the changes:

```bash
# Rollback the migration
alembic downgrade -1

# This will:
# - Drop location columns from user_accounts
# - Drop district_branches table
# - Drop province_branches table
# - Drop main_branches table
# - Drop the ENUM type
```

## Next Steps

1. **Add Permissions**: Create and assign `location:read`, `location:create` permissions
2. **Extend Filtering**: Apply location filtering to other entities (temples, certificates, etc.)
3. **Admin UI**: Build interface for managing location assignments
4. **Reporting**: Create location-based reports and dashboards
5. **Audit**: Enable audit logging for location changes

## Support

For detailed documentation, see: `LOCATION_BASED_ACCESS_CONTROL.md`

For questions or issues:

- Check the main documentation
- Review the code in `app/services/location_access_control_service.py`
- Examine the migration file: `alembic/versions/20251116000001_add_location_based_access_control.py`
