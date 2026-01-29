# Vihara Foreign Key Constraints - Implementation Guide

## Overview

Foreign key constraints have been added to the `vihaddata` table to ensure data integrity with reference tables. This ensures that only valid codes from the reference tables can be used.

## Foreign Key Mapping

| Vihara Field                | References Table   | Reference Column | On Delete | Required |
| --------------------------- | ------------------ | ---------------- | --------- | -------- |
| `vh_nikaya`                 | `cmm_nikayadata`   | `nk_nkn`         | SET NULL  | No       |
| `vh_province`               | `cmm_province`     | `cp_code`        | SET NULL  | No       |
| `vh_district`               | `cmm_districtdata` | `dd_dcode`       | SET NULL  | No       |
| `vh_divisional_secretariat` | `cmm_dvsec`        | `dv_dvcode`      | SET NULL  | No       |
| `vh_gndiv`                  | `cmm_gndata`       | `gn_gnc`         | RESTRICT  | **Yes**  |

**Note:** `vh_pradeshya_sabha` does NOT have a foreign key as there is no reference table for it.

## Valid Code Examples

### Provinces (use codes, not names)

```
WP - Western Province
CP - Central Province
SP - Southern Province
NP - Northern Province
EP - Eastern Province
NWP - North Western Province
NC - North Central Province
UV - Uva Province
SG - Sabaragamuwa Province
```

### Districts (use codes, not names)

```
DC001 - Colombo (කොළඹ)
DC002 - Kandy (මහනුවර)
DC003 - Gampaha (ගම්පහ)
DC007 - Galle (ගාල්ල)
DC008 - Matara (මාතර)
etc.
```

### Nikaya (use codes, not names)

```
NK001 - සියම් නිකාය (Siam Nikaya)
NK002 - අමරපුර නිකාය (Amarapura Nikaya)
NK003 - රාමඤ්ඤ නිකාය (Ramanna Nikaya)
```

### Divisional Secretariats (use codes)

```
DV001 - කොළඹ (Colombo)
DV002 - ශ්‍රී ජයවර්ධනපුර කෝට්ටේ (Sri Jayawardenepura)
DV003 - හෝමාගම (Homagama)
etc.
```

### Grama Niladhari Divisions (required - use full codes)

```
1-1-03-005 - සම්මන්ත්‍රණපුර / Sammanthranapura
1-1-03-010 - මට්ටක්කුලිය / Mattakkuliya
1-2-24-070 - (Example GN division)
2-1-03-170 - (Example GN division)
etc.
```

## Impact on API

### ✅ NO CHANGE to Payload Format

The payload format remains **exactly the same** - you can still use camelCase or snake_case.

### Example Correct Payload (camelCase)

```json
{
  "action": "CREATE",
  "payload": {
    "data": {
      "temple_name": "ශ්‍රී සුදර්ශනාරාම විහාරය",
      "province": "WP",
      "district": "DC003",
      "divisional_secretariat": "DV015",
      "grama_niladhari_division": "1-2-24-070",
      "nikaya": "NK001",
      "pradeshya_sabha": "Gampaha Municipal Council",
      ...other fields
    }
  }
}
```

### ❌ Invalid - Will Cause Constraint Violation

```json
{
  "province": "Western Province", // ❌ Use "WP" instead
  "district": "Gampaha", // ❌ Use "DC003" instead
  "nikaya": "Siam Nikaya", // ❌ Use "NK001" instead
  "grama_niladhari_division": "invalid-code" // ❌ Must be valid code from cmm_gndata
}
```

## Error Messages

