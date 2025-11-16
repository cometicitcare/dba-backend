# Example: Using Location-Based Access Control in API Endpoints

This document shows practical examples of how to use the location-based access control system in your API endpoints.

## Example 1: Simple Query with Location Filtering

### Bhikku List Endpoint (Already Implemented)

```python
# app/api/v1/routes/bhikkus.py

@router.get("/", response_model=schemas.BhikkuListResponse)
def list_bhikkus(
    skip: int = 0,
    limit: int = 100,
    search_key: Optional[str] = None,
    province: Optional[str] = None,
    district: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Get paginated list of bhikkus with location-based filtering.

    - MAIN_BRANCH users: See all bhikkus
    - PROVINCE_BRANCH users: See only bhikkus from their province
    - DISTRICT_BRANCH users: See only bhikkus from their district
    """
    # Simply pass current_user to the repository
    bhikkus = bhikku_repo.get_all(
        db=db,
        skip=skip,
        limit=limit,
        search_key=search_key,
        province=province,
        district=district,
        current_user=current_user  # ← Location filtering applied here
    )

    total = bhikku_repo.get_total_count(
        db=db,
        search_key=search_key,
        province=province,
        district=district,
        current_user=current_user  # ← Location filtering applied here
    )

    return {
        "status": "success",
        "message": "Bhikkus retrieved successfully",
        "data": bhikkus,
        "total": total,
        "skip": skip,
        "limit": limit
    }
```

## Example 2: Manual Access Control Check

### Get Single Bhikku with Access Check

```python
# app/api/v1/routes/bhikkus.py

from app.services.location_access_control_service import LocationAccessControlService

@router.get("/{br_id}", response_model=schemas.BhikkuResponse)
def get_bhikku(
    br_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Get a specific bhikku by ID with location-based access control.
    """
    # Get the bhikku record
    bhikku = bhikku_repo.get_by_id(db, br_id)
    if not bhikku:
        raise HTTPException(status_code=404, detail="Bhikku not found")

    # Check if current user can access this record
    can_access = LocationAccessControlService.can_user_access_record(
        db=db,
        user=current_user,
        record_province=bhikku.br_province,
        record_district=bhikku.br_district
    )

    if not can_access:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this bhikku record"
        )

    return {
        "status": "success",
        "message": "Bhikku retrieved successfully",
        "data": bhikku
    }
```

## Example 3: Applying Filter to Custom Query

### Temple (Vihara) List with Location Filtering

```python
# app/api/v1/routes/vihara_data.py

from app.services.location_access_control_service import LocationAccessControlService
from app.models.vihara import ViharaData

@router.get("/", response_model=ViharaListResponse)
def list_viharas(
    skip: int = 0,
    limit: int = 100,
    province: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Get temples with location-based filtering.

    Assumes ViharaData model has:
    - vh_province (province code)
    - vh_district (district code)
    """
    # Start with base query
    query = db.query(ViharaData).filter(ViharaData.vh_is_deleted == False)

    # Apply location-based filtering
    query = LocationAccessControlService.apply_location_filter_to_query(
        query=query,
        db=db,
        user=current_user,
        province_field='vh_province',  # Adjust to your actual field name
        district_field='vh_district'   # Adjust to your actual field name
    )

    # Apply additional filters
    if province:
        query = query.filter(ViharaData.vh_province == province)

    # Execute query
    total = query.count()
    viharas = query.offset(skip).limit(limit).all()

    return {
        "status": "success",
        "data": viharas,
        "total": total,
        "skip": skip,
        "limit": limit
    }
```

## Example 4: Getting User's Accessible Locations

### Get Accessible Provinces for Dropdown

