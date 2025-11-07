from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas.vihara import (
    CRUDAction,
    ViharaCreate,
    ViharaManagementRequest,
    ViharaManagementResponse,
    ViharaOut,
    ViharaUpdate,
)
from app.services.vihara_service import vihara_service
from app.utils.http_exceptions import validation_error

router = APIRouter(tags=["Vihara Data"])


@router.post("/manage", response_model=ViharaManagementResponse)
def manage_vihara_records(
    request: ViharaManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    action = request.action
    payload = request.payload
    user_id = current_user.ua_user_id

    if action == CRUDAction.CREATE:
        create_payload = _coerce_payload(
            payload.data,
            target=ViharaCreate,
            prefix="payload.data",
        )
        try:
            created = vihara_service.create_vihara(
                db, payload=create_payload, actor_id=user_id
            )
            return ViharaManagementResponse(
                status="success",
                message="Vihara created successfully.",
                data=created,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    if action == CRUDAction.READ_ONE:
        identifier_id = payload.vh_id
        identifier_trn = payload.vh_trn
        if identifier_id is None and not identifier_trn:
            raise validation_error(
                [("payload.vh_id", "vh_id or vh_trn is required for READ_ONE action")]
            )

        entity: ViharaOut | None = None
        if identifier_id is not None:
            entity = vihara_service.get_vihara(db, identifier_id)
        elif identifier_trn:
            entity = vihara_service.get_vihara_by_trn(db, identifier_trn)

        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Vihara not found"
            )

        return ViharaManagementResponse(
            status="success",
            message="Vihara retrieved successfully.",
            data=entity,
        )

    if action == CRUDAction.READ_ALL:
        page = payload.page or 1
        limit = payload.limit
        search = payload.search_key.strip() if payload.search_key else None
        if search == "":
            search = None
        skip = payload.skip if payload.page is None else (page - 1) * limit

        records = vihara_service.list_viharas(
            db, skip=skip, limit=limit, search=search
        )
        total = vihara_service.count_viharas(db, search=search)
        return ViharaManagementResponse(
            status="success",
            message="Vihara records retrieved successfully.",
            data=records,
            totalRecords=total,
            page=page,
            limit=limit,
        )

    if action == CRUDAction.UPDATE:
        if payload.vh_id is None:
            raise validation_error(
                [("payload.vh_id", "vh_id is required for UPDATE action")]
            )
        update_payload = _coerce_payload(
            payload.data,
            target=ViharaUpdate,
            prefix="payload.data",
        )

        try:
            updated = vihara_service.update_vihara(
                db,
                vh_id=payload.vh_id,
                payload=update_payload,
                actor_id=user_id,
            )
            return ViharaManagementResponse(
                status="success",
                message="Vihara updated successfully.",
                data=updated,
            )
        except ValueError as exc:
            if "not found" in str(exc).lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
                ) from exc
            raise validation_error([(None, str(exc))]) from exc

    if action == CRUDAction.DELETE:
        if payload.vh_id is None:
            raise validation_error(
                [("payload.vh_id", "vh_id is required for DELETE action")]
            )
        try:
            vihara_service.delete_vihara(
                db,
                vh_id=payload.vh_id,
                actor_id=user_id,
            )
            return ViharaManagementResponse(
                status="success",
                message="Vihara deleted successfully.",
                data=None,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
            ) from exc

    raise validation_error([("action", "Invalid action specified")])


def _build_pydantic_errors(
    exc: ValidationError,
    *,
    prefix: str | None = None,
) -> list[tuple[str | None, str]]:
    errors: list[tuple[str | None, str]] = []
    for err in exc.errors():
        loc = err.get("loc") or ()
        msg = err.get("msg") or "Invalid value"
        field_parts = [str(part) for part in loc if part != "__root__"]
        field = ".".join(field_parts) if field_parts else None
        if prefix:
            field = f"{prefix}.{field}" if field else prefix
        errors.append((field, msg))
    return errors or [(prefix, "Invalid payload") if prefix else (None, "Invalid payload")]


def _coerce_payload(
    raw_payload: object,
    *,
    target: type[BaseModel],
    prefix: str,
) -> BaseModel:
    if raw_payload is None:
        raise validation_error([(prefix, "Payload is required")])

    if isinstance(raw_payload, target):
        return raw_payload

    if isinstance(raw_payload, BaseModel):
        raw_payload = raw_payload.model_dump(exclude_unset=True)

    if isinstance(raw_payload, dict):
        try:
            return target.model_validate(raw_payload)
        except ValidationError as exc:
            raise validation_error(_build_pydantic_errors(exc, prefix=prefix)) from exc

    raise validation_error(
        [(prefix, f"Expected object compatible with {target.__name__}")],
    )
