# app/api/v1/routes/bhikku_high.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.deps import get_db
from app.models.user import UserAccount
from app.repositories.bhikku_high_repo import bhikku_high_repo
from app.schemas import bhikku_high as schemas
from app.utils.http_exceptions import validation_error

router = APIRouter(tags=["Bhikku High"])


@router.post("/manage", response_model=schemas.BhikkuHighManagementResponse)
def manage_bhikku_high_records(
    request: schemas.BhikkuHighManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    action = request.action
    payload = request.payload
    user_id = current_user.ua_user_id

    if action == schemas.CRUDAction.CREATE:
        if not payload.data or not isinstance(payload.data, schemas.BhikkuHighCreate):
            raise validation_error(
                [("payload.data", "Invalid data for CREATE action")]
            )

        existing = bhikku_high_repo.get_by_regn(db, payload.data.bhr_regn)
        if existing:
            raise validation_error(
                [
                    (
                        "payload.data.bhr_regn",
                        f"Registration number '{payload.data.bhr_regn}' already exists.",
                    )
                ]
            )

        created = bhikku_high_repo.create(db, data=payload.data, actor_id=user_id)
        return schemas.BhikkuHighManagementResponse(
            status="success",
            message="Higher bhikku registration created successfully.",
            data=created,
        )

    if action == schemas.CRUDAction.READ_ONE:
        if payload.bhr_id is None and not payload.bhr_regn:
            raise validation_error(
                [("payload.bhr_id", "bhr_id or bhr_regn is required for READ_ONE action")]
            )

        entity = None
        if payload.bhr_id is not None:
            entity = bhikku_high_repo.get(db, payload.bhr_id)
        elif payload.bhr_regn:
            entity = bhikku_high_repo.get_by_regn(db, payload.bhr_regn)

        if not entity:
            raise HTTPException(status_code=404, detail="Higher bhikku registration not found")

        return schemas.BhikkuHighManagementResponse(
            status="success",
            message="Higher bhikku registration retrieved successfully.",
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

        records = bhikku_high_repo.list(db, skip=skip, limit=limit, search=search)
        total = bhikku_high_repo.count(db, search=search)

        return schemas.BhikkuHighManagementResponse(
            status="success",
            message="Higher bhikku registrations retrieved successfully.",
            data=records,
            totalRecords=total,
            page=page,
            limit=limit,
        )

    if action == schemas.CRUDAction.UPDATE:
        if payload.bhr_id is None:
            raise validation_error(
                [("payload.bhr_id", "bhr_id is required for UPDATE action")]
            )
        if not payload.data or not isinstance(payload.data, schemas.BhikkuHighUpdate):
            raise validation_error(
                [("payload.data", "Invalid data for UPDATE action")]
            )

        entity = bhikku_high_repo.get(db, payload.bhr_id)
        if not entity:
            raise HTTPException(status_code=404, detail="Higher bhikku registration not found")

        if payload.data.bhr_regn and payload.data.bhr_regn != entity.bhr_regn:
            existing = bhikku_high_repo.get_by_regn(db, payload.data.bhr_regn)
            if existing and existing.bhr_id != entity.bhr_id:
                raise validation_error(
                    [
                        (
                            "payload.data.bhr_regn",
                            f"Registration number '{payload.data.bhr_regn}' already exists.",
                        )
                    ]
                )

        updated = bhikku_high_repo.update(
            db, entity=entity, data=payload.data, actor_id=user_id
        )
        return schemas.BhikkuHighManagementResponse(
            status="success",
            message="Higher bhikku registration updated successfully.",
            data=updated,
        )

    if action == schemas.CRUDAction.DELETE:
        if payload.bhr_id is None:
            raise validation_error(
                [("payload.bhr_id", "bhr_id is required for DELETE action")]
            )

        entity = bhikku_high_repo.get(db, payload.bhr_id)
        if not entity:
            raise HTTPException(status_code=404, detail="Higher bhikku registration not found")

        bhikku_high_repo.soft_delete(
            db, entity=entity, actor_id=user_id
        )
        return schemas.BhikkuHighManagementResponse(
            status="success",
            message="Higher bhikku registration deleted successfully.",
            data=None,
        )

    raise validation_error([("action", "Invalid action specified")])
