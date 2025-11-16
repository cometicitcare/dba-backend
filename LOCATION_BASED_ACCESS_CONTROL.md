# Location-Based Access Control Implementation

This document describes the location-based access control feature that has been added to the DBA Backend system.

## Overview

The system now supports hierarchical location-based access control for users, allowing fine-grained data access restrictions based on organizational structure.

## Location Hierarchy

The system implements a 3-tier location hierarchy:

```
Main Branches (3)
    ├── Province Branches (9 total, ~3 per main branch)
    │   └── District Branches (25 total, distributed across province branches)
```

### Organizational Structure

1. **Main Branch Level** (3 branches)

   - Central Region
   - Southern Region
   - Northern Region

2. **Province Branch Level** (9 branches)

   - Distributed across the 3 main branches
   - Aligned with Sri Lanka's 9 provinces

3. **District Branch Level** (25 branches)
   - Distributed across the 9 province branches
   - Aligned with Sri Lanka's 25 administrative districts

## User Location Types

Users are assigned one of three location types:

### 1. MAIN_BRANCH

- **Access**: Can see ALL data from all branches, provinces, and districts
- **No restrictions** on bhikku records or location-based data
- **Required fields**: `ua_main_branch_id`

### 2. PROVINCE_BRANCH

- **Access**: Can only see data from their assigned province
- **Cannot see**: Data from other provinces or districts outside their province
- **Required fields**: `ua_province_branch_id`

### 3. DISTRICT_BRANCH

- **Access**: Can only see data from their assigned district
- **Cannot see**: Data from other districts or province-wide data outside their district
- **Required fields**: `ua_district_branch_id`

## Database Schema

### New Tables

#### `main_branches`

```sql
- mb_id (PK)
- mb_code (unique)
- mb_name
- mb_description
- Standard audit fields (created_at, updated_at, is_deleted, etc.)
```

#### `province_branches`

```sql
- pb_id (PK)
- pb_code (unique)
- pb_name
- pb_description
- pb_main_branch_id (FK to main_branches)
- pb_province_code (links to cmm_province.cp_code)
- Standard audit fields
```

#### `district_branches`

```sql
- db_id (PK)
- db_code (unique)
- db_name
- db_description
- db_province_branch_id (FK to province_branches)
- db_district_code (links to cmm_districtdata.dd_dcode)
- Standard audit fields
```

### Updated Tables

#### `user_accounts`

New columns added:

```sql
- ua_location_type (ENUM: MAIN_BRANCH, PROVINCE_BRANCH, DISTRICT_BRANCH)
- ua_main_branch_id (FK to main_branches.mb_id)
- ua_province_branch_id (FK to province_branches.pb_id)
- ua_district_branch_id (FK to district_branches.db_id)
```

## API Endpoints

### Location Branch Management

#### Main Branches

- `GET /api/v1/location-branches/main-branches` - List all main branches
- `GET /api/v1/location-branches/main-branches/{mb_id}` - Get specific main branch
- `POST /api/v1/location-branches/main-branches` - Create main branch

#### Province Branches

- `GET /api/v1/location-branches/province-branches` - List all province branches
- `GET /api/v1/location-branches/province-branches/{pb_id}` - Get specific province branch
- `POST /api/v1/location-branches/province-branches` - Create province branch

#### District Branches

- `GET /api/v1/location-branches/district-branches` - List all district branches
- `GET /api/v1/location-branches/district-branches/{db_id}` - Get specific district branch
- `POST /api/v1/location-branches/district-branches` - Create district branch

### User Management

When creating or updating users, include location fields:

```json
{
  "ua_username": "john.doe",
  "ua_email": "john@example.com",
  "ua_password": "SecurePass123!",
  "confirmPassword": "SecurePass123!",
  "ro_role_id": "ROLE_001",
  "ua_location_type": "PROVINCE_BRANCH",
  "ua_province_branch_id": 1
}
```

## Access Control Service

### `LocationAccessControlService`

This service provides methods to enforce location-based access control:

#### Key Methods

1. **`get_user_province_codes(db, user)`**

   - Returns list of province codes accessible to the user
   - Returns `None` for MAIN_BRANCH users (access to all)
   - Returns specific province codes for PROVINCE_BRANCH and DISTRICT_BRANCH users

2. **`get_user_district_codes(db, user)`**

   - Returns list of district codes accessible to the user
   - Returns `None` for MAIN_BRANCH users (access to all)
   - Returns specific district codes for PROVINCE_BRANCH users (all districts in their province)
   - Returns single district code for DISTRICT_BRANCH users

3. **`apply_location_filter_to_query(query, db, user, province_field, district_field)`**

   - Applies location-based filtering to SQLAlchemy queries
   - Automatically restricts query results based on user's location type and assignment

