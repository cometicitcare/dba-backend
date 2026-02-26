# 🛕 Temple/Vihara Management API

A **FastAPI-based** backend for temple/vihara management.  
It provides APIs for user accounts, bhikku registrations, certificates, and file storage, with a modular architecture and Postgres + Alembic migrations.

## Quick Start
1. `cp .env.example .env` and adjust values.
2. `docker compose up --build -d`
3. Run migrations: `docker compose exec api alembic upgrade head`
4. (Optional) seed: `docker compose exec api python -m app.db.seed`
5. Open docs: http://localhost:8000/docs


## Local (without Docker)
- Create venv, `pip install -r requirements.txt`
- Ensure Postgres is running and `DATABASE_URL` is set in `.env`
- `alembic upgrade head`
- `uvicorn app.main:app --reload`


---

## 🚀 Features
- **FastAPI** REST API with interactive docs (`/docs` and `/redoc`).
- **Postgres** as the primary database (via SQLAlchemy + Alembic).
- **Cookie-based auth** with JWT.
- **Persistent file storage** (via Railway volumes or local mounts).
- **CORS + middleware** for frontend integration.
- **Linting & formatting** (`black`, `isort`, `flake8`, `pylint`).
- **Docker-first deployment**, with Railway integration.
- **Vihara Flow** with bypass statuses, historical date support, and enhanced filtering/sorting.
- **Unified Bhikku Search** across regular and temporary registrations with TEMP- prefix identification.
- **Advanced Validation** with improved error recovery and workflow handling.

---

## 🏛️ Vihara Flow Enhancements (Stage D/F)

### Unified Bhikku Search
- **/bhikkus/manage READ_ALL** now returns both regular and temporary bhikkus in a single paginated response
- Temporary records prefixed with `TEMP-{id}` (e.g., `TEMP-15`) for instant UI distinction
- Includes `tb_living_temple` field for temporary bhikkus
- Smart filtering: temp records only fetched when no advanced filters applied

### Vihara Filtering & Sorting (Stage D)
- **Province, District, Nikaya, Divisional Secretariat** filters now fully functional in `vihara_repo.list()`
- **Workflow Status Filter** added for all vihara states including 3 bypass statuses
- **Dynamic Column Sorting**: `sort_by` + `sort_dir` params for TRN, Name, Status, Created/Updated dates
- **Accurate Pagination**: Fixed `totalRecords` count to include TEMP records

### Historical Date Field (Stage C)
- **Period Established** now supports ancient dates and Buddhist Era notation:
  - Era: AD, BC, BE (Buddhist Era), or blank
  - Year: Free-text VARCHAR(10) — supports ~600 BC, ~1000 BE format
  - Month/Day: Optional, day requires month to be present
  - Notes: Free-text field for ambiguous/approximate dates
- Full validation: era requires year; day requires month

### Vihara Bypass Statuses (Stage B)
Three new toggle-based bypass states for completing sections without full approval chain:
- **S1_NO_DETAIL_COMP**: No Details — Complete (Religious Affiliation)
- **S1_NO_CHIEF_COMP**: No Chief Incumbent (Leadership)
- **S1_LTR_CERT_DONE**: Letter & Certificate Done (Mahanyake)

Bypass Features:
- Admin can unlock/reverse bypass via `UNLOCK_BYPASS` action
- Bypass states treated as equivalent to `S1_APPROVED` for auto-completion
- 8 audit columns track who set/unlocked bypass and when
- Data is KEPT in DB when bypass activated (fields never cleared)

### Service Layer Enhancements
- **Improved Validation**: Field-level validation before DB operations
- **Error Recovery**: Better handling of validation errors with clear messaging
- **Workflow Handling**: Streamlined status transitions with enhanced audit trails
- **Data Integrity**: Better null/required field checks and consistency validation

---

## 📂 Project Structure
```
app/
 ├── api/           # API routes (v1, auth, etc.)
 ├── core/          # Config, security, logging
 ├── db/            # Models, migrations, session
 ├── services/      # Business logic (vihara, bhikku services)
 ├── repositories/  # Data access layer (vihara_repo, bhikku_repo)
 ├── schemas/       # Pydantic schemas with validation
 ├── storage/       # File handling layer
 └── main.py        # FastAPI entrypoint
alembic/            # Alembic migrations
  └── versions/     # Migration scripts (Stage B/C/F enhancements)
alembic.ini         # Alembic config
requirements.txt    # Python deps
Dockerfile          # Docker build
start.sh            # Startup script (migrations + uvicorn)
railway.toml        # Railway deploy config
```

