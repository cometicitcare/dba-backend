from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas.district import (
    CRUDAction,
    DistrictCreate,
    DistrictManagementRequest,
    DistrictManagementResponse,
    DistrictOut,
    DistrictUpdate,
)
from app.services.district_service import district_service
from app.utils.http_exceptions import validation_error

router = APIRouter(tags=["District"])


@router.post("/manage", response_model=DistrictManagementResponse)
def manage_districts(
    request: DistrictManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    action = request.action
    payload = request.payload
    user_id = current_user.ua_user_id

    if action == CRUDAction.CREATE:
        if not payload.data or not isinstance(payload.data, DistrictCreate):
            raise validation_error(
                [("payload.data", "Invalid data for CREATE action")]
            )
        try:
            created = district_service.create_district(
                db, payload=payload.data, actor_id=user_id
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        return DistrictManagementResponse(
            status="success",
            message="District created successfully.",
            data=DistrictOut.model_validate(created),
        )

    if action == CRUDAction.READ_ONE:
        if payload.dd_id is None and not payload.dd_dcode:
            raise validation_error(
                [("payload.dd_id", "dd_id or dd_dcode is required for READ_ONE action")]
            )

        entity = None
        if payload.dd_id is not None:
            entity = district_service.get_district(db, dd_id=payload.dd_id)
        elif payload.dd_dcode:
            entity = district_service.get_district_by_code(
                db, dd_dcode=payload.dd_dcode
            )

        if not entity:
            raise HTTPException(status_code=404, detail="District not found")

        return DistrictManagementResponse(
            status="success",
            message="District retrieved successfully.",
            data=DistrictOut.model_validate(entity),
        )

    if action == CRUDAction.READ_ALL:
        page = payload.page if payload.page is not None else 1
        limit = payload.limit
        search = payload.search_key.strip() if payload.search_key else None
        if search == "":
            search = None
        skip = payload.skip if payload.page is None else (page - 1) * limit
        province_code = payload.dd_prcode

        limit = max(1, min(limit, 200))
        skip = max(0, skip)

        records = district_service.list_districts(
            db, skip=skip, limit=limit, search=search, province_code=province_code
        )
        total = district_service.count_districts(
            db, search=search, province_code=province_code
        )
        records_out = [DistrictOut.model_validate(item) for item in records]

        return DistrictManagementResponse(
            status="success",
            message="Districts retrieved successfully.",
            data=records_out,
            totalRecords=total,
            page=page,
            limit=limit,
        )

    if action == CRUDAction.UPDATE:
        if payload.dd_id is None:
            raise validation_error(
                [("payload.dd_id", "dd_id is required for UPDATE action")]
            )
        if not payload.data:
            raise validation_error(
                [("payload.data", "Invalid data for UPDATE action")]
            )

        update_payload: DistrictUpdate
        if isinstance(payload.data, DistrictUpdate):
            update_payload = payload.data
        else:
            raw_data = (
                payload.data.model_dump()
                if hasattr(payload.data, "model_dump")
                else payload.data
            )
            try:
                update_payload = DistrictUpdate(**raw_data)
            except ValidationError as exc:
                formatted_errors = []
                for error in exc.errors():
                    loc = ".".join(str(part) for part in error.get("loc", []))
                    formatted_errors.append(
                        (loc or None, error.get("msg", "Invalid data"))
                    )
                raise validation_error(formatted_errors) from exc

        try:
            updated = district_service.update_district(
                db, dd_id=payload.dd_id, payload=update_payload, actor_id=user_id
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message) from exc
            raise validation_error([(None, message)]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        return DistrictManagementResponse(
            status="success",
            message="District updated successfully.",
            data=DistrictOut.model_validate(updated),
        )

    if action == CRUDAction.DELETE:
        if payload.dd_id is None:
            raise validation_error(
                [("payload.dd_id", "dd_id is required for DELETE action")]
            )

        try:
            district_service.delete_district(db, dd_id=payload.dd_id, actor_id=user_id)
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message) from exc
            raise validation_error([(None, message)]) from exc

        return DistrictManagementResponse(
            status="success",
            message="District deleted successfully.",
            data=None,
        )

    raise validation_error([("action", "Invalid action specified")])
