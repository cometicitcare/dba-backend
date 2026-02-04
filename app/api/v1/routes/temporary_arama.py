# app/api/v1/routes/temporary_arama.py
"""  
API routes for Temporary Arama Management
Provides CRUD operations for temporary arama records
"""
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission, has_any_permission
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas.temporary_arama import (
    CRUDAction,
    TemporaryAramaCreate,
    TemporaryAramaManagementRequest,
    TemporaryAramaManagementResponse,
    TemporaryAramaUpdate,
    TemporaryAramaResponse,
    ProvinceResponse,
    DistrictResponse,
)
from app.schemas.arama import AramaCreate, AramaOut
from app.schemas.arama import (
    ProvinceResponse as AramaProvinceResponse,
    DistrictResponse as AramaDistrictResponse,
    DivisionalSecretariatResponse,
    GNDivisionResponse,
    NikayaResponse,
    ParshawaResponse,
    SilmathaResponse,
)
from app.services.temporary_arama_service import temporary_arama_service
from app.services.arama_service import arama_service
from app.repositories.province_repo import province_repo
from app.repositories.district_repo import district_repo
from app.utils.http_exceptions import validation_error

router = APIRouter()


def _convert_arama_to_out(arama) -> AramaOut:
    """Convert AramaData model to AramaOut schema with nested foreign key objects"""
    arama_dict = {
        **{col.name: getattr(arama, col.name) for col in arama.__table__.columns},
        "arama_lands": getattr(arama, 'arama_lands', []),
        "resident_silmathas": getattr(arama, 'resident_silmathas', []),
    }
    
    # Convert foreign key relationships to nested response objects
    if hasattr(arama, 'province_ref') and arama.province_ref:
        arama_dict["ar_province"] = AramaProvinceResponse(
            cp_code=arama.province_ref.cp_code,
            cp_name=arama.province_ref.cp_name
        )
    
    if hasattr(arama, 'district_ref') and arama.district_ref:
        arama_dict["ar_district"] = AramaDistrictResponse(
            dd_dcode=arama.district_ref.dd_dcode,
            dd_dname=arama.district_ref.dd_dname
        )
    
    if hasattr(arama, 'divisional_secretariat_ref') and arama.divisional_secretariat_ref:
        arama_dict["ar_divisional_secretariat"] = DivisionalSecretariatResponse(
            dv_dvcode=arama.divisional_secretariat_ref.dv_dvcode,
            dv_dvname=arama.divisional_secretariat_ref.dv_dvname
        )
    
    if hasattr(arama, 'gn_division_ref') and arama.gn_division_ref:
        arama_dict["ar_gndiv"] = GNDivisionResponse(
            gn_gnc=arama.gn_division_ref.gn_gnc,
            gn_gnname=arama.gn_division_ref.gn_gnname
        )
    
    if hasattr(arama, 'nikaya_ref') and arama.nikaya_ref:
        arama_dict["ar_nikaya"] = NikayaResponse(
            nk_nkn=arama.nikaya_ref.nk_nkn,
            nk_nname=arama.nikaya_ref.nk_nname
        )
    
    if hasattr(arama, 'parshawa_ref') and arama.parshawa_ref:
        arama_dict["ar_parshawa"] = ParshawaResponse(
            pr_prn=arama.parshawa_ref.pr_prn,
            pr_pname=arama.parshawa_ref.pr_pname
        )
    
    if hasattr(arama, 'owner_silmatha_ref') and arama.owner_silmatha_ref:
        arama_dict["ar_ownercd"] = SilmathaResponse(
            sil_regn=arama.owner_silmatha_ref.sil_regn,
            sil_gihiname=arama.owner_silmatha_ref.sil_gihiname,
            sil_mahananame=arama.owner_silmatha_ref.sil_mahananame
        )
    
    if hasattr(arama, 'viharadhipathi_ref') and arama.viharadhipathi_ref:
        arama_dict["ar_viharadhipathi_name"] = SilmathaResponse(
            sil_regn=arama.viharadhipathi_ref.sil_regn,
            sil_gihiname=arama.viharadhipathi_ref.sil_gihiname,
            sil_mahananame=arama.viharadhipathi_ref.sil_mahananame
        )
    
    return AramaOut.model_validate(arama_dict)


def _convert_temp_arama_to_response(temp_arama, db: Session) -> TemporaryAramaResponse:
    """Convert temporary arama model to response schema with FK resolution"""
    arama_dict = {k: v for k, v in temp_arama.__dict__.items() if not k.startswith('_')}
    
    # Resolve province FK
    if temp_arama.ta_province:
        province = province_repo.get_by_code(db, temp_arama.ta_province)
        if province:
            arama_dict["ta_province"] = ProvinceResponse(
                cp_code=province.cp_code,
                cp_name=province.cp_name
            )
    
    # Resolve district FK
    if temp_arama.ta_district:
        district = district_repo.get_by_code(db, temp_arama.ta_district)
        if district:
            arama_dict["ta_district"] = DistrictResponse(
                dd_dcode=district.dd_dcode,
                dd_dname=district.dd_dname
            )
    
    return TemporaryAramaResponse(**arama_dict)


