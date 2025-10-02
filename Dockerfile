# Dockerfile — FastAPI on Railway with non-root user and writable volume
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System deps for psycopg2 and builds
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Create the app user early so we can set ownership properly
RUN useradd -m appuser

WORKDIR /app

# Install Python dependencies first (maximize cache)
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the application source
COPY . /app

# Prepare a writable storage directory under the user's home and fix ownership
RUN mkdir -p /home/appuser/storage && chown -R appuser:appuser /home/appuser && \
    chown -R appuser:appuser /app && \
    chmod +x /app/start.sh

# Drop privileges
USER appuser

# Railway injects $PORT at runtime; EXPOSE is informational
EXPOSE 8080

CMD ["bash", "/app/start.sh"]
