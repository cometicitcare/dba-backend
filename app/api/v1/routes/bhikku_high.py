from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission, has_any_permission
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas import bhikku_high as schemas
from app.services.bhikku_high_service import bhikku_high_service
from app.utils.http_exceptions import validation_error
from app.services.permission_service import permission_service  # New service for permission check
from pydantic import ValidationError

router = APIRouter()  # Tags defined in router.py

# Check if the user has permission to perform an action on Bhikku High
def check_permission(db: Session, user_id: str, permission_name: str):
    permissions = permission_service.get_user_permissions(db, user_id)
    if permission_name not in permissions:
        raise HTTPException(status_code=403, detail="Permission denied")

@router.post("/manage", response_model=schemas.BhikkuHighManagementResponse, dependencies=[has_any_permission("bhikku:create", "bhikku:update", "bhikku:delete")])
def manage_bhikku_high_records(
    request: schemas.BhikkuHighManagementRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # Use get_current_user to get user info from JWT
):
    action = request.action
    payload = request.payload
    user_id = current_user["user_id"]  # Access user ID from the current_user dictionary
    user_role = current_user["role"]   # Access user role from the current_user dictionary
    user_group = current_user["group"]  # Access user group from the current_user dictionary

    # You can now use `user_role` and `user_group` in your response
    print(f"User Role: {user_role}, User Group: {user_group}")

    # Permission checks before CRUD actions
    if action == schemas.CRUDAction.CREATE:
        check_permission(db, user_id, 'CREATE_BHIKKU_HIGH')
        if not payload.data:
            raise validation_error([("payload.data", "data is required for CREATE action")])

        create_payload: schemas.BhikkuHighCreate
        if isinstance(payload.data, schemas.BhikkuHighCreate):
            create_payload = payload.data
        else:
            raw_data = payload.data.model_dump() if hasattr(payload.data, "model_dump") else payload.data
            try:
                create_payload = schemas.BhikkuHighCreate(**raw_data)
            except ValidationError as exc:
                formatted_errors = []
                for error in exc.errors():
                    loc = ".".join(str(part) for part in error.get("loc", []))
                    formatted_errors.append((loc or None, error.get("msg", "Invalid data")))
                raise validation_error(formatted_errors) from exc

        try:
            created = bhikku_high_service.create_bhikku_high(db, payload=create_payload, actor_id=user_id)
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        return schemas.BhikkuHighManagementResponse(status="success", message="Higher bhikku registration created successfully.", data=created)

    if action == schemas.CRUDAction.READ_ONE:
        check_permission(db, user_id, 'READ_BHIKKU_HIGH')
        if payload.bhr_id is None and not payload.bhr_regn:
            raise validation_error([("payload.bhr_id", "bhr_id or bhr_regn is required for READ_ONE action")])

        entity = None
        if payload.bhr_id:
            entity = bhikku_high_service.get_bhikku_high(db, bhr_id=payload.bhr_id)
        elif payload.bhr_regn:
            entity = bhikku_high_service.get_bhikku_high_by_regn(db, bhr_regn=payload.bhr_regn)

        if not entity:
            raise HTTPException(status_code=404, detail="Higher bhikku registration not found")

        return schemas.BhikkuHighManagementResponse(status="success", message="Higher bhikku registration retrieved successfully.", data=entity)

    if action == schemas.CRUDAction.READ_ALL:
        check_permission(db, user_id, 'READ_BHIKKU_HIGH')
        page = payload.page or 1
        limit = payload.limit
        search = payload.search_key.strip() if payload.search_key else None
        if search == "":
            search = None
        skip = payload.skip if payload.page is None else (page - 1) * limit
        limit = max(1, min(limit, 200))
        skip = max(0, skip)

        records = bhikku_high_service.list_bhikku_highs(db, skip=skip, limit=limit, search=search)
        total = bhikku_high_service.count_bhikku_highs(db, search=search)

        return schemas.BhikkuHighManagementResponse(
            status="success",
            message="Higher bhikku registrations retrieved successfully.",
            data=records,
            totalRecords=total,
            user_info={"role": user_role, "group": user_group},
            page=page,
            limit=limit,
        )

    if action == schemas.CRUDAction.UPDATE:
        check_permission(db, user_id, 'UPDATE_BHIKKU_HIGH')
        if not payload.data:
            raise validation_error([("payload.data", "data is required for UPDATE action")])

        update_payload: schemas.BhikkuHighUpdate
        if isinstance(payload.data, schemas.BhikkuHighUpdate):
            update_payload = payload.data
        else:
            raw_data = payload.data.model_dump() if hasattr(payload.data, "model_dump") else payload.data
            try:
                update_payload = schemas.BhikkuHighUpdate(**raw_data)
            except ValidationError as exc:
                formatted_errors = []
                for error in exc.errors():
                    loc = ".".join(str(part) for part in error.get("loc", []))
                    formatted_errors.append((loc or None, error.get("msg", "Invalid data")))
                raise validation_error(formatted_errors) from exc

        try:
            updated = bhikku_high_service.update_bhikku_high(db, bhr_id=payload.bhr_id, payload=update_payload, actor_id=user_id)
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        return schemas.BhikkuHighManagementResponse(status="success", message="Higher bhikku registration updated successfully.", data=updated)

    if action == schemas.CRUDAction.DELETE:
        check_permission(db, user_id, 'DELETE_BHIKKU_HIGH')
        if payload.bhr_id is None:
            raise validation_error([("payload.bhr_id", "bhr_id is required for DELETE action")])

        try:
            bhikku_high_service.delete_bhikku_high(db, bhr_id=payload.bhr_id, actor_id=user_id)
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message) from exc
            raise validation_error([(None, message)]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        return schemas.BhikkuHighManagementResponse(status="success", message="Higher bhikku registration deleted successfully.", data=None)

    raise validation_error([("action", "Invalid action specified")])
