# app/api/v1/routes/banks.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas import bank as schemas
from app.services.bank_service import bank_service
from app.utils.http_exceptions import validation_error

router = APIRouter(tags=["Banks"])


@router.post("/manage", response_model=schemas.BankManagementResponse)
def manage_bank_records(
    request: schemas.BankManagementRequest,
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
            create_payload = schemas.BankCreate.model_validate(payload.data)
        except ValidationError as exc:
            raise validation_error([(None, str(exc))]) from exc

        try:
            created = bank_service.create_bank(
                db, payload=create_payload, actor_id=user_id
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

        created_out = schemas.Bank.model_validate(created)
        return schemas.BankManagementResponse(
            status="success",
            message="Bank created successfully.",
            data=created_out,
        )

    if action == schemas.CRUDAction.READ_ONE:
        if payload.bk_id is None and not payload.bk_bcode:
            raise validation_error(
                [
                    (
                        "payload.bk_id",
                        "bk_id or bk_bcode is required for READ_ONE action",
                    )
                ]
            )

        entity = None
        if payload.bk_id is not None:
            entity = bank_service.get_bank(db, payload.bk_id)
        elif payload.bk_bcode:
            entity = bank_service.get_bank_by_code(db, payload.bk_bcode)

        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bank not found",
            )

        entity_out = schemas.Bank.model_validate(entity)
        return schemas.BankManagementResponse(
            status="success",
            message="Bank retrieved successfully.",
            data=entity_out,
        )

    if action == schemas.CRUDAction.READ_ALL:
        page = payload.page or 1
        limit = payload.limit
        search = payload.search_key.strip() if payload.search_key else None
        if search == "":
            search = None
        skip = payload.skip if payload.page is None else (page - 1) * limit

        records = bank_service.list_banks(db, skip=skip, limit=limit, search=search)
        total = bank_service.count_banks(db, search=search)

        records_out = [schemas.Bank.model_validate(item) for item in records]
        return schemas.BankManagementResponse(
            status="success",
            message="Banks retrieved successfully.",
            data=records_out,
            totalRecords=total,
            page=page,
            limit=limit,
        )

    if action == schemas.CRUDAction.UPDATE:
        if payload.bk_id is None:
            raise validation_error(
                [("payload.bk_id", "bk_id is required for UPDATE action")]
            )
        if not payload.data:
            raise validation_error(
                [("payload.data", "data is required for UPDATE action")]
            )
        try:
            update_payload = schemas.BankUpdate.model_validate(payload.data)
        except ValidationError as exc:
            raise validation_error([(None, str(exc))]) from exc

        try:
            updated = bank_service.update_bank(
                db, bk_id=payload.bk_id, payload=update_payload, actor_id=user_id
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=message
                ) from exc
            raise validation_error([(None, message)]) from exc

        updated_out = schemas.Bank.model_validate(updated)
        return schemas.BankManagementResponse(
            status="success",
            message="Bank updated successfully.",
            data=updated_out,
        )

    if action == schemas.CRUDAction.DELETE:
        if payload.bk_id is None:
            raise validation_error(
                [("payload.bk_id", "bk_id is required for DELETE action")]
            )

        try:
            bank_service.delete_bank(db, bk_id=payload.bk_id, actor_id=user_id)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
            ) from exc

        return schemas.BankManagementResponse(
            status="success",
            message="Bank deleted successfully.",
            data=None,
        )

    raise validation_error([("action", "Invalid action specified")])
