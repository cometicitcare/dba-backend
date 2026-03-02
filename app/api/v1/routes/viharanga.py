# app/api/v1/routes/viharanga.py
from fastapi import APIRouter, Depends, HTTPException, status as http_status
from pydantic import ValidationError
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime

from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission, has_any_permission, get_user_permissions, is_super_admin
from app.api.deps import get_db
from app.models.user import UserAccount
from app.models.user_roles import UserRole
from app.schemas.viharanga import (
    CRUDAction,
    ViharangaCreate,
    ViharangaManagementRequest,
    ViharangaManagementResponse,
    ViharangaOut,
    ViharangaUpdate,
)
from app.services.viharanga_service import viharanga_service
from app.utils.http_exceptions import validation_error

router = APIRouter()  # Tags defined in router.py


def check_viharanga_access(
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if user has access to viharanga endpoints.
    Grants access to:
    - Super admins
    - Users with system:create, system:update, or system:delete permissions
    - Users with VIHA_DATA role (vihara_dataentry)
    - Users with VIHA_ADM role (vihara_admin)
    """
    # Super admins bypass all checks
    if is_super_admin(db, current_user):
        return
    
    current_time = datetime.utcnow()
    
    # Check if user has vihara roles (VIHA_DATA or VIHA_ADM)
    vihara_role = db.query(UserRole).filter(
        and_(
            UserRole.ur_user_id == current_user.ua_user_id,
            UserRole.ur_role_id.in_(["VIHA_DATA", "VIHA_ADM"]),
            UserRole.ur_is_active == True,
            UserRole.ur_expires_date.is_(None) | (UserRole.ur_expires_date > current_time)
        )
    ).first()
    
    if vihara_role:
        return  # User has vihara role, grant access
    
    # Check if user has system permissions
    user_permissions = get_user_permissions(db, current_user)
    required_permissions = ["system:create", "system:update", "system:delete"]
    
    if any(perm in user_permissions for perm in required_permissions):
        return  # User has system permissions, grant access
    
    # User has neither vihara roles nor system permissions
    raise HTTPException(
        status_code=http_status.HTTP_403_FORBIDDEN,
        detail="Access denied. Required: system permissions OR vihara_dataentry/vihara_admin role."
    )


def _extract_payload(data):
    """Extract raw data from payload"""
    if hasattr(data, 'model_dump'):
        return data.model_dump()
    return data


def _format_validation_errors(exc: ValidationError):
    """Format validation errors for response"""
    formatted_errors = []
    for error in exc.errors():
        loc = ".".join(str(part) for part in error.get("loc", []))
        formatted_errors.append((loc or None, error.get("msg", "Invalid data")))
    return formatted_errors


@router.post(
    "/manage",
    response_model=ViharangaManagementResponse,
    dependencies=[Depends(check_viharanga_access)],
)
def manage_viharanga_records(
    request: ViharangaManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Unified endpoint for all Viharanga CRUD operations.
    
    Supported Actions:
    - CREATE: Create a new viharanga record
    - READ_ONE: Get a single viharanga by ID or code
    - READ_ALL: Get all viharanga records with pagination and search
    - UPDATE: Update an existing viharanga record
    - DELETE: Delete (soft delete) a viharanga record
    
    Access granted to:
    - Users with system:create, system:update, or system:delete permissions
    - Users with vihara_dataentry role (VIHA_DATA)
    - Users with vihara_admin role (VIHA_ADM)
    """
    action = request.action
    payload = request.payload
    user_id = current_user.ua_user_id

    if action == CRUDAction.CREATE:
        if not payload.data:
            raise validation_error(
                [("payload.data", "Valid data is required for CREATE action")]
            )
        try:
            create_raw = _extract_payload(payload.data)
            create_payload = ViharangaCreate.model_validate(create_raw)
        except ValidationError as exc:
            raise validation_error(_format_validation_errors(exc)) from exc
        except TypeError as exc:
            raise validation_error([(None, str(exc))]) from exc
        
        try:
            created = viharanga_service.create_viharanga(
                db, payload=create_payload, actor_id=user_id
            )
            created_out = ViharangaOut.model_validate(created)
            return ViharangaManagementResponse(
                status="success",
                message="Viharanga created successfully.",
                data=created_out,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    if action == CRUDAction.READ_ONE:
        identifier_id = payload.vg_id
        identifier_code = payload.vg_code
        if identifier_id is None and not identifier_code:
            raise validation_error(
                [
                    (
                        "payload.vg_id",
                        "vg_id or vg_code is required for READ_ONE action",
                    )
                ]
            )

        entity = None
        if identifier_id is not None:
            entity = viharanga_service.get_viharanga(db, vg_id=identifier_id)
        elif identifier_code:
            entity = viharanga_service.get_viharanga(db, vg_code=identifier_code)

        if not entity:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Viharanga not found",
            )

        entity_out = ViharangaOut.model_validate(entity)
        return ViharangaManagementResponse(
            status="success",
            message="Viharanga retrieved successfully.",
            data=entity_out,
        )

    if action == CRUDAction.READ_ALL:
        page = payload.page or 1
        limit = payload.limit
        search = payload.search_key.strip() if payload.search_key else None
        if search == "":
            search = None
        skip = payload.skip if payload.page is None else (page - 1) * limit

        records = viharanga_service.list_viharangas(
            db, skip=skip, limit=limit, search=search
        )
        total_count = viharanga_service.count_viharangas(db, search=search)

        records_out = [ViharangaOut.model_validate(record) for record in records]
        return ViharangaManagementResponse(
            status="success",
            message="Viharangas retrieved successfully.",
            data=records_out,
            totalRecords=total_count,
            page=page,
            limit=limit,
        )

    if action == CRUDAction.UPDATE:
        identifier_id = payload.vg_id
        identifier_code = payload.vg_code
        if identifier_id is None and not identifier_code:
            raise validation_error(
                [
                    (
                        "payload.vg_id",
                        "vg_id or vg_code is required for UPDATE action",
                    )
                ]
            )
        if not payload.data:
            raise validation_error(
                [("payload.data", "Valid data is required for UPDATE action")]
            )

        try:
            update_raw = _extract_payload(payload.data)
            update_payload = ViharangaUpdate.model_validate(update_raw)
        except ValidationError as exc:
            raise validation_error(_format_validation_errors(exc)) from exc
        except TypeError as exc:
            raise validation_error([(None, str(exc))]) from exc

        try:
            updated = viharanga_service.update_viharanga(
                db,
                vg_id=identifier_id,
                vg_code=identifier_code,
                payload=update_payload,
                actor_id=user_id,
            )
            updated_out = ViharangaOut.model_validate(updated)
            return ViharangaManagementResponse(
                status="success",
                message="Viharanga updated successfully.",
                data=updated_out,
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(
                    status_code=http_status.HTTP_404_NOT_FOUND, detail=message
                ) from exc
            raise validation_error([(None, message)]) from exc

    if action == CRUDAction.DELETE:
        identifier_id = payload.vg_id
        identifier_code = payload.vg_code
        if identifier_id is None and not identifier_code:
            raise validation_error(
                [
                    (
                        "payload.vg_id",
                        "vg_id or vg_code is required for DELETE action",
                    )
                ]
            )

        try:
            viharanga_service.delete_viharanga(
                db, vg_id=identifier_id, vg_code=identifier_code, actor_id=user_id
            )
            return ViharangaManagementResponse(
                status="success",
                message="Viharanga deleted successfully.",
                data=None,
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(
                    status_code=http_status.HTTP_404_NOT_FOUND, detail=message
                ) from exc
            raise validation_error([(None, message)]) from exc

    raise validation_error([("action", "Invalid action specified")])
