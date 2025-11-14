from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission, has_any_permission
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas.bhikku_category import (
    BhikkuCategoryCreate,
    BhikkuCategoryManagementRequest,
    BhikkuCategoryManagementResponse,
    BhikkuCategoryOut,
    BhikkuCategoryUpdate,
    CRUDAction,
)
from app.services.bhikku_category_service import bhikku_category_service
from app.utils.http_exceptions import validation_error

router = APIRouter(tags=["Bhikku Category"])


@router.post("/manage", response_model=BhikkuCategoryManagementResponse, dependencies=[has_any_permission("bhikku:create", "bhikku:update", "bhikku:delete")])
def manage_bhikku_categories(
    request: BhikkuCategoryManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    action = request.action
    payload = request.payload
    user_id = current_user.ua_user_id

    if action == CRUDAction.CREATE:
        if not payload.data:
            raise validation_error(
                [("payload.data", "data is required for CREATE action")]
            )

        create_payload: BhikkuCategoryCreate
        if isinstance(payload.data, BhikkuCategoryCreate):
            create_payload = payload.data
        else:
            raw_data = (
                payload.data.model_dump()
                if hasattr(payload.data, "model_dump")
                else payload.data
            )
            try:
                create_payload = BhikkuCategoryCreate(**raw_data)
            except ValidationError as exc:
                formatted_errors = []
                for error in exc.errors():
                    loc = ".".join(str(part) for part in error.get("loc", []))
                    formatted_errors.append(
                        (loc or None, error.get("msg", "Invalid data"))
                    )
                raise validation_error(formatted_errors) from exc

        try:
            created = bhikku_category_service.create_category(
                db, payload=create_payload, actor_id=user_id
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        return BhikkuCategoryManagementResponse(
            status="success",
            message="Bhikku category created successfully.",
            data=BhikkuCategoryOut.model_validate(created),
        )

    if action == CRUDAction.READ_ONE:
        if payload.cc_id is None and not payload.cc_code:
            raise validation_error(
                [("payload.cc_id", "cc_id or cc_code is required for READ_ONE action")]
            )

        entity = None
        if payload.cc_id is not None:
            entity = bhikku_category_service.get_category(db, cc_id=payload.cc_id)
        elif payload.cc_code:
            entity = bhikku_category_service.get_category_by_code(
                db, cc_code=payload.cc_code
            )

        if not entity:
            raise HTTPException(status_code=404, detail="Bhikku category not found")

        return BhikkuCategoryManagementResponse(
            status="success",
            message="Bhikku category retrieved successfully.",
            data=BhikkuCategoryOut.model_validate(entity),
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

        records = bhikku_category_service.list_categories(
            db, skip=skip, limit=limit, search=search
        )
        total = bhikku_category_service.count_categories(db, search=search)
        records_out = [BhikkuCategoryOut.model_validate(item) for item in records]

        return BhikkuCategoryManagementResponse(
            status="success",
            message="Bhikku categories retrieved successfully.",
            data=records_out,
            totalRecords=total,
            page=page,
            limit=limit,
        )

    if action == CRUDAction.UPDATE:
        if payload.cc_id is None:
            raise validation_error(
                [("payload.cc_id", "cc_id is required for UPDATE action")]
            )
        if not payload.data:
            raise validation_error(
                [("payload.data", "data is required for UPDATE action")]
            )

        update_payload: BhikkuCategoryUpdate
        if isinstance(payload.data, BhikkuCategoryUpdate):
            update_payload = payload.data
        else:
            raw_data = (
                payload.data.model_dump()
                if hasattr(payload.data, "model_dump")
                else payload.data
            )
            try:
                update_payload = BhikkuCategoryUpdate(**raw_data)
            except ValidationError as exc:
                formatted_errors = []
                for error in exc.errors():
                    loc = ".".join(str(part) for part in error.get("loc", []))
                    formatted_errors.append(
                        (loc or None, error.get("msg", "Invalid data"))
                    )
                raise validation_error(formatted_errors) from exc

        try:
            updated = bhikku_category_service.update_category(
                db, cc_id=payload.cc_id, payload=update_payload, actor_id=user_id
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message) from exc
            raise validation_error([(None, message)]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        return BhikkuCategoryManagementResponse(
            status="success",
            message="Bhikku category updated successfully.",
            data=BhikkuCategoryOut.model_validate(updated),
        )

    if action == CRUDAction.DELETE:
        if payload.cc_id is None:
            raise validation_error(
                [("payload.cc_id", "cc_id is required for DELETE action")]
            )

        try:
            bhikku_category_service.delete_category(
                db, cc_id=payload.cc_id, actor_id=user_id
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message) from exc
            raise validation_error([(None, message)]) from exc

        return BhikkuCategoryManagementResponse(
            status="success",
            message="Bhikku category deleted successfully.",
            data=None,
        )

    raise validation_error([("action", "Invalid action specified")])
