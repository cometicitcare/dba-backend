# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.core.config import settings
from app.core.error_handlers import register_exception_handlers
from app.api.v1.router import api_router
from app.api.v1.routes import health  # <-- Import the health router
from app.middleware.audit import AuditMiddleware

# API Documentation Metadata
tags_metadata = [
    {
        "name": "🏥 Health & Status",
        "description": "API health check and system status endpoints",
    },
    {
        "name": "🔐 Authentication & Authorization",
        "description": "User login, registration, password reset, OTP verification, and access control",
    },
    {
        "name": "👤 DBA-HRMS: Bhikku Registration",
        "description": "Bhikku registration, profile management, search, and workflow operations",
    },
    {
        "name": "🪪 DBA-HRMS: Bhikku ID Card",
        "description": "Bhikku ID card generation, workflow, printing, and reprint operations",
    },
    {
        "name": "📜 DBA-HRMS: Certifications & Documents",
        "description": "Bhikku certifications, certificates, and certificate change management",
    },
    {
        "name": "🕉️ Silmatha Management",
        "description": "Silmatha ID card generation and management system",
    },
    {
        "name": "🏛️ Vihara & Religious Data",
        "description": "Vihara (temple) data, Nikaya, Parshawa, and religious information",
    },
    {
        "name": "📊 Master Data Management",
        "description": "Banks, payment methods, beneficiary data, categories, and reference data",
    },
    {
        "name": "📍 Location Management",
        "description": "Province, district, city, divisional secretariat, and location hierarchy",
    },
    {
        "name": "👥 User & Role Management",
        "description": "RBAC administration, user management, roles, permissions, and groups",
    },
    {
        "name": "📈 Dashboard & Reports",
        "description": "Dashboard statistics, summaries, and reporting endpoints",
    },
    {
        "name": "🔍 Audit & Monitoring",
        "description": "Audit logs, activity tracking, and system monitoring",
    },
    {
        "name": "🛠️ System & Debug",
        "description": "System utilities, debugging tools, and administrative functions",
    },
]

app = FastAPI(
    title="DBA-HRMS API",
    description="""
## Department of Buddhist Affairs - Human Resource Management System

Complete API for managing:
- **Bhikku Registration & ID Card Workflow** - Complete lifecycle management
- **Silmatha Management** - Silmatha ID card system
- **Authentication & Authorization** - Secure user access control
- **Master Data & Locations** - Reference data and geographic information

### Base URL
- Production: `https://api.dbagovlk.com`
- Development: `http://127.0.0.1:8000`

### Authentication
Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_token>
```
    """,
    version=settings.PROJECT_VERSION,
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
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

# Mount storage directory for serving uploaded files
# This allows files to be accessed via URLs like: https://hrms.dbagovlk.com/storage/bhikku_regist/2025/11/23/BH2025000011/scanned_document_*.pdf
storage_path = Path("app/storage")
storage_path.mkdir(parents=True, exist_ok=True)
app.mount("/storage", StaticFiles(directory=str(storage_path)), name="storage")

app.include_router(health.router)  # <-- Add the health router at the root
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Bhikku Registry API"}
