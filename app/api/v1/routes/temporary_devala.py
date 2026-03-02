# app/api/v1/routes/temporary_devala.py
"""
API routes for Temporary Devala Management
Provides CRUD operations for temporary devala records
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission, has_any_permission
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas.temporary_devala import (
    CRUDAction,
    TemporaryDevalaCreate,
    TemporaryDevalaManagementRequest,
    TemporaryDevalaManagementResponse,
    TemporaryDevalaUpdate,
    TemporaryDevalaResponse,
    ProvinceResponse,
    DistrictResponse,
)
from app.services.temporary_devala_service import temporary_devala_service
from app.repositories.province_repo import province_repo
from app.repositories.district_repo import district_repo
from app.utils.http_exceptions import validation_error

router = APIRouter()


def _convert_temp_devala_to_response(temp_devala, db: Session) -> TemporaryDevalaResponse:
    """Convert temporary devala model to response schema with FK resolution"""
    devala_dict = {k: v for k, v in temp_devala.__dict__.items() if not k.startswith('_')}
    
    # Resolve province FK
    if temp_devala.td_province:
        province = province_repo.get_by_code(db, temp_devala.td_province)
        if province:
            devala_dict["td_province"] = ProvinceResponse(
                cp_code=province.cp_code,
                cp_name=province.cp_name
            )
    
    # Resolve district FK
    if temp_devala.td_district:
        district = district_repo.get_by_code(db, temp_devala.td_district)
        if district:
            devala_dict["td_district"] = DistrictResponse(
                dd_dcode=district.dd_dcode,
                dd_dname=district.dd_dname
            )
    
    return TemporaryDevalaResponse(**devala_dict)


@router.post(
    "/manage",
    response_model=TemporaryDevalaManagementResponse,
    response_model_by_alias=True,
    dependencies=[has_any_permission("devala:create", "devala:read", "devala:update", "devala:delete")]
)
def manage_temporary_devala_records(
    request: TemporaryDevalaManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Manage temporary devala records with CRUD operations.
    
    This endpoint handles CREATE, READ_ONE, READ_ALL, UPDATE, and DELETE actions.
    
    **Actions:**
    - **CREATE**: Create a new temporary devala record
    - **READ_ONE**: Retrieve a single temporary devala by ID
    - **READ_ALL**: List all temporary devala records with pagination
    - **UPDATE**: Update an existing temporary devala record
    - **DELETE**: Delete a temporary devala record
    
    **Use Case:**
    Used when creating records with incomplete devala information.
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
            created = temporary_devala_service.create_temporary_devala(
                db, payload=payload.data, actor_id=user_id
            )
            return TemporaryDevalaManagementResponse(
                status="success",
                message="Temporary devala record created successfully.",
                data=created,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    # ==================== READ_ONE ====================
    if action == CRUDAction.READ_ONE:
        if payload.td_id is None:
            raise validation_error([
                ("payload.td_id", "td_id is required for READ_ONE action")
            ])

        entity = temporary_devala_service.get_temporary_devala(db, payload.td_id)
        if not entity:
            raise HTTPException(status_code=404, detail="Temporary devala record not found")

        return TemporaryDevalaManagementResponse(
            status="success",
            message="Temporary devala record retrieved successfully.",
            data=entity,
        )

    # ==================== READ_ALL ====================
    if action == CRUDAction.READ_ALL:
        skip = payload.skip
        limit = payload.limit
        search = payload.search

        records = temporary_devala_service.list_temporary_devalas(
            db, skip=skip, limit=limit, search=search
        )
        total = temporary_devala_service.count_temporary_devalas(db, search=search)

        # Convert SQLAlchemy models to response schemas with FK resolution
        records_list = [_convert_temp_devala_to_response(record, db) for record in records]

        return TemporaryDevalaManagementResponse(
            status="success",
            message=f"Retrieved {len(records_list)} temporary devala records.",
            data={
                "records": [r.model_dump() for r in records_list],
                "total": total,
                "skip": skip,
                "limit": limit,
            },
        )

    # ==================== UPDATE ====================
    if action == CRUDAction.UPDATE:
        if payload.td_id is None:
            raise validation_error([
                ("payload.td_id", "td_id is required for UPDATE action")
            ])
        if not payload.updates:
            raise validation_error([
                ("payload.updates", "updates is required for UPDATE action")
            ])

        try:
            updated = temporary_devala_service.update_temporary_devala(
                db, td_id=payload.td_id, payload=payload.updates, actor_id=user_id
            )
            return TemporaryDevalaManagementResponse(
                status="success",
                message="Temporary devala record updated successfully.",
                data=updated,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    # ==================== DELETE ====================
    if action == CRUDAction.DELETE:
        if payload.td_id is None:
            raise validation_error([
                ("payload.td_id", "td_id is required for DELETE action")
            ])

        try:
            temporary_devala_service.delete_temporary_devala(db, td_id=payload.td_id)
            return TemporaryDevalaManagementResponse(
                status="success",
                message="Temporary devala record deleted successfully.",
                data=None,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    # Should not reach here
    raise validation_error([("action", f"Unsupported action: {action}")])
