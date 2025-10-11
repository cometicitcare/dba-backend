# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router
from app.api.v1.routes import health  # <-- Import the health router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION
)

# --- CORS Configuration ---
origins = [
    "http://localhost:3000",          # local frontend (React, Next.js, etc.)
    "https://your-frontend-domain.com"  # production domain (optional, replace later)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # whitelist origins
    allow_credentials=True,
    allow_methods=["*"],          # allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],          # allow all headers
)
# --- End of CORS Configuration ---

# Include routers
app.include_router(health.router)  # health check at root
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Bhikku Registry API"}
