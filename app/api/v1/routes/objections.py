from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.orm import Session
from typing import List

from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission, has_any_permission
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas.objection import (
    ObjectionAction,
    ObjectionCreate,
    ObjectionManagementRequest,
    ObjectionManagementResponse,
    ObjectionOut,
    ObjectionCheckResponse,
)
from app.services.objection_service import objection_service
from app.utils.http_exceptions import validation_error

router = APIRouter()


@router.post(
    "/manage",
    response_model=ObjectionManagementResponse,
    dependencies=[has_any_permission("objection:create", "objection:update", "objection:delete")],
)
def manage_objections(
    request: ObjectionManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Manage objections for vihara, arama, or devala resident restrictions.
    
    Supports actions:
    - CREATE: Submit new objection (status: PENDING)
    - READ_ONE: Get specific objection by ID
    - READ_ALL: List objections with filters
    - APPROVE: Approve pending objection (restricts resident additions)
    - REJECT: Reject pending objection (requires reason)
    - CANCEL: Cancel pending/approved objection (removes restriction)
    """
    action = request.action
    payload = request.payload
    user_id = current_user.ua_username

    # CREATE - Submit new objection
    if action == ObjectionAction.CREATE:
        if not payload.data:
            raise validation_error(
                [("payload.data", "data is required for CREATE action")]
            )

        create_data: ObjectionCreate
        if isinstance(payload.data, ObjectionCreate):
            create_data = payload.data
        else:
            try:
                create_data = ObjectionCreate(**payload.data.model_dump())
            except ValidationError as exc:
                formatted_errors = []
                for error in exc.errors():
                    loc = ".".join(str(part) for part in error.get("loc", []))
                    formatted_errors.append(
                        (loc or None, error.get("msg", "Invalid data"))
                    )
                raise validation_error(formatted_errors) from exc

        try:
            objection = objection_service.create_objection(
                db, data=create_data, submitted_by=user_id
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc
        except HTTPException:
            raise

        objection_out = ObjectionOut.model_validate(objection)
        return ObjectionManagementResponse(
            status="success",
            message="Objection submitted successfully. Status: PENDING",
            data=objection_out,
        )

    # READ_ONE - Get specific objection
    elif action == ObjectionAction.READ_ONE:
        if not payload.obj_id:
            raise validation_error(
                [("payload.obj_id", "obj_id is required for READ_ONE action")]
            )

        try:
            objection = objection_service.get_objection(db, payload.obj_id)
        except HTTPException:
            raise

        objection_out = ObjectionOut.model_validate(objection)
        return ObjectionManagementResponse(
            status="success",
            message="Objection retrieved successfully.",
            data=objection_out,
        )

    # READ_ALL - List objections with filters
    elif action == ObjectionAction.READ_ALL:
        page = payload.page or 1
        limit = payload.limit or 10
        skip = (page - 1) * limit

        objections, total = objection_service.list_objections(
            db,
            skip=skip,
            limit=limit,
            vh_trn=payload.vh_trn,
            ar_trn=payload.ar_trn,
            dv_trn=payload.dv_trn,
            bh_regn=payload.bh_regn,
            sil_regn=payload.sil_regn,
            dbh_regn=payload.dbh_regn,
            status=payload.obj_status,
        )

        objections_out = [ObjectionOut.model_validate(obj) for obj in objections]
        return ObjectionManagementResponse(
            status="success",
            message=f"Retrieved {len(objections_out)} objections.",
            data=objections_out,
            totalRecords=total,
            page=page,
            limit=limit,
        )

    # APPROVE - Approve pending objection
    elif action == ObjectionAction.APPROVE:
        if not payload.obj_id:
            raise validation_error(
                [("payload.obj_id", "obj_id is required for APPROVE action")]
            )

        try:
            objection = objection_service.approve_objection(
                db, obj_id=payload.obj_id, approved_by=user_id
            )
        except HTTPException:
            raise

        objection_out = ObjectionOut.model_validate(objection)
        return ObjectionManagementResponse(
            status="success",
            message="Objection approved. Resident additions are now restricted for this entity.",
            data=objection_out,
        )

    # REJECT - Reject pending objection
    elif action == ObjectionAction.REJECT:
        if not payload.obj_id:
            raise validation_error(
                [("payload.obj_id", "obj_id is required for REJECT action")]
            )
        
        if not payload.rejection_reason or not payload.rejection_reason.strip():
            raise validation_error(
                [("payload.rejection_reason", "rejection_reason is required for REJECT action")]
            )

        try:
            objection = objection_service.reject_objection(
                db,
                obj_id=payload.obj_id,
                rejection_reason=payload.rejection_reason,
                rejected_by=user_id,
            )
        except HTTPException:
            raise

        objection_out = ObjectionOut.model_validate(objection)
        return ObjectionManagementResponse(
            status="success",
            message="Objection rejected.",
            data=objection_out,
        )

    # CANCEL - Cancel objection
    elif action == ObjectionAction.CANCEL:
        if not payload.obj_id:
            raise validation_error(
                [("payload.obj_id", "obj_id is required for CANCEL action")]
            )

        try:
            objection = objection_service.cancel_objection(
                db,
                obj_id=payload.obj_id,
                cancellation_reason=payload.cancellation_reason,
                cancelled_by=user_id,
            )
        except HTTPException:
            raise

        objection_out = ObjectionOut.model_validate(objection)
        return ObjectionManagementResponse(
            status="success",
            message="Objection cancelled. Resident additions are now allowed for this entity.",
            data=objection_out,
        )

    else:
        raise validation_error([("action", "Invalid action specified")])


@router.get(
    "/check/{trn}",
    response_model=ObjectionCheckResponse,
)
def check_objection_by_trn(
    trn: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Check if a vihara, arama, or devala has an active objection by TRN.
    
    Entity type is determined from TRN prefix:
    - TRN* = Vihara
    - ARN* = Arama
    - DVL* = Devala
    
    Returns information about whether resident additions are restricted.
    """
    has_active, objection = objection_service.check_active_objection_by_trn(
        db, trn=trn
    )
    
    # Determine entity type from TRN prefix
    trn_upper = trn.upper().strip()
    if trn_upper.startswith("TRN"):
        entity_type = "VIHARA"
    elif trn_upper.startswith("ARN"):
        entity_type = "ARAMA"
    elif trn_upper.startswith("DVL"):
        entity_type = "DEVALA"
    else:
        entity_type = "entity"

    if has_active and objection:
        return ObjectionCheckResponse(
            has_active_objection=True,
            objection=ObjectionOut.model_validate(objection),
            message=f"Active objection exists. Cannot add resident bhikkus/silmathas to this {entity_type}.",
        )
    else:
        return ObjectionCheckResponse(
            has_active_objection=False,
            objection=None,
            message=f"No active objection. Can add resident bhikkus/silmathas to this {entity_type}.",
        )
