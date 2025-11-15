from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission, has_any_permission
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas.nikaya import (
    CRUDAction,
    NikayaCreate,
    NikayaManagementRequest,
    NikayaManagementResponse,
    NikayaOut,
    NikayaUpdate,
)
from app.services.nikaya_service import nikaya_service
from app.utils.http_exceptions import validation_error

router = APIRouter()  # Tags defined in router.py


@router.post("/manage", response_model=NikayaManagementResponse, dependencies=[has_any_permission("bhikku:create", "bhikku:update", "bhikku:delete")])
def manage_bhikku_nikaya_data(
    request: NikayaManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
) -> NikayaManagementResponse:
    action = request.action
    payload = request.payload
    actor_id = current_user.ua_user_id

    if action == CRUDAction.CREATE:
        data = payload.data
        if not isinstance(data, NikayaCreate):
            raise validation_error(
                [("payload.data", "NikayaCreate payload is required for CREATE action")]
            )
        try:
            created = nikaya_service.create_entry(
                db,
                payload=data,
                actor_id=actor_id,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

        return NikayaManagementResponse(
            status="success",
            message="Nikaya data record created successfully.",
            data=NikayaOut.model_validate(created),
        )

    if action == CRUDAction.READ_ONE:
        if payload.nk_id is None and not payload.nk_nkn:
            raise validation_error(
                [
                    (
                        "payload.nk_id",
                        "nk_id or nk_nkn is required for READ_ONE action",
                    )
                ]
            )

        entity = None
        if payload.nk_id is not None:
            entity = nikaya_service.get_by_id(db, payload.nk_id)
        elif payload.nk_nkn:
            entity = nikaya_service.get_by_nkn(db, payload.nk_nkn)

        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nikaya data record not found.",
            )

        return NikayaManagementResponse(
            status="success",
            message="Nikaya data record retrieved successfully.",
            data=NikayaOut.model_validate(entity),
        )

    if action == CRUDAction.READ_ALL:
        page = payload.page if payload.page is not None else 1
        limit = payload.limit
        search = payload.search_key.strip() if payload.search_key else None
        if search == "":
            search = None
        skip = payload.skip if payload.page is None else (page - 1) * limit

        records = nikaya_service.list_entries(
            db,
            skip=skip,
            limit=limit,
            search=search,
        )
        total = nikaya_service.count_entries(db, search=search)

        return NikayaManagementResponse(
            status="success",
            message="Nikaya data records retrieved successfully.",
            data=[NikayaOut.model_validate(item) for item in records],
            totalRecords=total,
            page=page,
            limit=limit,
        )

    if action == CRUDAction.UPDATE:
        data = payload.data
        if payload.nk_id is None:
            raise validation_error(
                [("payload.nk_id", "nk_id is required for UPDATE action")]
            )
        if data is None:
            raise validation_error(
                [("payload.data", "NikayaUpdate payload is required for UPDATE action")]
            )
        if isinstance(data, NikayaCreate):
            data = NikayaUpdate(**data.model_dump())
        if not isinstance(data, NikayaUpdate):
            raise validation_error(
                [("payload.data", "NikayaUpdate payload is required for UPDATE action")]
            )

        try:
            updated = nikaya_service.update_entry(
                db,
                entity_id=payload.nk_id,
                payload=data,
                actor_id=actor_id,
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=message
                ) from exc
            raise validation_error([(None, message)]) from exc

        return NikayaManagementResponse(
            status="success",
            message="Nikaya data record updated successfully.",
            data=NikayaOut.model_validate(updated),
        )

    if action == CRUDAction.DELETE:
        if payload.nk_id is None:
            raise validation_error(
                [("payload.nk_id", "nk_id is required for DELETE action")]
            )
        try:
            nikaya_service.delete_entry(
                db,
                entity_id=payload.nk_id,
                actor_id=actor_id,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
            ) from exc

        return NikayaManagementResponse(
            status="success",
            message="Nikaya data record deleted successfully.",
            data=None,
        )

    raise validation_error([("action", "Invalid action specified")])
