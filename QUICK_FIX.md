# Quick Fix Guide - Bhikku Management Permissions

## ⚠️ PROBLEM IDENTIFIED

The users `bhikku_admin` and `bhikku_dataentry` cannot access the bhikku management API because they lack the required permissions.

## ✅ SOLUTION READY

I've created automated scripts to fix this issue. Follow the instructions below based on your deployment environment.

---

## 🚀 For Production (Railway/Cloud Deployment)

### Option 1: Using Railway CLI

```bash
# SSH into your Railway container
railway run bash

# Run the setup script
python -m app.utils.setup_bhikku_complete
```

### Option 2: Using Railway Console

1. Open Railway dashboard
2. Go to your project
3. Open the "Deploy" tab
4. Click on "..." → "Shell"
5. Run:
   ```bash
   python -m app.utils.setup_bhikku_complete
   ```

---

## 🐳 For Docker Compose Deployment

```bash
# Navigate to project directory
cd /path/to/dba-backend

# Make sure Docker Compose is running
docker-compose up -d

# Run the setup script
docker-compose exec api python -m app.utils.setup_bhikku_complete
```

---

## 💻 For Local Development

```bash
# Navigate to project directory
cd /path/to/dba-backend

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# OR
.venv\Scripts\activate  # Windows

# Run the setup script
python -m app.utils.setup_bhikku_complete
```

---

## 📋 What the Script Does

1. ✅ Creates "Bhikku Department" group
2. ✅ Creates 10 permissions for bhikku management
3. ✅ Creates/updates 2 roles:
   - `bhikku_admin` (BHIK_ADM) - Full access
   - `bhikku_dataentry` (BHIK_DATA) - Create/Update access
4. ✅ Assigns appropriate permissions to each role
5. ✅ Creates users (if they don't exist):
   - Username: `bhikku_admin`, Password: `Bhikku@123`
   - Username: `bhikku_dataentry`, Password: `Bhikku@123`
6. ✅ Assigns roles to users

---

## 🧪 Testing After Setup

### 1. Login

```bash
curl -X POST https://api.dbagovlk.com/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -c cookies.txt \
  -d '{
    "ua_username": "bhikku_admin",
    "ua_password": "Bhikku@123"
  }'
```

### 2. Test the API Endpoint

```bash
curl -X POST https://api.dbagovlk.com/api/v1/bhikkus-high/manage \
  -H 'Content-Type: application/json' \
  -b cookies.txt \
  -d '{
    "action": "CREATE",
    "payload": {
      "data": {
        "bhr_reqstdate": "2025-11-24",
        "bhr_currstat": "ST01",
        "bhr_parshawaya": "",
        "bhr_livtemple": "VH001",
        "bhr_candidate_regn": "BH2025000001",
        "bhr_cc_code": "CAT02",
        "bhr_samanera_serial_no": "BH2025000001",
        "bhr_higher_ordination_place": "Test Temple",
        "bhr_higher_ordination_date": "2025-10-30",
        "bhr_karmacharya_name": "Test Name",
        "bhr_upaddhyaya_name": "Test Name",
        "bhr_assumed_name": "Test Name",
        "bhr_residence_higher_ordination_trn": "VH001",
        "bhr_residence_permanent_trn": "VH001",
        "bhr_declaration_residence_address": "Test Address",
        "bhr_tutors_tutor_regn": "BH2025000001",
        "bhr_presiding_bhikshu_regn": "BH2025000001",
        "bhr_declaration_date": "2025-11-01",
        "bhr_remarks": "Test remarks"
      }
    }
  }'
```

### Expected Response

```json
{
  "status": "success",
  "message": "Higher bhikku registration created successfully.",
  "data": { ... }
}
```

---

## 📝 Permissions Breakdown

### bhikku_admin Gets:
- ✅ `bhikku:create`, `bhikku:read`, `bhikku:update`, `bhikku:delete`
- ✅ `CREATE_BHIKKU_HIGH`, `READ_BHIKKU_HIGH`, `UPDATE_BHIKKU_HIGH`, `DELETE_BHIKKU_HIGH`
- ✅ `bhikku:manage_id_card`, `bhikku:manage_certificate`

### bhikku_dataentry Gets:
- ✅ `bhikku:create`, `bhikku:read`, `bhikku:update` (no delete)
- ✅ `CREATE_BHIKKU_HIGH`, `READ_BHIKKU_HIGH`, `UPDATE_BHIKKU_HIGH` (no delete)
- ✅ `bhikku:manage_id_card`, `bhikku:manage_certificate`

---

## ❓ Troubleshooting

### Error: "ModuleNotFoundError"
- Make sure you're running the command in the correct environment
- For Docker: Use `docker-compose exec api python -m ...`
- For local: Activate virtual environment first

### Error: "Permission denied" after setup
- Clear browser cookies and login again
- Verify the setup script completed successfully
- Check if user has the correct role: 
  ```bash
  # In Python shell
  from app.db.session import SessionLocal
  from app.models.user_roles import UserRole
  db = SessionLocal()
  roles = db.query(UserRole).filter_by(ur_user_id="USER_ID").all()
  ```

### Error: "Database connection failed"
- Verify DATABASE_URL is set correctly in `.env`
- Ensure database is running: `docker-compose ps`

---

## 📚 Additional Resources

- Full setup documentation: `BHIKKU_SETUP.md`
- Script locations:
  - `/app/utils/setup_bhikku_complete.py` - All-in-one setup
  - `/app/utils/seed_bhikku_permissions.py` - Permissions only
  - `/app/utils/assign_bhikku_roles.py` - Users only
  - `/setup_bhikku.sh` - Bash wrapper

---

## ✨ Summary

**The fix is ready!** Just run the setup script in your deployment environment, and the users will have the necessary permissions to access all bhikku management APIs.

The script is **idempotent** (safe to run multiple times) and will not duplicate existing data.
