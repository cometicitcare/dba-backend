# app/api/v1/router.py
from fastapi import APIRouter

from app.api.v1.routes import (
    auth,
    banks,
    bank_branches,
    beneficiary_data,
    bhikkus,
    bhikku_regist,
    bhikku_high,
    bhikku_certification,
    certificates,
    certificate_changes,
    dashboard,
    bhikku_summary,
    nilame,
    health,
    roles,
    vihara_data,
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(bhikkus.router, prefix="/bhikkus", tags=["Bhikkus"])
api_router.include_router(
    bhikku_regist.router, prefix="/bhikku_regist", tags=["Bhikku Registration"]
)
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
api_router.include_router(
    certificate_changes.router,
    prefix="/certificate-changes",
    tags=["Certificate Changes"],
)
api_router.include_router(
    banks.router,
    prefix="/banks",
    tags=["Banks"],
)
api_router.include_router(
    bank_branches.router,
    prefix="/bank-branches",
    tags=["Bank Branches"],
)
api_router.include_router(
    bhikku_summary.router,
    prefix="/bhikkus-summary",
    tags=["Bhikku Summary"],
)
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(nilame.router, prefix="/nilame", tags=["Nilame"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(vihara_data.router, prefix="/vihara-data")
api_router.include_router(beneficiary_data.router, prefix="/beneficiary-data")
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
