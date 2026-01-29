# Temporary Entities - Field Mapping & Comparison Guide

## Field Mapping by Entity Type

This guide provides a complete field-by-field comparison of all temporary entities, helping developers understand:
- What fields each entity has
- How fields map between entity types
- Which fields are required vs optional
- Field constraints and formats

---

## 1. Entity Comparison Matrix

### Required Fields Summary

| Silmatha | Bhikku | Devala | Arama |
|----------|--------|--------|-------|
| ts_name ✅ | tb_name ✅ | td_name ✅ | ta_name ✅ |

**Pattern:** Every entity has ONE required `{entity}_name` field

---

### Optional Fields by Category

#### Identification Fields
```
Silmatha: ts_nic (National ID)
Bhikku:   tb_id_number (National ID or other)
Devala:   (none)
Arama:    (none)
```

#### Contact Fields
```
All entities have:
  - {entity}_contact_number (15 chars max)
  - {entity}_address (500 chars max, optional)
```

#### Location Fields
```
Silmatha: ts_district, ts_province
Bhikku:   (none)
Devala:   td_district, td_province
Arama:    ta_district, ta_province
```

#### Role/Position Fields
```
Silmatha: ts_arama_name (associated arama)
Bhikku:   tb_samanera_name (novice name), tb_living_temple
Devala:   td_basnayake_nilame_name (chief custodian)
Arama:    ta_aramadhipathi_name (chief incumbent)
```

#### Special Fields
```
Silmatha: ts_ordained_date (date of ordination)
Bhikku:   (none)
Devala:   (none)
Arama:    (none)
```

---

## 2. Detailed Field Reference

### Silmatha Entity (ts_*)

```
Field Name                  | Type     | Max Len | Required | Usage
─────────────────────────────────────────────────────────────────────
ts_id                       | int      | -       | 🔑 ID    | Auto-generated
ts_name                     | string   | 200     | ✅ YES   | Nun/Silmatha name
ts_nic                      | string   | 15      | ❌ NO    | National ID Card
ts_contact_number           | string   | 15      | ❌ NO    | Phone number
ts_address                  | string   | 500     | ❌ NO    | Residential address
ts_district                 | string   | 100     | ❌ NO    | District (CMB, KDY, etc)
ts_province                 | string   | 100     | ❌ NO    | Province (WP, CP, etc)
ts_arama_name               | string   | 200     | ❌ NO    | Associated arama
ts_ordained_date            | date     | -       | ❌ NO    | Ordination date (YYYY-MM-DD)
ts_created_at               | datetime | -       | 🔒      | Server timestamp
ts_created_by               | string   | -       | 🔒      | Creator user ID
ts_updated_at               | datetime | -       | 🔒      | Update timestamp
ts_updated_by               | string   | -       | 🔒      | Last updater ID
```

**Unique Fields:** `ts_ordained_date`, `ts_arama_name`
**Similar To:** Arama (location fields), Devala (location fields)

---

### Bhikku Entity (tb_*)

```
Field Name                  | Type     | Max Len | Required | Usage
─────────────────────────────────────────────────────────────────────
tb_id                       | int      | -       | 🔑 ID    | Auto-generated
tb_name                     | string   | 100     | ✅ YES   | Bhikku/Monk name
tb_id_number                | string   | 20      | ❌ NO    | National ID or other
tb_contact_number           | string   | 15      | ❌ NO    | Phone number
tb_samanera_name            | string   | 100     | ❌ NO    | Novice name (pre-ordination)
tb_address                  | string   | 500     | ❌ NO    | Residential address
tb_living_temple            | string   | 200     | ❌ NO    | Current temple/vihara
tb_created_at               | datetime | -       | 🔒      | Server timestamp
tb_created_by               | string   | -       | 🔒      | Creator user ID
tb_updated_at               | datetime | -       | 🔒      | Update timestamp
tb_updated_by               | string   | -       | 🔒      | Last updater ID
```

**Unique Fields:** `tb_samanera_name`, `tb_living_temple`
**Pattern Difference:** No location fields (district/province)

---

### Devala Entity (td_*)

```
Field Name                  | Type     | Max Len | Required | Usage
─────────────────────────────────────────────────────────────────────
td_id                       | int      | -       | 🔑 ID    | Auto-generated
td_name                     | string   | 200     | ✅ YES   | Devala/Shrine name
td_address                  | string   | 500     | ❌ NO    | Devala address
td_contact_number           | string   | 15      | ❌ NO    | Phone number
td_district                 | string   | 100     | ❌ NO    | District (CMB, KDY, etc)
td_province                 | string   | 100     | ❌ NO    | Province (WP, CP, etc)
td_basnayake_nilame_name    | string   | 200     | ❌ NO    | Chief custodian name
td_created_at               | datetime | -       | 🔒      | Server timestamp
td_created_by               | string   | -       | 🔒      | Creator user ID
td_updated_at               | datetime | -       | 🔒      | Update timestamp
td_updated_by               | string   | -       | 🔒      | Last updater ID
```

