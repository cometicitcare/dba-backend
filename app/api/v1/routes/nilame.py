# app/api/v1/routes/nilame.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.deps import get_db
from app.models.user import UserAccount
from app.repositories.nilame_repo import nilame_repo
from app.schemas import nilame as schemas
from app.utils.http_exceptions import validation_error

router = APIRouter(tags=["Nilame"])


@router.post("/manage", response_model=schemas.NilameManagementResponse)
def manage_nilame_records(
    request: schemas.NilameManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    action = request.action
    payload = request.payload
    user_id = current_user.ua_user_id

    if action == schemas.CRUDAction.CREATE:
        if not payload.data or not isinstance(payload.data, schemas.NilameCreate):
            raise validation_error(
                [("payload.data", "Invalid data for CREATE action")]
            )

        try:
            created = nilame_repo.create(db, data=payload.data, actor_id=user_id)
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

        return schemas.NilameManagementResponse(
            status="success",
            message="Nilame registration created successfully.",
            data=created,
        )

    if action == schemas.CRUDAction.READ_ONE:
        if payload.kr_id is None and not payload.kr_krn:
            raise validation_error(
                [("payload.kr_id", "kr_id or kr_krn is required for READ_ONE action")]
            )

        entity = None
        if payload.kr_id is not None:
            entity = nilame_repo.get(db, payload.kr_id)
        elif payload.kr_krn:
            entity = nilame_repo.get_by_krn(db, payload.kr_krn)

        if not entity:
            raise HTTPException(status_code=404, detail="Nilame registration not found")

        return schemas.NilameManagementResponse(
            status="success",
            message="Nilame registration retrieved successfully.",
            data=entity,
        )

    if action == schemas.CRUDAction.READ_ALL:
        page = payload.page if payload.page is not None else 1
        limit = payload.limit
        search = payload.search_key.strip() if payload.search_key else None
        if search == "":
            search = None
        skip = payload.skip if payload.page is None else (page - 1) * limit

        limit = max(1, min(limit, 200))
        skip = max(0, skip)

        records = nilame_repo.list(db, skip=skip, limit=limit, search=search)
        total = nilame_repo.count(db, search=search)

        return schemas.NilameManagementResponse(
            status="success",
            message="Nilame registrations retrieved successfully.",
            data=records,
            totalRecords=total,
            page=page,
            limit=limit,
        )

    if action == schemas.CRUDAction.UPDATE:
        if payload.kr_id is None:
            raise validation_error(
                [("payload.kr_id", "kr_id is required for UPDATE action")]
            )
        if not payload.data or not isinstance(payload.data, schemas.NilameUpdate):
            raise validation_error(
                [("payload.data", "Invalid data for UPDATE action")]
            )

        entity = nilame_repo.get(db, payload.kr_id)
        if not entity:
            raise HTTPException(status_code=404, detail="Nilame registration not found")

        try:
            updated = nilame_repo.update(
                db, entity=entity, data=payload.data, actor_id=user_id
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

        return schemas.NilameManagementResponse(
            status="success",
            message="Nilame registration updated successfully.",
            data=updated,
        )

    if action == schemas.CRUDAction.DELETE:
        if payload.kr_id is None:
            raise validation_error(
                [("payload.kr_id", "kr_id is required for DELETE action")]
            )

        entity = nilame_repo.get(db, payload.kr_id)
        if not entity:
            raise HTTPException(status_code=404, detail="Nilame registration not found")

        nilame_repo.soft_delete(db, entity=entity, actor_id=user_id)
        return schemas.NilameManagementResponse(
            status="success",
            message="Nilame registration deleted successfully.",
            data=None,
        )

    raise validation_error([("action", "Invalid action specified")])
