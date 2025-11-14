# app/api/v1/routes/bank_branches.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission, has_any_permission
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas import bank_branch as schemas
from app.services.bank_branch_service import bank_branch_service
from app.utils.http_exceptions import validation_error

router = APIRouter(tags=["Bank Branches"])


@router.post("/manage", response_model=schemas.BankBranchManagementResponse, dependencies=[has_any_permission("system:create", "system:update", "system:delete")])
def manage_bank_branch_records(
    request: schemas.BankBranchManagementRequest,
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
            create_payload = schemas.BankBranchCreate.model_validate(payload.data)
        except ValidationError as exc:
            raise validation_error([(None, str(exc))]) from exc

        try:
            created = bank_branch_service.create_bank_branch(
                db, payload=create_payload, actor_id=user_id
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

        created_out = schemas.BankBranch.model_validate(created)
        return schemas.BankBranchManagementResponse(
            status="success",
            message="Bank branch created successfully.",
            data=created_out,
        )

    if action == schemas.CRUDAction.READ_ONE:
        if payload.bb_id is None and not payload.bb_bbcode:
            raise validation_error(
                [
                    (
                        "payload.bb_id",
                        "bb_id or bb_bbcode is required for READ_ONE action",
                    )
                ]
            )

        entity = None
        if payload.bb_id is not None:
            entity = bank_branch_service.get_bank_branch(db, payload.bb_id)
        elif payload.bb_bbcode:
            entity = bank_branch_service.get_bank_branch_by_code(
                db, payload.bb_bbcode
            )

        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bank branch not found",
            )

        entity_out = schemas.BankBranch.model_validate(entity)
        return schemas.BankBranchManagementResponse(
            status="success",
            message="Bank branch retrieved successfully.",
            data=entity_out,
        )

    if action == schemas.CRUDAction.READ_ALL:
        page = payload.page or 1
        limit = payload.limit
        search = payload.search_key.strip() if payload.search_key else None
        if search == "":
            search = None
        skip = payload.skip if payload.page is None else (page - 1) * limit

        records = bank_branch_service.list_bank_branches(
            db, skip=skip, limit=limit, search=search
        )
        total = bank_branch_service.count_bank_branches(db, search=search)

        records_out = [schemas.BankBranch.model_validate(item) for item in records]
        return schemas.BankBranchManagementResponse(
            status="success",
            message="Bank branches retrieved successfully.",
            data=records_out,
            totalRecords=total,
            page=page,
            limit=limit,
        )

    if action == schemas.CRUDAction.UPDATE:
        if payload.bb_id is None:
            raise validation_error(
                [("payload.bb_id", "bb_id is required for UPDATE action")]
            )
        if not payload.data:
            raise validation_error(
                [("payload.data", "data is required for UPDATE action")]
            )
        try:
            update_payload = schemas.BankBranchUpdate.model_validate(payload.data)
        except ValidationError as exc:
            raise validation_error([(None, str(exc))]) from exc

        try:
            updated = bank_branch_service.update_bank_branch(
                db, bb_id=payload.bb_id, payload=update_payload, actor_id=user_id
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=message
                ) from exc
            raise validation_error([(None, message)]) from exc

        updated_out = schemas.BankBranch.model_validate(updated)
        return schemas.BankBranchManagementResponse(
            status="success",
            message="Bank branch updated successfully.",
            data=updated_out,
        )

    if action == schemas.CRUDAction.DELETE:
        if payload.bb_id is None:
            raise validation_error(
                [("payload.bb_id", "bb_id is required for DELETE action")]
            )

        try:
            bank_branch_service.delete_bank_branch(
                db, bb_id=payload.bb_id, actor_id=user_id
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
            ) from exc

        return schemas.BankBranchManagementResponse(
            status="success",
            message="Bank branch deleted successfully.",
            data=None,
        )

    raise validation_error([("action", "Invalid action specified")])
