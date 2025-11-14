# app/api/v1/routes/bhikku_summary.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission, has_any_permission
from app.api.deps import get_db
from app.models.user import UserAccount
from app.repositories.bhikku_summary_repo import bhikku_summary_repo
from app.schemas import bhikku_summary as schemas
from app.utils.http_exceptions import validation_error

router = APIRouter(tags=["Bhikku Summary"])


@router.post("/manage", response_model=schemas.BhikkuSummaryManagementResponse, dependencies=[has_any_permission("bhikku:create", "bhikku:update", "bhikku:delete")])
def manage_bhikku_summary_records(
    request: schemas.BhikkuSummaryManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    action = request.action
    payload = request.payload
    user_id = current_user.ua_user_id

    if action == schemas.CRUDAction.CREATE:
        if not payload.data or not isinstance(payload.data, schemas.BhikkuSummaryCreate):
            raise validation_error(
                [("payload.data", "Invalid data for CREATE action")]
            )

        existing = bhikku_summary_repo.get(db, payload.data.bs_regn)
        if existing:
            raise validation_error(
                [
                    (
                        "payload.data.bs_regn",
                        f"Summary already exists for registration '{payload.data.bs_regn}'.",
                    )
                ]
            )

        created = bhikku_summary_repo.create(db, data=payload.data, actor_id=user_id)
        return schemas.BhikkuSummaryManagementResponse(
            status="success",
            message="Bhikku summary created successfully.",
            data=created,
        )

    if action == schemas.CRUDAction.READ_ONE:
        if not payload.bs_regn:
            raise validation_error(
                [("payload.bs_regn", "bs_regn is required for READ_ONE action")]
            )

        entity = bhikku_summary_repo.get(db, payload.bs_regn)
        if not entity:
            raise HTTPException(status_code=404, detail="Bhikku summary not found")

        return schemas.BhikkuSummaryManagementResponse(
            status="success",
            message="Bhikku summary retrieved successfully.",
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

        records = bhikku_summary_repo.list(db, skip=skip, limit=limit, search=search)
        total = bhikku_summary_repo.count(db, search=search)

        return schemas.BhikkuSummaryManagementResponse(
            status="success",
            message="Bhikku summaries retrieved successfully.",
            data=records,
            totalRecords=total,
            page=page,
            limit=limit,
        )

    if action == schemas.CRUDAction.UPDATE:
        if not payload.bs_regn:
            raise validation_error(
                [("payload.bs_regn", "bs_regn is required for UPDATE action")]
            )
        if not payload.data or not isinstance(payload.data, schemas.BhikkuSummaryUpdate):
            raise validation_error(
                [("payload.data", "Invalid data for UPDATE action")]
            )

        entity = bhikku_summary_repo.get(db, payload.bs_regn)
        if not entity:
            raise HTTPException(status_code=404, detail="Bhikku summary not found")

        updated = bhikku_summary_repo.update(
            db, entity=entity, data=payload.data, actor_id=user_id
        )
        return schemas.BhikkuSummaryManagementResponse(
            status="success",
            message="Bhikku summary updated successfully.",
            data=updated,
        )

    if action == schemas.CRUDAction.DELETE:
        if not payload.bs_regn:
            raise validation_error(
                [("payload.bs_regn", "bs_regn is required for DELETE action")]
            )

        entity = bhikku_summary_repo.get(db, payload.bs_regn)
        if not entity:
            raise HTTPException(status_code=404, detail="Bhikku summary not found")

        bhikku_summary_repo.soft_delete(db, entity=entity, actor_id=user_id)
        return schemas.BhikkuSummaryManagementResponse(
            status="success",
            message="Bhikku summary deleted successfully.",
            data=None,
        )

    raise validation_error([("action", "Invalid action specified")])

