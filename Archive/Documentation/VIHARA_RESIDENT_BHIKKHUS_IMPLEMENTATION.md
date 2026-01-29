# Vihara Resident Bhikkhus Implementation Summary

## Overview
Added support for storing resident bhikkhus data in the vihara data create endpoint. The resident bhikkhus are stored in a separate `resident_bhikkhu` table with a foreign key relationship to the vihara record.

## Database Structure

### Table: `resident_bhikkhu`
The table already exists in the database with the following structure:

```sql
CREATE TABLE resident_bhikkhu (
    id SERIAL PRIMARY KEY,
    vh_id INTEGER NOT NULL REFERENCES vihaddata(vh_id) ON DELETE CASCADE,
    serial_number INTEGER NOT NULL,
    bhikkhu_name VARCHAR(200),
    registration_number VARCHAR(100),
    occupation_education VARCHAR(500),
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Changes Made

### 1. Schema Updates (`app/schemas/resident_bhikkhu.py`)
Added camelCase field aliases to support the frontend JSON format:

```python
class ResidentBhikkhuBase(BaseModel):
    serial_number: int = Field(ge=1, alias="serialNumber")
    bhikkhu_name: Optional[str] = Field(default=None, max_length=200, alias="bhikkhuName")
    registration_number: Optional[str] = Field(default=None, max_length=100, alias="registrationNumber")
    occupation_education: Optional[str] = Field(default=None, max_length=500, alias="occupationEducation")
    
    model_config = ConfigDict(populate_by_name=True)
```

This allows the endpoint to accept both snake_case and camelCase field names.

### 2. Vihara Payload Schema (`app/schemas/vihara.py`)
Added `resident_bhikkhus` field to `ViharaCreatePayload`:

```python
class ViharaCreatePayload(BaseModel):
    # ... other fields ...
    
    temple_owned_land: List[ViharaLandCreate] = Field(default_factory=list)
    
    land_info_certified: Optional[bool] = None
    
    resident_bhikkhus: List[ResidentBhikkhuCreate] = Field(default_factory=list)
    
    resident_bhikkhus_certified: Optional[bool] = None
    
    # ... other fields ...
```

### 3. Service Layer (`app/services/vihara_service.py`)
Updated the `create_vihara` method to include resident_bhikkhus in the payload conversion:

```python
if isinstance(payload, ViharaCreatePayload):
    payload_dict = {
        # ... other fields ...
        "resident_bhikkhus": [bhikkhu.model_dump(by_alias=False) for bhikkhu in payload.resident_bhikkhus],
        "vh_resident_bhikkhus_certified": payload.resident_bhikkhus_certified,
        # ... other fields ...
    }
```

### 4. Repository Layer (`app/repositories/vihara_repo.py`)
The repository already had support for creating resident bhikkhu records:

```python
# Create related resident bhikkhu records
if resident_bhikkhus_data:
    for bhikkhu_data in resident_bhikkhus_data:
        if isinstance(bhikkhu_data, dict):
            bhikkhu_data.pop("id", None)  # Remove id if present
            resident_bhikkhu = ResidentBhikkhu(vh_id=vihara.vh_id, **bhikkhu_data)
            db.add(resident_bhikkhu)
