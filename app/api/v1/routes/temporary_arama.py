# app/api/v1/routes/temporary_arama.py
"""
API routes for Temporary Arama Management
Provides CRUD operations for temporary arama records
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission, has_any_permission
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas.temporary_arama import (
    CRUDAction,
    TemporaryAramaCreate,
    TemporaryAramaManagementRequest,
    TemporaryAramaManagementResponse,
    TemporaryAramaUpdate,
)
from app.services.temporary_arama_service import temporary_arama_service
from app.utils.http_exceptions import validation_error

router = APIRouter()


@router.post(
    "/manage",
    response_model=TemporaryAramaManagementResponse,
    response_model_by_alias=True,
    dependencies=[has_any_permission("arama:create", "arama:read", "arama:update", "arama:delete")]
)
def manage_temporary_arama_records(
    request: TemporaryAramaManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Manage temporary arama records with CRUD operations.
    
    This endpoint handles CREATE, READ_ONE, READ_ALL, UPDATE, and DELETE actions.
    
    **Actions:**
    - **CREATE**: Create a new temporary arama record
    - **READ_ONE**: Retrieve a single temporary arama by ID
    - **READ_ALL**: List all temporary arama records with pagination
    - **UPDATE**: Update an existing temporary arama record
    - **DELETE**: Delete a temporary arama record
    
    **Use Case:**
    Used when creating records with incomplete arama information.
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
            created = temporary_arama_service.create_temporary_arama(
                db, payload=payload.data, actor_id=user_id
            )
            return TemporaryAramaManagementResponse(
                status="success",
                message="Temporary arama record created successfully.",
                data=created,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    # ==================== READ_ONE ====================
    if action == CRUDAction.READ_ONE:
        if payload.ta_id is None:
            raise validation_error([
                ("payload.ta_id", "ta_id is required for READ_ONE action")
            ])

        entity = temporary_arama_service.get_temporary_arama(db, payload.ta_id)
        if not entity:
            raise HTTPException(status_code=404, detail="Temporary arama record not found")

        return TemporaryAramaManagementResponse(
            status="success",
            message="Temporary arama record retrieved successfully.",
            data=entity,
        )

    # ==================== READ_ALL ====================
    if action == CRUDAction.READ_ALL:
        skip = payload.skip
        limit = payload.limit
        search = payload.search

        records = temporary_arama_service.list_temporary_aramas(
            db, skip=skip, limit=limit, search=search
        )
        total = temporary_arama_service.count_temporary_aramas(db, search=search)

        return TemporaryAramaManagementResponse(
            status="success",
            message=f"Retrieved {len(records)} temporary arama records.",
            data={
                "records": records,
                "total": total,
                "skip": skip,
                "limit": limit,
            },
        )

    # ==================== UPDATE ====================
    if action == CRUDAction.UPDATE:
        if payload.ta_id is None:
            raise validation_error([
                ("payload.ta_id", "ta_id is required for UPDATE action")
            ])
        if not payload.updates:
            raise validation_error([
                ("payload.updates", "updates is required for UPDATE action")
            ])

        try:
            updated = temporary_arama_service.update_temporary_arama(
                db, ta_id=payload.ta_id, payload=payload.updates, actor_id=user_id
            )
            return TemporaryAramaManagementResponse(
                status="success",
                message="Temporary arama record updated successfully.",
                data=updated,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    # ==================== DELETE ====================
    if action == CRUDAction.DELETE:
        if payload.ta_id is None:
            raise validation_error([
                ("payload.ta_id", "ta_id is required for DELETE action")
            ])

        try:
            temporary_arama_service.delete_temporary_arama(db, ta_id=payload.ta_id)
            return TemporaryAramaManagementResponse(
                status="success",
                message="Temporary arama record deleted successfully.",
                data=None,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    # Should not reach here
    raise validation_error([("action", f"Unsupported action: {action}")])
