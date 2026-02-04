# Temp-Bhikku Update - Quick Reference Guide

## 🚀 What Changed?

**Before**: temp-bhikku → `temporary_bhikku` table (tb_id: 1, 2, 3...)  
**After**: temp-bhikku → `bhikku_regist` table (br_regn: BH2026000001, BH2026000002...)

## 📡 API Endpoint (Unchanged)

```
POST /api/v1/temporary-bhikku/manage
```

## 📥 Request Format (Unchanged)

```json
{
  "action": "CREATE",
  "payload": {
    "data": {
      "tb_name": "Ven. Test Thero",
      "tb_id_number": "199012345678",
      "tb_contact_number": "0771234567",
      "tb_samanera_name": "Test Samanera",
      "tb_address": "123 Test Road, Colombo",
      "tb_living_temple": "Test Vihara"
    }
  }
}
```

## 📤 Response Format (+ br_regn)

```json
{
  "status": "success",
  "message": "Temporary bhikku record created successfully.",
  "data": {
    "tb_id": 123,
    "tb_name": "Ven. Test Thero",
    "tb_id_number": "199012345678",
    "tb_contact_number": "0771234567",
    "tb_samanera_name": "Test Samanera",
    "tb_address": "123 Test Road, Colombo",
    "tb_living_temple": "Test Vihara",
    "tb_created_at": "2026-02-01T10:30:00",
    "tb_created_by": "user123",
    "tb_updated_at": null,
    "tb_updated_by": null,
    "br_regn": "BH2026000001"  ← NEW: Auto-generated BH number
  }
}
```

## 🗄️ Database Storage

### New Records:
```sql
-- Stored in bhikku_regist table
SELECT br_regn, br_mahananame, br_gihiname, br_mobile, br_remarks
FROM bhikku_regist
WHERE br_regn = 'BH2026000001';

-- Result:
-- br_regn: BH2026000001
-- br_mahananame: Ven. Test Thero
-- br_gihiname: Test Samanera
-- br_mobile: 0771234567
-- br_remarks: Created from temp-bhikku registration...
```

### Old Records (preserved):
```sql
-- Still accessible in temporary_bhikku table
SELECT * FROM temporary_bhikku;
```

## 🔄 Field Mapping

| Frontend (tb_*) | Database (br_*) | Auto-Generated? |
|----------------|-----------------|-----------------|
| tb_name | br_mahananame | No |
| tb_samanera_name | br_gihiname | No |
| tb_contact_number | br_mobile | No |
| tb_address | br_fathrsaddrs | No |
| tb_living_temple | br_mahanatemple | No |
| tb_id_number | br_remarks (stored) | No |
| - | br_regn | ✅ **Yes** (BH2026000001) |
| - | br_reqstdate | ✅ Yes (today) |
| - | br_currstat | ✅ Yes ("BKR") |
| - | br_parshawaya | ✅ Yes ("N/A") |
| - | br_cat | ✅ **Yes ("TEMP")** - Flag |
| - | br_workflow_status | ✅ Yes ("PENDING") |

## ✅ Frontend Impact

**NONE!** 🎉

- No code changes needed
- Same request format
- Same response format (+ optional br_regn field)
- Existing code will continue to work

## 🧪 Quick Test

```bash
# 1. Get JWT token
TOKEN="your_jwt_token_here"

# 2. Create temp bhikku
curl -X POST http://localhost:8000/api/v1/temporary-bhikku/manage \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "CREATE",
    "payload": {
      "data": {
        "tb_name": "Ven. Quick Test Thero",
        "tb_contact_number": "0771234567"
      }
    }
  }'

# 3. Check response for br_regn field (BH2026XXXXXX)
```

## 📊 Verification Queries

```sqlusing TEMP flag)
SELECT COUNT(*) 
FROM bhikku_regist 
WHERE br_cat = 'TEMP'
AND br_is_deleted = false;

-- 2. View latest temp-bhikku records
SELECT br_regn, br_mahananame, br_mobile, br_cat, br_created_at
FROM bhikku_regist
WHERE br_cat = 'TEMP'
AND br_is_deleted = false
ORDER BY br_created_at DESC
LIMIT 10;

-- 3. Alternative: Search by remarks tag
SELECT br_regn, br_mahananame, br_cat, br_remarks
FROM bhikku_regist
WHERE br_remarks LIKE '[TEMP_BHIKKU]%'
AND br_is_deleted = false
ORDER BY br_created_at DESC
LIMIT 10;

-- 4
-- 3. Count old temp-bhikku records (still in temporary_bhikku)
SELECT COUNT(*) FROM temporary_bhikku;
```

## 🔍 Debugging

### Issue: "br_regn already exists"
```python
# Check if BH number generation is working
SELECT br_regn FROM bhikku_regist 
WHERE br_regn LIKE 'BH2026%' 
ORDER BY br_regn DESC 
LIMIT 1;
```

### Issue: Response missing br_regn
```python
# Check route code in temporary_bhikku.py
# Line ~70: "br_regn": created_bhikku.br_regn
```

### Issue: Frontend not working
```javascript
// Frontend should ignore new br_regn field if not needed
// Existing tb_* fields work as before
console.log(response.data.tb_name);  // Works
console.log(response.data.br_regn);  // New, optional
```

## 📝 Code Files Modified

1. `Temp Flag** - br_cat = "TEMP" to identify temp bhikkus  
✅ **Remarks Tag** - [TEMP_BHIKKU] prefix in br_remarks  
✅ **app/services/temporary_bhikku_service.py` - Creates bhikku record
2. `app/api/v1/routes/temporary_bhikku.py` - Maps response format
3. `app/api/v1/routes/bhikkus.py` - Added comment for clarity

## 🎯 Key Points

✅ **Backward Compatible** - Frontend works without changes  
✅ **Auto BH Number** - Format: BH{YEAR}{SEQUENCE}  
✅ **Standard Workflow** - Now part of bhikku workflow  
✅ **No Data Loss** - All existing data preserved  
✅ **Single Table** - Unified bhikku storage  

## 📚 Documentation

- Full details: `TEMP_BHIKKU_UPDATE_SUMMARY.md`
- Test file: `test_temp_bhikku_new_implementation.py`
- API docs: `TEMP_BHIKKU_API_GUIDE.txt`

## 🆘 Need Help?

Check the comprehensive documentation in `TEMP_BHIKKU_UPDATE_SUMMARY.md` for:
- Detailed implementation
- Testing procedures
- Troubleshooting guide
- Database queries
- Deployment steps