### Database Constraint Violation

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": [
    {
      "field": null,
      "message": "Failed to persist vihara record due to a database constraint violation."
    }
  ]
}
```

This error means:

1. One of the foreign key fields contains an invalid code
2. The code does not exist in the reference table
3. Check that you're using codes (e.g., "WP") not names (e.g., "Western Province")

## Migration Details

### Migration File

- **File:** `alembic/versions/ec9be833d776_add_foreign_keys_to_vihara.py`
- **Applied:** 2025-12-11

### What the Migration Does

1. **Data Cleanup** - Sets invalid references to NULL before adding constraints:

   ```sql
   UPDATE vihaddata SET vh_nikaya = NULL
   WHERE vh_nikaya NOT IN (SELECT nk_nkn FROM cmm_nikayadata WHERE nk_is_deleted = false)
   ```

2. **Foreign Key Creation** - Adds constraints:

   ```sql
   ALTER TABLE vihaddata
   ADD CONSTRAINT fk_vihaddata_nikaya
   FOREIGN KEY (vh_nikaya) REFERENCES cmm_nikayadata(nk_nkn)
   ON DELETE SET NULL
   ```

3. **Handles Required Field** - For `vh_gndiv` (required), sets to a valid default if invalid:
   ```sql
   UPDATE vihaddata SET vh_gndiv = (SELECT gn_gnc FROM cmm_gndata WHERE gn_is_deleted = false LIMIT 1)
   WHERE vh_gndiv NOT IN (SELECT gn_gnc FROM cmm_gndata WHERE gn_is_deleted = false)
   ```

## Model Updates

The `ViharaData` model has been updated with explicit `ForeignKey` definitions:

```python
from sqlalchemy import ForeignKey

class ViharaData(Base):
    __tablename__ = "vihaddata"

    vh_nikaya = Column(String(50), ForeignKey('cmm_nikayadata.nk_nkn', ondelete='SET NULL'))
    vh_province = Column(String(100), ForeignKey('cmm_province.cp_code', ondelete='SET NULL'))
    vh_district = Column(String(100), ForeignKey('cmm_districtdata.dd_dcode', ondelete='SET NULL'))
    vh_divisional_secretariat = Column(String(100), ForeignKey('cmm_dvsec.dv_dvcode', ondelete='SET NULL'))
    vh_gndiv = Column(String(10), ForeignKey('cmm_gndata.gn_gnc', ondelete='RESTRICT'), nullable=False)
```

## Testing

### Verify Foreign Keys Applied

```bash
cd /Users/shanuka/Desktop/Work\ project/dba-backend
alembic current
# Should show: ec9be833d776 (head)
```

### Query Valid Codes

```python
from app.db.session import SessionLocal
from app.models.province import Province

db = SessionLocal()
provinces = db.query(Province).filter(Province.cp_is_deleted == False).all()
for p in provinces:
    print(f'{p.cp_code}: {p.cp_name}')
```

### Test API with Valid Codes

Update your test scripts to use valid codes from the reference tables instead of full text names.

## Rollback (if needed)

To remove the foreign key constraints:

```bash
alembic downgrade -1
```

This will drop all the foreign key constraints added by this migration.

## Benefits

1. **Data Integrity** - Invalid reference codes are prevented at database level
2. **Referential Integrity** - Can't delete reference data (provinces, districts) that are in use
3. **Clear Error Messages** - Database will reject invalid codes immediately
4. **No API Changes** - Payload and response formats remain unchanged
5. **Cascading Behavior** - Proper ON DELETE handling (SET NULL for optional fields, RESTRICT for required)

## Common Issues

### Issue: "Failed to persist vihara record due to constraint violation"

**Solution:** Check that all foreign key fields use valid codes:

- Get valid codes from reference tables
- Use codes (e.g., "WP") not names (e.g., "Western Province")
- Ensure `grama_niladhari_division` contains a valid GN code

### Issue: Can't delete a province/district

**Solution:** This is expected behavior - foreign keys with RESTRICT prevent deletion of referenced data. First update all viharas to use a different code, then delete.

### Issue: Existing vihara records have NULL values

**Solution:** This is expected - the migration cleaned invalid data by setting it to NULL. Update records with valid codes.
