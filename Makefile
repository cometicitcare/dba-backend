.PHONY: dev fmt lint migrate revision


dev:
uvicorn app.main:app --reload --port 8000


fmt:
black app && isort app


migration:
alembic revision --autogenerate -m "auto"


upgrade:
alembic upgrade head


downgrade:
alembic downgrade -1