**Unique Fields:** `td_basnayake_nilame_name`
**Similar To:** Arama (location fields), Silmatha (location fields)

---

### Arama Entity (ta_*)

```
Field Name                  | Type     | Max Len | Required | Usage
─────────────────────────────────────────────────────────────────────
ta_id                       | int      | -       | 🔑 ID    | Auto-generated
ta_name                     | string   | 200     | ✅ YES   | Arama/Hermitage name
ta_address                  | string   | 500     | ❌ NO    | Arama address
ta_contact_number           | string   | 15      | ❌ NO    | Phone number
ta_district                 | string   | 100     | ❌ NO    | District (CMB, KDY, etc)
ta_province                 | string   | 100     | ❌ NO    | Province (WP, CP, etc)
ta_aramadhipathi_name       | string   | 200     | ❌ NO    | Chief incumbent name
ta_created_at               | datetime | -       | 🔒      | Server timestamp
ta_created_by               | string   | -       | 🔒      | Creator user ID
ta_updated_at               | datetime | -       | 🔒      | Update timestamp
ta_updated_by               | string   | -       | 🔒      | Last updater ID
```

**Unique Fields:** `ta_aramadhipathi_name`
**Similar To:** Devala (location fields), Silmatha (location fields)

---

## 3. Field Type Mapping

### String Fields (with constraints)

#### Name Fields
```
ts_name     (Silmatha/Nun name)          200 chars
tb_name     (Bhikku/Monk name)           100 chars
td_name     (Devala/Shrine name)         200 chars
ta_name     (Arama/Hermitage name)       200 chars
```

#### Contact Fields
```
ts_contact_number  (all entities)        15 chars
tb_contact_number  (all entities)        15 chars
td_contact_number  (all entities)        15 chars
ta_contact_number  (all entities)        15 chars
```

#### Address Fields
```
ts_address  (Silmatha)                   500 chars
tb_address  (Bhikku)                     500 chars
td_address  (Devala)                     500 chars
ta_address  (Arama)                      500 chars
```

#### ID/Identification Fields
```
ts_nic      (Silmatha NIC)               15 chars
tb_id_number (Bhikku ID)                 20 chars
```

#### Location Fields
```
ts_district, ts_province  (Silmatha)    100 chars each
td_district, td_province  (Devala)      100 chars each
ta_district, ta_province  (Arama)       100 chars each
(Bhikku has no location fields)
```

#### Role/Position Fields
```
ts_arama_name               (Silmatha)   200 chars
tb_samanera_name            (Bhikku)     100 chars
tb_living_temple            (Bhikku)     200 chars
td_basnayake_nilame_name    (Devala)     200 chars
ta_aramadhipathi_name       (Arama)      200 chars
```

### Date/DateTime Fields

#### Audit Timestamps (All Entities)
```
{entity}_created_at         datetime (ISO 8601)
{entity}_updated_at         datetime (ISO 8601) or null
```

#### Special Date (Silmatha Only)
```
ts_ordained_date            date (YYYY-MM-DD format)
```

### Integer Fields (All Entities)
```
{entity}_id                 auto-generated, unique, auto-increment
```

---

## 4. Field Similarity Matrix

### Which entities have similar fields?

```
                    Silmatha  Bhikku  Devala  Arama
Name field          ✅        ✅      ✅      ✅
Contact number      ✅        ✅      ✅      ✅
Address             ✅        ✅      ✅      ✅
District/Province   ✅        ❌      ✅      ✅
Identification      ✅ (NIC)  ✅(ID)  ❌      ❌
Role/Position       ✅ (arama) ✅(temple) ✅(chief) ✅(chief)
Special date        ✅        ❌      ❌      ❌

Common Pattern:     {entity}_name, {entity}_contact_number,
                    {entity}_address, {entity}_created_at
```

---

## 5. Location Code Reference

### District Codes (Common Examples)
```
CMB  → Colombo
KDY  → Kandy
GMP  → Gampaha
KLN  → Kalutara
MAT  → Matara
DDS  → Dambulla
RNL  → Ratnapura
MPT  → Matapana
```

### Province Codes
```
WP   → Western Province
CP   → Central Province
EP   → Eastern Province
NP   → Northern Province
NWP  → North Western Province
SP   → Southern Province
UVA  → Uva Province
```

---

## 6. Field Validation Rules

### All Entities

| Rule | Apply To | Example |
|------|----------|---------|
| Required | `{entity}_name` | Cannot be null/empty |
| Max Length | All string fields | See field reference |
| Phone Format | `{entity}_contact_number` | Optional, max 15 chars |
| Date Format | `ts_ordained_date` | YYYY-MM-DD |
| DateTime Format | `{entity}_created_at` | ISO 8601 |
| Auto-generated | `{entity}_id` | Set by server |
| Read-only | Timestamps, audit fields | Cannot modify |

