from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas.city import (
    CityCreate,
    CityManagementRequest,
    CityManagementResponse,
    CityOut,
    CityUpdate,
    CRUDAction,
)
from app.services.city_service import city_service
from app.utils.http_exceptions import validation_error

router = APIRouter(tags=["City"])


@router.post("/manage", response_model=CityManagementResponse)
def manage_city_records(
    request: CityManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    action = request.action
    payload = request.payload
    user_id = current_user.ua_user_id

    if action == CRUDAction.CREATE:
        if not payload.data or not isinstance(payload.data, CityCreate):
            raise validation_error(
                [("payload.data", "Invalid data for CREATE action")]
            )
        try:
            created = city_service.create_city(
                db, payload=payload.data, actor_id=user_id
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        return CityManagementResponse(
            status="success",
            message="City created successfully.",
            data=CityOut.model_validate(created),
        )

    if action == CRUDAction.READ_ONE:
        if payload.ct_id is None and not payload.ct_code:
            raise validation_error(
                [("payload.ct_id", "ct_id or ct_code is required for READ_ONE action")]
            )

        entity = None
        if payload.ct_id is not None:
            entity = city_service.get_city(db, ct_id=payload.ct_id)
        elif payload.ct_code:
            entity = city_service.get_city_by_code(db, ct_code=payload.ct_code)

        if not entity:
            raise HTTPException(status_code=404, detail="City not found")

        return CityManagementResponse(
            status="success",
            message="City retrieved successfully.",
            data=CityOut.model_validate(entity),
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

        records = city_service.list_cities(
            db, skip=skip, limit=limit, search=search
        )
        total = city_service.count_cities(db, search=search)
        records_out = [CityOut.model_validate(item) for item in records]

        return CityManagementResponse(
            status="success",
            message="Cities retrieved successfully.",
            data=records_out,
            totalRecords=total,
            page=page,
            limit=limit,
        )

    if action == CRUDAction.UPDATE:
        if payload.ct_id is None:
            raise validation_error(
                [("payload.ct_id", "ct_id is required for UPDATE action")]
            )
        if not payload.data or not isinstance(payload.data, CityUpdate):
            raise validation_error(
                [("payload.data", "Invalid data for UPDATE action")]
            )

        try:
            updated = city_service.update_city(
                db, ct_id=payload.ct_id, payload=payload.data, actor_id=user_id
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message) from exc
            raise validation_error([(None, message)]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        return CityManagementResponse(
            status="success",
            message="City updated successfully.",
            data=CityOut.model_validate(updated),
        )

    if action == CRUDAction.DELETE:
        if payload.ct_id is None:
            raise validation_error(
                [("payload.ct_id", "ct_id is required for DELETE action")]
            )

        try:
            city_service.delete_city(db, ct_id=payload.ct_id, actor_id=user_id)
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message) from exc
            raise validation_error([(None, message)]) from exc

        return CityManagementResponse(
            status="success",
            message="City deleted successfully.",
            data=None,
        )

    raise validation_error([("action", "Invalid action specified")])
