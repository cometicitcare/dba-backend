from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas import gramasewaka as schemas
from app.services.gramasewaka_service import gramasewaka_service
from app.utils.http_exceptions import validation_error
from pydantic import ValidationError

router = APIRouter()


@router.post("/manage", response_model=schemas.GramasewakaManagementResponse)
def manage_gramasewaka_records(
    request: schemas.GramasewakaManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    action = request.action
    payload = request.payload
    user_id = current_user.ua_user_id

    if action == schemas.CRUDAction.CREATE:
        if not payload.data:
            raise validation_error(
                [("payload.data", "data is required for CREATE action")]
            )

        create_payload: schemas.GramasewakaCreate
        if isinstance(payload.data, schemas.GramasewakaCreate):
            create_payload = payload.data
        else:
            raw_data = (
                payload.data.model_dump()
                if hasattr(payload.data, "model_dump")
                else payload.data
            )
            try:
                create_payload = schemas.GramasewakaCreate(**raw_data)
            except ValidationError as exc:
                formatted_errors = []
                for error in exc.errors():
                    loc = ".".join(str(part) for part in error.get("loc", []))
                    formatted_errors.append(
                        (loc or None, error.get("msg", "Invalid data"))
                    )
                raise validation_error(formatted_errors) from exc

        try:
            created = gramasewaka_service.create_gramasewaka(
                db, payload=create_payload, actor_id=user_id
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        return {
            "status": "success",
            "message": "Gramasewaka created successfully.",
            "data": created,
        }

    if action == schemas.CRUDAction.READ_ONE:
        if payload.gn_id is None and not payload.gn_gnc:
            raise validation_error(
                [
                    (
                        "payload.gn_id",
                        "gn_id or gn_gnc is required for READ_ONE action",
                    )
                ]
            )

        entity = None
        if payload.gn_id is not None:
            entity = gramasewaka_service.get_gramasewaka(db, gn_id=payload.gn_id)
        elif payload.gn_gnc:
            entity = gramasewaka_service.get_gramasewaka_by_code(
                db, gn_gnc=payload.gn_gnc
            )

        if not entity:
            raise HTTPException(status_code=404, detail="Gramasewaka not found")

        return {
            "status": "success",
            "message": "Gramasewaka retrieved successfully.",
            "data": entity,
        }

    if action == schemas.CRUDAction.READ_ALL:
        page = payload.page if payload.page is not None else 1
        limit = payload.limit
        search = payload.search_key.strip() if payload.search_key else None
        if search == "":
            search = None
        skip = payload.skip if payload.page is None else (page - 1) * limit
        skip = max(0, skip)
        limit = max(1, min(limit, 200))

        records = gramasewaka_service.list_gramasewaka(
            db, skip=skip, limit=limit, search=search
        )
        total = gramasewaka_service.count_gramasewaka(db, search=search)

        return {
            "status": "success",
            "message": "Gramasewaka records retrieved successfully.",
            "data": records,
            "totalRecords": total,
            "page": page,
            "limit": limit,
        }

    if action == schemas.CRUDAction.UPDATE:
        if payload.gn_id is None:
            raise validation_error(
                [("payload.gn_id", "gn_id is required for UPDATE action")]
            )
        if not payload.data:
            raise validation_error(
                [("payload.data", "data is required for UPDATE action")]
            )

        update_payload: schemas.GramasewakaUpdate
        if isinstance(payload.data, schemas.GramasewakaUpdate):
            update_payload = payload.data
        else:
            raw_data = (
                payload.data.model_dump()
                if hasattr(payload.data, "model_dump")
                else payload.data
            )
            try:
                update_payload = schemas.GramasewakaUpdate(**raw_data)
            except ValidationError as exc:
                formatted_errors = []
                for error in exc.errors():
                    loc = ".".join(str(part) for part in error.get("loc", []))
                    formatted_errors.append(
                        (loc or None, error.get("msg", "Invalid data"))
                    )
                raise validation_error(formatted_errors) from exc

        try:
            updated = gramasewaka_service.update_gramasewaka(
                db, gn_id=payload.gn_id, payload=update_payload, actor_id=user_id
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message) from exc
            raise validation_error([(None, message)]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        return {
            "status": "success",
            "message": "Gramasewaka updated successfully.",
            "data": updated,
        }

    if action == schemas.CRUDAction.DELETE:
        if payload.gn_id is None:
            raise validation_error(
                [("payload.gn_id", "gn_id is required for DELETE action")]
            )

        try:
            gramasewaka_service.delete_gramasewaka(
                db, gn_id=payload.gn_id, actor_id=user_id
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message) from exc
            raise validation_error([(None, message)]) from exc

        return {
            "status": "success",
            "message": "Gramasewaka deleted successfully.",
            "data": None,
        }

    raise validation_error([("action", "Invalid action specified")])
