# app/api/v1/routes/dayakasaba_regist.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_any_permission, get_user_permissions, is_super_admin
from app.models.user import UserAccount
from app.schemas import dayakasaba_regist as schemas
from app.services.dayakasaba_regist_service import dayakasaba_regist_service
from app.utils.http_exceptions import validation_error

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
# Unified CRUD  +  Workflow  manage endpoint
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/manage",
    response_model=schemas.DayakasabaRegistManagementResponse,
    dependencies=[has_any_permission(
        "dayakasaba:create",
        "dayakasaba:read",
        "dayakasaba:update",
        "dayakasaba:delete",
        "dayakasaba:approve",
    )],
    summary="Unified CRUD + Workflow endpoint for Dayaka Sabha Registration",
)
def manage_dayakasaba_regist(
    request: schemas.DayakasabaRegistManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Single endpoint that handles all Dayaka Sabha Registration operations.

    **Actions:**
    | Action     | Description                                                        |
    |------------|--------------------------------------------------------------------|
    | CREATE     | Create a new record (status starts at **PENDING**)                 |
    | READ_ONE   | Fetch a single record by `ds_id`                                   |
    | READ_ALL   | Paginated list with optional search / filters                      |
    | UPDATE     | Update an existing record by `ds_id`                               |
    | DELETE     | Soft-delete a record by `ds_id`                                    |
    | APPROVE    | Approve a record (must be in **PEND-APPROVAL** → **COMPLETED**)    |
    | REJECT     | Reject a record (must be in **PEND-APPROVAL** → **REJECTED**)      |

    **Workflow:**
    ```
    CREATE → PENDING
                │
                │  (upload scanned document via /upload-scanned-document)
                ▼
          PEND-APPROVAL
                │
        ┌───────┴───────┐
        ▼               ▼
    COMPLETED       REJECTED
    ```
    """
    action = request.action
    payload = request.payload
    actor_id = current_user.ua_user_id

    # ------------------------------------------------------------------ CREATE
    if action == schemas.DayakasabaAction.CREATE:
        _check_permission(db, current_user, "dayakasaba:create")

        if not payload.data:
            raise validation_error("payload.data is required for CREATE action")

        try:
            create_payload = schemas.DayakasabaRegistCreate(**payload.data.model_dump())
        except Exception as exc:
            raise validation_error(str(exc))

        try:
            record = dayakasaba_regist_service.create(
                db, payload=create_payload, actor_id=actor_id
            )
        except ValueError as exc:
            raise validation_error(str(exc))

        return schemas.DayakasabaRegistManagementResponse(
            status="success",
            message="Dayaka Sabha registration created successfully.",
            data=record,
        )

    # --------------------------------------------------------------- READ_ONE
    elif action == schemas.DayakasabaAction.READ_ONE:
        _check_permission(db, current_user, "dayakasaba:read")

        if not payload.ds_id:
            raise validation_error("payload.ds_id is required for READ_ONE action")

        record = dayakasaba_regist_service.get_by_id(db, payload.ds_id)
        if not record:
            raise HTTPException(
                status_code=404,
                detail=f"Dayaka Sabha registration with ID {payload.ds_id} not found",
            )

        return schemas.DayakasabaRegistManagementResponse(
            status="success",
            message="Dayaka Sabha registration retrieved successfully.",
            data=record,
        )

    # --------------------------------------------------------------- READ_ALL
    elif action == schemas.DayakasabaAction.READ_ALL:
        _check_permission(db, current_user, "dayakasaba:read")

        page = payload.page or 1
        limit = payload.limit
        skip = (page - 1) * limit
        search_key = payload.search_key.strip() if payload.search_key else None
        if not search_key:
            search_key = None

        records, total = dayakasaba_regist_service.get_all(
            db,
            skip=skip,
            limit=limit,
            search_key=search_key,
            workflow_status=payload.workflow_status or None,
            temple_trn=payload.temple_trn or None,
        )

        return schemas.DayakasabaRegistManagementResponse(
            status="success",
            message="Dayaka Sabha registration list retrieved successfully.",
            data=records,
            total=total,
            page=page,
            limit=limit,
        )

    # ----------------------------------------------------------------- UPDATE
    elif action == schemas.DayakasabaAction.UPDATE:
        _check_permission(db, current_user, "dayakasaba:update")

        if not payload.ds_id:
            raise validation_error("payload.ds_id is required for UPDATE action")
        if not payload.data:
            raise validation_error("payload.data is required for UPDATE action")

        try:
            update_payload = schemas.DayakasabaRegistUpdate(
                **payload.data.model_dump(exclude_unset=True)
            )
        except Exception as exc:
            raise validation_error(str(exc))

        try:
            record = dayakasaba_regist_service.update(
                db, ds_id=payload.ds_id, payload=update_payload, actor_id=actor_id
            )
        except ValueError as exc:
            raise validation_error(str(exc))

        if not record:
            raise HTTPException(
                status_code=404,
                detail=f"Dayaka Sabha registration with ID {payload.ds_id} not found",
            )

        return schemas.DayakasabaRegistManagementResponse(
            status="success",
            message="Dayaka Sabha registration updated successfully.",
            data=record,
        )

    # ----------------------------------------------------------------- DELETE
    elif action == schemas.DayakasabaAction.DELETE:
        _check_permission(db, current_user, "dayakasaba:delete")

        if not payload.ds_id:
            raise validation_error("payload.ds_id is required for DELETE action")

        deleted = dayakasaba_regist_service.delete(
            db, ds_id=payload.ds_id, actor_id=actor_id
        )
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"Dayaka Sabha registration with ID {payload.ds_id} not found",
            )

        return schemas.DayakasabaRegistManagementResponse(
            status="success",
            message=f"Dayaka Sabha registration with ID {payload.ds_id} deleted successfully.",
            data={"ds_id": payload.ds_id},
        )

    # ----------------------------------------------------------------- APPROVE
    elif action == schemas.DayakasabaAction.APPROVE:
        _check_permission(db, current_user, "dayakasaba:approve")

        if not payload.ds_id:
            raise validation_error("payload.ds_id is required for APPROVE action")

        try:
            record = dayakasaba_regist_service.approve(
                db, ds_id=payload.ds_id, actor_id=actor_id
            )
        except ValueError as exc:
            msg = str(exc)
            if "not found" in msg.lower():
                raise HTTPException(status_code=404, detail=msg)
            raise validation_error(msg)

        return schemas.DayakasabaRegistManagementResponse(
            status="success",
            message="Dayaka Sabha registration approved successfully.",
            data=record,
        )

    # ----------------------------------------------------------------- REJECT
    elif action == schemas.DayakasabaAction.REJECT:
        _check_permission(db, current_user, "dayakasaba:approve")

        if not payload.ds_id:
            raise validation_error("payload.ds_id is required for REJECT action")
        if not payload.rejection_reason:
            raise validation_error(
                "payload.rejection_reason is required for REJECT action"
            )

        try:
            record = dayakasaba_regist_service.reject(
                db,
                ds_id=payload.ds_id,
                rejection_reason=payload.rejection_reason,
                actor_id=actor_id,
            )
        except ValueError as exc:
            msg = str(exc)
            if "not found" in msg.lower():
                raise HTTPException(status_code=404, detail=msg)
            raise validation_error(msg)

        return schemas.DayakasabaRegistManagementResponse(
            status="success",
            message="Dayaka Sabha registration rejected.",
            data=record,
        )

    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {action}")


# ─────────────────────────────────────────────────────────────────────────────
# Scanned document upload
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/{ds_id}/upload-scanned-document",
    response_model=schemas.DayakasabaRegistManagementResponse,
    dependencies=[has_any_permission("dayakasaba:update")],
    summary="Upload scanned document for a Dayaka Sabha registration",
)
async def upload_scanned_document(
    ds_id: int,
    file: UploadFile = File(
        ...,
        description="Scanned document file (max 5 MB; PDF, JPG, JPEG, PNG)",
    ),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Upload a scanned document for a Dayaka Sabha registration record.

    - **Max size:** 5 MB
    - **Allowed formats:** PDF, JPG, JPEG, PNG
    - If the record is in **PENDING** status it will automatically transition to
      **PEND-APPROVAL** after a successful upload.

    **Path parameter:**
    - `ds_id`: Primary key of the Dayaka Sabha registration record.

    **Form data:**
    - `file`: The scanned document file.
    """
    actor_id = current_user.ua_user_id

    # Client-side size guard (server re-validates inside service)
    MAX_FILE_SIZE = 5 * 1024 * 1024
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=(
                f"File size ({len(file_content) / 1024 / 1024:.2f} MB) "
                "exceeds maximum allowed size (5 MB)."
            ),
        )
    await file.seek(0)

    try:
        record = await dayakasaba_regist_service.upload_scanned_document(
            db, ds_id=ds_id, file=file, actor_id=actor_id
        )
    except ValueError as exc:
        msg = str(exc)
        if "not found" in msg.lower():
            raise HTTPException(status_code=404, detail=msg)
        raise HTTPException(status_code=400, detail=msg)

    return schemas.DayakasabaRegistManagementResponse(
        status="success",
        message="Scanned document uploaded successfully.",
        data=record,
    )