```

## API Usage

### Endpoint
`POST /api/v1/vihara-data/manage`

### Request Format
```json
{
  "action": "CREATE",
  "payload": {
    "data": {
      "temple_name": "string",
      "temple_address": "string",
      "telephone_number": "string",
      "whatsapp_number": "string",
      "email_address": "string",
      "province": "string",
      "district": "string",
      "divisional_secretariat": "string",
      "pradeshya_sabha": "string",
      "grama_niladhari_division": "string",
      "nikaya": "string",
      "parshawaya": "string",
      "viharadhipathi_name": "string",
      "period_established": "string",
      "buildings_description": "string",
      "dayaka_families_count": "string",
      "kulangana_committee": "string",
      "dayaka_sabha": "string",
      "temple_working_committee": "string",
      "other_associations": "string",
      
      "temple_owned_land": [
        {
          "serialNumber": 1,
          "landName": "string",
          "village": "string",
          "district": "string",
          "extent": "string",
          "cultivationDescription": "string",
          "ownershipNature": "string",
          "deedNumber": "string",
          "titleRegistrationNumber": "string",
          "taxDetails": "string",
          "landOccupants": "string"
        }
      ],
      
      "land_info_certified": true,
      
      "resident_bhikkhus": [
        {
          "serialNumber": 1,
          "bhikkhuName": "Ven. Chief Monk",
          "registrationNumber": "REG001",
          "occupationEducation": "Chief Monk, BA in Buddhist Studies"
        },
        {
          "serialNumber": 2,
          "bhikkhuName": "Ven. Assistant Monk",
          "registrationNumber": "REG002",
          "occupationEducation": "Teacher"
        }
      ],
      
      "resident_bhikkhus_certified": true,
      "inspection_report": "string",
      "inspection_code": "string",
      "grama_niladhari_division_ownership": "string",
      
      "sanghika_donation_deed": true,
      "government_donation_deed": false,
      "government_donation_deed_in_progress": false,
      "authority_consent_attached": true,
      "recommend_new_center": false,
      "recommend_registered_temple": true,
      
      "annex2_recommend_construction": false,
      "annex2_land_ownership_docs": true,
      "annex2_chief_incumbent_letter": true,
      "annex2_coordinator_recommendation": true,
      "annex2_divisional_secretary_recommendation": true,
      "annex2_approval_construction": false,
      "annex2_referral_resubmission": false
    }
  }
}
```

## Field Mapping

### Resident Bhikkhu Fields
| Frontend (camelCase) | Backend (snake_case) | Type | Required | Description |
|---------------------|---------------------|------|----------|-------------|
| serialNumber | serial_number | number | Yes | Serial number of the resident bhikkhu |
| bhikkhuName | bhikkhu_name | string | No | Name of the bhikkhu |
| registrationNumber | registration_number | string | No | Registration number |
| occupationEducation | occupation_education | string | No | Occupation and education details |

## Testing

A test script has been created: `test_vihara_resident_bhikkhus.py`

To run the test:
```bash
python test_vihara_resident_bhikkhus.py
```

**Note:** Update the credentials in the `get_auth_token()` function before running the test.

## Key Points

1. ✅ **Database table exists**: The `resident_bhikkhu` table was already created
2. ✅ **Model exists**: The `ResidentBhikkhu` model was already defined
3. ✅ **Repository support exists**: The repository already handles resident bhikkhu creation
4. ✅ **Schema updated**: Added camelCase aliases for frontend compatibility
5. ✅ **Payload schema updated**: Added `resident_bhikkhus` field to `ViharaCreatePayload`
6. ✅ **Service updated**: Service now includes resident_bhikkhus in payload conversion
7. ✅ **No other endpoints touched**: Only vihara-related code was modified

## No Breaking Changes

- Existing endpoints remain unchanged
- Other tables (arama, devala, etc.) are not affected
- The `resident_bhikkhus` field is optional (empty array by default)
- Backward compatible with existing vihara creation requests

## Related Files Modified

1. `/app/schemas/resident_bhikkhu.py` - Added camelCase field aliases
2. `/app/schemas/vihara.py` - Added resident_bhikkhus field to ViharaCreatePayload
3. `/app/services/vihara_service.py` - Added resident_bhikkhus to payload conversion
4. `/test_vihara_resident_bhikkhus.py` - Created test script (new file)

## Verification Steps

1. Start the server: `uvicorn app.main:app --reload`
2. Run the test script: `python test_vihara_resident_bhikkhus.py`
3. Check database for resident_bhikkhu records after successful creation
4. Verify the relationship by querying vihara with its resident bhikkhus