4. **`can_user_access_record(db, user, record_province, record_district)`**
   - Checks if a user can access a specific record
   - Returns boolean indicating access permission

## Usage Examples

### Applying Location Filter to Bhikku Queries

The `BhikkuRepository.get_all()` method has been updated to accept a `current_user` parameter:

```python
from app.repositories.bhikku_repo import bhikku_repo
from app.models.user import UserAccount

# In your endpoint
bhikkus = bhikku_repo.get_all(
    db=db,
    skip=0,
    limit=100,
    current_user=current_user  # Pass the authenticated user
)
```

The repository automatically applies location filtering based on the user's access level.

### Checking Individual Record Access

```python
from app.services.location_access_control_service import LocationAccessControlService

# Check if user can access a specific bhikku record
can_access = LocationAccessControlService.can_user_access_record(
    db=db,
    user=current_user,
    record_province=bhikku.br_province,
    record_district=bhikku.br_district
)

if not can_access:
    raise HTTPException(status_code=403, detail="Access denied")
```

## Setup and Migration

### 1. Run Database Migration

```bash
# Apply the migration
alembic upgrade head
```

This creates the new tables and adds location columns to `user_accounts`.

### 2. Seed Location Data

```bash
# Run the seed script
python seed_location_branches.py
```

This populates:

- 3 Main Branches
- 9 Province Branches
- 25 District Branches

### 3. Update Existing Users (Optional)

Existing users without location assignments will have `ua_location_type = NULL`, which means they have unrestricted access (backward compatible).

To assign locations to existing users:

```sql
-- Example: Assign a user to a province branch
UPDATE user_accounts
SET ua_location_type = 'PROVINCE_BRANCH',
    ua_province_branch_id = 1
WHERE ua_user_id = 'USER_001';
```

## Permissions

The location branch management endpoints require the following permissions:

- `location:read` - View location branches
- `location:create` - Create new location branches
- `location:update` - Update location branches (to be implemented)
- `location:delete` - Delete location branches (to be implemented)

## Business Rules Validation

### User Creation

When creating a user with a location type:

1. **MAIN_BRANCH users**

   - MUST have `ua_main_branch_id`
   - MUST NOT have `ua_province_branch_id` or `ua_district_branch_id`

2. **PROVINCE_BRANCH users**

   - MUST have `ua_province_branch_id`
   - MUST NOT have `ua_district_branch_id`
   - System auto-populates `ua_main_branch_id` from province branch

3. **DISTRICT_BRANCH users**
   - MUST have `ua_district_branch_id`
   - System auto-populates `ua_province_branch_id` and `ua_main_branch_id` from district branch

### Data Access

- Users can only access bhikku records matching their location constraints
- Province codes in bhikku records (`br_province`) are matched against user's accessible provinces
- District codes in bhikku records (`br_district`) are matched against user's accessible districts
- Filters are applied automatically in repository layer

## Backward Compatibility

- Existing users with `ua_location_type = NULL` retain full access (no restrictions)
- Existing API endpoints continue to work without modification
- Location filtering is opt-in via the `current_user` parameter

## Future Enhancements

1. **Extend to Other Entities**

   - Apply location filtering to temples (vihara)
   - Apply to certificates and certifications
   - Apply to user management (users can only manage users in their location)

2. **Additional Features**

   - Location-based reporting
   - Location transfer workflows
   - Multi-location user support
   - Location hierarchy visualization

3. **Administration**
   - UI for managing location branches
   - Bulk user location assignment
   - Location audit trail

## Testing

### Test Scenarios

1. **MAIN_BRANCH User**
   - Should see all bhikku records regardless of province/district
2. **PROVINCE_BRANCH User**
   - Should only see bhikku records from their province
   - Should not see records from other provinces
3. **DISTRICT_BRANCH User**
   - Should only see bhikku records from their district
   - Should not see records from other districts in same province

### Sample Test Data

```python
# Create test users with different access levels
main_user = create_user(
    username="main_admin",
    location_type="MAIN_BRANCH",
    main_branch_id=1
)

province_user = create_user(
    username="province_admin",
    location_type="PROVINCE_BRANCH",
    province_branch_id=1  # Western Province
)

district_user = create_user(
    username="district_admin",
    location_type="DISTRICT_BRANCH",
    district_branch_id=1  # Colombo District
)
```

## Troubleshooting

### Issue: Users see no data after migration

**Solution**: Check that the user has a location assignment. Users with no location type will need to be assigned one.

### Issue: Province/District codes not matching

**Solution**: Verify that `pb_province_code` and `db_district_code` values match the codes in `cmm_province` and `cmm_districtdata` tables.

### Issue: Foreign key constraint errors

**Solution**: Ensure the migration ran successfully and all relationships are properly created.

## Support

For questions or issues related to location-based access control, please contact the development team or refer to the main project documentation.
