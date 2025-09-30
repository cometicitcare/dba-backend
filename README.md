# Temple/Vihara Management API


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