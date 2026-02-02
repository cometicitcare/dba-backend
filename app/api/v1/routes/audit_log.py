# app/api/v1/routes/audit_log.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission, has_any_permission
from app.api.deps import get_db
from app.models.user import UserAccount
from app.repositories.audit_log_repo import audit_log_repo
from app.schemas.audit_log import (
    AuditLogManagementRequest,
    AuditLogManagementResponse,
    AuditLogUpdate,
    CRUDAction,
)
from app.utils.http_exceptions import validation_error

router = APIRouter()  # Tags defined in router.py


def _is_system_user(user: UserAccount) -> bool:
    try:
        role = user.role
        return bool(role and getattr(role, "ro_is_system_role", False))
    except Exception:
        return False


@router.post("/manage", response_model=AuditLogManagementResponse, dependencies=[has_any_permission("system:view_audit_log")])
def manage_audit_log(
    request: AuditLogManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
) -> AuditLogManagementResponse:
    action = request.action
    payload = request.payload
    is_admin = _is_system_user(current_user)

    if action == CRUDAction.READ_ONE:
        if not payload.al_id:
            raise validation_error(
                [("payload.al_id", "al_id is required for READ_ONE action")]
            )
        entity = audit_log_repo.get(db, al_id=payload.al_id)
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Audit log not found"
            )

        return AuditLogManagementResponse(
            status="success",
            message="Audit log retrieved successfully.",
            data=entity,
        )

    if action == CRUDAction.READ_ALL:
        records, total = audit_log_repo.list(db, payload=payload)
        page = payload.page if payload.page and payload.page > 0 else 1
        return AuditLogManagementResponse(
            status="success",
            message="Audit logs retrieved successfully.",
            data=list(records),
            totalRecords=total,
            page=page,
            limit=payload.limit,
        )

    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify audit logs.",
        )

    if action == CRUDAction.DELETE:
        if not payload.al_id:
            raise validation_error(
                [("payload.al_id", "al_id is required for DELETE action")]
            )
        entity = audit_log_repo.get(db, al_id=payload.al_id)
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Audit log not found"
            )
        audit_log_repo.delete(db, entity=entity)
        db.commit()
        return AuditLogManagementResponse(
            status="success",
            message="Audit log deleted successfully.",
            data=None,
        )

    if action == CRUDAction.UPDATE:
        if not payload.al_id:
            raise validation_error(
                [("payload.al_id", "al_id is required for UPDATE action")]
            )
        if not payload.data or not isinstance(payload.data, AuditLogUpdate):
            raise validation_error(
                [("payload.data", "AuditLogUpdate payload is required")]
            )
        entity = audit_log_repo.get(db, al_id=payload.al_id)
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Audit log not found"
            )
        audit_log_repo.update(db, entity=entity, data=payload.data)
        db.commit()
        db.refresh(entity)
        return AuditLogManagementResponse(
            status="success",
            message="Audit log updated successfully.",
            data=entity,
        )

    if action == CRUDAction.CREATE:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="Audit logs are generated automatically and cannot be created manually.",
        )

    raise validation_error([("action", "Invalid action specified")])

