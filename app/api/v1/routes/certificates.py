# app/api/v1/routes/certificates.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.deps import get_db
from app.models.user import UserAccount
from app.repositories.certificate_repo import certificate_repo
from app.schemas import certificate as schemas
from app.services.certificate_service import certificate_service
from app.utils.http_exceptions import validation_error

router = APIRouter(tags=["Certificates"])


@router.post("/manage", response_model=schemas.CertificateManagementResponse)
def manage_certificate_records(
    request: schemas.CertificateManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    action = request.action
    payload = request.payload
    user_id = current_user.ua_user_id

    if action == schemas.CRUDAction.CREATE:
        if not payload.data:
            raise validation_error([("payload.data", "Invalid data for CREATE action")])
        try:
            create_payload = schemas.CertificateCreate.model_validate(payload.data)
        except ValidationError as exc:
            raise validation_error([(None, str(exc))]) from exc

        try:
            created = certificate_service.create_certificate(
                db, payload=create_payload, actor_id=user_id
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
            ) from exc

        created_out = schemas.Certificate.model_validate(created)
        return schemas.CertificateManagementResponse(
            status="success",
            message="Certificate created successfully.",
            data=created_out,
        )

    if action == schemas.CRUDAction.READ_ONE:
        if payload.cd_id is None and not payload.cd_code:
            raise validation_error(
                [("payload.cd_id", "cd_id or cd_code is required for READ_ONE action")]
            )

        entity = None
        if payload.cd_id is not None:
            entity = certificate_repo.get(db, payload.cd_id)
        elif payload.cd_code:
            entity = certificate_repo.get_by_code(db, payload.cd_code)

        if not entity:
            raise HTTPException(status_code=404, detail="Certificate not found")

        entity_out = schemas.Certificate.model_validate(entity)
        return schemas.CertificateManagementResponse(
            status="success",
            message="Certificate retrieved successfully.",
            data=entity_out,
        )

    if action == schemas.CRUDAction.READ_ALL:
        page = payload.page or 1
        limit = payload.limit
        search = payload.search_key.strip() if payload.search_key else None
        if search == "":
            search = None
        skip = payload.skip if payload.page is None else (page - 1) * limit

        limit = max(1, min(limit, 200))
        skip = max(0, skip)

        records = certificate_repo.list(db, skip=skip, limit=limit, search=search)
        total = certificate_repo.count(db, search=search)

        records_out = [schemas.Certificate.model_validate(item) for item in records]
        return schemas.CertificateManagementResponse(
            status="success",
            message="Certificates retrieved successfully.",
            data=records_out,
            totalRecords=total,
            page=page,
            limit=limit,
        )

    if action == schemas.CRUDAction.UPDATE:
        if payload.cd_id is None:
            raise validation_error(
                [("payload.cd_id", "cd_id is required for UPDATE action")]
            )
        if not payload.data:
            raise validation_error([("payload.data", "Invalid data for UPDATE action")])
        try:
            update_payload = schemas.CertificateUpdate.model_validate(payload.data)
        except ValidationError as exc:
            raise validation_error([(None, str(exc))]) from exc

        try:
            updated = certificate_service.update_certificate(
                db, cd_id=payload.cd_id, payload=update_payload, actor_id=user_id
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message) from exc
            raise validation_error([(None, message)]) from exc
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
            ) from exc

        updated_out = schemas.Certificate.model_validate(updated)
        return schemas.CertificateManagementResponse(
            status="success",
            message="Certificate updated successfully.",
            data=updated_out,
        )

    if action == schemas.CRUDAction.DELETE:
        if payload.cd_id is None:
            raise validation_error(
                [("payload.cd_id", "cd_id is required for DELETE action")]
            )

        try:
            certificate_service.delete_certificate(
                db, cd_id=payload.cd_id, actor_id=user_id
            )
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
            ) from exc

        return schemas.CertificateManagementResponse(
            status="success",
            message="Certificate deleted successfully.",
            data=None,
        )

    raise validation_error([("action", "Invalid action specified")])