```python
# app/api/v1/routes/locations.py

from app.services.location_access_control_service import LocationAccessControlService

@router.get("/accessible-provinces")
def get_accessible_provinces(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Get list of provinces accessible to the current user.
    Used for populating dropdown filters.
    """
    province_codes = LocationAccessControlService.get_user_province_codes(db, current_user)

    if province_codes is None:
        # User has access to all provinces
        provinces = db.query(Province).filter(Province.cp_is_deleted == False).all()
    else:
        # User has limited access
        provinces = db.query(Province).filter(
            Province.cp_code.in_(province_codes),
            Province.cp_is_deleted == False
        ).all()

    return {
        "status": "success",
        "data": provinces
    }
```

## Example 5: Creating Record with Location Validation

### Create Bhikku with Location Validation

```python
# app/api/v1/routes/bhikkus.py

@router.post("/", response_model=schemas.BhikkuResponse, status_code=201)
def create_bhikku(
    bhikku_data: schemas.BhikkuCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Create a new bhikku record with location validation.
    Users can only create records in their accessible locations.
    """
    # Validate that user can create record in this location
    can_create = LocationAccessControlService.can_user_access_record(
        db=db,
        user=current_user,
        record_province=bhikku_data.br_province,
        record_district=bhikku_data.br_district
    )

    if not can_create:
        raise HTTPException(
            status_code=403,
            detail="You cannot create bhikku records in this location"
        )

    # Create the record
    bhikku = bhikku_service.create_bhikku(db, bhikku_data, current_user.ua_username)

    return {
        "status": "success",
        "message": "Bhikku created successfully",
        "data": bhikku
    }
```

## Example 6: Repository Pattern Implementation

### Generic Repository with Location Support

```python
# app/repositories/base_location_repo.py

from typing import TypeVar, Generic, Type, Optional, List
from sqlalchemy.orm import Session, Query
from app.services.location_access_control_service import LocationAccessControlService
from app.models.user import UserAccount

ModelType = TypeVar("ModelType")

class BaseLocationRepository(Generic[ModelType]):
    """Base repository with location-based access control support"""

    def __init__(
        self,
        model: Type[ModelType],
        province_field: str,
        district_field: str
    ):
        self.model = model
        self.province_field = province_field
        self.district_field = district_field

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        current_user: Optional[UserAccount] = None
    ) -> List[ModelType]:
        """Get all records with location filtering"""
        query = db.query(self.model)

        # Apply location filter if user provided
        if current_user:
            query = LocationAccessControlService.apply_location_filter_to_query(
                query=query,
                db=db,
                user=current_user,
                province_field=self.province_field,
                district_field=self.district_field
            )

        return query.offset(skip).limit(limit).all()

    def can_access(
        self,
        db: Session,
        record: ModelType,
        current_user: UserAccount
    ) -> bool:
        """Check if user can access a specific record"""
        province = getattr(record, self.province_field, None)
        district = getattr(record, self.district_field, None)

        return LocationAccessControlService.can_user_access_record(
            db=db,
            user=current_user,
            record_province=province,
            record_district=district
        )


# Usage Example:
class TempleRepository(BaseLocationRepository[ViharaData]):
    def __init__(self):
        super().__init__(
            model=ViharaData,
            province_field='vh_province',
            district_field='vh_district'
        )

temple_repo = TempleRepository()
```

## Example 7: User Management with Location

### Create User with Location Assignment

```python
# app/api/v1/routes/users.py

@router.post("/", response_model=UserResponse, status_code=201)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
    _: None = Depends(has_permission("user:create")),
):
    """
    Create a new user with location assignment.

    Validates that:
    1. Location type and location IDs are consistent
    2. Referenced location branches exist
    3. Current user has permission to create users in that location
    """
    # The UserCreate schema already validates location field consistency
    # via the _validate_location_fields model validator

    # Create the user (service handles the rest)
    user = user_service.create_user(db, user_data)

    return {
        "status": "success",
        "message": "User created successfully",
        "data": user
    }
```

## Example 8: Dashboard Statistics with Location Filtering

### Get Statistics for User's Location

