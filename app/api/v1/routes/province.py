from typing import Any, Type, TypeVar

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission, has_any_permission
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas.province import (
    CRUDAction,
    ProvinceCreate,
    ProvinceManagementRequest,
    ProvinceManagementResponse,
    ProvinceOut,
    ProvinceUpdate,
)
from app.services.province_service import province_service
from app.utils.http_exceptions import validation_error

router = APIRouter(tags=["Province"])

PayloadModel = TypeVar("PayloadModel", bound=BaseModel)


@router.post("/manage", response_model=ProvinceManagementResponse, dependencies=[has_any_permission("system:create", "system:update", "system:delete")])
def manage_provinces(
    request: ProvinceManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    action = request.action
    payload = request.payload
    user_id = current_user.ua_user_id

    if action == CRUDAction.CREATE:
        if not payload.data:
            raise validation_error(
                [("payload.data", "Invalid data for CREATE action")]
            )
        try:
            create_payload = _parse_payload(payload.data, ProvinceCreate)
        except ValidationError as exc:
            raise validation_error(_format_validation_errors(exc)) from exc
        try:
            created = province_service.create_province(
                db, payload=create_payload, actor_id=user_id
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        return ProvinceManagementResponse(
            status="success",
            message="Province created successfully.",
            data=ProvinceOut.model_validate(created),
        )

    if action == CRUDAction.READ_ONE:
        if payload.cp_id is None and not payload.cp_code:
            raise validation_error(
                [("payload.cp_id", "cp_id or cp_code is required for READ_ONE action")]
            )

        entity = None
        if payload.cp_id is not None:
            entity = province_service.get_province(db, cp_id=payload.cp_id)
        elif payload.cp_code:
            entity = province_service.get_province_by_code(
                db, cp_code=payload.cp_code
            )

        if not entity:
            raise HTTPException(status_code=404, detail="Province not found")

        return ProvinceManagementResponse(
            status="success",
            message="Province retrieved successfully.",
            data=ProvinceOut.model_validate(entity),
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

        records = province_service.list_provinces(
            db, skip=skip, limit=limit, search=search
        )
        total = province_service.count_provinces(db, search=search)
        records_out = [ProvinceOut.model_validate(item) for item in records]

        return ProvinceManagementResponse(
            status="success",
            message="Provinces retrieved successfully.",
            data=records_out,
            totalRecords=total,
            page=page,
            limit=limit,
        )

    if action == CRUDAction.UPDATE:
        if payload.cp_id is None:
            raise validation_error(
                [("payload.cp_id", "cp_id is required for UPDATE action")]
            )
        if not payload.data:
            raise validation_error(
                [("payload.data", "Invalid data for UPDATE action")]
            )
        try:
            update_payload = _parse_payload(payload.data, ProvinceUpdate)
        except ValidationError as exc:
            raise validation_error(_format_validation_errors(exc)) from exc
        try:
            updated = province_service.update_province(
                db, cp_id=payload.cp_id, payload=update_payload, actor_id=user_id
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message) from exc
            raise validation_error([(None, message)]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        return ProvinceManagementResponse(
            status="success",
            message="Province updated successfully.",
            data=ProvinceOut.model_validate(updated),
        )

    if action == CRUDAction.DELETE:
        if payload.cp_id is None:
            raise validation_error(
                [("payload.cp_id", "cp_id is required for DELETE action")]
            )

        try:
            province_service.delete_province(db, cp_id=payload.cp_id, actor_id=user_id)
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message) from exc
            raise validation_error([(None, message)]) from exc

        return ProvinceManagementResponse(
            status="success",
            message="Province deleted successfully.",
            data=None,
        )

    raise validation_error([("action", "Invalid action specified")])


def _parse_payload(data: Any, model_cls: Type[PayloadModel]) -> PayloadModel:
    if isinstance(data, model_cls):
        return data
    if isinstance(data, BaseModel):
        raw = data.model_dump()
    else:
        raw = data
    return model_cls.model_validate(raw)


def _format_validation_errors(exc: ValidationError) -> list[tuple[str | None, str]]:
    formatted = []
    for error in exc.errors():
        loc = error.get("loc") or []
        field = loc[-1] if loc else None
        formatted.append((str(field) if field is not None else None, error.get("msg", "")))
    return formatted
