# app/api/v1/routes/main_bhikkus.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission
from app.models.user import UserAccount
from app.schemas.main_bhikku import (
    SetParshawaMahanayakaRequest,
    SetNikayaMahanayakaRequest,
    SetMahanayakaResponse,
    MainBhikkuOut,
)
from app.services.main_bhikku_service import main_bhikku_service

router = APIRouter()


@router.post(
    "/set-parshawa-mahanayaka",
    response_model=SetMahanayakaResponse,
    dependencies=[has_permission("bhikku:write")],
)
def set_parshawa_mahanayaka(
    payload: SetParshawaMahanayakaRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Assign (or re-assign) the Mahanayaka for a Parshawaya.
    Deactivates the previously-active appointment automatically.
    """
    try:
        result = main_bhikku_service.set_parshawa_mahanayaka(
            db,
            mb_nikaya_cd=payload.mb_nikaya_cd,
            mb_parshawa_cd=payload.mb_parshawa_cd,
            br_regn=payload.br_regn,
            mb_start_date=payload.mb_start_date,
            mb_remarks=payload.mb_remarks,
            actor_id=current_user.username if current_user else None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "status": "success",
        "message": "Parshawa Mahanayaka assigned successfully.",
        "data": MainBhikkuOut.model_validate(result["record"]),
        "assigned_bhikku": result["bhikku"],
        "nikaya": result["nikaya"],
        "parshawa": result["parshawa"],
    }


@router.post(
    "/set-nikaya-mahanayaka",
    response_model=SetMahanayakaResponse,
    dependencies=[has_permission("bhikku:write")],
)
def set_nikaya_mahanayaka(
    payload: SetNikayaMahanayakaRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Assign (or re-assign) the Mahanayaka for a Nikaya.
    Deactivates the previously-active appointment automatically.
    """
    try:
        result = main_bhikku_service.set_nikaya_mahanayaka(
            db,
            mb_nikaya_cd=payload.mb_nikaya_cd,
            br_regn=payload.br_regn,
            mb_start_date=payload.mb_start_date,
            mb_remarks=payload.mb_remarks,
            actor_id=current_user.username if current_user else None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "status": "success",
        "message": "Nikaya Mahanayaka assigned successfully.",
        "data": MainBhikkuOut.model_validate(result["record"]),
        "assigned_bhikku": result["bhikku"],
        "nikaya": result["nikaya"],
        "parshawa": result["parshawa"],
    }
