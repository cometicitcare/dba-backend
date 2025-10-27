from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas import bhikku as schemas
from app.services.bhikku_service import bhikku_service
from app.utils.http_exceptions import validation_error

router = APIRouter(tags=["Bhikku Registration"])


@router.post("/", response_model=schemas.BhikkuManagementResponse)
def manage_bhikku_registrations(
    request: schemas.BhikkuManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    action = request.action
    payload = request.payload
    user_id = current_user.ua_user_id

    if action == schemas.CRUDAction.CREATE:
        if not payload.data or not isinstance(payload.data, schemas.BhikkuCreate):
            raise validation_error(
                [("payload.data", "Invalid data for CREATE action")]
            )
        try:
            created = bhikku_service.create_bhikku(
                db, payload=payload.data, actor_id=user_id
            )
            return schemas.BhikkuManagementResponse(
                status="success",
                message="Bhikku registration created successfully.",
                data=created,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    if action == schemas.CRUDAction.READ_ONE:
        if payload.br_regn:
            entity = bhikku_service.get_bhikku(db, br_regn=payload.br_regn)
        elif payload.br_id is not None:
            entity = bhikku_service.get_bhikku_by_id(db, br_id=payload.br_id)
        else:
            raise validation_error(
                [
                    (
                        "payload.br_regn",
                        "br_regn or br_id is required for READ_ONE action",
                    )
                ]
            )
        if not entity:
            raise HTTPException(
                status_code=404, detail="Bhikku registration not found."
            )
        return schemas.BhikkuManagementResponse(
            status="success",
            message="Bhikku registration retrieved successfully.",
            data=entity,
        )

    if action == schemas.CRUDAction.READ_ALL:
        page = payload.page if payload.page is not None else 1
        limit = payload.limit
        search_key = payload.search_key.strip() if payload.search_key else None
        if search_key == "":
            search_key = None
        skip = payload.skip if payload.page is None else (page - 1) * limit

        records = bhikku_service.list_bhikkus(
            db, skip=skip, limit=limit, search=search_key
        )
        total = bhikku_service.count_bhikkus(db, search=search_key)

        return schemas.BhikkuManagementResponse(
            status="success",
            message="Bhikku registrations retrieved successfully.",
            data=records,
            totalRecords=total,
            page=page,
            limit=limit,
        )

    if action == schemas.CRUDAction.UPDATE:
        target_regn = payload.br_regn
        if not target_regn:
            if payload.br_id is None:
                raise validation_error(
                    [
                        (
                            "payload.br_regn",
                            "br_regn or br_id is required for UPDATE action",
                        )
                    ]
                )
            entity = bhikku_service.get_bhikku_by_id(db, br_id=payload.br_id)
            if not entity:
                raise HTTPException(
                    status_code=404, detail="Bhikku registration not found."
                )
            target_regn = entity.br_regn

        if not payload.data or not isinstance(payload.data, schemas.BhikkuUpdate):
            raise validation_error(
                [("payload.data", "Invalid data for UPDATE action")]
            )

        try:
            updated = bhikku_service.update_bhikku(
                db, br_regn=target_regn, payload=payload.data, actor_id=user_id
            )
            return schemas.BhikkuManagementResponse(
                status="success",
                message="Bhikku registration updated successfully.",
                data=updated,
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message) from exc
            raise validation_error([(None, message)]) from exc

    if action == schemas.CRUDAction.DELETE:
        target_regn = payload.br_regn
        if not target_regn:
            if payload.br_id is None:
                raise validation_error(
                    [
                        (
                            "payload.br_regn",
                            "br_regn or br_id is required for DELETE action",
                        )
                    ]
                )
            entity = bhikku_service.get_bhikku_by_id(db, br_id=payload.br_id)
            if not entity:
                raise HTTPException(
                    status_code=404, detail="Bhikku registration not found."
                )
            target_regn = entity.br_regn

        try:
            bhikku_service.delete_bhikku(
                db,
                br_regn=target_regn,
                actor_id=user_id,
            )
            return schemas.BhikkuManagementResponse(
                status="success",
                message="Bhikku registration deleted successfully.",
                data=None,
            )
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    raise validation_error([("action", "Invalid action specified")])