### Data Type Mapping

```python
# String fields
ts_name: str (max 200)
tb_name: str (max 100)

# Optional string fields
ts_nic: Optional[str] (max 15)
tb_id_number: Optional[str] (max 20)

# Date fields
ts_ordained_date: Optional[date]  # YYYY-MM-DD format

# DateTime fields
ts_created_at: datetime           # Server-set

# Integer fields
ts_id: int                        # Auto-generated
```

---

## 7. Quick Field Lookup

### "I need to store [X] information. Which field?"

| Information | Silmatha | Bhikku | Devala | Arama |
|------------|----------|--------|--------|-------|
| Person's name | ts_name | tb_name | - | - |
| Facility name | ts_arama_name | - | td_name | ta_name |
| Phone number | ts_contact_number | tb_contact_number | td_contact_number | ta_contact_number |
| Physical address | ts_address | tb_address | td_address | ta_address |
| District location | ts_district | - | td_district | ta_district |
| Province location | ts_province | - | td_province | ta_province |
| ID/NIC number | ts_nic | tb_id_number | - | - |
| Chief position | - | - | td_basnayake_nilame_name | ta_aramadhipathi_name |
| Current location | ts_arama_name | tb_living_temple | - | - |
| Ordination date | ts_ordained_date | - | - | - |

---

## 8. Import/Export Mapping

### CSV Column Headers

**Silmatha:**
```
ts_name,ts_nic,ts_contact_number,ts_address,ts_district,ts_province,ts_arama_name,ts_ordained_date
```

**Bhikku:**
```
tb_name,tb_id_number,tb_contact_number,tb_samanera_name,tb_address,tb_living_temple
```

**Devala:**
```
td_name,td_address,td_contact_number,td_district,td_province,td_basnayake_nilame_name
```

**Arama:**
```
ta_name,ta_address,ta_contact_number,ta_district,ta_province,ta_aramadhipathi_name
```

---

## 9. API Request Field Mapping

### CREATE Request Structure

```python
# Silmatha CREATE
{
    "data": {
        "ts_name": "Ven. Ananda",
        "ts_nic": "123456789V",
        "ts_contact_number": "0771234567",
        "ts_address": "Address here",
        "ts_district": "CMB",
        "ts_province": "WP",
        "ts_arama_name": "Kelaniya Arama",
        "ts_ordained_date": "2020-01-15"
    }
}

# UPDATE Request Structure (only changed fields)
{
    "ts_id": 1,
    "updates": {
        "ts_contact_number": "0772222222"
        # Only include fields to update
    }
}
```

---

## 10. Common Mistakes to Avoid

### ❌ Common Error: Mixing Field Names

```python
# WRONG - mixing field prefixes
{
    "ts_name": "Ven. Ananda",
    "contact_number": "0771234567",  # ❌ Wrong prefix
    "district": "CMB"                  # ❌ Wrong prefix
}

# CORRECT
{
    "ts_name": "Ven. Ananda",
    "ts_contact_number": "0771234567",  # ✅ Correct prefix
    "ts_district": "CMB"                # ✅ Correct prefix
}
```

### ❌ Common Error: Exceeding Max Length

```python
# WRONG - name too long
{
    "ts_name": "Very long name that exceeds the 200 character limit..."  # ❌
}

# CORRECT - within limit
{
    "ts_name": "Ven. Ananda"  # ✅ Well under 200 chars
}
```

### ❌ Common Error: Wrong Date Format

```python
# WRONG - American date format
{"ts_ordained_date": "01/15/2020"}  # ❌

# CORRECT - ISO 8601 format
{"ts_ordained_date": "2020-01-15"}  # ✅
```

---

## Summary

| Aspect | Details |
|--------|---------|
| **Total Entities** | 4 (Silmatha, Bhikku, Devala, Arama) |
| **Required Fields** | 1 per entity: `{entity}_name` |
| **Optional Fields** | 7-10 per entity (varies) |
| **Common Fields** | name, contact_number, address, created_at, updated_at |
| **Unique Fields** | ts_ordained_date (Silmatha), tb_samanera_name (Bhikku), role fields (all) |
| **Field Naming** | `{entity_prefix}_{field_name}` |
| **Max String Length** | 500 (address), 200 (name), 100 (name variant), 15 (phone) |
| **Location Fields** | Silmatha, Devala, Arama (district, province) |
| **Date Format** | YYYY-MM-DD (dates), ISO 8601 (datetimes) |

See [TEMPORARY_ENTITIES_ENDPOINT_SPECIFICATIONS.md](TEMPORARY_ENTITIES_ENDPOINT_SPECIFICATIONS.md) for complete endpoint documentation with examples.
