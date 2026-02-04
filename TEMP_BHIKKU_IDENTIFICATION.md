# Temp Bhikku Identification Guide

## 🏷️ How to Identify Temp Bhikkus

Temp bhikku registrations saved to `bhikku_regist` table have **TWO identification flags**:

### 1. Category Flag: `br_cat = 'TEMP'`

The primary identifier for temp bhikku registrations.

```sql
-- Find all temp bhikkus
SELECT * FROM bhikku_regist 
WHERE br_cat = 'TEMP' 
AND br_is_deleted = false;

-- Count temp bhikkus
SELECT COUNT(*) FROM bhikku_regist 
WHERE br_cat = 'TEMP' 
AND br_is_deleted = false;
```

### 2. Remarks Tag: `[TEMP_BHIKKU]` prefix

Secondary identifier stored in the remarks field.

```sql
-- Find temp bhikkus by remarks tag
SELECT * FROM bhikku_regist 
WHERE br_remarks LIKE '[TEMP_BHIKKU]%'
AND br_is_deleted = false;
```

## 📊 Complete Query Examples

### Get All Temp Bhikkus
```sql
SELECT 
    br_regn,
    br_mahananame,
    br_gihiname,
    br_mobile,
    br_cat,
    br_remarks,
    br_workflow_status,
    br_created_at
FROM bhikku_regist
WHERE br_cat = 'TEMP'
AND br_is_deleted = false
ORDER BY br_created_at DESC;
```

### Filter by Date Range
```sql
SELECT br_regn, br_mahananame, br_created_at
FROM bhikku_regist
WHERE br_cat = 'TEMP'
AND br_created_at >= '2026-02-01'
AND br_is_deleted = false
ORDER BY br_created_at DESC;
```

### Get Temp Bhikkus with Contact Info
```sql
SELECT 
    br_regn,
    br_mahananame,
    br_mobile,
    br_fathrsaddrs,
    br_created_at
FROM bhikku_regist
WHERE br_cat = 'TEMP'
AND br_mobile IS NOT NULL
AND br_is_deleted = false;
```

### Search Temp Bhikkus by Name
```sql
SELECT br_regn, br_mahananame, br_mobile
FROM bhikku_regist
WHERE br_cat = 'TEMP'
AND br_mahananame ILIKE '%search_term%'
AND br_is_deleted = false;
```

## 🔍 Backend Code - How to Filter Temp Bhikkus

### Python/SQLAlchemy
```python
from app.models.bhikku import Bhikku

# Get all temp bhikkus
temp_bhikkus = db.query(Bhikku).filter(
    Bhikku.br_cat == "TEMP",
    Bhikku.br_is_deleted.is_(False)
).all()

# Count temp bhikkus
temp_count = db.query(Bhikku).filter(
    Bhikku.br_cat == "TEMP",
    Bhikku.br_is_deleted.is_(False)
).count()

# Exclude temp bhikkus from regular list
regular_bhikkus = db.query(Bhikku).filter(
    Bhikku.br_cat != "TEMP",
    Bhikku.br_is_deleted.is_(False)
).all()
```

### API Endpoint - Filter by Category
```python
# In your API endpoint
if filter_temp_only:
    query = query.filter(Bhikku.br_cat == "TEMP")
elif exclude_temp:
    query = query.filter(Bhikku.br_cat != "TEMP")
```

## 📝 Temp Bhikku Record Structure

When you query a temp bhikku, you'll see:

```json
{
  "br_regn": "BH2026000001",
  "br_mahananame": "Ven. Test Thero",
  "br_gihiname": "Test Samanera Name",
  "br_mobile": "0771234567",
  "br_fathrsaddrs": "123 Test Road, Colombo",
  "br_cat": "TEMP",  ← Temp flag
  "br_remarks": "[TEMP_BHIKKU] Created from temp-bhikku registration...",  ← Tag
  "br_currstat": "BKR",
  "br_parshawaya": "N/A",
  "br_workflow_status": "PENDING",
  "br_created_at": "2026-02-02T10:30:00"
}
```

## 🎯 Use Cases

### 1. List Only Temp Bhikkus
```sql
SELECT * FROM bhikku_regist 
WHERE br_cat = 'TEMP';
```

### 2. Exclude Temp Bhikkus from Regular Lists
```sql
SELECT * FROM bhikku_regist 
WHERE br_cat != 'TEMP' OR br_cat IS NULL;
```

### 3. Count by Category
```sql
SELECT 
    br_cat,
    COUNT(*) as total
FROM bhikku_regist
WHERE br_is_deleted = false
GROUP BY br_cat;
```

