# app/api/v1/routes/temporary_vihara.py
"""
API routes for Temporary Vihara Management
Provides CRUD operations for temporary vihara records
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission, has_any_permission
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas.temporary_vihara import (
    CRUDAction,
    TemporaryViharaCreate,
    TemporaryViharaManagementRequest,
    TemporaryViharaManagementResponse,
    TemporaryViharaUpdate,
    TemporaryViharaResponse,
    ProvinceResponse,
    DistrictResponse,
)
from app.schemas.vihara import ViharaCreate
from app.services.temporary_vihara_service import temporary_vihara_service
from app.services.vihara_service import vihara_service
from app.repositories.province_repo import province_repo
from app.repositories.district_repo import district_repo
from app.utils.http_exceptions import validation_error

router = APIRouter()


def _convert_temp_vihara_to_response(temp_vihara, db: Session) -> TemporaryViharaResponse:
    """Convert temporary vihara model to response schema with FK resolution"""
    vihara_dict = {k: v for k, v in temp_vihara.__dict__.items() if not k.startswith('_')}
    
    # Resolve province FK
    if temp_vihara.tv_province:
        province = province_repo.get_by_code(db, temp_vihara.tv_province)
        if province:
            vihara_dict["tv_province"] = ProvinceResponse(
                cp_code=province.cp_code,
                cp_name=province.cp_name
            )
    
    # Resolve district FK
    if temp_vihara.tv_district:
        district = district_repo.get_by_code(db, temp_vihara.tv_district)
        if district:
            vihara_dict["tv_district"] = DistrictResponse(
                dd_dcode=district.dd_dcode,
                dd_dname=district.dd_dname
            )
    
    return TemporaryViharaResponse(**vihara_dict)


@router.post(
    "/manage",
    response_model=TemporaryViharaManagementResponse,
    response_model_by_alias=True,
    dependencies=[has_any_permission("vihara:create", "vihara:read", "vihara:update", "vihara:delete")]
)
def manage_temporary_vihara_records(
    request: TemporaryViharaManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Manage temporary vihara records with CRUD operations.
    
    This endpoint handles CREATE, READ_ONE, READ_ALL, UPDATE, and DELETE actions.
    
    **Actions:**
    - **CREATE**: Create a new temporary vihara record
    - **READ_ONE**: Retrieve a single temporary vihara by ID
    - **READ_ALL**: List all temporary vihara records with pagination
    - **UPDATE**: Update an existing temporary vihara record
    - **DELETE**: Delete a temporary vihara record
    
    **Use Case:**
    Used when creating records with incomplete vihara information.
    Stores partial data temporarily until full details are available.
    """
    action = request.action
    payload = request.payload
    user_id = current_user.ua_user_id

    # ==================== CREATE ====================
    if action == CRUDAction.CREATE:
        if not payload.data:
            raise validation_error([("payload.data", "data is required for CREATE action")])

        temp_data = payload.data

        # Validate and look up province/district codes
        province_code = None
        district_code = None
        tv_province = temp_data.tv_province if isinstance(temp_data.tv_province, str) else None
        tv_district = temp_data.tv_district if isinstance(temp_data.tv_district, str) else None

        if tv_province:
            from app.models.province import Province
            province = db.query(Province).filter(
                Province.cp_name.ilike(f"%{tv_province}%"),
                Province.cp_is_deleted.is_(False)
            ).first()
            if province:
                province_code = province.cp_code

        if tv_district:
            from app.models.district import District
            district = db.query(District).filter(
                District.dd_dname.ilike(f"%{tv_district}%"),
                District.dd_is_deleted.is_(False)
            ).first()
            if district:
                district_code = district.dd_dcode

        # Build main-table vihara payload
        mobile = (temp_data.tv_contact_number or "")[:10] or None
        vihara_payload = ViharaCreate(
            vh_trn=None,  # Auto-generated as VH{YEAR}{SEQUENCE}
            vh_vname=temp_data.tv_name,
            vh_addrs=temp_data.tv_address or "N/A",
            vh_mobile=mobile if mobile and len(mobile) == 10 else None,
            vh_province=province_code,
            vh_district=district_code,
            vh_is_temporary_record=True,
            vh_minissecrmrks=(
                f"[TEMP_VIHARA] Created from temporary vihara registration. "
                f"{f'Province (unvalidated): {tv_province}' if tv_province and not province_code else ''}"
                f"{f', District (unvalidated): {tv_district}' if tv_district and not district_code else ''}"
            ).strip(", ") or None,
        )

        try:
            created_vihara = vihara_service.create_vihara(
                db, payload=vihara_payload, actor_id=user_id
            )
            db.refresh(created_vihara)
            return TemporaryViharaManagementResponse(
                status="success",
                message="Vihara record created successfully.",
                data={
                    "vh_trn": created_vihara.vh_trn,
                    "vh_vname": created_vihara.vh_vname,
                    "vh_addrs": created_vihara.vh_addrs,
                    "vh_is_temporary_record": created_vihara.vh_is_temporary_record,
                },
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    # ==================== READ_ONE ====================
    if action == CRUDAction.READ_ONE:
        if payload.tv_id is None:
            raise validation_error([
                ("payload.tv_id", "tv_id is required for READ_ONE action")
            ])

        entity = temporary_vihara_service.get_temporary_vihara(db, payload.tv_id)
        if not entity:
            raise HTTPException(status_code=404, detail="Temporary vihara record not found")

        return TemporaryViharaManagementResponse(
            status="success",
            message="Temporary vihara record retrieved successfully.",
            data=entity,
        )

    # ==================== READ_ALL ====================
    if action == CRUDAction.READ_ALL:
        # Support both page-based and skip-based pagination
        # Default: if page is provided, use it; otherwise use skip
        page = payload.page or 1
        limit = payload.limit
        search = payload.search

        # Calculate skip from page if page is provided, otherwise use skip directly
        skip = payload.skip if payload.page is None else (page - 1) * limit
        skip = skip if skip is not None else 0  # Default to 0 if neither provided
        
        # Ensure skip and limit are within valid ranges
        limit = max(1, min(limit, 200))
        skip = max(0, skip)

        records = temporary_vihara_service.list_temporary_viharas(
            db, skip=skip, limit=limit, search=search
        )
        total = temporary_vihara_service.count_temporary_viharas(db, search=search)
        
        # Convert SQLAlchemy models to response schemas with FK resolution
        records_list = [_convert_temp_vihara_to_response(record, db) for record in records]

        # Calculate page from skip for consistent pagination format
        calculated_page = (skip // limit) + 1 if limit > 0 else 1

        return TemporaryViharaManagementResponse(
            status="success",
            message=f"Retrieved {len(records_list)} temporary vihara records.",
            data={
                "records": [r.model_dump() for r in records_list],
                "total": total,
                # Return both pagination formats for client flexibility
                "page": calculated_page,
                "skip": skip,
                "limit": limit,
            },
        )

    # ==================== UPDATE ====================
    if action == CRUDAction.UPDATE:
        if payload.tv_id is None:
            raise validation_error([
                ("payload.tv_id", "tv_id is required for UPDATE action")
            ])
        if not payload.updates:
            raise validation_error([
                ("payload.updates", "updates is required for UPDATE action")
            ])

        try:
            updated = temporary_vihara_service.update_temporary_vihara(
                db, tv_id=payload.tv_id, payload=payload.updates, actor_id=user_id
            )
            return TemporaryViharaManagementResponse(
                status="success",
                message="Temporary vihara record updated successfully.",
                data=updated,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    # ==================== DELETE ====================
    if action == CRUDAction.DELETE:
        if payload.tv_id is None:
            raise validation_error([
                ("payload.tv_id", "tv_id is required for DELETE action")
            ])

        try:
            temporary_vihara_service.delete_temporary_vihara(db, tv_id=payload.tv_id)
            return TemporaryViharaManagementResponse(
                status="success",
                message="Temporary vihara record deleted successfully.",
                data=None,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    # If we reach here, unsupported action
    raise validation_error([("action", f"Unsupported action: {action}")])
