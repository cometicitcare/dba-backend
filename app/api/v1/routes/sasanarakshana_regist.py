# app/api/v1/routes/sasanarakshana_regist.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_any_permission, get_user_permissions, is_super_admin
from app.models.user import UserAccount
from app.schemas import sasanarakshana_regist as schemas
from app.services.sasanarakshana_regist_service import sasanarakshana_regist_service
from pydantic import ValidationError
from app.utils.http_exceptions import validation_error, format_pydantic_errors

router = APIRouter()


def _check_permission(db: Session, user: UserAccount, permission: str):
    # Super admins bypass all permission checks
    if is_super_admin(db, user):
        return
    perms = get_user_permissions(db, user)
    if permission not in perms:
        raise HTTPException(
            status_code=403,
            detail=f"Permission denied. Required: {permission}",
        )


@router.post(
    "/manage",
    response_model=schemas.SasanarakshanaRegistManagementResponse,
    dependencies=[has_any_permission(
        "sasanarakshaka:create",
        "sasanarakshaka:read",
        "sasanarakshaka:update",
        "sasanarakshaka:delete",
    )],
)
def manage_sasanarakshana_regist(
    request: schemas.SasanarakshanaRegistManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Unified CRUD endpoint for Sasanaarakshana Registration Management.

    Actions:
    - **CREATE**   – create a new record (requires sasanarakshaka:create)
    - **READ_ONE** – fetch a single record by sar_id (requires sasanarakshaka:read)
    - **READ_ALL** – paginated list with optional search (requires sasanarakshaka:read)
    - **UPDATE**   – update an existing record by sar_id (requires sasanarakshaka:update)
    - **DELETE**   – soft-delete a record by sar_id (requires sasanarakshaka:delete)
    """
    action = request.action
    payload = request.payload
    actor_id = current_user.ua_user_id

    # ------------------------------------------------------------------ CREATE
    if action == schemas.CRUDAction.CREATE:
        _check_permission(db, current_user, "sasanarakshaka:create")

        if not payload.data:
            raise validation_error("payload.data is required for CREATE action")

        try:
            create_payload = schemas.SasanarakshanaRegistCreate(**payload.data.model_dump())
        except ValidationError as exc:
            raise validation_error(format_pydantic_errors(exc))
        except Exception as exc:
            raise validation_error(str(exc))

        try:
            record = sasanarakshana_regist_service.create(
                db, payload=create_payload, actor_id=actor_id
            )
        except ValueError as exc:
            raise validation_error(str(exc))

        return schemas.SasanarakshanaRegistManagementResponse(
            status="success",
            message="Sasanaarakshana Registration created successfully.",
            data=record,
        )

    # --------------------------------------------------------------- READ_ONE
    elif action == schemas.CRUDAction.READ_ONE:
        _check_permission(db, current_user, "sasanarakshaka:read")

        if not payload.sar_id:
            raise validation_error("payload.sar_id is required for READ_ONE action")

        record = sasanarakshana_regist_service.get_by_id(db, payload.sar_id)
        if not record:
            raise HTTPException(
                status_code=404,
                detail=f"Sasanaarakshana Registration with ID {payload.sar_id} not found",
            )

        return schemas.SasanarakshanaRegistManagementResponse(
            status="success",
            message="Sasanaarakshana Registration retrieved successfully.",
            data=record,
        )

    # --------------------------------------------------------------- READ_ALL
    elif action == schemas.CRUDAction.READ_ALL:
        _check_permission(db, current_user, "sasanarakshaka:read")

        page = payload.page or 1
        limit = payload.limit
        search_key = payload.search_key.strip() if payload.search_key else None
        if search_key == "":
            search_key = None
        skip = (page - 1) * limit

        records, total = sasanarakshana_regist_service.get_all(
            db, skip=skip, limit=limit, search_key=search_key
        )

        return schemas.SasanarakshanaRegistManagementResponse(
            status="success",
            message="Sasanaarakshana Registration list retrieved successfully.",
            data=records,
            total=total,
            page=page,
            limit=limit,
        )

    # ----------------------------------------------------------------- UPDATE
    elif action == schemas.CRUDAction.UPDATE:
        _check_permission(db, current_user, "sasanarakshaka:update")

        if not payload.sar_id:
            raise validation_error("payload.sar_id is required for UPDATE action")
        if not payload.data:
            raise validation_error("payload.data is required for UPDATE action")

        try:
            update_payload = schemas.SasanarakshanaRegistUpdate(
                **payload.data.model_dump(exclude_unset=True)
            )
        except ValidationError as exc:
            raise validation_error(format_pydantic_errors(exc))
        except Exception as exc:
            raise validation_error(str(exc))

        try:
            record = sasanarakshana_regist_service.update(
                db, sar_id=payload.sar_id, payload=update_payload, actor_id=actor_id
            )
        except ValueError as exc:
            raise validation_error(str(exc))

        if not record:
            raise HTTPException(
                status_code=404,
                detail=f"Sasanaarakshana Registration with ID {payload.sar_id} not found",
            )

        return schemas.SasanarakshanaRegistManagementResponse(
            status="success",
            message="Sasanaarakshana Registration updated successfully.",
            data=record,
        )

    # ----------------------------------------------------------------- DELETE
    elif action == schemas.CRUDAction.DELETE:
        _check_permission(db, current_user, "sasanarakshaka:delete")

        if not payload.sar_id:
            raise validation_error("payload.sar_id is required for DELETE action")

        deleted = sasanarakshana_regist_service.delete(
            db, sar_id=payload.sar_id, actor_id=actor_id
        )
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"Sasanaarakshana Registration with ID {payload.sar_id} not found",
            )

        return schemas.SasanarakshanaRegistManagementResponse(
            status="success",
            message=f"Sasanaarakshana Registration with ID {payload.sar_id} deleted successfully.",
            data={"sar_id": payload.sar_id},
        )

    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {action}")
