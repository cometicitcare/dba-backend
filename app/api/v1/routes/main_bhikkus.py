# app/api/v1/routes/main_bhikkus.py
"""Full CRUD (single /manage endpoint) + set-parshawa-mahanayaka for main_bhikkus."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_any_permission
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas.main_bhikku import (
    CRUDAction,
    MainBhikkuCreate,
    MainBhikkuManagementRequest,
    MainBhikkuManagementResponse,
    MainBhikkuOut,
    MainBhikkuUpdate,
)
from app.services.main_bhikku_service import main_bhikku_service
from app.utils.http_exceptions import validation_error

router = APIRouter()

_PERMS = has_any_permission(
    "system:create", "system:update", "system:delete",
    "vihara:create", "vihara:read", "vihara:update", "vihara:delete",
    "bhikku:create", "bhikku:read", "bhikku:update", "bhikku:delete",
)


# ======================================================================
# Single-endpoint CRUD  –  POST /main-bhikkus/manage
# ======================================================================

@router.post("/manage", response_model=MainBhikkuManagementResponse, dependencies=[_PERMS])
def manage_main_bhikkus(
    request: MainBhikkuManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    action = request.action
    payload = request.payload
    actor_id = current_user.ua_user_id

    # ------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------
    if action == CRUDAction.CREATE:
        if not payload.data:
            raise validation_error([("payload.data", "data is required for CREATE")])
        try:
            raw = _extract(payload.data)
            create_data = MainBhikkuCreate.model_validate(raw)
        except (ValidationError, TypeError) as exc:
            raise _to_validation_error(exc) from exc
        try:
            created = main_bhikku_service.create_entry(db, payload=create_data, actor_id=actor_id)
            return MainBhikkuManagementResponse(
                status="success",
                message="Main bhikku record created successfully.",
                data=MainBhikkuOut.model_validate(created),
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    # ------------------------------------------------------------------
    # READ_ONE
    # ------------------------------------------------------------------
    if action == CRUDAction.READ_ONE:
        if payload.mb_id is None:
            raise validation_error([("payload.mb_id", "mb_id is required for READ_ONE")])
        entity = main_bhikku_service.get_by_id(db, payload.mb_id)
        if not entity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found.")
        return MainBhikkuManagementResponse(
            status="success",
            message="Record retrieved.",
            data=MainBhikkuOut.model_validate(entity),
        )

    # ------------------------------------------------------------------
    # READ_ALL
    # ------------------------------------------------------------------
    if action == CRUDAction.READ_ALL:
        page = payload.page or 1
        limit = payload.limit
        search = (payload.search_key.strip() if payload.search_key else None) or None
        skip = payload.skip if payload.page is None else (page - 1) * limit

        records = main_bhikku_service.list_entries(
            db,
            skip=skip,
            limit=limit,
            search=search,
            mb_type=payload.mb_type.value if payload.mb_type else None,
            mb_nikaya_cd=payload.mb_nikaya_cd,
            mb_parshawa_cd=payload.mb_parshawa_cd,
        )
        total = main_bhikku_service.count_entries(
            db,
            search=search,
            mb_type=payload.mb_type.value if payload.mb_type else None,
            mb_nikaya_cd=payload.mb_nikaya_cd,
            mb_parshawa_cd=payload.mb_parshawa_cd,
        )
        return MainBhikkuManagementResponse(
            status="success",
            message="Records retrieved.",
            data=[MainBhikkuOut.model_validate(r) for r in records],
            totalRecords=total,
            page=page,
            limit=limit,
        )

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------
    if action == CRUDAction.UPDATE:
        if payload.mb_id is None:
            raise validation_error([("payload.mb_id", "mb_id is required for UPDATE")])
        if not payload.data:
            raise validation_error([("payload.data", "data is required for UPDATE")])
        try:
            raw = _extract(payload.data, exclude_unset=True)
            if not raw:
                raise validation_error([("payload.data", "At least one field required for UPDATE")])
            update_data = MainBhikkuUpdate.model_validate(raw)
        except (ValidationError, TypeError) as exc:
            raise _to_validation_error(exc) from exc
        try:
            updated = main_bhikku_service.update_entry(db, mb_id=payload.mb_id, payload=update_data, actor_id=actor_id)
            return MainBhikkuManagementResponse(
                status="success",
                message="Record updated.",
                data=MainBhikkuOut.model_validate(updated),
            )
        except ValueError as exc:
            msg = str(exc)
            if "not found" in msg.lower():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg) from exc
            raise validation_error([(None, msg)]) from exc

    # ------------------------------------------------------------------
    # DELETE
    # ------------------------------------------------------------------
    if action == CRUDAction.DELETE:
        if payload.mb_id is None:
            raise validation_error([("payload.mb_id", "mb_id is required for DELETE")])
        try:
            main_bhikku_service.delete_entry(db, mb_id=payload.mb_id, actor_id=actor_id)
            return MainBhikkuManagementResponse(status="success", message="Record deleted.", data=None)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    raise validation_error([("action", "Invalid action specified")])


# ======================================================================
# SET PARSHAWA MAHANAYAKA – POST /main-bhikkus/set-parshawa-mahanayaka
# ======================================================================

from pydantic import field_validator, ConfigDict, Field
from typing import Optional, Annotated
from datetime import date

from app.schemas.main_bhikku import BhikkuBriefOut, NikayaBriefOut, ParshawaBriefOut


class SetParshawaMahanayakaRequest(BaseModel):
    """Pick nikaya → parshawaya → bhikku."""

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    mb_nikaya_cd: Annotated[str, Field(min_length=1, max_length=10)]
    mb_parshawa_cd: Annotated[str, Field(min_length=1, max_length=20)]
    br_regn: Annotated[str, Field(min_length=1, max_length=20)]
    mb_start_date: Optional[date] = None
    mb_remarks: Annotated[Optional[str], Field(default=None, max_length=500)] = None

    @field_validator("mb_nikaya_cd", "mb_parshawa_cd", "br_regn", mode="before")
    @classmethod
    def _upper(cls, v: Optional[str]) -> str:
        if not v or not str(v).strip():
            raise ValueError("This field is required.")
        return str(v).strip().upper()


class SetParshawaMahanayakaResponse(BaseModel):
    status: str
    message: str
    data: Optional[MainBhikkuOut] = None
    assigned_bhikku: Optional[BhikkuBriefOut] = None
    nikaya: Optional[NikayaBriefOut] = None
    parshawa: Optional[ParshawaBriefOut] = None


@router.post(
    "/set-parshawa-mahanayaka",
    response_model=SetParshawaMahanayakaResponse,
    dependencies=[has_any_permission(
        "system:create", "system:update",
        "vihara:create", "vihara:update",
        "bhikku:create", "bhikku:update",
    )],
)
def set_parshawa_mahanayaka(
    request: SetParshawaMahanayakaRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """Select nikaya → select parshawaya → assign a bhikku as parshawaya mahanayaka.

    Also saves the record in the `main_bhikkus` table.
    """
    actor_id = current_user.ua_user_id
    try:
        record = main_bhikku_service.upsert_from_appointment(
            db,
            mb_type="PARSHAWA_MAHANAYAKA",
            mb_nikaya_cd=request.mb_nikaya_cd,
            mb_parshawa_cd=request.mb_parshawa_cd,
            mb_bhikku_regn=request.br_regn,
            mb_start_date=request.mb_start_date,
            mb_remarks=request.mb_remarks,
            actor_id=actor_id,
        )
    except ValueError as exc:
        msg = str(exc)
        if "not found" in msg.lower() or "does not exist" in msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg) from exc
        raise validation_error([(None, msg)]) from exc

    out = MainBhikkuOut.model_validate(record)

    bhikku_info = None
    if record.bhikku:
        bhikku_info = BhikkuBriefOut(
            br_regn=record.bhikku.br_regn,
            br_mahananame=record.bhikku.br_mahananame,
            br_gihiname=record.bhikku.br_gihiname,
        )

    nikaya_info = None
    if record.nikaya:
        nikaya_info = NikayaBriefOut(nk_nkn=record.nikaya.nk_nkn, nk_nname=record.nikaya.nk_nname)

    parshawa_info = None
    if record.parshawa:
        parshawa_info = ParshawaBriefOut(pr_prn=record.parshawa.pr_prn, pr_pname=record.parshawa.pr_pname)

    return SetParshawaMahanayakaResponse(
        status="success",
        message="Parshawaya Mahanayaka assigned successfully.",
        data=out,
        assigned_bhikku=bhikku_info,
        nikaya=nikaya_info,
        parshawa=parshawa_info,
    )


# ======================================================================
# Helpers
# ======================================================================

def _extract(data, *, exclude_unset: bool = False) -> dict:
    if data is None:
        raise TypeError("Payload data cannot be null.")
    if isinstance(data, BaseModel):
        return data.model_dump(exclude_unset=exclude_unset)
    if isinstance(data, dict):
        return data
    raise TypeError("Payload data must be an object.")


def _to_validation_error(exc):
    if isinstance(exc, ValidationError):
        results = []
        for e in exc.errors():
            loc = ".".join(str(i) for i in e.get("loc", []))
            results.append((loc or None, e.get("msg", "")))
        return validation_error(results or [(None, "Invalid payload")])
    return validation_error([(None, str(exc))])
