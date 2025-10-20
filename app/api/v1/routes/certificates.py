# app/api/v1/routes/certificates.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.deps import get_db
from app.models.user import UserAccount
from app.repositories.certificate_repo import certificate_repo
from app.schemas import certificate as schemas
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
        if not payload.data or not isinstance(payload.data, schemas.CertificateCreate):
            raise validation_error(
                [("payload.data", "Invalid data for CREATE action")]
            )

        existing = certificate_repo.get_by_code(db, payload.data.cd_code)
        if existing:
            raise validation_error(
                [
                    (
                        "payload.data.cd_code",
                        f"Certificate code '{payload.data.cd_code}' already exists.",
                    )
                ]
            )

        created = certificate_repo.create(db, data=payload.data, actor_id=user_id)
        return schemas.CertificateManagementResponse(
            status="success",
            message="Certificate created successfully.",
            data=created,
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

        return schemas.CertificateManagementResponse(
            status="success",
            message="Certificate retrieved successfully.",
            data=entity,
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

        return schemas.CertificateManagementResponse(
            status="success",
            message="Certificates retrieved successfully.",
            data=records,
            totalRecords=total,
            page=page,
            limit=limit,
        )

    if action == schemas.CRUDAction.UPDATE:
        if payload.cd_id is None:
            raise validation_error(
                [("payload.cd_id", "cd_id is required for UPDATE action")]
            )
        if not payload.data or not isinstance(payload.data, schemas.CertificateUpdate):
            raise validation_error(
                [("payload.data", "Invalid data for UPDATE action")]
            )

        entity = certificate_repo.get(db, payload.cd_id)
        if not entity:
            raise HTTPException(status_code=404, detail="Certificate not found")

        if payload.data.cd_code and payload.data.cd_code != entity.cd_code:
            existing = certificate_repo.get_by_code(db, payload.data.cd_code)
            if existing and existing.cd_id != entity.cd_id:
                raise validation_error(
                    [
                        (
                            "payload.data.cd_code",
                            f"Certificate code '{payload.data.cd_code}' already exists.",
                        )
                    ]
                )

        updated = certificate_repo.update(
            db, entity=entity, data=payload.data, actor_id=user_id
        )
        return schemas.CertificateManagementResponse(
            status="success",
            message="Certificate updated successfully.",
            data=updated,
        )

    if action == schemas.CRUDAction.DELETE:
        if payload.cd_id is None:
            raise validation_error(
                [("payload.cd_id", "cd_id is required for DELETE action")]
            )

        entity = certificate_repo.get(db, payload.cd_id)
        if not entity:
            raise HTTPException(status_code=404, detail="Certificate not found")

        certificate_repo.soft_delete(db, entity=entity, actor_id=user_id)
        return schemas.CertificateManagementResponse(
            status="success",
            message="Certificate deleted successfully.",
            data=None,
        )

    raise validation_error([("action", "Invalid action specified")])

