# app/main.py
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.error_handlers import register_exception_handlers
from app.api.v1.router import api_router
from app.api.v1.routes import health  # <-- Import the health router
from app.middleware.audit import AuditMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION
)

register_exception_handlers(app)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuditMiddleware)

app.include_router(health.router)  # <-- Add the health router at the root
app.include_router(api_router, prefix="/api/v1")

# Ensure storage directory exists on Railway persistent volume
storage_path = Path("app/storage")
storage_path.mkdir(parents=True, exist_ok=True)

# Mount static file serving for uploaded files
app.mount("/storage", StaticFiles(directory=str(storage_path)), name="storage")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Bhikku Registry API"}