@router.post(
    "/manage",
    response_model=TemporaryAramaManagementResponse,
    response_model_by_alias=True,
    dependencies=[has_any_permission("arama:create", "arama:read", "arama:update", "arama:delete")]
)
def manage_temporary_arama_records(
    request: TemporaryAramaManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Manage temporary arama records with CRUD operations.
    
    This endpoint handles CREATE, READ_ONE, READ_ALL, UPDATE, and DELETE actions.
    
    **Actions:**
    - **CREATE**: Create a new temporary arama record
    - **READ_ONE**: Retrieve a single temporary arama by ID
    - **READ_ALL**: List all temporary arama records with pagination
    - **UPDATE**: Update an existing temporary arama record
    - **DELETE**: Delete a temporary arama record
    
    **Use Case:**
    Used when creating records with incomplete arama information.
    Stores partial data temporarily until full details are available.
    """
    action = request.action
    payload = request.payload
    user_id = current_user.ua_user_id

    # ==================== CREATE ====================
    if action == CRUDAction.CREATE:
        if not payload.data:
            raise validation_error([("payload.data", "data is required for CREATE action")])

        # Map temporary arama payload to aramadata payload
        temp_data = payload.data
        
        # Create aramadata payload from temporary arama data
        # Need to provide required fields for arama
        arama_payload = AramaCreate(
            ar_vname=temp_data.ta_name,
            ar_addrs=temp_data.ta_address or "",
            ar_mobile=temp_data.ta_contact_number or "0000000000",  # Default if not provided
            ar_whtapp=temp_data.ta_contact_number or "0000000000",  # Same as mobile
            ar_email=None,  # Email is optional - set to None for temporary records
            ar_province=temp_data.ta_province if isinstance(temp_data.ta_province, str) else None,
            ar_district=temp_data.ta_district if isinstance(temp_data.ta_district, str) else None,
            ar_typ="01",  # Default arama type
            ar_gndiv="0000000000",  # Default GN division (will need to be updated later)
            ar_ownercd="SIL00000000",  # Default owner code (12 chars max - will need to be updated later)
            ar_parshawa="0000000000",  # Default parshawa (will need to be updated later)
            ar_is_temporary_record=True,  # Flag to identify temporary endpoint records
        )
        
        # Add aramadhipathi info to remarks if provided
        if temp_data.ta_aramadhipathi_name:
            arama_payload.ar_minissecrmrks = f"Aramadhipathi: {temp_data.ta_aramadhipathi_name}"

        try:
            # Use the arama service to create (auto-generates AR number)
            created_arama = arama_service.create_arama(
                db, payload=arama_payload, actor_id=user_id
            )
            
            # Refresh to load relationships
            db.refresh(created_arama)
            
            # Convert to AramaOut with nested foreign key objects
            created_out = _convert_arama_to_out(created_arama)
            
            return TemporaryAramaManagementResponse(
                status="success",
                message="Arama record created successfully.",
                data=created_out.model_dump(),
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    # ==================== READ_ONE ====================
    if action == CRUDAction.READ_ONE:
        if payload.ta_id is None:
            raise validation_error([
                ("payload.ta_id", "ta_id is required for READ_ONE action")
            ])

        entity = temporary_arama_service.get_temporary_arama(db, payload.ta_id)
        if not entity:
            raise HTTPException(status_code=404, detail="Temporary arama record not found")

        return TemporaryAramaManagementResponse(
            status="success",
            message="Temporary arama record retrieved successfully.",
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

        records = temporary_arama_service.list_temporary_aramas(
            db, skip=skip, limit=limit, search=search
        )
        total = temporary_arama_service.count_temporary_aramas(db, search=search)

        # Convert SQLAlchemy models to response schemas with FK resolution
        records_list = [_convert_temp_arama_to_response(record, db) for record in records]

        # Calculate page from skip for consistent pagination format
        calculated_page = (skip // limit) + 1 if limit > 0 else 1

        return TemporaryAramaManagementResponse(
            status="success",
            message=f"Retrieved {len(records_list)} temporary arama records.",
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
        if payload.ta_id is None:
            raise validation_error([
                ("payload.ta_id", "ta_id is required for UPDATE action")
            ])
        if not payload.updates:
            raise validation_error([
                ("payload.updates", "updates is required for UPDATE action")
            ])

        try:
            updated = temporary_arama_service.update_temporary_arama(
                db, ta_id=payload.ta_id, payload=payload.updates, actor_id=user_id
            )
            return TemporaryAramaManagementResponse(
                status="success",
                message="Temporary arama record updated successfully.",
                data=updated,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    # ==================== DELETE ====================
    if action == CRUDAction.DELETE:
        if payload.ta_id is None:
            raise validation_error([
                ("payload.ta_id", "ta_id is required for DELETE action")
            ])

        try:
            temporary_arama_service.delete_temporary_arama(db, ta_id=payload.ta_id)
            return TemporaryAramaManagementResponse(
                status="success",
                message="Temporary arama record deleted successfully.",
                data=None,
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc

    # Should not reach here
    raise validation_error([("action", f"Unsupported action: {action}")])
