from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission, has_any_permission
from app.api.deps import get_db
from app.models.user import UserAccount
from app.repositories.role_repo import role_repo
from app.schemas.roles import (
    CRUDAction,
    RoleCreate,
    RoleManagementRequest,
    RoleManagementResponse,
    RoleUpdate,
)
from app.utils.http_exceptions import validation_error

router = APIRouter()  # Tags defined in router.py


@router.post("/manage", response_model=RoleManagementResponse, dependencies=[has_permission("system:manage_roles")])
def manage_roles(
    request: RoleManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
) -> RoleManagementResponse:
    action = request.action
    payload = request.payload
    user_id = current_user.ua_user_id

    if action == CRUDAction.CREATE:
        if not payload.data or not isinstance(payload.data, RoleCreate):
            raise validation_error([("payload.data", "Invalid data for CREATE action")])

        created_by = payload.data.ro_created_by or user_id
        updated_by = payload.data.ro_updated_by or created_by or user_id

        try:
            role = role_repo.create(
                db,
                data=payload.data,
                created_by=created_by,
                updated_by=updated_by,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

        return RoleManagementResponse(
            status="success",
            message="Role created successfully.",
            data=role,
        )

    if action == CRUDAction.READ_ONE:
        if not payload.ro_role_id:
            raise validation_error(
                [("payload.ro_role_id", "ro_role_id is required for READ_ONE action")]
            )

        role = role_repo.get(
            db, payload.ro_role_id, include_deleted=payload.include_deleted
        )
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

        return RoleManagementResponse(
            status="success",
            message="Role retrieved successfully.",
            data=role,
        )

    if action == CRUDAction.READ_ALL:
        page = payload.page if payload.page is not None else 1
        limit = payload.limit
        search = payload.search_key.strip() if payload.search_key else None
        if search == "":
            search = None
        skip = payload.skip if payload.page is None else max(0, (page - 1) * limit)

        records, total = role_repo.list(
            db,
            skip=skip,
            limit=limit,
            search=search,
            include_deleted=payload.include_deleted,
        )

        return RoleManagementResponse(
            status="success",
            message="Roles retrieved successfully.",
            data=records,
            totalRecords=total,
            page=page,
            limit=limit,
        )

    if action == CRUDAction.UPDATE:
        if not payload.ro_role_id:
            raise validation_error(
                [("payload.ro_role_id", "ro_role_id is required for UPDATE action")]
            )
        if not payload.data or not isinstance(payload.data, RoleUpdate):
            raise validation_error(
                [("payload.data", "Invalid data for UPDATE action")]
            )

        role = role_repo.get(db, payload.ro_role_id)
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

        updates = payload.data.model_dump(exclude_unset=True, exclude={"ro_updated_by"})
        if not updates:
            raise validation_error([(None, "No fields provided to update.")])

        updated_by = payload.data.ro_updated_by or user_id

        try:
            updated_role = role_repo.update(
                db, entity=role, data=payload.data, updated_by=updated_by
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

        return RoleManagementResponse(
            status="success",
            message="Role updated successfully.",
            data=updated_role,
        )

    if action == CRUDAction.DELETE:
        if not payload.ro_role_id:
            raise validation_error(
                [("payload.ro_role_id", "ro_role_id is required for DELETE action")]
            )

        role = role_repo.get(db, payload.ro_role_id)
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

        try:
            role_repo.soft_delete(
                db,
                entity=role,
                updated_by=user_id,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

        return RoleManagementResponse(
            status="success",
            message="Role deleted successfully.",
            data=None,
        )

    raise validation_error([("action", "Invalid action specified")])
