# Dockerfile
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System deps (psycopg2 + build essentials minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install deps first (maximize cache)
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy app
COPY . /app

# Ensure start script executable
RUN chmod +x /app/start.sh

# Non-root
RUN useradd -m appuser
USER appuser

# Expose (Railway injects $PORT; EXPOSE is informational)
EXPOSE 8080

CMD ["bash", "/app/start.sh"]
