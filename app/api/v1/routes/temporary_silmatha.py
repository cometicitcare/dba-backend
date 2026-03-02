# app/api/v1/routes/temporary_silmatha.py
"""
API routes for Temporary Silmatha Management
Provides CRUD operations for temporary silmatha records
"""
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission, has_any_permission
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas.temporary_silmatha import (
    CRUDAction,
    TemporarySilmathaCreate,
    TemporarySilmathaManagementRequest,
    TemporarySilmathaManagementResponse,
    TemporarySilmathaUpdate,
    TemporarySilmathaResponse,
    ProvinceResponse,
    DistrictResponse,
)
from app.schemas.silmatha_regist import SilmathaRegistCreate, Silmatha
from app.services.temporary_silmatha_service import temporary_silmatha_service
from app.services.silmatha_regist_service import silmatha_regist_service
from app.repositories.province_repo import province_repo
from app.repositories.district_repo import district_repo
from app.utils.http_exceptions import validation_error

router = APIRouter()


def _convert_temp_silmatha_to_response(temp_silmatha, db: Session) -> TemporarySilmathaResponse:
    """Convert temporary silmatha model to response schema with FK resolution"""
    silmatha_dict = {k: v for k, v in temp_silmatha.__dict__.items() if not k.startswith('_')}
    
    # Resolve province FK
    if temp_silmatha.ts_province:
        province = province_repo.get_by_code(db, temp_silmatha.ts_province)
        if province:
            silmatha_dict["ts_province"] = ProvinceResponse(
                cp_code=province.cp_code,
                cp_name=province.cp_name
            )
    
    # Resolve district FK
    if temp_silmatha.ts_district:
        district = district_repo.get_by_code(db, temp_silmatha.ts_district)
        if district:
            silmatha_dict["ts_district"] = DistrictResponse(
                dd_dcode=district.dd_dcode,
                dd_dname=district.dd_dname
            )
    
    return TemporarySilmathaResponse(**silmatha_dict)


@router.post(
    "/manage",
    response_model=TemporarySilmathaManagementResponse,
    response_model_by_alias=True,
    dependencies=[has_any_permission("silmatha:create", "silmatha:read", "silmatha:update", "silmatha:delete")]
)
def manage_temporary_silmatha_records(
    request: TemporarySilmathaManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Manage temporary silmatha records with CRUD operations.
    
    This endpoint handles CREATE, READ_ONE, READ_ALL, UPDATE, and DELETE actions.
    
    **Actions:**
    - **CREATE**: Create a new temporary silmatha record
    - **READ_ONE**: Retrieve a single temporary silmatha by ID
    - **READ_ALL**: List all temporary silmatha records with pagination
    - **UPDATE**: Update an existing temporary silmatha record
    - **DELETE**: Delete a temporary silmatha record
    
    **Use Case:**
    Used when creating records with incomplete silmatha (nun) information.
    Stores partial data temporarily until full details are available.
    """
    action = request.action
    payload = request.payload
    user_id = current_user.ua_user_id

    # ==================== CREATE ====================
    if action == CRUDAction.CREATE:
        if not payload.data:
            raise validation_error([("payload.data", "data is required for CREATE action")])

        # Map temporary silmatha payload to silmatha_regist payload
        temp_data = payload.data
        
        # Create silmatha_regist payload from temporary silmatha data
        silmatha_payload = SilmathaRegistCreate(
            sil_reqstdate=temp_data.ts_ordained_date or date.today(),
            sil_mahananame=temp_data.ts_name,
            sil_mahanadate=temp_data.ts_ordained_date,
            sil_fathrsaddrs=temp_data.ts_address,
            sil_province=temp_data.ts_province if isinstance(temp_data.ts_province, str) else None,
            sil_district=temp_data.ts_district if isinstance(temp_data.ts_district, str) else None,
            sil_currstat="ST01",  # Default status (Active)
            sil_is_temporary_record=True,  # Flag to identify temporary endpoint records
            # Map arama_name to mahanatemple if it exists
            # Note: ts_arama_name is just a string, not a reference, so we store it in remarks
        )
        
        # Add arama_name to remarks if provided
        if temp_data.ts_arama_name:
            silmatha_payload.sil_remarks = f"Arama: {temp_data.ts_arama_name}"

        try:
            # Use the silmatha_regist service to create (auto-generates SIL number)
            created_silmatha = silmatha_regist_service.create_silmatha(
                db, payload=silmatha_payload, actor_id=user_id, current_user=current_user
            )
            
            # Enrich the response with nested objects (like normal silmatha create)
            silmatha_enriched = silmatha_regist_service.enrich_silmatha_dict(created_silmatha, db)
            silmatha_schema = Silmatha.model_validate(silmatha_enriched)
            
            return TemporarySilmathaManagementResponse(
                status="success",
                message="Silmatha record created successfully.",
                data=silmatha_schema.model_dump(),
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    # ==================== READ_ONE ====================
    if action == CRUDAction.READ_ONE:
        if payload.ts_id is None:
            raise validation_error([
                ("payload.ts_id", "ts_id is required for READ_ONE action")
            ])

        entity = temporary_silmatha_service.get_temporary_silmatha(db, payload.ts_id)
        if not entity:
            raise HTTPException(status_code=404, detail="Temporary silmatha record not found")

        return TemporarySilmathaManagementResponse(
            status="success",
            message="Temporary silmatha record retrieved successfully.",
            data=entity,
        )

    # ==================== READ_ALL ====================
    if action == CRUDAction.READ_ALL:
        skip = payload.skip
        limit = payload.limit
        search = payload.search

        records = temporary_silmatha_service.list_temporary_silmathas(
            db, skip=skip, limit=limit, search=search
        )
        total = temporary_silmatha_service.count_temporary_silmathas(db, search=search)

        # Convert SQLAlchemy models to response schemas with FK resolution
        records_list = [_convert_temp_silmatha_to_response(record, db) for record in records]

        return TemporarySilmathaManagementResponse(
            status="success",
            message=f"Retrieved {len(records_list)} temporary silmatha records.",
            data={
                "records": [r.model_dump() for r in records_list],
                "total": total,
                "skip": skip,
                "limit": limit,
            },
        )

    # ==================== UPDATE ====================
    if action == CRUDAction.UPDATE:
        if payload.ts_id is None:
            raise validation_error([
                ("payload.ts_id", "ts_id is required for UPDATE action")
            ])
        if not payload.updates:
            raise validation_error([
                ("payload.updates", "updates is required for UPDATE action")
            ])

        try:
            updated = temporary_silmatha_service.update_temporary_silmatha(
                db, ts_id=payload.ts_id, payload=payload.updates, actor_id=user_id
            )
            return TemporarySilmathaManagementResponse(
                status="success",
                message="Temporary silmatha record updated successfully.",
                data=updated,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    # ==================== DELETE ====================
    if action == CRUDAction.DELETE:
        if payload.ts_id is None:
            raise validation_error([
                ("payload.ts_id", "ts_id is required for DELETE action")
            ])

        try:
            temporary_silmatha_service.delete_temporary_silmatha(db, ts_id=payload.ts_id)
            return TemporarySilmathaManagementResponse(
                status="success",
                message="Temporary silmatha record deleted successfully.",
                data=None,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    # Should not reach here
    raise validation_error([("action", f"Unsupported action: {action}")])
