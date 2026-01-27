# Pagination Fix - Frontend Guide

## ⚠️ IMPORTANT: No Action Required for Frontend!

**Your frontend code will continue to work exactly as before.** This fix is 100% backward compatible.

---

## What Happened?

We fixed an inconsistency where:
- **Main entities** (Vihara, Arama) used `page` parameter
- **Temporary entities** (Temp Vihara, Temp Arama) used `skip` parameter

This has been resolved to support **BOTH** formats seamlessly.

---

## Your Current Code - Still Works! ✅

### If You're Using Skip-Based (Temporary Entities)

```javascript
// This request format still works exactly as before:
POST /api/v1/temporary-vihara/manage
{
  "action": "READ_ALL",
  "payload": {
    "skip": 0,
    "limit": 20
  }
}

// Response now includes both formats:
{
  "status": "success",
  "data": {
    "records": [...],
    "total": 100,
    "skip": 0,        // ← You can still use this
    "limit": 20,
    "page": 1         // ← NEW: Also included (you can ignore)
  }
}
```

**No changes needed to your code.** Old fields are still there.

---

## New Option - Using Page-Based (When You're Ready)

If you want to modernize your code to use the same pagination pattern as main entities:

### Before (Skip-Based):
```javascript
const response = await fetch('/api/v1/temporary-vihara/manage', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    action: 'READ_ALL',
    payload: {
      skip: 50,     // Page 3 of 50-item pages
      limit: 50
    }
  })
});
```

### After (Page-Based) - Optional:
```javascript
const response = await fetch('/api/v1/temporary-vihara/manage', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    action: 'READ_ALL',
    payload: {
      page: 3,      // Much more intuitive!
      limit: 50
    }
  })
});
```

**Both work identically.** Use whichever you prefer.

---

## Migration Timeline

1. **Right Now:** Your code works as-is ✅
2. **Whenever:** Optionally update to use `page` parameter
3. **No Deadline:** No breaking changes will be introduced

---

## Quick Reference

### Temporary Vihara Endpoint
- **URL:** `POST /api/v1/temporary-vihara/manage`
- **Pagination:** Supports `page` OR `skip` parameter
- **Default:** If neither provided, uses page 1 (skip 0)

### Temporary Arama Endpoint
- **URL:** `POST /api/v1/arama-data/manage`
- **Pagination:** Supports `page` OR `skip` parameter
- **Default:** If neither provided, uses page 1 (skip 0)

### Response Format
```json
{
  "status": "success",
  "message": "...",
  "data": {
    "records": [...],
    "total": 100,
    "page": 1,      // Calculated from page or skip
    "skip": 0,      // Calculated from page or skip
    "limit": 20
  }
}
```

---

## FAQ

### Q: Do I need to update my code?
**A:** No. Your existing code will continue to work perfectly.

### Q: Can I mix page and skip?
**A:** Yes. If you provide both, `page` takes precedence. But we recommend using only one.

### Q: What if I don't provide either?
**A:** Defaults to page 1 (skip 0).

### Q: Are there any changes to the response structure?
**A:** No breaking changes. The response now includes both `page` and `skip`, but your existing code can ignore the new fields.

### Q: When do I need to update?
**A:** Never. But if you want consistency across all entities, consider switching to `page` parameter.

### Q: What if something breaks?
**A:** Report it immediately. This fix was designed to be completely safe, but we're monitoring for issues.

---

## Testing Your Integration (Optional)

### Test 1: Old Format (Still Works)
```bash
curl -X POST http://localhost:8001/api/v1/temporary-vihara/manage \
  -H "Content-Type: application/json" \
  -d '{
    "action": "READ_ALL",
    "payload": {"skip": 0, "limit": 20}
  }'
```

### Test 2: New Format (Also Works)
```bash
curl -X POST http://localhost:8001/api/v1/temporary-vihara/manage \
  -H "Content-Type: application/json" \
  -d '{
    "action": "READ_ALL",
    "payload": {"page": 1, "limit": 20}
  }'
```

Both return the same data structure.

---

## Troubleshooting

### If your code suddenly breaks:
1. **Check:** Did you receive a new API version notification?
2. **Verify:** Are you sending `action` and `payload` correctly?
3. **Confirm:** Is your limit value between 1-200?
4. **Report:** If something seems wrong, contact the backend team

---

## Summary

✅ **Your code is safe**
✅ **No action required**
✅ **Backward compatible**
✅ **Future-proof**
✅ **Optional improvements available**

You can migrate to page-based pagination whenever you're ready, or stick with skip-based forever. Both work equally well.
