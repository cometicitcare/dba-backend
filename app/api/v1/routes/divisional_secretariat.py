from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas.divisional_secretariat import (
    CRUDAction,
    DivisionalSecretariatCreate,
    DivisionalSecretariatManagementRequest,
    DivisionalSecretariatManagementResponse,
    DivisionalSecretariatOut,
    DivisionalSecretariatUpdate,
)
from app.services.divisional_secretariat_service import (
    divisional_secretariat_service,
)
from app.utils.http_exceptions import validation_error
from app.utils.authorization import ensure_crud_permission

router = APIRouter(tags=["Divisional Secretariat"])


@router.post("/manage", response_model=DivisionalSecretariatManagementResponse)
def manage_divisional_secretariat_records(
    request: DivisionalSecretariatManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    action = request.action
    payload = request.payload
    user_id = current_user.ua_user_id
    ensure_crud_permission(db, user_id, "divisional_secretariat", action)

    if action == CRUDAction.CREATE:
        if not payload.data or not isinstance(payload.data, DivisionalSecretariatCreate):
            raise validation_error(
                [("payload.data", "Invalid data for CREATE action")]
            )
        try:
            created = divisional_secretariat_service.create_divisional_secretariat(
                db, payload=payload.data, actor_id=user_id
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        return DivisionalSecretariatManagementResponse(
            status="success",
            message="Divisional secretariat created successfully.",
            data=DivisionalSecretariatOut.model_validate(created),
        )

    if action == CRUDAction.READ_ONE:
        if payload.dv_id is None and not payload.dv_dvcode:
            raise validation_error(
                [
                    (
                        "payload.dv_id",
                        "dv_id or dv_dvcode is required for READ_ONE action",
                    )
                ]
            )

        entity = None
        if payload.dv_id is not None:
            entity = divisional_secretariat_service.get_divisional_secretariat(
                db, dv_id=payload.dv_id
            )
        elif payload.dv_dvcode:
            entity = (
                divisional_secretariat_service.get_divisional_secretariat_by_code(
                    db, dv_dvcode=payload.dv_dvcode
                )
            )

        if not entity:
            raise HTTPException(status_code=404, detail="Divisional secretariat not found")

        return DivisionalSecretariatManagementResponse(
            status="success",
            message="Divisional secretariat retrieved successfully.",
            data=DivisionalSecretariatOut.model_validate(entity),
        )

    if action == CRUDAction.READ_ALL:
        page = payload.page if payload.page is not None else 1
        limit = payload.limit
        search = payload.search_key.strip() if payload.search_key else None
        if search == "":
            search = None
        skip = payload.skip if payload.page is None else (page - 1) * limit

        limit = max(1, min(limit, 200))
        skip = max(0, skip)

        records = divisional_secretariat_service.list_divisional_secretariats(
            db, skip=skip, limit=limit, search=search
        )
        total = divisional_secretariat_service.count_divisional_secretariats(
            db, search=search
        )
        records_out = [DivisionalSecretariatOut.model_validate(item) for item in records]

        return DivisionalSecretariatManagementResponse(
            status="success",
            message="Divisional secretariats retrieved successfully.",
            data=records_out,
            totalRecords=total,
            page=page,
            limit=limit,
        )

    if action == CRUDAction.UPDATE:
        if payload.dv_id is None:
            raise validation_error(
                [("payload.dv_id", "dv_id is required for UPDATE action")]
            )
        if not payload.data:
            raise validation_error(
                [("payload.data", "Invalid data for UPDATE action")]
            )

        update_payload: DivisionalSecretariatUpdate
        if isinstance(payload.data, DivisionalSecretariatUpdate):
            update_payload = payload.data
        else:
            raw_data = (
                payload.data.model_dump()
                if hasattr(payload.data, "model_dump")
                else payload.data
            )
            try:
                update_payload = DivisionalSecretariatUpdate(**raw_data)
            except ValidationError as exc:
                formatted_errors = []
                for error in exc.errors():
                    loc = ".".join(str(part) for part in error.get("loc", []))
                    formatted_errors.append(
                        (loc or None, error.get("msg", "Invalid data"))
                    )
                raise validation_error(formatted_errors) from exc

        try:
            updated = divisional_secretariat_service.update_divisional_secretariat(
                db, dv_id=payload.dv_id, payload=update_payload, actor_id=user_id
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message) from exc
            raise validation_error([(None, message)]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        return DivisionalSecretariatManagementResponse(
            status="success",
            message="Divisional secretariat updated successfully.",
            data=DivisionalSecretariatOut.model_validate(updated),
        )

    if action == CRUDAction.DELETE:
        if payload.dv_id is None:
            raise validation_error(
                [("payload.dv_id", "dv_id is required for DELETE action")]
            )

        try:
            divisional_secretariat_service.delete_divisional_secretariat(
                db, dv_id=payload.dv_id, actor_id=user_id
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message) from exc
            raise validation_error([(None, message)]) from exc

        return DivisionalSecretariatManagementResponse(
            status="success",
            message="Divisional secretariat deleted successfully.",
            data=None,
        )

    raise validation_error([("action", "Invalid action specified")])
