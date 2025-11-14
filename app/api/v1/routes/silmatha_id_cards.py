# app/api/v1/routes/silmatha_id_cards.py
from __future__ import annotations

import json
from typing import Any, Dict

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas import silmatha_id_card as schemas
from app.services.silmatha_id_card_service import silmatha_id_card_service
from app.utils.http_exceptions import validation_error

router = APIRouter(tags=["Silmatha ID Cards"])


@router.post("/manage", response_model=schemas.SilmathaIDCardManagementResponse)
def manage_silmatha_id_cards(
    request: schemas.SilmathaIDCardManagementRequest,
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
            create_payload = schemas.SilmathaIDCardCreate.model_validate(
                payload.data
            )
        except ValidationError as exc:
            raise validation_error(_format_validation_errors(exc)) from exc

        try:
            created = silmatha_id_card_service.create_card(
                db,
                payload=create_payload,
                actor_id=user_id,
                left_thumbprint=None,
                applicant_image=None,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

        created_out = schemas.SilmathaIDCard.model_validate(created)
        return schemas.SilmathaIDCardManagementResponse(
            status="success",
            message="Silmatha ID card created successfully.",
            data=created_out,
        )

    if action == schemas.CRUDAction.READ_ONE:
        if payload.sic_id is None:
            raise validation_error(
                [("payload.sic_id", "sic_id is required for READ_ONE action")]
            )

        entity = silmatha_id_card_service.get_card(db, payload.sic_id)
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Silmatha ID card not found",
            )

        entity_out = schemas.SilmathaIDCard.model_validate(entity)
        return schemas.SilmathaIDCardManagementResponse(
            status="success",
            message="Silmatha ID card retrieved successfully.",
            data=entity_out,
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

        records = silmatha_id_card_service.list_cards(
            db, skip=skip, limit=limit, search=search
        )
        total = silmatha_id_card_service.count_cards(db, search=search)
        records_out = [
            schemas.SilmathaIDCard.model_validate(item) for item in records
        ]

        return schemas.SilmathaIDCardManagementResponse(
            status="success",
            message="Silmatha ID cards retrieved successfully.",
            data=records_out,
            totalRecords=total,
            page=page,
            limit=limit,
        )

    if action == schemas.CRUDAction.UPDATE:
        if payload.sic_id is None:
            raise validation_error(
                [("payload.sic_id", "sic_id is required for UPDATE action")]
            )
        if not payload.data:
            raise validation_error(
                [("payload.data", "data is required for UPDATE action")]
            )
        try:
            update_payload = schemas.SilmathaIDCardUpdate.model_validate(
                payload.data
            )
        except ValidationError as exc:
            raise validation_error(_format_validation_errors(exc)) from exc

        try:
            updated = silmatha_id_card_service.update_card(
                db,
                sic_id=payload.sic_id,
                payload=update_payload,
                actor_id=user_id,
                left_thumbprint=None,
                applicant_image=None,
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=message
                ) from exc
            raise validation_error([(None, message)]) from exc

        updated_out = schemas.SilmathaIDCard.model_validate(updated)
        return schemas.SilmathaIDCardManagementResponse(
            status="success",
            message="Silmatha ID card updated successfully.",
            data=updated_out,
        )

    if action == schemas.CRUDAction.DELETE:
        if payload.sic_id is None:
            raise validation_error(
                [("payload.sic_id", "sic_id is required for DELETE action")]
            )

        try:
            silmatha_id_card_service.delete_card(
                db, sic_id=payload.sic_id, actor_id=user_id
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=message
                ) from exc
            raise validation_error([(None, message)]) from exc

        return schemas.SilmathaIDCardManagementResponse(
            status="success",
            message="Silmatha ID card deleted successfully.",
            data=None,
        )

    raise validation_error([("action", "Invalid action specified.")])


@router.post("/", response_model=schemas.SilmathaIDCardResponse)
async def create_silmatha_id_card(
    *,
    payload: str = Form(
        ..., description="JSON encoded Silmatha ID card payload (multipart form)."
    ),
    left_thumbprint: UploadFile | None = File(
        default=None, description="Optional left thumbprint image."
    ),
    applicant_image: UploadFile | None = File(
        default=None, description="Optional applicant photo."
    ),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    payload_data = _load_payload(payload)
    try:
        create_payload = schemas.SilmathaIDCardCreate(**payload_data)
    except ValidationError as exc:
        raise validation_error(_format_validation_errors(exc)) from exc

    try:
        created = silmatha_id_card_service.create_card(
            db,
            payload=create_payload,
            actor_id=current_user.ua_user_id,
            left_thumbprint=left_thumbprint,
            applicant_image=applicant_image,
        )
    except ValueError as exc:
        raise validation_error([(None, str(exc))]) from exc

    created_out = schemas.SilmathaIDCard.model_validate(created)
    return schemas.SilmathaIDCardResponse(
        status="success",
        message="Silmatha ID card created successfully.",
        data=created_out,
    )


@router.get("/", response_model=schemas.SilmathaIDCardListResponse)
def list_silmatha_id_cards(
    *,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=200),
    search: str | None = Query(None, max_length=100),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    skip = (page - 1) * limit
    records = silmatha_id_card_service.list_cards(
        db, skip=skip, limit=limit, search=search
    )
    total = silmatha_id_card_service.count_cards(db, search=search)
    records_out = [
        schemas.SilmathaIDCard.model_validate(item) for item in records
    ]
    return schemas.SilmathaIDCardListResponse(
        status="success",
        message="Silmatha ID cards retrieved successfully.",
        data=records_out,
        totalRecords=total,
        page=page,
        limit=limit,
    )


@router.get("/{sic_id}", response_model=schemas.SilmathaIDCardResponse)
def get_silmatha_id_card(
    *,
    sic_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    entity = silmatha_id_card_service.get_card(db, sic_id)
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Silmatha ID card not found",
        )
    entity_out = schemas.SilmathaIDCard.model_validate(entity)
    return schemas.SilmathaIDCardResponse(
        status="success",
        message="Silmatha ID card retrieved successfully.",
        data=entity_out,
    )


@router.put("/{sic_id}", response_model=schemas.SilmathaIDCardResponse)
async def update_silmatha_id_card(
    *,
    sic_id: int,
    payload: str = Form(
        "{}", description="JSON encoded Silmatha ID card payload (multipart form)."
    ),
    left_thumbprint: UploadFile | None = File(
        default=None, description="Optional updated left thumbprint image."
    ),
    applicant_image: UploadFile | None = File(
        default=None, description="Optional updated applicant photo."
    ),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    payload_data = _load_payload(payload)
    try:
        update_payload = schemas.SilmathaIDCardUpdate(**payload_data)
    except ValidationError as exc:
        raise validation_error(_format_validation_errors(exc)) from exc

    try:
        updated = silmatha_id_card_service.update_card(
            db,
            sic_id=sic_id,
            payload=update_payload,
            actor_id=current_user.ua_user_id,
            left_thumbprint=left_thumbprint,
            applicant_image=applicant_image,
        )
    except ValueError as exc:
        message = str(exc)
        if "not found" in message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=message
            ) from exc
        raise validation_error([(None, message)]) from exc

    updated_out = schemas.SilmathaIDCard.model_validate(updated)
    return schemas.SilmathaIDCardResponse(
        status="success",
        message="Silmatha ID card updated successfully.",
        data=updated_out,
    )


@router.delete("/{sic_id}", response_model=schemas.SilmathaIDCardResponse)
def delete_silmatha_id_card(
    *,
    sic_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    try:
        silmatha_id_card_service.delete_card(
            db, sic_id=sic_id, actor_id=current_user.ua_user_id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc

    return schemas.SilmathaIDCardResponse(
        status="success",
        message="Silmatha ID card deleted successfully.",
        data=None,
    )


def _load_payload(raw_payload: str) -> Dict[str, Any]:
    if raw_payload is None:
        return {}
    stripped = raw_payload.strip()
    if stripped == "":
        return {}
    try:
        decoded = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise validation_error(
            [(None, "Invalid JSON payload supplied.")]
        ) from exc
    if decoded is None:
        return {}
    if not isinstance(decoded, dict):
        raise validation_error(
            [(None, "payload must be a JSON object.")],
        )
    return decoded


def _format_validation_errors(exc: ValidationError):
    formatted = []
    for error in exc.errors():
        loc = ".".join(str(part) for part in error.get("loc", []))
        formatted.append((loc or None, error.get("msg", "Invalid data")))
    return formatted
