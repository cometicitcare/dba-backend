# app/api/v1/routes/certificate_changes.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission, has_any_permission
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas import certificate_change as schemas
from app.services.certificate_change_service import certificate_change_service
from app.utils.http_exceptions import validation_error

router = APIRouter()  # Tags defined in router.py


@router.post("/manage", response_model=schemas.CertificateChangeManagementResponse, dependencies=[has_any_permission("certificate:create", "certificate:update", "certificate:delete")])
def manage_certificate_change_records(
    request: schemas.CertificateChangeManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    action = request.action
    payload = request.payload
    user_id = current_user.ua_user_id

    if action == schemas.CRUDAction.CREATE:
        if not payload.data:
            raise validation_error(
                [("payload.data", "data is required for CREATE action")]
            )
        try:
            create_payload = schemas.CertificateChangeCreate.model_validate(
                payload.data
            )
        except ValidationError as exc:
            raise validation_error([(None, str(exc))]) from exc

        try:
            created = certificate_change_service.create_certificate_change(
                db, payload=create_payload, actor_id=user_id
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
            ) from exc

        created_out = schemas.CertificateChange.model_validate(created)
        return schemas.CertificateChangeManagementResponse(
            status="success",
            message="Certificate change record created successfully.",
            data=created_out,
        )

    if action == schemas.CRUDAction.READ_ONE:
        if payload.ch_id is None:
            raise validation_error(
                [("payload.ch_id", "ch_id is required for READ_ONE action")]
            )

        entity = certificate_change_service.get_certificate_change(
            db, payload.ch_id
        )
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Certificate change record not found",
            )

        entity_out = schemas.CertificateChange.model_validate(entity)
        return schemas.CertificateChangeManagementResponse(
            status="success",
            message="Certificate change record retrieved successfully.",
            data=entity_out,
        )

    if action == schemas.CRUDAction.READ_ALL:
        page = payload.page or 1
        limit = payload.limit
        search = payload.search_key.strip() if payload.search_key else None
        if search == "":
            search = None
        skip = payload.skip if payload.page is None else (page - 1) * limit

        records = certificate_change_service.list_certificate_changes(
            db, skip=skip, limit=limit, search=search
        )
        total = certificate_change_service.count_certificate_changes(
            db, search=search
        )

        records_out = [
            schemas.CertificateChange.model_validate(item) for item in records
        ]
        return schemas.CertificateChangeManagementResponse(
            status="success",
            message="Certificate change records retrieved successfully.",
            data=records_out,
            totalRecords=total,
            page=page,
            limit=limit,
        )

    if action == schemas.CRUDAction.UPDATE:
        if payload.ch_id is None:
            raise validation_error(
                [("payload.ch_id", "ch_id is required for UPDATE action")]
            )
        if not payload.data:
            raise validation_error(
                [("payload.data", "data is required for UPDATE action")]
            )
        try:
            update_payload = schemas.CertificateChangeUpdate.model_validate(
                payload.data
            )
        except ValidationError as exc:
            raise validation_error([(None, str(exc))]) from exc

        try:
            updated = certificate_change_service.update_certificate_change(
                db, ch_id=payload.ch_id, payload=update_payload, actor_id=user_id
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=message
                ) from exc
            raise validation_error([(None, message)]) from exc
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
            ) from exc

        updated_out = schemas.CertificateChange.model_validate(updated)
        return schemas.CertificateChangeManagementResponse(
            status="success",
            message="Certificate change record updated successfully.",
            data=updated_out,
        )

    if action == schemas.CRUDAction.DELETE:
        if payload.ch_id is None:
            raise validation_error(
                [("payload.ch_id", "ch_id is required for DELETE action")]
            )

        try:
            certificate_change_service.delete_certificate_change(
                db, ch_id=payload.ch_id, actor_id=user_id
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
            ) from exc
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
            ) from exc

        return schemas.CertificateChangeManagementResponse(
            status="success",
            message="Certificate change record deleted successfully.",
            data=None,
        )

    raise validation_error([("action", "Invalid action specified")])
