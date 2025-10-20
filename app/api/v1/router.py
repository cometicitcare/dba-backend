# app/api/v1/router.py
from fastapi import APIRouter

from app.api.v1.routes import (
    auth,
    beneficiary_data,
    bhikkus,
    health,
    vihara_data,
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(bhikkus.router, prefix="/bhikkus", tags=["Bhikkus"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(vihara_data.router, prefix="/vihara-data")
api_router.include_router(beneficiary_data.router, prefix="/beneficiary-data")
