# app/api/v1/routes/bhikku_certification.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission, has_any_permission
from app.api.deps import get_db
from app.models.user import UserAccount
from app.repositories.bhikku_certification_repo import bhikku_certification_repo
from app.schemas import bhikku_certification as schemas
from app.utils.http_exceptions import validation_error

router = APIRouter()  # Tags defined in router.py


@router.post("/manage", response_model=schemas.BhikkuCertificationManagementResponse, dependencies=[has_any_permission("bhikku:create", "bhikku:update", "bhikku:delete")])
def manage_bhikku_certification_records(
    request: schemas.BhikkuCertificationManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    action = request.action
    payload = request.payload
    user_id = current_user.ua_user_id

    if action == schemas.CRUDAction.CREATE:
        if not payload.data or not isinstance(payload.data, schemas.BhikkuCertificationCreate):
            raise validation_error(
                [("payload.data", "Invalid data for CREATE action")]
            )

        created = bhikku_certification_repo.create(
            db, data=payload.data, actor_id=user_id
        )
        return schemas.BhikkuCertificationManagementResponse(
            status="success",
            message="Bhikku certification created successfully.",
            data=created,
        )

    if action == schemas.CRUDAction.READ_ONE:
        if payload.bc_id is None and not payload.bc_regno:
            raise validation_error(
                [("payload.bc_id", "bc_id or bc_regno is required for READ_ONE action")]
            )

        entity = None
        if payload.bc_id is not None:
            entity = bhikku_certification_repo.get(db, payload.bc_id)
        elif payload.bc_regno:
            entity = bhikku_certification_repo.get_by_regno(db, payload.bc_regno)

        if not entity:
            raise HTTPException(status_code=404, detail="Bhikku certification not found")

        return schemas.BhikkuCertificationManagementResponse(
            status="success",
            message="Bhikku certification retrieved successfully.",
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

        records = bhikku_certification_repo.list(db, skip=skip, limit=limit, search=search)
        total = bhikku_certification_repo.count(db, search=search)

        return schemas.BhikkuCertificationManagementResponse(
            status="success",
            message="Bhikku certifications retrieved successfully.",
            data=records,
            totalRecords=total,
            page=page,
            limit=limit,
        )

    if action == schemas.CRUDAction.UPDATE:
        if payload.bc_id is None:
            raise validation_error(
                [("payload.bc_id", "bc_id is required for UPDATE action")]
            )
        if not payload.data or not isinstance(payload.data, schemas.BhikkuCertificationUpdate):
            raise validation_error(
                [("payload.data", "Invalid data for UPDATE action")]
            )

        entity = bhikku_certification_repo.get(db, payload.bc_id)
        if not entity:
            raise HTTPException(status_code=404, detail="Bhikku certification not found")

        updated = bhikku_certification_repo.update(
            db, entity=entity, data=payload.data, actor_id=user_id
        )
        return schemas.BhikkuCertificationManagementResponse(
            status="success",
            message="Bhikku certification updated successfully.",
            data=updated,
        )

    if action == schemas.CRUDAction.DELETE:
        if payload.bc_id is None:
            raise validation_error(
                [("payload.bc_id", "bc_id is required for DELETE action")]
            )

        entity = bhikku_certification_repo.get(db, payload.bc_id)
        if not entity:
            raise HTTPException(status_code=404, detail="Bhikku certification not found")

        bhikku_certification_repo.soft_delete(
            db, entity=entity, actor_id=user_id
        )
        return schemas.BhikkuCertificationManagementResponse(
            status="success",
            message="Bhikku certification deleted successfully.",
            data=None,
        )

    raise validation_error([("action", "Invalid action specified")])

