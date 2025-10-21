# app/api/v1/router.py
from fastapi import APIRouter

from app.api.v1.routes import (
    auth,
    beneficiary_data,
    bhikkus,
    bhikku_high,
    bhikku_certification,
    dashboard,
    certificates,
    nilame,
    health,
    vihara_data,
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(bhikkus.router, prefix="/bhikkus", tags=["Bhikkus"])
api_router.include_router(bhikku_high.router, prefix="/bhikkus-high", tags=["Bhikku High"])
api_router.include_router(
    bhikku_certification.router,
    prefix="/bhikkus-certifications",
    tags=["Bhikku Certification"],
)
api_router.include_router(
    certificates.router,
    prefix="/certificates",
    tags=["Certificates"],
)
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(nilame.router, prefix="/nilame", tags=["Nilame"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(vihara_data.router, prefix="/vihara-data")
api_router.include_router(beneficiary_data.router, prefix="/beneficiary-data")
