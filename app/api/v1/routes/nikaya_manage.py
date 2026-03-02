# app/api/v1/routes/nikaya_manage.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, ValidationError

from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_any_permission
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas.nikaya import (
    AssignedBhikkuInfo,
    CRUDAction,
    NikayaCreate,
    NikayaManagementRequest,
    NikayaManagementResponse,
    NikayaOut,
    NikayaUpdate,
    SetMahanayakaRequest,
    SetMahanayakaResponse,
)
from app.services.nikaya_service import nikaya_service
from app.utils.http_exceptions import validation_error

router = APIRouter()  # Tags defined in router.py


@router.post(
    "/manage",
    response_model=NikayaManagementResponse,
    dependencies=[has_any_permission(
        # System / super-admin
        "system:create", "system:update", "system:delete",
        # Vihara Admin & Vihara Data Entry
        "vihara:create", "vihara:read", "vihara:update", "vihara:delete",
        # Bhikku Admin & Bhikku Data Entry
        "bhikku:create", "bhikku:read", "bhikku:update", "bhikku:delete",
    )],
)
def manage_nikaya_records(
    request: NikayaManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    action = request.action
    payload = request.payload
    user_id = current_user.ua_user_id

    # ------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------
    if action == CRUDAction.CREATE:
        if not payload.data:
            raise validation_error(
                [("payload.data", "Valid data is required for CREATE action")]
            )
        try:
            create_raw = _extract_payload(payload.data)
            create_payload = NikayaCreate.model_validate(create_raw)
        except ValidationError as exc:
            raise validation_error(_format_validation_errors(exc)) from exc
        except TypeError as exc:
            raise validation_error([(None, str(exc))]) from exc
        try:
            created = nikaya_service.create_entry(
                db, payload=create_payload, actor_id=user_id
            )
            created_out = NikayaOut.model_validate(created)
            return NikayaManagementResponse(
                status="success",
                message="Nikaya record created successfully.",
                data=created_out,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    # ------------------------------------------------------------------
    # READ_ONE
    # ------------------------------------------------------------------
    if action == CRUDAction.READ_ONE:
        if payload.nk_id is None and not payload.nk_nkn:
            raise validation_error(
                [("payload.nk_id", "nk_id or nk_nkn is required for READ_ONE action")]
            )

        entity = None
        if payload.nk_id is not None:
            entity = nikaya_service.get_by_id(db, payload.nk_id)
        elif payload.nk_nkn:
            entity = nikaya_service.get_by_nkn(db, payload.nk_nkn)

        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Nikaya record not found."
            )

        entity_out = NikayaOut.model_validate(entity)
        return NikayaManagementResponse(
            status="success",
            message="Nikaya record retrieved successfully.",
            data=entity_out,
        )

    # ------------------------------------------------------------------
    # READ_ALL
    # ------------------------------------------------------------------
    if action == CRUDAction.READ_ALL:
        page = payload.page or 1
        limit = payload.limit
        search = payload.search_key.strip() if payload.search_key else None
        if search == "":
            search = None
        skip = payload.skip if payload.page is None else (page - 1) * limit

        records = nikaya_service.list_entries(
            db, skip=skip, limit=limit, search=search
        )
        total = nikaya_service.count_entries(db, search=search)

        records_out = [NikayaOut.model_validate(item) for item in records]
        return NikayaManagementResponse(
            status="success",
            message="Nikaya records retrieved successfully.",
            data=records_out,
            totalRecords=total,
            page=page,
            limit=limit,
        )

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------
    if action == CRUDAction.UPDATE:
        if payload.nk_id is None:
            raise validation_error(
                [("payload.nk_id", "nk_id is required for UPDATE action")]
            )
        if not payload.data:
            raise validation_error(
                [("payload.data", "Valid data is required for UPDATE action")]
            )
        try:
            update_raw = _extract_payload(payload.data, exclude_unset=True)
        except TypeError as exc:
            raise validation_error([(None, str(exc))]) from exc
        if not update_raw:
            raise validation_error(
                [("payload.data", "At least one field must be provided for UPDATE action")]
            )
        try:
            update_payload = NikayaUpdate.model_validate(update_raw)
        except ValidationError as exc:
            raise validation_error(_format_validation_errors(exc)) from exc
        try:
            updated = nikaya_service.update_entry(
                db,
                entity_id=payload.nk_id,
                payload=update_payload,
                actor_id=user_id,
            )
            updated_out = NikayaOut.model_validate(updated)
            return NikayaManagementResponse(
                status="success",
                message="Nikaya record updated successfully.",
                data=updated_out,
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=message
                ) from exc
            raise validation_error([(None, message)]) from exc

    # ------------------------------------------------------------------
    # DELETE
    # ------------------------------------------------------------------
    if action == CRUDAction.DELETE:
        if payload.nk_id is None:
            raise validation_error(
                [("payload.nk_id", "nk_id is required for DELETE action")]
            )
        try:
            nikaya_service.delete_entry(
                db,
                entity_id=payload.nk_id,
                actor_id=user_id,
            )
            return NikayaManagementResponse(
                status="success",
                message="Nikaya record deleted successfully.",
                data=None,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
            ) from exc

    raise validation_error([("action", "Invalid action specified")])


@router.post(
    "/set-mahanayaka",
    response_model=SetMahanayakaResponse,
    dependencies=[has_any_permission(
        "system:create", "system:update",
        "vihara:create", "vihara:update",
        "bhikku:create", "bhikku:update",
    )],
)
def set_nikaya_mahanayaka(
    request: SetMahanayakaRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """Assign a bhikku as the Mahanayaka of a nikaya.

    Identify the nikaya by **nk_id** or **nk_nkn** (at least one is required).
    Provide the bhikku registration number via **br_regn**.
    Optionally supply **nk_startdate** and **nk_rmakrs**.
    """
    if request.nk_id is None and not request.nk_nkn:
        raise validation_error(
            [("nk_id", "Either nk_id or nk_nkn is required to identify the nikaya")]
        )

    actor_id = current_user.ua_user_id
    try:
        updated = nikaya_service.set_mahanayaka(
            db,
            nk_id=request.nk_id,
            nk_nkn=request.nk_nkn,
            br_regn=request.br_regn,
            nk_startdate=request.nk_startdate,
            nk_rmakrs=request.nk_rmakrs,
            actor_id=actor_id,
        )
    except ValueError as exc:
        message = str(exc)
        if "not found" in message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=message
            ) from exc
        raise validation_error([(None, message)]) from exc

    nikaya_out = NikayaOut.model_validate(updated)

    # Build assigned bhikku info from the joined relationship
    bhikku_info: AssignedBhikkuInfo | None = None
    if updated.main_bhikku_info is not None:
        bhikku_info = AssignedBhikkuInfo(
            br_regn=updated.main_bhikku_info.br_regn,
            br_mahananame=updated.main_bhikku_info.br_mahananame,
            br_gihiname=updated.main_bhikku_info.br_gihiname,
        )

    return SetMahanayakaResponse(
        status="success",
        message="Mahanayaka assigned successfully.",
        data=nikaya_out,
        assigned_bhikku=bhikku_info,
    )


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _format_validation_errors(exc: ValidationError) -> list[tuple[str | None, str]]:
    results: list[tuple[str | None, str]] = []
    for error in exc.errors():
        loc = ".".join(str(item) for item in error.get("loc", []))
        message = error.get("msg", "")
        results.append((loc or None, message))
    return results or [(None, "Invalid payload data")]


def _extract_payload(
    data: NikayaCreate | NikayaUpdate | dict | None,
    *,
    exclude_unset: bool = False,
) -> dict:
    if data is None:
        raise TypeError("Payload data cannot be null.")
    if isinstance(data, BaseModel):
        return data.model_dump(exclude_unset=exclude_unset)
    if isinstance(data, dict):
        return data
    raise TypeError("Payload data must be an object.")
