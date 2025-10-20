from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas.vihara import (
    CRUDAction,
    ViharaCreate,
    ViharaManagementRequest,
    ViharaManagementResponse,
    ViharaOut,
    ViharaUpdate,
)
from app.services.vihara_service import vihara_service

router = APIRouter(tags=["Vihara Data"])


@router.post("/manage", response_model=ViharaManagementResponse)
def manage_vihara_records(
    request: ViharaManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    action = request.action
    payload = request.payload
    user_id = current_user.ua_user_id

    if action == CRUDAction.CREATE:
        if not payload.data or not isinstance(payload.data, ViharaCreate):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid data for CREATE action",
            )
        try:
            created = vihara_service.create_vihara(
                db, payload=payload.data, actor_id=user_id
            )
            return ViharaManagementResponse(
                status="success",
                message="Vihara created successfully.",
                data=created,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
            ) from exc

    if action == CRUDAction.READ_ONE:
        identifier_id = payload.vh_id
        identifier_trn = payload.vh_trn
        if identifier_id is None and not identifier_trn:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="vh_id or vh_trn is required for READ_ONE action",
            )

        entity: ViharaOut | None = None
        if identifier_id is not None:
            entity = vihara_service.get_vihara(db, identifier_id)
        elif identifier_trn:
            entity = vihara_service.get_vihara_by_trn(db, identifier_trn)

        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Vihara not found"
            )

        return ViharaManagementResponse(
            status="success",
            message="Vihara retrieved successfully.",
            data=entity,
        )

    if action == CRUDAction.READ_ALL:
        page = payload.page or 1
        limit = payload.limit
        search = payload.search_key.strip() if payload.search_key else None
        if search == "":
            search = None
        skip = payload.skip if payload.page is None else (page - 1) * limit

        records = vihara_service.list_viharas(
            db, skip=skip, limit=limit, search=search
        )
        total = vihara_service.count_viharas(db, search=search)
        return ViharaManagementResponse(
            status="success",
            message="Vihara records retrieved successfully.",
            data=records,
            totalRecords=total,
            page=page,
            limit=limit,
        )

    if action == CRUDAction.UPDATE:
        if payload.vh_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="vh_id is required for UPDATE action",
            )
        if not payload.data or not isinstance(payload.data, ViharaUpdate):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid data for UPDATE action",
            )

        try:
            updated = vihara_service.update_vihara(
                db,
                vh_id=payload.vh_id,
                payload=payload.data,
                actor_id=user_id,
            )
            return ViharaManagementResponse(
                status="success",
                message="Vihara updated successfully.",
                data=updated,
            )
        except ValueError as exc:
            if "not found" in str(exc).lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
                ) from exc
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
            ) from exc

    if action == CRUDAction.DELETE:
        if payload.vh_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="vh_id is required for DELETE action",
            )
        try:
            vihara_service.delete_vihara(
                db,
                vh_id=payload.vh_id,
                actor_id=user_id,
            )
            return ViharaManagementResponse(
                status="success",
                message="Vihara deleted successfully.",
                data=None,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
            ) from exc

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid action specified"
    )
