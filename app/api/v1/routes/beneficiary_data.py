from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas.beneficiary import (
    BeneficiaryCreate,
    BeneficiaryManagementRequest,
    BeneficiaryManagementResponse,
    BeneficiaryOut,
    BeneficiaryUpdate,
    CRUDAction,
)
from app.services.beneficiary_service import beneficiary_service
from app.utils.http_exceptions import validation_error
from app.utils.authorization import ensure_crud_permission

router = APIRouter(tags=["Beneficiary Data"])


@router.post("/manage", response_model=BeneficiaryManagementResponse)
def manage_beneficiary_records(
    request: BeneficiaryManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    action = request.action
    payload = request.payload
    user_id = current_user.ua_user_id
    ensure_crud_permission(db, user_id, "beneficiary_data", action)

    if action == CRUDAction.CREATE:
        if not payload.data:
            raise validation_error(
                [("payload.data", "data is required for CREATE action")]
            )
        try:
            created = beneficiary_service.create_beneficiary(
                db, payload=payload.data, actor_id=user_id
            )
            created_out = BeneficiaryOut.model_validate(created)
            return BeneficiaryManagementResponse(
                status="success",
                message="Beneficiary created successfully.",
                data=created_out,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    if action == CRUDAction.READ_ONE:
        identifier_id = payload.bf_id
        identifier_bnn = payload.bf_bnn
        if identifier_id is None and not identifier_bnn:
            raise validation_error(
                [("payload.bf_id", "bf_id or bf_bnn is required for READ_ONE action")]
            )

        entity: BeneficiaryOut | None = None
        if identifier_id is not None:
            entity = beneficiary_service.get_beneficiary(db, identifier_id)
        elif identifier_bnn:
            entity = beneficiary_service.get_beneficiary_by_bnn(db, identifier_bnn)

        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Beneficiary not found"
            )

        entity_out = BeneficiaryOut.model_validate(entity)
        return BeneficiaryManagementResponse(
            status="success",
            message="Beneficiary retrieved successfully.",
            data=entity_out,
        )

    if action == CRUDAction.READ_ALL:
        page = payload.page or 1
        limit = payload.limit
        search = payload.search_key.strip() if payload.search_key else None
        if search == "":
            search = None
        skip = payload.skip if payload.page is None else (page - 1) * limit

        records = beneficiary_service.list_beneficiaries(
            db, skip=skip, limit=limit, search=search
        )
        total = beneficiary_service.count_beneficiaries(db, search=search)

        records_out = [BeneficiaryOut.model_validate(item) for item in records]
        return BeneficiaryManagementResponse(
            status="success",
            message="Beneficiary records retrieved successfully.",
            data=records_out,
            totalRecords=total,
            page=page,
            limit=limit,
        )

    if action == CRUDAction.UPDATE:
        if payload.bf_id is None:
            raise validation_error(
                [("payload.bf_id", "bf_id is required for UPDATE action")]
            )
        if not payload.data:
            raise validation_error(
                [("payload.data", "data is required for UPDATE action")]
            )
        try:
            updated = beneficiary_service.update_beneficiary(
                db,
                bf_id=payload.bf_id,
                payload=payload.data,
                actor_id=user_id,
            )
            updated_out = BeneficiaryOut.model_validate(updated)
            return BeneficiaryManagementResponse(
                status="success",
                message="Beneficiary updated successfully.",
                data=updated_out,
            )
        except ValueError as exc:
            if "not found" in str(exc).lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
                ) from exc
            raise validation_error([(None, str(exc))]) from exc

    if action == CRUDAction.DELETE:
        if payload.bf_id is None:
            raise validation_error(
                [("payload.bf_id", "bf_id is required for DELETE action")]
            )
        try:
            beneficiary_service.delete_beneficiary(
                db,
                bf_id=payload.bf_id,
                actor_id=user_id,
            )
            return BeneficiaryManagementResponse(
                status="success",
                message="Beneficiary deleted successfully.",
                data=None,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
            ) from exc

    raise validation_error([("action", "Invalid action specified")])
