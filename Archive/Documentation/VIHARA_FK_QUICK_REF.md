# Vihara Foreign Keys - Quick Reference

## Valid Codes for Foreign Key Fields

### ⚠️ IMPORTANT

Use **codes** not **names** for these fields:

- ❌ `"province": "Western Province"`
- ✅ `"province": "WP"`

## Required Foreign Key Fields

### Grama Niladhari Division (REQUIRED)

```
Field: grama_niladhari_division (camelCase) or vh_gndiv (snake_case)
Type: String (max 10 chars)
Required: YES
Examples: "1-1-03-005", "1-2-24-070", "2-1-03-170"
```

## Optional Foreign Key Fields

### Province

```
Field: province (camelCase) or vh_province (snake_case)
Type: String (max 100 chars)
Required: NO
Valid Codes:
  WP  - Western Province
  CP  - Central Province
  SP  - Southern Province
  NP  - Northern Province
  EP  - Eastern Province
  NWP - North Western Province
  NC  - North Central Province
  UV  - Uva Province
  SG  - Sabaragamuwa Province
```

### District

```
Field: district (camelCase) or vh_district (snake_case)
Type: String (max 100 chars)
Required: NO
Valid Codes: DC001, DC002, DC003, DC007, DC008, etc.
Get Full List: GET /api/v1/districts
Example: "DC001" (Colombo), "DC003" (Gampaha)
```

### Divisional Secretariat

```
Field: divisional_secretariat (camelCase) or vh_divisional_secretariat (snake_case)
Type: String (max 100 chars)
Required: NO
Valid Codes: DV001, DV002, DV003, etc.
Get Full List: GET /api/v1/divisional-secretariats
Example: "DV001" (Colombo), "DV015" (Gampaha)
```

### Nikaya

```
Field: nikaya (camelCase) or vh_nikaya (snake_case)
Type: String (max 50 chars)
Required: NO
Valid Codes:
  NK001 - සියම් නිකාය (Siam Nikaya)
  NK002 - අමරපුර නිකාය (Amarapura Nikaya)
  NK003 - රාමඤ්ඤ නිකාය (Ramanna Nikaya)
```

## No Foreign Key (Free Text)

### Pradeshya Sabha

```
Field: pradeshya_sabha (camelCase) or vh_pradeshya_sabha (snake_case)
Type: String (max 100 chars)
Required: NO
Format: Any text (no FK constraint)
Example: "Colombo Municipal Council", "Gampaha Pradeshiya Sabha"
```

## Error Messages

### Constraint Violation

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": [
    {
      "message": "Failed to persist vihara record due to a database constraint violation."
    }
  ]
}
```

**Cause:** Invalid code in nikaya, province, district, divisional_secretariat, or grama_niladhari_division

**Solution:** Use valid codes from reference tables

### Invalid Reference

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": [
    {
      "message": "Invalid reference: vh_gndiv not found"
    }
  ]
}
```

**Cause:** GN division code doesn't exist in database

**Solution:** Get valid GN codes from `/api/v1/grama-niladhari` endpoint

## Example Valid Payload

### camelCase Format

```json
{
  "action": "CREATE",
  "payload": {
    "data": {
      "temple_name": "ශ්‍රී සුදර්ශනාරාම විහාරය",
      "temple_address": "No. 123, Temple Road, Colombo",
      "telephone_number": "0112345678",
      "whatsapp_number": "0771234567",
      "email_address": "temple@example.lk",
      "temple_type": "VIHARA",
      "province": "WP",
      "district": "DC001",
      "divisional_secretariat": "DV001",
      "pradeshya_sabha": "Colombo Municipal Council",
      "grama_niladhari_division": "1-1-03-005",
      "nikaya": "NK001",
      "parshawaya": "PR005",
      "owner_code": "BH2025000001"
    }
  }
}
```

### snake_case Format

```json
{
  "action": "CREATE",
  "payload": {
    "data": {
      "vh_vname": "ශ්‍රී සුදර්ශනාරාම විහාරය",
      "vh_addrs": "No. 123, Temple Road, Colombo",
      "vh_mobile": "0112345678",
      "vh_whtapp": "0771234567",
      "vh_email": "temple@example.lk",
      "vh_typ": "VIHARA",
      "vh_province": "WP",
      "vh_district": "DC001",
      "vh_divisional_secretariat": "DV001",
      "vh_pradeshya_sabha": "Colombo Municipal Council",
      "vh_gndiv": "1-1-03-005",
      "vh_nikaya": "NK001",
      "vh_parshawa": "PR005",
      "vh_ownercd": "BH2025000001"
    }
  }
}
```

## Getting Valid Codes

### Python Script

```python
from app.db.session import SessionLocal
from app.models.province import Province
from app.models.district import District
from app.models.nikaya import NikayaData

db = SessionLocal()

# Get provinces
provinces = db.query(Province).filter(Province.cp_is_deleted == False).all()
for p in provinces:
    print(f'{p.cp_code}: {p.cp_name}')

# Get districts
districts = db.query(District).filter(District.dd_is_deleted == False).all()
for d in districts:
    print(f'{d.dd_dcode}: {d.dd_dname}')

# Get nikayas
nikayas = db.query(NikayaData).filter(NikayaData.nk_is_deleted == False).all()
for n in nikayas:
    print(f'{n.nk_nkn}: {n.nk_nname}')
```

### API Endpoints

```bash
# Get provinces
GET /api/v1/provinces

# Get districts
GET /api/v1/districts

# Get divisional secretariats
GET /api/v1/divisional-secretariats

# Get GN divisions
GET /api/v1/grama-niladhari

# Get nikayas
GET /api/v1/nikayas
```

## Test Script

Run the test to verify FK constraints:

```bash
cd /Users/shanuka/Desktop/Work\ project/dba-backend
chmod +x test_vihara_foreign_keys.sh
./test_vihara_foreign_keys.sh
```

Expected output:

```
✅ Valid FK codes: PASSED (vihara created)
✅ Invalid nikaya: PASSED (correctly rejected)
✅ Invalid GN division: PASSED (correctly rejected)
Foreign key constraints are working correctly!
```
