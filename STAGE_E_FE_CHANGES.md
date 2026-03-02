# STAGE E FE IMPLEMENTATION GUIDE
**Date:** March 2, 2026  
**Status:** FE Changes Required  
**Backend Status:** ✅ Complete (Flags added, migrations applied)

---

## 📋 EXECUTIVE SUMMARY

**What Changed on Backend:**
- All TEMP tables now have `*_is_transferred` flags (tracking transfer status)
- All main tables now have `is_temporary_record` flags (marking originally-temp records)
- New columns are boolean, default FALSE, nullable FALSE
- Database migrations applied and ready

**What FE Needs to Do:**
1. Update display logic to show TEMP record indicator
2. Update filtering to support `is_temporary_record` flag
3. Verify creation endpoints still work
4. Update list components to show temp/permanent status
5. Implement transfer status tracking (optional)

---

## 🔄 DATA MODEL CHANGES

### New Flags in Main Tables

**Vihara (vihaddata):**
```javascript
// NEW COLUMN:
vh_is_temporary_record: boolean  // true if created via temporary_vihara first
```

**Bhikku (bhikku_regist):**
```javascript
// NEW COLUMN:
br_is_temporary_record: boolean  // true if created via temporary_bhikku first
```

**Silmatha (silmatha_regist):** ✅ Already has this
```javascript
sil_is_temporary_record: boolean  // Existing - use as reference
```

**Arama (aramadata):** ✅ Already has this
```javascript
ar_is_temporary_record: boolean  // Existing - use as reference
```

### New Flags in TEMP Tables (Backend Only)

These track which TEMP records have been transferred:
- `temporary_vihara.tv_is_transferred`
- `temporary_bhikku.tb_is_transferred`
- `temporary_silmatha.ts_is_transferred`
- `temporary_arama.ta_is_transferred`

**Note:** FE doesn't need to use these directly; they're for backend tracking.

---

## 📺 FE COMPONENT CHANGES

### 1. Display Components - Show TEMP Indicator

**Current Behavior (OLD):**
```typescript
// Checked TEMP prefix to identify temp records
const isTempVihara = vihara.vh_trn?.startsWith("TEMP-");
const tempStyle = isTempVihara ? { color: "orange" } : {};
```

**New Behavior (REQUIRED):**
```typescript
// Check is_temporary_record flag instead
const isTempVihara = vihara.vh_is_temporary_record === true;
const tempStyle = isTempVihara ? { color: "orange", fontStyle: "italic" } : {};

// Display indicator
<span className={tempStyle}>
  {vihara.vh_vname}
  {isTempVihara && <span className="badge-temp">TEMP</span>}
</span>
```

### 2. List Components - Filter by Status

**Vihara List Component (ViharaList.tsx or similar):**

**Current:**
```typescript
// Probably mixes TEMP + main records with no visual distinction
const viharas = response.data.data;  // Mix of TEMP and permanent
```

**New - Add Filtering:**
```typescript
const [filterTempStatus, setFilterTempStatus] = useState('all');  // 'all', 'temp', 'permanent'

// Filter logic
const filteredViharas = viharas.filter(vh => {
  if (filterTempStatus === 'temp') return vh.is_temporary_record === true;
  if (filterTempStatus === 'permanent') return vh.is_temporary_record === false;
  return true;  // 'all'
});

// UI toggle
<div className="filter-status">
  <Radio
    label="All Records"
    checked={filterTempStatus === 'all'}
    onChange={() => setFilterTempStatus('all')}
  />
  <Radio
    label="Temp Only"
    checked={filterTempStatus === 'temp'}
    onChange={() => setFilterTempStatus('temp')}
  />
  <Radio
    label="Permanent Only"
    checked={filterTempStatus === 'permanent'}
    onChange={() => setFilterTempStatus('permanent')}
  />
</div>
```

### 3. Creation Endpoints - No Changes Needed

**Vihara Creation (ViharaForm.tsx):**
```typescript
// THIS SHOULD STILL WORK AS-IS - no changes needed!
const createTempVihara = async (formData) => {
  // Backend handles the redirect to main table now
  return api.post('/vihara-data/manage', formData, {
    action: 'CREATE_TEMP'  // OR appropriate action
  });
};

// Result will have: vh_is_temporary_record = true automatically
```

**Why?** Backend API now:
1. Receives CREATE request with TEMP flag indication
2. Auto-sets `is_temporary_record = true` on save
3. Returns record with flag set

