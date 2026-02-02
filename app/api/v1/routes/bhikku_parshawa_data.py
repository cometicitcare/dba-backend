from pydantic import ValidationError
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission, has_any_permission
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas.parshawadata import (
    CRUDAction,
    ParshawaCreate,
    ParshawaManagementRequest,
    ParshawaManagementResponse,
    ParshawaOut,
    ParshawaUpdate,
)
from app.services.parshawadata_service import parshawa_service
from app.utils.http_exceptions import validation_error

router = APIRouter()  # Tags defined in router.py


@router.post("/manage", response_model=ParshawaManagementResponse, dependencies=[has_any_permission("bhikku:create", "bhikku:update", "bhikku:delete")])
def manage_parshawa_records(
    request: ParshawaManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    action = request.action
    payload = request.payload
    user_id = current_user.ua_user_id

    if action == CRUDAction.CREATE:
        if not payload.data or not isinstance(payload.data, ParshawaCreate):
            raise validation_error(
                [("payload.data", "Invalid data for CREATE action")]
            )
        try:
            created = parshawa_service.create(
                db, payload=payload.data, actor_id=user_id
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

        created_out = ParshawaOut.model_validate(created)
        return ParshawaManagementResponse(
            status="success",
            message="Parshawa data created successfully.",
            data=created_out,
        )

    if action == CRUDAction.READ_ONE:
        if payload.pr_id is None and not payload.pr_prn:
            raise validation_error(
                [("payload.pr_id", "pr_id or pr_prn is required for READ_ONE action")]
            )

        entity = None
        if payload.pr_id is not None:
            entity = parshawa_service.get(db, payload.pr_id)
        elif payload.pr_prn:
            entity = parshawa_service.get_by_prn(db, payload.pr_prn)

        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parshawa data record not found",
            )

        entity_out = ParshawaOut.model_validate(entity)
        return ParshawaManagementResponse(
            status="success",
            message="Parshawa data retrieved successfully.",
            data=entity_out,
        )

    if action == CRUDAction.READ_ALL:
        page = payload.page if payload.page is not None else 1
        limit = payload.limit
        search = payload.search_key.strip() if payload.search_key else None
        if search == "":
            search = None
        skip = payload.skip if payload.page is None else (page - 1) * limit

        records = parshawa_service.list(
            db, skip=skip, limit=limit, search=search
        )
        total = parshawa_service.count(db, search=search)

        records_out = [ParshawaOut.model_validate(item) for item in records]
        return ParshawaManagementResponse(
            status="success",
            message="Parshawa data records retrieved successfully.",
            data=records_out,
            totalRecords=total,
            page=page,
            limit=limit,
        )

    if action == CRUDAction.UPDATE:
        if payload.pr_id is None:
            raise validation_error(
                [("payload.pr_id", "pr_id is required for UPDATE action")]
            )
        if not payload.data:
            raise validation_error(
                [("payload.data", "data is required for UPDATE action")]
            )

        try:
            if isinstance(payload.data, ParshawaUpdate):
                update_payload = payload.data
            else:
                update_payload = ParshawaUpdate.model_validate(
                    payload.data.model_dump(exclude_unset=True)
                    if hasattr(payload.data, "model_dump")
                    else payload.data
                )
        except ValidationError as exc:
            error_details = []
            for err in exc.errors():
                loc = ".".join(str(item) for item in err.get("loc", []))
                field = f"payload.data.{loc}" if loc else "payload.data"
                error_details.append((field, err.get("msg", "Invalid value")))
            raise validation_error(error_details) from exc

        if not update_payload.model_dump(exclude_unset=True):
            raise validation_error(
                [("payload.data", "At least one field must be provided for update")]
            )

        entity = parshawa_service.get(db, payload.pr_id)
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parshawa data record not found",
            )

        try:
            updated = parshawa_service.update(
                db, entity=entity, payload=update_payload, actor_id=user_id
            )
        except ValueError as exc:
            message = str(exc)
            if "not exist" in message.lower():
                raise validation_error([(None, message)]) from exc
            if "not found" in message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=message,
                ) from exc
            raise validation_error([(None, message)]) from exc

        updated_out = ParshawaOut.model_validate(updated)
        return ParshawaManagementResponse(
            status="success",
            message="Parshawa data updated successfully.",
            data=updated_out,
        )

    if action == CRUDAction.DELETE:
        if payload.pr_id is None:
            raise validation_error(
                [("payload.pr_id", "pr_id is required for DELETE action")]
            )

        entity = parshawa_service.get(db, payload.pr_id)
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parshawa data record not found",
            )

        try:
            parshawa_service.soft_delete(
                db,
                entity=entity,
                actor_id=user_id,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

        return ParshawaManagementResponse(
            status="success",
            message="Parshawa data deleted successfully.",
            data=None,
        )

    raise validation_error([("action", "Invalid action specified")])
