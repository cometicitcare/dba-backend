# app/api/v1/routes/religion.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, ValidationError

from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission, has_any_permission
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas.religion import (
    CRUDAction,
    ReligionCreate,
    ReligionManagementRequest,
    ReligionManagementResponse,
    ReligionOut,
    ReligionUpdate,
)
from app.services.religion_service import religion_service
from app.utils.http_exceptions import validation_error

router = APIRouter(tags=["Religion"])


@router.post("/manage", response_model=ReligionManagementResponse, dependencies=[has_any_permission("system:create", "system:update", "system:delete")])
def manage_religion_records(
    request: ReligionManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    action = request.action
    payload = request.payload
    user_id = current_user.ua_user_id

    if action == CRUDAction.CREATE:
        if not payload.data:
            raise validation_error(
                [("payload.data", "Valid data is required for CREATE action")]
            )
        try:
            create_raw = _extract_payload(payload.data)
            create_payload = ReligionCreate.model_validate(create_raw)
        except ValidationError as exc:
            raise validation_error(_format_validation_errors(exc)) from exc
        except TypeError as exc:
            raise validation_error([(None, str(exc))]) from exc
        try:
            created = religion_service.create_religion(
                db, payload=create_payload, actor_id=user_id
            )
            created_out = ReligionOut.model_validate(created)
            return ReligionManagementResponse(
                status="success",
                message="Religion created successfully.",
                data=created_out,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    if action == CRUDAction.READ_ONE:
        identifier_id = payload.rl_id
        identifier_code = payload.rl_code
        if identifier_id is None and not identifier_code:
            raise validation_error(
                [("payload.rl_id", "rl_id or rl_code is required for READ_ONE action")]
            )

        entity = None
        if identifier_id is not None:
            entity = religion_service.get_religion(db, identifier_id)
        elif identifier_code:
            entity = religion_service.get_religion_by_code(db, identifier_code)

        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Religion not found"
            )

        entity_out = ReligionOut.model_validate(entity)
        return ReligionManagementResponse(
            status="success",
            message="Religion retrieved successfully.",
            data=entity_out,
        )

    if action == CRUDAction.READ_ALL:
        page = payload.page or 1
        limit = payload.limit
        search = payload.search_key.strip() if payload.search_key else None
        if search == "":
            search = None
        skip = payload.skip if payload.page is None else (page - 1) * limit

        records = religion_service.list_religions(
            db, skip=skip, limit=limit, search=search
        )
        total = religion_service.count_religions(db, search=search)

        records_out = [ReligionOut.model_validate(item) for item in records]
        return ReligionManagementResponse(
            status="success",
            message="Religion records retrieved successfully.",
            data=records_out,
            totalRecords=total,
            page=page,
            limit=limit,
        )

    if action == CRUDAction.UPDATE:
        if payload.rl_id is None:
            raise validation_error(
                [("payload.rl_id", "rl_id is required for UPDATE action")]
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
            update_payload = ReligionUpdate.model_validate(update_raw)
        except ValidationError as exc:
            raise validation_error(_format_validation_errors(exc)) from exc
        try:
            updated = religion_service.update_religion(
                db,
                rl_id=payload.rl_id,
                payload=update_payload,
                actor_id=user_id,
            )
            updated_out = ReligionOut.model_validate(updated)
            return ReligionManagementResponse(
                status="success",
                message="Religion updated successfully.",
                data=updated_out,
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=message
                ) from exc
            raise validation_error([(None, message)]) from exc

    if action == CRUDAction.DELETE:
        if payload.rl_id is None:
            raise validation_error(
                [("payload.rl_id", "rl_id is required for DELETE action")]
            )
        try:
            religion_service.delete_religion(
                db,
                rl_id=payload.rl_id,
                actor_id=user_id,
            )
            return ReligionManagementResponse(
                status="success",
                message="Religion deleted successfully.",
                data=None,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
            ) from exc

    raise validation_error([("action", "Invalid action specified")])


def _format_validation_errors(exc: ValidationError) -> list[tuple[str | None, str]]:
    results: list[tuple[str | None, str]] = []
    for error in exc.errors():
        loc = ".".join(str(item) for item in error.get("loc", []))
        message = error.get("msg", "")
        results.append((loc or None, message))
    return results or [(None, "Invalid payload data")]


def _extract_payload(
    data: ReligionCreate | ReligionUpdate | dict | None,
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
