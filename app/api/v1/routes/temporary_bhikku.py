# app/api/v1/routes/temporary_bhikku.py
"""
API routes for Temporary Bhikku Management
Provides CRUD operations for temporary bhikku records
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission, has_any_permission
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas.temporary_bhikku import (
    CRUDAction,
    TemporaryBhikkuCreate,
    TemporaryBhikkuManagementRequest,
    TemporaryBhikkuManagementResponse,
    TemporaryBhikkuUpdate,
)
from app.services.temporary_bhikku_service import temporary_bhikku_service
from app.utils.http_exceptions import validation_error

router = APIRouter()


@router.post(
    "/manage",
    response_model=TemporaryBhikkuManagementResponse,
    response_model_by_alias=True,
    dependencies=[has_any_permission("bhikku:create", "bhikku:read", "bhikku:update", "bhikku:delete")]
)
def manage_temporary_bhikku_records(
    request: TemporaryBhikkuManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Manage temporary bhikku records with CRUD operations.
    
    This endpoint handles CREATE, READ_ONE, READ_ALL, UPDATE, and DELETE actions.
    
    **Actions:**
    - **CREATE**: Create a new temporary bhikku record
    - **READ_ONE**: Retrieve a single temporary bhikku by ID
    - **READ_ALL**: List all temporary bhikku records with pagination
    - **UPDATE**: Update an existing temporary bhikku record
    - **DELETE**: Delete a temporary bhikku record
    
    **Use Case:**
    Used when creating direct high bhikku registrations with incomplete information.
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
            created = temporary_bhikku_service.create_temporary_bhikku(
                db, payload=payload.data, actor_id=user_id
            )
            return TemporaryBhikkuManagementResponse(
                status="success",
                message="Temporary bhikku record created successfully.",
                data=created,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    # ==================== READ_ONE ====================
    if action == CRUDAction.READ_ONE:
        if payload.tb_id is None:
            raise validation_error([
                ("payload.tb_id", "tb_id is required for READ_ONE action")
            ])

        entity = temporary_bhikku_service.get_temporary_bhikku(db, payload.tb_id)
        if not entity:
            raise HTTPException(status_code=404, detail="Temporary bhikku record not found")

        return TemporaryBhikkuManagementResponse(
            status="success",
            message="Temporary bhikku record retrieved successfully.",
            data=entity,
        )

    # ==================== READ_ALL ====================
    if action == CRUDAction.READ_ALL:
        skip = payload.skip
        limit = payload.limit
        search = payload.search

        records = temporary_bhikku_service.list_temporary_bhikkus(
            db, skip=skip, limit=limit, search=search
        )
        total = temporary_bhikku_service.count_temporary_bhikkus(db, search=search)

        return TemporaryBhikkuManagementResponse(
            status="success",
            message=f"Retrieved {len(records)} temporary bhikku records.",
            data={
                "records": records,
                "total": total,
                "skip": skip,
                "limit": limit,
            },
        )

    # ==================== UPDATE ====================
    if action == CRUDAction.UPDATE:
        if payload.tb_id is None:
            raise validation_error([
                ("payload.tb_id", "tb_id is required for UPDATE action")
            ])
        if not payload.updates:
            raise validation_error([
                ("payload.updates", "updates is required for UPDATE action")
            ])

        try:
            updated = temporary_bhikku_service.update_temporary_bhikku(
                db, tb_id=payload.tb_id, payload=payload.updates, actor_id=user_id
            )
            return TemporaryBhikkuManagementResponse(
                status="success",
                message="Temporary bhikku record updated successfully.",
                data=updated,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    # ==================== DELETE ====================
    if action == CRUDAction.DELETE:
        if payload.tb_id is None:
            raise validation_error([
                ("payload.tb_id", "tb_id is required for DELETE action")
            ])

        try:
            temporary_bhikku_service.delete_temporary_bhikku(db, tb_id=payload.tb_id)
            return TemporaryBhikkuManagementResponse(
                status="success",
                message="Temporary bhikku record deleted successfully.",
                data=None,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    # If we reach here, unsupported action
    raise validation_error([("action", f"Unsupported action: {action}")])
