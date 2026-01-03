# app/api/v1/routes/temporary_silmatha.py
"""
API routes for Temporary Silmatha Management
Provides CRUD operations for temporary silmatha records
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission, has_any_permission
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas.temporary_silmatha import (
    CRUDAction,
    TemporarySilmathaCreate,
    TemporarySilmathaManagementRequest,
    TemporarySilmathaManagementResponse,
    TemporarySilmathaUpdate,
)
from app.services.temporary_silmatha_service import temporary_silmatha_service
from app.utils.http_exceptions import validation_error

router = APIRouter()


@router.post(
    "/manage",
    response_model=TemporarySilmathaManagementResponse,
    response_model_by_alias=True,
    dependencies=[has_any_permission("silmatha:create", "silmatha:read", "silmatha:update", "silmatha:delete")]
)
def manage_temporary_silmatha_records(
    request: TemporarySilmathaManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Manage temporary silmatha records with CRUD operations.
    
    This endpoint handles CREATE, READ_ONE, READ_ALL, UPDATE, and DELETE actions.
    
    **Actions:**
    - **CREATE**: Create a new temporary silmatha record
    - **READ_ONE**: Retrieve a single temporary silmatha by ID
    - **READ_ALL**: List all temporary silmatha records with pagination
    - **UPDATE**: Update an existing temporary silmatha record
    - **DELETE**: Delete a temporary silmatha record
    
    **Use Case:**
    Used when creating records with incomplete silmatha (nun) information.
    Stores partial data temporarily until full details are available.
    """
    action = request.action
    payload = request.payload
    user_id = current_user.ua_user_id

    # ==================== CREATE ====================
    if action == CRUDAction.CREATE:
        if not payload.data:
            raise validation_error([("payload.data", "data is required for CREATE action")])

        try:
            created = temporary_silmatha_service.create_temporary_silmatha(
                db, payload=payload.data, actor_id=user_id
            )
            return TemporarySilmathaManagementResponse(
                status="success",
                message="Temporary silmatha record created successfully.",
                data=created,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    # ==================== READ_ONE ====================
    if action == CRUDAction.READ_ONE:
        if payload.ts_id is None:
            raise validation_error([
                ("payload.ts_id", "ts_id is required for READ_ONE action")
            ])

        entity = temporary_silmatha_service.get_temporary_silmatha(db, payload.ts_id)
        if not entity:
            raise HTTPException(status_code=404, detail="Temporary silmatha record not found")

        return TemporarySilmathaManagementResponse(
            status="success",
            message="Temporary silmatha record retrieved successfully.",
            data=entity,
        )

    # ==================== READ_ALL ====================
    if action == CRUDAction.READ_ALL:
        skip = payload.skip
        limit = payload.limit
        search = payload.search

        records = temporary_silmatha_service.list_temporary_silmathas(
            db, skip=skip, limit=limit, search=search
        )
        total = temporary_silmatha_service.count_temporary_silmathas(db, search=search)

        return TemporarySilmathaManagementResponse(
            status="success",
            message=f"Retrieved {len(records)} temporary silmatha records.",
            data={
                "records": records,
                "total": total,
                "skip": skip,
                "limit": limit,
            },
        )

    # ==================== UPDATE ====================
    if action == CRUDAction.UPDATE:
        if payload.ts_id is None:
            raise validation_error([
                ("payload.ts_id", "ts_id is required for UPDATE action")
            ])
        if not payload.updates:
            raise validation_error([
                ("payload.updates", "updates is required for UPDATE action")
            ])

        try:
            updated = temporary_silmatha_service.update_temporary_silmatha(
                db, ts_id=payload.ts_id, payload=payload.updates, actor_id=user_id
            )
            return TemporarySilmathaManagementResponse(
                status="success",
                message="Temporary silmatha record updated successfully.",
                data=updated,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    # ==================== DELETE ====================
    if action == CRUDAction.DELETE:
        if payload.ts_id is None:
            raise validation_error([
                ("payload.ts_id", "ts_id is required for DELETE action")
            ])

        try:
            temporary_silmatha_service.delete_temporary_silmatha(db, ts_id=payload.ts_id)
            return TemporarySilmathaManagementResponse(
                status="success",
                message="Temporary silmatha record deleted successfully.",
                data=None,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    # Should not reach here
    raise validation_error([("action", f"Unsupported action: {action}")])
