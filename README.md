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

---

## 📂 Project Structure
```
app/
 ├── api/           # API routes (v1, auth, etc.)
 ├── core/          # Config, security, logging
 ├── db/            # Models, migrations, session
 ├── services/      # Business logic
 ├── storage/       # File handling layer
 └── main.py        # FastAPI entrypoint
alembic/            # Alembic migrations
alembic.ini         # Alembic config
requirements.txt    # Python deps
Dockerfile          # Docker build
start.sh            # Startup script (migrations + uvicorn)
railway.toml        # Railway deploy config
```

---

## 🛠️ Setup & Development

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

---

## 📄 License
MIT License — see `LICENSE` for details.