```python
# app/api/v1/routes/dashboard.py

from app.services.location_access_control_service import LocationAccessControlService

@router.get("/statistics")
def get_dashboard_statistics(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Get dashboard statistics filtered by user's location access.
    """
    # Base queries
    bhikku_query = db.query(Bhikku).filter(Bhikku.br_is_deleted == False)
    temple_query = db.query(ViharaData).filter(ViharaData.vh_is_deleted == False)

    # Apply location filtering
    bhikku_query = LocationAccessControlService.apply_location_filter_to_query(
        query=bhikku_query,
        db=db,
        user=current_user,
        province_field='br_province',
        district_field='br_district'
    )

    temple_query = LocationAccessControlService.apply_location_filter_to_query(
        query=temple_query,
        db=db,
        user=current_user,
        province_field='vh_province',
        district_field='vh_district'
    )

    # Calculate statistics
    total_bhikkus = bhikku_query.count()
    total_temples = temple_query.count()
    active_bhikkus = bhikku_query.filter(Bhikku.br_currstat == 'ACT').count()

    return {
        "status": "success",
        "data": {
            "total_bhikkus": total_bhikkus,
            "total_temples": total_temples,
            "active_bhikkus": active_bhikkus,
            "location_scope": current_user.ua_location_type.value if current_user.ua_location_type else "ALL"
        }
    }
```

## Best Practices

### 1. Always Pass current_user

```python
# ✅ Good
bhikkus = bhikku_repo.get_all(db, current_user=current_user)

# ❌ Bad - No location filtering
bhikkus = bhikku_repo.get_all(db)
```

### 2. Validate Access Before Modification

```python
# ✅ Good
if not LocationAccessControlService.can_user_access_record(db, current_user, record.province, record.district):
    raise HTTPException(status_code=403, detail="Access denied")

# ❌ Bad - No validation
bhikku_service.update_bhikku(db, bhikku_id, update_data)
```

### 3. Use Consistent Field Names

```python
# ✅ Good - Clear and consistent
apply_location_filter_to_query(
    query=query,
    db=db,
    user=current_user,
    province_field='br_province',  # Match your model
    district_field='br_district'   # Match your model
)
```

### 4. Handle None Gracefully

```python
# ✅ Good
if current_user and current_user.ua_location_type:
    # Apply filtering
    query = LocationAccessControlService.apply_location_filter_to_query(...)
else:
    # No filtering (backward compatibility)
    pass
```

## Testing Examples

```python
# tests/test_location_access_control.py

def test_main_branch_user_sees_all_bhikkus(db, main_branch_user):
    """Main branch users should see all bhikkus"""
    bhikkus = bhikku_repo.get_all(db, current_user=main_branch_user)
    assert len(bhikkus) > 0  # Should see all

def test_province_user_sees_only_province_bhikkus(db, province_user):
    """Province branch users should only see their province"""
    bhikkus = bhikku_repo.get_all(db, current_user=province_user)
    for bhikku in bhikkus:
        assert bhikku.br_province in accessible_provinces

def test_district_user_sees_only_district_bhikkus(db, district_user):
    """District branch users should only see their district"""
    bhikkus = bhikku_repo.get_all(db, current_user=district_user)
    for bhikku in bhikkus:
        assert bhikku.br_district == district_user.district_code
```

## Common Patterns

### Pattern 1: Filter Then Count

```python
query = get_base_query(db)
query = apply_location_filter(query, current_user)
query = apply_search_filter(query, search_term)
total = query.count()
results = query.offset(skip).limit(limit).all()
```

### Pattern 2: Check Then Modify

```python
record = get_record(db, record_id)
if not can_access(record, current_user):
    raise HTTPException(403)
update_record(db, record, new_data)
```

### Pattern 3: Get Accessible Options

```python
accessible_codes = get_user_province_codes(db, current_user)
options = get_options_by_codes(db, accessible_codes)
return options
```

---

For more information, see:

- `LOCATION_BASED_ACCESS_CONTROL.md` - Full documentation
- `LOCATION_SETUP_GUIDE.md` - Setup instructions
- `app/services/location_access_control_service.py` - Service implementation
