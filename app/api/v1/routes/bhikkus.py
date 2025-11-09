# app/api/v1/routes/bhikkus.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.auth_middleware import get_current_user
from app.models.user import UserAccount
from app.schemas import bhikku as schemas
from app.services.bhikku_service import bhikku_service
from app.services.bhikku_workflow_service import bhikku_workflow_service
from app.utils.http_exceptions import validation_error
from app.utils.authorization import ensure_crud_permission
from pydantic import ValidationError

router = APIRouter()

@router.post("/manage", response_model=schemas.BhikkuManagementResponse)
def manage_bhikku_records(
    request: schemas.BhikkuManagementRequest, 
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """
    Unified endpoint for all Bhikku CRUD operations.
    Requires authentication via session ID in Authorization header.
    """
    action = request.action
    payload = request.payload

    # Get user identifier for audit trail
    user_id = current_user.ua_user_id
    ensure_crud_permission(db, user_id, "bhikkus", action)

    if action == schemas.CRUDAction.CREATE:
        if not payload.data:
            raise validation_error(
                [("payload.data", "data is required for CREATE action")]
            )

        create_payload: schemas.BhikkuCreate
        if isinstance(payload.data, schemas.BhikkuCreate):
            create_payload = payload.data
        else:
            raw_data = (
                payload.data.model_dump()
                if hasattr(payload.data, "model_dump")
                else payload.data
            )
            try:
                create_payload = schemas.BhikkuCreate(**raw_data)
            except ValidationError as exc:
                formatted_errors = []
                for error in exc.errors():
                    loc = ".".join(str(part) for part in error.get("loc", []))
                    formatted_errors.append(
                        (loc or None, error.get("msg", "Invalid data"))
                    )
                raise validation_error(formatted_errors) from exc

        try:
            created_bhikku = bhikku_service.create_bhikku(
                db, payload=create_payload, actor_id=user_id
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        workflow = bhikku_workflow_service.build_registration_flow(
            bhikku=created_bhikku
        )

        return {
            "status": "success",
            "message": "Bhikku created successfully.",
            "data": {
                "bhikku": created_bhikku,
                "workflow": workflow,
            },
        }

    elif action == schemas.CRUDAction.READ_ONE:
        if not payload.br_regn:
            raise validation_error(
                [("payload.br_regn", "br_regn is required for READ_ONE action")]
            )
        
        db_bhikku = bhikku_service.get_bhikku(db, br_regn=payload.br_regn)
        if db_bhikku is None:
            raise HTTPException(status_code=404, detail="Bhikku not found")
        return {"status": "success", "message": "Bhikku retrieved successfully.", "data": db_bhikku}

    elif action == schemas.CRUDAction.READ_ALL:
        # Handle pagination - use page-based or skip-based
        page = payload.page if payload.page is not None else 1
        limit = payload.limit
        search_key = payload.search_key.strip() if payload.search_key else None
        
        # If search_key is empty string, treat as None
        if search_key == "":
            search_key = None
        
        # Calculate skip based on page if page is provided, otherwise use skip directly
        skip = payload.skip if payload.page is None else (page - 1) * limit
        skip = max(0, skip)
        
        # Get paginated bhikku records with search
        bhikkus = bhikku_service.list_bhikkus(
            db, skip=skip, limit=limit, search=search_key
        )
        
        # Get total count for pagination
        total_count = bhikku_service.count_bhikkus(db, search=search_key)
        
        return {
            "status": "success",
            "message": "Bhikkus retrieved successfully.",
            "data": bhikkus,
            "totalRecords": total_count,
            "page": page,
            "limit": limit
        }

    elif action == schemas.CRUDAction.UPDATE:
        if not payload.br_regn:
            raise validation_error(
                [("payload.br_regn", "br_regn is required for UPDATE action")]
            )
        if not payload.data:
            raise validation_error(
                [("payload.data", "data is required for UPDATE action")]
            )

        update_payload: schemas.BhikkuUpdate
        if isinstance(payload.data, schemas.BhikkuUpdate):
            update_payload = payload.data
        else:
            raw_data = (
                payload.data.model_dump()
                if hasattr(payload.data, "model_dump")
                else payload.data
            )
            try:
                update_payload = schemas.BhikkuUpdate(**raw_data)
            except ValidationError as exc:
                formatted_errors = []
                for error in exc.errors():
                    loc = ".".join(str(part) for part in error.get("loc", []))
                    formatted_errors.append(
                        (loc or None, error.get("msg", "Invalid data"))
                    )
                raise validation_error(formatted_errors) from exc

        try:
            updated_bhikku = bhikku_service.update_bhikku(
                db, br_regn=payload.br_regn, payload=update_payload, actor_id=user_id
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message) from exc
            raise validation_error([(None, message)]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        return {
            "status": "success",
            "message": "Bhikku updated successfully.",
            "data": updated_bhikku,
        }

    elif action == schemas.CRUDAction.DELETE:
        if not payload.br_regn:
            raise validation_error(
                [("payload.br_regn", "br_regn is required for DELETE action")]
            )
        
        try:
            bhikku_service.delete_bhikku(
                db, br_regn=payload.br_regn, actor_id=user_id
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message) from exc
            raise validation_error([(None, message)]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        return {
            "status": "success",
            "message": "Bhikku deleted successfully.",
            "data": None,
        }

    else:
        raise validation_error([("action", "Invalid action specified")])
