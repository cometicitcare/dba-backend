# app/api/v1/routes/health.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    """Response model for health check endpoint"""
    status: str


@router.get("/health", response_model=HealthResponse)
def health_check():
    """API health check endpoint"""
    return {"status": "ok"}
