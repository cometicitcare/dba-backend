# app/api/v1/routes/temporary_vihara.py
"""
API routes for Temporary Vihara Management
Provides CRUD operations for temporary vihara records
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission, has_any_permission
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas.temporary_vihara import (
    CRUDAction,
    TemporaryViharaCreate,
    TemporaryViharaManagementRequest,
    TemporaryViharaManagementResponse,
    TemporaryViharaUpdate,
)
from app.services.temporary_vihara_service import temporary_vihara_service
from app.utils.http_exceptions import validation_error

router = APIRouter()


@router.post(
    "/manage",
    response_model=TemporaryViharaManagementResponse,
    response_model_by_alias=True,
    dependencies=[has_any_permission("vihara:create", "vihara:read", "vihara:update", "vihara:delete")]
)
def manage_temporary_vihara_records(
    request: TemporaryViharaManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Manage temporary vihara records with CRUD operations.
    
    This endpoint handles CREATE, READ_ONE, READ_ALL, UPDATE, and DELETE actions.
    
    **Actions:**
    - **CREATE**: Create a new temporary vihara record
    - **READ_ONE**: Retrieve a single temporary vihara by ID
    - **READ_ALL**: List all temporary vihara records with pagination
    - **UPDATE**: Update an existing temporary vihara record
    - **DELETE**: Delete a temporary vihara record
    
    **Use Case:**
    Used when creating records with incomplete vihara information.
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
            created = temporary_vihara_service.create_temporary_vihara(
                db, payload=payload.data, actor_id=user_id
            )
            return TemporaryViharaManagementResponse(
                status="success",
                message="Temporary vihara record created successfully.",
                data=created,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    # ==================== READ_ONE ====================
    if action == CRUDAction.READ_ONE:
        if payload.tv_id is None:
            raise validation_error([
                ("payload.tv_id", "tv_id is required for READ_ONE action")
            ])

        entity = temporary_vihara_service.get_temporary_vihara(db, payload.tv_id)
        if not entity:
            raise HTTPException(status_code=404, detail="Temporary vihara record not found")

        return TemporaryViharaManagementResponse(
            status="success",
            message="Temporary vihara record retrieved successfully.",
            data=entity,
        )

    # ==================== READ_ALL ====================
    if action == CRUDAction.READ_ALL:
        skip = payload.skip
        limit = payload.limit
        search = payload.search

        records = temporary_vihara_service.list_temporary_viharas(
            db, skip=skip, limit=limit, search=search
        )
        total = temporary_vihara_service.count_temporary_viharas(db, search=search)
        
        # Convert SQLAlchemy models to dicts for serialization
        records_list = []
        for record in records:
            if hasattr(record, '__dict__'):
                record_dict = {k: v for k, v in record.__dict__.items() if not k.startswith('_')}
                records_list.append(record_dict)
            else:
                records_list.append(record)

        return TemporaryViharaManagementResponse(
            status="success",
            message=f"Retrieved {len(records_list)} temporary vihara records.",
            data={
                "records": records_list,
                "total": total,
                "skip": skip,
                "limit": limit,
            },
        )

    # ==================== UPDATE ====================
    if action == CRUDAction.UPDATE:
        if payload.tv_id is None:
            raise validation_error([
                ("payload.tv_id", "tv_id is required for UPDATE action")
            ])
        if not payload.updates:
            raise validation_error([
                ("payload.updates", "updates is required for UPDATE action")
            ])

        try:
            updated = temporary_vihara_service.update_temporary_vihara(
                db, tv_id=payload.tv_id, payload=payload.updates, actor_id=user_id
            )
            return TemporaryViharaManagementResponse(
                status="success",
                message="Temporary vihara record updated successfully.",
                data=updated,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    # ==================== DELETE ====================
    if action == CRUDAction.DELETE:
        if payload.tv_id is None:
            raise validation_error([
                ("payload.tv_id", "tv_id is required for DELETE action")
            ])

        try:
            temporary_vihara_service.delete_temporary_vihara(db, tv_id=payload.tv_id)
            return TemporaryViharaManagementResponse(
                status="success",
                message="Temporary vihara record deleted successfully.",
                data=None,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    # If we reach here, unsupported action
    raise validation_error([("action", f"Unsupported action: {action}")])
