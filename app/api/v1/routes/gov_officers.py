# app/api/v1/routes/gov_officers.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_any_permission, get_user_permissions, is_super_admin
from app.models.user import UserAccount
from app.schemas import gov_officers as schemas
from app.services.gov_officers_service import gov_officers_service
from app.utils.http_exceptions import validation_error, format_pydantic_errors

router = APIRouter()


def _check_permission(db: Session, user: UserAccount, permission: str) -> None:
    """Raise 403 unless the user has the required permission or is a super admin."""
    if is_super_admin(db, user):
        return
    if permission not in get_user_permissions(db, user):
        raise HTTPException(
            status_code=403,
            detail=f"Permission denied. Required: {permission}",
        )


# ─────────────────────────────────────────────────────────────────────────────
# Unified CRUD manage endpoint
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/manage",
    response_model=schemas.GovOfficerManagementResponse,
    dependencies=[has_any_permission(
        "gov_officers:create",
        "gov_officers:read",
        "gov_officers:update",
        "gov_officers:delete",
    )],
    summary="Unified CRUD endpoint for Government Officers",
)
def manage_gov_officers(
    request: schemas.GovOfficerManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Single endpoint that handles all Government Officer operations.

    **Actions:**
    | Action   | Description                                      |
    |----------|--------------------------------------------------|
    | CREATE   | Create a new government officer record           |
    | READ_ONE | Fetch a single record by `go_id`                 |
    | READ_ALL | Paginated list with optional search              |
    | UPDATE   | Update an existing record by `go_id`             |
    | DELETE   | Soft-delete a record by `go_id`                  |

    **Required fields for CREATE:**
    - `go_title`, `go_first_name`, `go_last_name`, `go_contact_number`, `go_address`

    **Optional fields:**
    - `go_email`, `go_id_number`
    """
    action = request.action
    payload = request.payload
    actor_id = current_user.ua_user_id

    # ------------------------------------------------------------------ CREATE
    if action == schemas.GovOfficerAction.CREATE:
        _check_permission(db, current_user, "gov_officers:create")

        if not payload.data:
            raise validation_error("payload.data is required for CREATE action")

        try:
            create_payload = schemas.GovOfficerCreate(**payload.data.model_dump())
        except ValidationError as exc:
            raise validation_error(format_pydantic_errors(exc))
        except Exception as exc:
            raise validation_error(str(exc))

        try:
            record = gov_officers_service.create(
                db, payload=create_payload, actor_id=actor_id
            )
        except ValueError as exc:
            raise validation_error(str(exc))

        return schemas.GovOfficerManagementResponse(
            status="success",
            message="Government officer created successfully.",
            data=record,
        )

    # --------------------------------------------------------------- READ_ONE
    elif action == schemas.GovOfficerAction.READ_ONE:
        _check_permission(db, current_user, "gov_officers:read")

        if not payload.go_id:
            raise validation_error("payload.go_id is required for READ_ONE action")

        record = gov_officers_service.get_by_id(db, payload.go_id)
        if not record:
            raise HTTPException(
                status_code=404,
                detail=f"Government officer with ID {payload.go_id} not found",
            )

        return schemas.GovOfficerManagementResponse(
            status="success",
            message="Government officer retrieved successfully.",
            data=record,
        )

    # --------------------------------------------------------------- READ_ALL
    elif action == schemas.GovOfficerAction.READ_ALL:
        _check_permission(db, current_user, "gov_officers:read")

        page = payload.page or 1
        limit = payload.limit
        skip = (page - 1) * limit
        search_key = payload.search_key.strip() if payload.search_key else None
        if not search_key:
            search_key = None

        records, total = gov_officers_service.get_all(
            db,
            skip=skip,
            limit=limit,
            search_key=search_key,
        )

        return schemas.GovOfficerManagementResponse(
            status="success",
            message="Government officers list retrieved successfully.",
            data=records,
            total=total,
            page=page,
            limit=limit,
        )

    # ----------------------------------------------------------------- UPDATE
    elif action == schemas.GovOfficerAction.UPDATE:
        _check_permission(db, current_user, "gov_officers:update")

        if not payload.go_id:
            raise validation_error("payload.go_id is required for UPDATE action")
        if not payload.data:
            raise validation_error("payload.data is required for UPDATE action")

        try:
            update_payload = schemas.GovOfficerUpdate(
                **payload.data.model_dump(exclude_unset=True)
            )
        except ValidationError as exc:
            raise validation_error(format_pydantic_errors(exc))
        except Exception as exc:
            raise validation_error(str(exc))

        try:
            record = gov_officers_service.update(
                db, go_id=payload.go_id, payload=update_payload, actor_id=actor_id
            )
        except ValueError as exc:
            msg = str(exc)
            if "not found" in msg.lower():
                raise HTTPException(status_code=404, detail=msg)
            raise validation_error(msg)

        return schemas.GovOfficerManagementResponse(
            status="success",
            message="Government officer updated successfully.",
            data=record,
        )

    # ----------------------------------------------------------------- DELETE
    elif action == schemas.GovOfficerAction.DELETE:
        _check_permission(db, current_user, "gov_officers:delete")

        if not payload.go_id:
            raise validation_error("payload.go_id is required for DELETE action")

        deleted = gov_officers_service.delete(
            db, go_id=payload.go_id, actor_id=actor_id
        )
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"Government officer with ID {payload.go_id} not found",
            )

        return schemas.GovOfficerManagementResponse(
            status="success",
            message=f"Government officer with ID {payload.go_id} deleted successfully.",
            data={"go_id": payload.go_id},
        )

    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {action}")