### 4. Autocomplete Components - Update Display

**AutocompleteBhikkhu.tsx:**

**OLD:**
```typescript
// Checked TEMP prefix
const displayLabel = bhikku.br_regn?.startsWith("TEMP-") 
  ? bhikku.br_regn 
  : bhikku.br_regn;
```

**NEW:**
```typescript
const isTempBhikku = bhikku.br_is_temporary_record === true;
const displayLabel = isTempBhikku 
  ? `${bhikku.br_regn} (TEMP)` 
  : bhikku.br_regn;
```

**AutocompleteVihara.tsx - Similar Pattern:**
```typescript
const isTempVihara = vihara.vh_is_temporary_record === true;
const displayLabel = isTempVihara 
  ? `${vihara.vh_vname} (TEMP)` 
  : vihara.vh_vname;
```

---

## 🔍 API RESPONSE EXAMPLES

### Get Vihara (Single Record)
```json
{
  "success": true,
  "data": {
    "vh_id": 123,
    "vh_trn": "VH-2026-00001",
    "vh_vname": "Colombo Temple",
    "vh_is_temporary_record": false,  // ← NEW FIELD
    "vh_workflow_status": "S1_PENDING",
    ...
  }
}
```

### List Viharas (Mixed TEMP + Permanent)
```json
{
  "success": true,
  "data": [
    {
      "vh_id": 123,
      "vh_vname": "Colombo Temple",
      "vh_is_temporary_record": false  // ← Permanent record
    },
    {
      "vh_id": 125,
      "vh_vname": "New Temple (Draft)",
      "vh_is_temporary_record": true  // ← TEMP record (created via /temporary-vihara/manage)
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total_records": 2  // ← Now includes BOTH types
  }
}
```

---

## 📝 IMPLEMENTATION CHECKLIST

### ViharaList / ViharaTable Component
- [ ] Add display indicator for `vh_is_temporary_record === true`
- [ ] Add filter toggle (All / TEMP Only / Permanent Only)
- [ ] Update table to show TEMP status visually (badge, color, italics)
- [ ] Test pagination with mixed TEMP/permanent records
- [ ] Verify count matches actual display

### BhikkuList / BhikkuTable Component
- [ ] Add display indicator for `br_is_temporary_record === true`
- [ ] Add filter toggle
- [ ] Update autocomplete display
- [ ] Verify registration number display (no TEMP prefix needed anymore)

### SilmathaList / SilmathaTable Component
- [ ] Verify existing `sil_is_temporary_record` flag display works
- [ ] Check filter is present (should already be done for Silmatha)
- [ ] Confirm no breaking changes

### AramaList / AramaTable Component
- [ ] Verify existing `ar_is_temporary_record` flag display works
- [ ] Check filter is present (should already be done for Arama)
- [ ] Confirm no breaking changes

### Creation Flows
- [ ] ViharaFormCreateTemp - Verify POST still works (no changes needed)
- [ ] BhikkuFormCreateTemp - Verify POST still works (no changes needed)
- [ ] Silmatha - Verify still works (should be unchanged)
- [ ] Arama - Verify still works (should be unchanged)

### Autocomplete Components
- [ ] AutocompleteVihara.tsx - Update display logic
- [ ] AutocompleteBhikkhu.tsx - Update display logic  
- [ ] AutocompleteSilmatha.tsx - Verify works
- [ ] AutocompleteArama.tsx - Verify works

### Search / Filter Components
- [ ] Add `is_temporary_record` to search/filter options
- [ ] Test filtering by temp status
- [ ] Verify pagination still works with filters

---

## 💡 IMPLEMENTATION GUIDE

### Step 1: Update Display Components (30 mins)
```typescript
// In any list/table component showing records:

// OLD:
const isTempRecord = record.some_prefix_field?.startsWith("TEMP-");

// NEW:
const isTempRecord = record.is_temporary_record === true;

// Apply styling
const styling = isTempRecord ? "temp-badge" : "";
```

### Step 2: Add Filter Toggles (45 mins)
Use your existing filter component pattern:
```typescript
const [statusFilter, setStatusFilter] = useState({
  includeTemp: true,
  includePermanent: true
});

const filtered = records.filter(r => {
  if (r.is_temporary_record && !statusFilter.includeTemp) return false;
  if (!r.is_temporary_record && !statusFilter.includePermanent) return false;
  return true;
});
```