---

## � Key API Endpoints

### Vihara Management
- **GET/POST** `/vihara-data/manage` — Create, read, update vihara records
  - Query params: `province`, `district`, `nikaya`, `divisional_secretariat`, `workflow_status`, `sort_by`, `sort_dir`, `skip`, `limit`
  - Enhanced validation and error handling
  - Supports bypass status actions: `BYPASS_NO_DETAIL`, `BYPASS_NO_CHIEF`, `BYPASS_LTR_CERT`, `UNLOCK_BYPASS`

### Bhikku Management
- **GET/POST** `/bhikkus/manage` — Create, read, update bhikku records
  - Returns both regular and temporary bhikkus (TEMP- prefix)
  - Unified search across all registrations
  - Includes temple relationship data

### Statistics & Reporting
- **POST** `/vihara-data/statistics` — Admin-only aggregated statistics
- **POST** `/vihara-data/my-dashboard-stats` — User's personal dashboard metrics

---

## 📊 Database Migrations

Key Alembic migrations:
- **20260223000001**: Adds bypass audit columns, period fields, and enhancements for Stage B/C/F

Apply all migrations:
```bash
alembic upgrade head
```

Check applied migrations:
```bash
alembic current
```

---

## �🛠️ Setup & Development

### 1. Environment
```bash
cp .env.example .env
```
Edit `.env` with your local DB credentials and secrets.

### 2. Run with Docker
```bash
docker compose up --build -d
docker compose exec api alembic upgrade head
docker compose exec api python -m app.db.seed   # optional seeding
```
API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Run without Docker
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

alembic upgrade head
uvicorn app.main:app --reload
```

---

## 📦 Deployment (Railway)

1. Push to GitHub.  
2. Create a **Railway project** → “Deploy from GitHub.”  
3. Attach **Postgres** plugin → exposes `DATABASE_URL`.  
4. Add a **Volume** mounted at `/app/storage`.  
5. Add Environment Variables:
   - `SECRET_KEY=your-secret`
   - `APP_ENV=production`
   - `API_V1_STR=/api/v1`
   - `STORAGE_DIR=/app/storage`
   - (`DATABASE_URL` auto-injected by Postgres plugin)
6. Deploy 🚀  
7. Healthcheck: `GET /health` should return `{ "status": "ok" }`.

---

## 🧑‍💻 Useful Commands

- Run migrations:
  ```bash
  alembic upgrade head
  ```
- Create migration:
  ```bash
  alembic revision --autogenerate -m "desc"
  ```
- Run tests (if `pytest` added):
  ```bash
  pytest
  ```
- Lint & format:
  ```bash
  black .
  isort .
  flake8
  pylint app
  ```

---

## 📚 Docs & References
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [Railway Deployments](https://docs.railway.app/)
- **Vihara Flow Plan**: See `VIHARA_CHANGE_REQUEST_PLAN.md` for comprehensive stage-by-stage implementation details
- **Vihara Flow Analysis**: See `VIHARA_FLOW_COMPREHENSIVE_ANALYSIS.md` for architectural overview

---

## 🔄 Recent Updates (v4)

### Backend Changes (fix/be-vihraflow-issues-v4)
- **Unified Bhikku Search**: Regular + temporary bhikkus in single endpoint with TEMP- prefix ✅
- **Enhanced Validation**: Improved field-level validation and error recovery ✅
- **Vihara Service Enhancements**: Streamlined validation and workflow handling ✅
- **Filtering & Sorting**: Fixed province/district/nikaya filters; added sort_by/sort_dir ✅

### Frontend Alignment
- Bhikku autocomplete supports TEMP- prefix records
- Dual temple display (living + mahana temples)
- Enhanced vihara add/update forms with better error recovery
- Improved step validation and data persistence

### Deployment Notes
- **Critical**: Run `alembic upgrade head` to apply all migrations
- Backward compatible with existing API endpoints
- No breaking changes to authentication or file storage
- Test with both temporary and regular bhikkus before production deployment

---

## 📄 License
MIT License — see `LICENSE` for details.