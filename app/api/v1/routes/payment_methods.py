# app/api/v1/routes/payment_methods.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas import payment_method as schemas
from app.services.payment_method_service import payment_method_service
from app.utils.http_exceptions import validation_error

router = APIRouter(tags=["Payment Methods"])


@router.post("/manage", response_model=schemas.PaymentMethodManagementResponse)
def manage_payment_methods(
    request: schemas.PaymentMethodManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    action = request.action
    payload = request.payload
    user_id = current_user.ua_user_id

    def _as_plain_dict(data: object, *, exclude_unset: bool = False) -> object:
        if isinstance(data, BaseModel):
            return data.model_dump(exclude_unset=exclude_unset)
        return data

    if action == schemas.CRUDAction.CREATE:
        if not payload.data:
            raise validation_error(
                [("payload.data", "data is required for CREATE action")]
            )
        try:
            create_payload = schemas.PaymentMethodCreate.model_validate(
                _as_plain_dict(payload.data)
            )
        except ValidationError as exc:
            raise validation_error([(None, str(exc))]) from exc

        try:
            created = payment_method_service.create_payment_method(
                db,
                payload=create_payload,
                actor_id=user_id,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

        created_out = schemas.PaymentMethod.model_validate(created)
        return schemas.PaymentMethodManagementResponse(
            status="success",
            message="Payment method created successfully.",
            data=created_out,
        )

    if action == schemas.CRUDAction.READ_ONE:
        if payload.pm_id is None and not payload.pm_code:
            raise validation_error(
                [
                    (
                        "payload.pm_id",
                        "pm_id or pm_code is required for READ_ONE action",
                    )
                ]
            )

        entity = None
        if payload.pm_id is not None:
            entity = payment_method_service.get_payment_method(db, payload.pm_id)
        elif payload.pm_code:
            entity = payment_method_service.get_payment_method_by_code(
                db, payload.pm_code
            )

        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment method not found",
            )

        entity_out = schemas.PaymentMethod.model_validate(entity)
        return schemas.PaymentMethodManagementResponse(
            status="success",
            message="Payment method retrieved successfully.",
            data=entity_out,
        )

    if action == schemas.CRUDAction.READ_ALL:
        page = payload.page or 1
        limit = payload.limit
        search = payload.search_key.strip() if payload.search_key else None
        if search == "":
            search = None
        skip = payload.skip if payload.page is None else (page - 1) * limit

        records = payment_method_service.list_payment_methods(
            db,
            skip=skip,
            limit=limit,
            search=search,
        )
        total = payment_method_service.count_payment_methods(db, search=search)

        records_out = [schemas.PaymentMethod.model_validate(item) for item in records]
        return schemas.PaymentMethodManagementResponse(
            status="success",
            message="Payment methods retrieved successfully.",
            data=records_out,
            totalRecords=total,
            page=page,
            limit=limit,
        )

    if action == schemas.CRUDAction.UPDATE:
        if payload.pm_id is None:
            raise validation_error(
                [("payload.pm_id", "pm_id is required for UPDATE action")]
            )
        if not payload.data:
            raise validation_error(
                [("payload.data", "data is required for UPDATE action")]
            )
        try:
            update_payload = schemas.PaymentMethodUpdate.model_validate(
                _as_plain_dict(payload.data, exclude_unset=True)
            )
        except ValidationError as exc:
            raise validation_error([(None, str(exc))]) from exc

        try:
            updated = payment_method_service.update_payment_method(
                db,
                pm_id=payload.pm_id,
                payload=update_payload,
                actor_id=user_id,
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=message,
                ) from exc
            raise validation_error([(None, message)]) from exc

        updated_out = schemas.PaymentMethod.model_validate(updated)
        return schemas.PaymentMethodManagementResponse(
            status="success",
            message="Payment method updated successfully.",
            data=updated_out,
        )

    if action == schemas.CRUDAction.DELETE:
        if payload.pm_id is None:
            raise validation_error(
                [("payload.pm_id", "pm_id is required for DELETE action")]
            )

        try:
            payment_method_service.delete_payment_method(
                db,
                pm_id=payload.pm_id,
                actor_id=user_id,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc

        return schemas.PaymentMethodManagementResponse(
            status="success",
            message="Payment method deleted successfully.",
            data=None,
        )

    raise validation_error([("action", "Invalid action specified")])