### 4. Convert Temp to Regular
```sql
-- When temp bhikku gets full information, update the category
UPDATE bhikku_regist
SET 
    br_cat = NULL,  -- or appropriate category
    br_remarks = REPLACE(br_remarks, '[TEMP_BHIKKU] ', ''),
    br_updated_at = NOW()
WHERE br_regn = 'BH2026000001';
```

## 🔄 Migration from Old System

### Old temporary_bhikku Table
- Records with: `tb_id`, `tb_name`, etc.
- Stored in separate `temporary_bhikku` table

### New System (temp bhikkus in bhikku_regist)
- Records with: `br_regn`, `br_cat = 'TEMP'`, etc.
- Stored in main `bhikku_regist` table
- Identified by `br_cat = 'TEMP'` flag

### Both Systems Coexist
```sql
-- Old temp bhikkus (legacy)
SELECT COUNT(*) FROM temporary_bhikku;

-- New temp bhikkus (current)
SELECT COUNT(*) FROM bhikku_regist WHERE br_cat = 'TEMP';

-- Total temp bhikkus across both systems
SELECT 
    (SELECT COUNT(*) FROM temporary_bhikku) as old_temp,
    (SELECT COUNT(*) FROM bhikku_regist WHERE br_cat = 'TEMP') as new_temp;
```

## 📊 Reporting Queries

### Daily Temp Bhikku Registrations
```sql
SELECT 
    DATE(br_created_at) as registration_date,
    COUNT(*) as total_temp_bhikkus
FROM bhikku_regist
WHERE br_cat = 'TEMP'
AND br_created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(br_created_at)
ORDER BY registration_date DESC;
```

### Temp Bhikkus by District
```sql
SELECT 
    br_created_by_district,
    COUNT(*) as total
FROM bhikku_regist
WHERE br_cat = 'TEMP'
AND br_is_deleted = false
GROUP BY br_created_by_district
ORDER BY total DESC;
```

### Latest Temp Registrations
```sql
SELECT 
    br_regn,
    br_mahananame,
    br_mobile,
    br_created_at,
    br_created_by
FROM bhikku_regist
WHERE br_cat = 'TEMP'
ORDER BY br_created_at DESC
LIMIT 20;
```

## ⚙️ Configuration

### Category Values
- **TEMP**: Temporary bhikku registration (incomplete information)
- **NULL** or other values: Regular bhikku registration

### Remarks Prefix
- **[TEMP_BHIKKU]**: Tag added to remarks for temp registrations
- Can be searched/filtered using LIKE query

## 🔒 Important Notes

1. **Primary Identifier**: Always use `br_cat = 'TEMP'` as the primary filter
2. **Backup Identifier**: `br_remarks LIKE '[TEMP_BHIKKU]%'` as secondary check
3. **Both Flags Set**: Both `br_cat` and remarks prefix are set together
4. **Not Deleted**: Always include `br_is_deleted = false` in queries
5. **Case Sensitive**: 'TEMP' is uppercase, ensure exact match

## 🎨 UI/Frontend Considerations

### Display Temp Bhikkus Differently
```javascript
// Example: Add visual indicator for temp bhikkus
if (bhikku.br_cat === 'TEMP') {
  badge = '<span class="badge badge-warning">TEMP</span>';
  rowClass = 'temp-bhikku-row';
}
```

### Filter Options
```javascript
// Add filter option in UI
filterOptions = [
  { value: 'all', label: 'All Bhikkus' },
  { value: 'temp', label: 'Temp Registrations Only' },
  { value: 'regular', label: 'Regular Registrations' }
];
```

## 📈 Statistics Dashboard

```sql
-- Comprehensive temp bhikku statistics
SELECT 
    COUNT(*) as total_temp_bhikkus,
    COUNT(CASE WHEN br_mobile IS NOT NULL THEN 1 END) as with_mobile,
    COUNT(CASE WHEN br_workflow_status = 'PENDING' THEN 1 END) as pending,
    COUNT(CASE WHEN br_workflow_status = 'APPROVED' THEN 1 END) as approved,
    MIN(br_created_at) as first_registration,
    MAX(br_created_at) as latest_registration
FROM bhikku_regist
WHERE br_cat = 'TEMP'
AND br_is_deleted = false;
```

---

**Summary**: Temp bhikkus are identified by `br_cat = 'TEMP'` flag and `[TEMP_BHIKKU]` remarks prefix, making them easy to query, filter, and distinguish from regular bhikku registrations.