### Step 3: Update Autocomplete (20 mins)
```typescript
// In getOptionLabel function:
const label = option.is_temporary_record 
  ? `${option.some_id_field} (TEMP)` 
  : option.some_id_field;
```

### Step 4: Test (1 hour)
- [ ] Create new TEMP record via form
- [ ] Verify it appears in list with TEMP indicator
- [ ] Verify it can be filtered
- [ ] Create permanent record (if available)
- [ ] Verify both show correctly
- [ ] Test pagination with mixed records

---

## 🎨 UI/UX SUGGESTIONS

###Temporary Record Badges
```css
.badge-temp {
  background: #ff9800;
  color: white;
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 0.8em;
  margin-left: 5px;
  font-weight: bold;
}

.temp-row {
  background: #fff3e0;  /* Light orange */
  opacity: 0.9;
}

.temp-text {
  font-style: italic;
  color: #f57c00;
}
```

### Filter UI
```jsx
<div className="status-filter">
  <label>
    <Checkbox
      checked={showTemp}
      onChange={(e) => setShowTemp(e.target.checked)}
    />
    Include Temporary Records
  </label>
</div>
```

---

## 🚨 IMPORTANT: BACKWARD COMPATIBILITY

**What Still Works:**
- ✅ Creating TEMP records (no FE changes to creation logic needed)
- ✅ API endpoints return data in same format (just added new field)
- ✅ Silmatha/Arama filtering (already uses similar flag)
- ✅ Existing searches and sorts

**What Changed:**
- ❌ Cannot rely on TEMP prefix in registration numbers anymore (use `is_temporary_record` flag)
- ❌ Pagination counts will now include TEMP records (might show more than before)
- ❌ Need to handle mixed TEMP/permanent in lists (they'll both be returned)

---

## 🧪 TESTING SCENARIOS

### Test 1: Create and Display TEMP Record
1. Create new TEMP Vihara via form
2. List all Viharas
3. Verify new record shows with TEMP indicator
4. Verify `is_temporary_record = true`

### Test 2: Filter by Status
1. Create 3 TEMP + 5 permanent Viharas
2. Filter "TEMP Only" - should show 3
3. Filter "Permanent Only" - should show 5
4. Filter "All" - should show 8
5. Pagination counts should match

### Test 3: Autocomplete Display
1. Type in autocomplete to search TEMPrecord
2. Should show with (TEMP) indicator
3. Permanent records show without indicator
4. Can select either type

### Test 4: Mixed Pagination
1. Create many TEMP + permanent records
2. Request page 1 with limit 20
3. Verify pagination metadata correct
4. Request page 2 - verify no duplicates

---

## 📞 QUESTIONS FOR FE TEAM

Before implementing, confirm:

1. **Display Format:** How should TEMP records be visually distinct?
   - [ ] Badge (recommended)
   - [ ] Color change
   - [ ] Icon
   - [ ] Other: _______

2. **Filter Location:** Where should temp/permanent filter go?
   - [ ] Top of list (recommended)
   - [ ] Sidebar
   - [ ] Dropdown
   - [ ] Other: _______

3. **Pagination:** Should temp records be in ALL lists or only specific?
   - [ ] All lists show mixed (recommended)
   - [ ] Separate temp-only lists
   - [ ] Toggle to show/hide temps
   - [ ] Other: _______

4. **Registration Numbers:** Can we assume TEMP- prefix won't exist anymore?
   - [ ] YES - use only `is_temporary_record` flag
   - [ ] NO - need both checks for compatibility
   - [ ] Other: _______

---

## ✅ COMPLETION CRITERIA

After implementation, verify:

- [ ] All TEMP records display with visual indicator
- [ ] Filters work for both temp and permanent
- [ ] Pagination counts are accurate
- [ ] Autocomplete shows temp status
- [ ] No console errors
- [ ] Existing tests still pass
- [ ] Can create TEMP records (no API changes needed)
- [ ] Can view both TEMP and permanent records

---

## 📚 REFERENCES

**Backend Changes:**
- New Model Columns: `vh_is_temporary_record`, `br_is_temporary_record`
- Migrations Applied: 20260302000002, 20260302000003
- Transfer Flags in TEMP: `tv_is_transferred`, `tb_is_transferred`

**Existing Implementations (Use as Reference):**
- Silmatha: Already has `sil_is_temporary_record` filter
- Arama: Already has `ar_is_temporary_record` filter

---

**Ready to Implement on FE Side!** 🚀
