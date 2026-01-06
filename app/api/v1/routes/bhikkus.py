# app/api/v1/routes/bhikkus.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.api.deps import get_db
from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission, has_any_permission, get_user_permissions
from app.models.user import UserAccount
from app.schemas import bhikku as schemas
from app.schemas.vihara import BhikkuViharaListResponse, BhikkuViharaManagementRequest
from app.services.bhikku_service import bhikku_service
from app.services.vihara_service import vihara_service
from app.services.temporary_bhikku_service import temporary_bhikku_service
from app.services.temporary_vihara_service import temporary_vihara_service
from app.utils.http_exceptions import validation_error
from pydantic import ValidationError

router = APIRouter()


def check_bhikku_permission(db: Session, user: UserAccount, required_permission: str):
    """Check if user has the required permission for bhikku operations"""
    user_permissions = get_user_permissions(db, user)
    if required_permission not in user_permissions:
        raise HTTPException(
            status_code=403,
            detail=f"Permission denied. Required permission: {required_permission}"
        )


@router.get(
    "/mahanayaka-list",
    response_model=schemas.BhikkuMahanayakaListResponse,
    dependencies=[has_permission("bhikku:read")],
)
def list_mahanayaka_bhikkus(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Return rows from the `bikkudtls_mahanayakalist` database view.
    Requires: bhikku:read permission
    """
    records = bhikku_service.list_mahanayaka_view(db)
    return {
        "status": "success",
        "message": "Mahanayaka bhikku list retrieved successfully.",
        "data": records,
    }


@router.get(
    "/nikaya-list",
    response_model=schemas.BhikkuNikayaListResponse,
    dependencies=[has_permission("bhikku:read")],
)
def list_nikaya_bhikkus(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Return rows from the `bikkudtls_nikaya_list` database view.
    Requires: bhikku:read permission
    """
    records = bhikku_service.list_nikaya_view(db)
    return {
        "status": "success",
        "message": "Nikaya bhikku list retrieved successfully.",
        "data": records,
    }


@router.get(
    "/nikaya-hierarchy",
    response_model=schemas.BhikkuNikayaHierarchyResponse,
    dependencies=[has_permission("bhikku:read")],
)
def list_nikaya_hierarchy(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Return nikaya records with their main bhikku and related parshawayas.
    """
    records = bhikku_service.list_nikaya_hierarchy(db)
    return {
        "status": "success",
        "message": "Nikaya hierarchy retrieved successfully.",
        "data": records,
    }


@router.get(
    "/acharya-list",
    response_model=schemas.BhikkuAcharyaListResponse,
    dependencies=[has_permission("bhikku:read")],
)
def list_acharya_bhikkus(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Return rows from the `bikkudtls_archarya_dtls` database view.
    """
    records = bhikku_service.list_acharya_view(db)
    return {
        "status": "success",
        "message": "Acharya bhikku list retrieved successfully.",
        "data": records,
    }


@router.get(
    "/details-list",
    response_model=schemas.BhikkuDetailsListResponse,
    dependencies=[has_permission("bhikku:read")],
)
def list_bhikku_details(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Return rows from the `bikkudtls_bikkullist` database view.
    """
    records = bhikku_service.list_bhikku_details_view(db)
    return {
        "status": "success",
        "message": "Bhikku details list retrieved successfully.",
        "data": records,
    }


@router.get(
    "/certification-list",
    response_model=schemas.BhikkuCertificationListResponse,
    dependencies=[has_permission("bhikku:read")],
)
def list_certification_bhikkus(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Return rows from the `bikkudtls_certification_data` database view.
    """
    records = bhikku_service.list_certification_view(db)
    return {
        "status": "success",
        "message": "Certification bhikku list retrieved successfully.",
        "data": records,
    }


@router.get(
    "/certification-printnow",
    response_model=schemas.BhikkuCertificationPrintListResponse,
    dependencies=[has_permission("bhikku:read")],
)
def list_certification_print_bhikkus(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Return rows from the `bikkudtls_certification_printnow` database view.
    """
    records = bhikku_service.list_certification_print_view(db)
    return {
        "status": "success",
        "message": "Certification print list retrieved successfully.",
        "data": records,
    }


@router.get(
    "/current-status-list",
    response_model=schemas.BhikkuCurrentStatusListResponse,
    dependencies=[has_permission("bhikku:read")],
)
def list_current_status_bhikkus(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Return rows from the `bikkudtls_currstatus_list` database view.
    """
    records = bhikku_service.list_current_status_view(db)
    return {
        "status": "success",
        "message": "Current status list retrieved successfully.",
        "data": records,
    }


@router.get(
    "/by-vihara",
    response_model=schemas.BhikkuByViharaResponse,
    dependencies=[has_permission("bhikku:read")],
)
def list_bhikkus_by_vihara(
    vh_trn: str = Query(..., min_length=1, description="Vihara code (vh_trn)"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    List bhikkus residing at a given vihara (livtemple).
    Returns registration number and br_mahananame only.
    """
    records = bhikku_service.list_bhikkus_by_vihara(db, vh_trn=vh_trn)
    return {
        "status": "success",
        "message": "Bhikkus for vihara retrieved successfully.",
        "data": records,
    }


@router.post(
    "/by-vihara",
    response_model=schemas.BhikkuByViharaResponse,
    dependencies=[has_permission("bhikku:read")],
)
def list_bhikkus_by_vihara_body(
    request: schemas.BhikkuByViharaRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Same as GET /by-vihara but accepts JSON payload:
    { "action": "READ_ONE", "vh_trn": "<vihara-code>" }
    """
    if request.action != "READ_ONE":
        raise HTTPException(status_code=400, detail="Invalid action. Use READ_ONE.")

    vh_trn = (request.vh_trn or "").strip()
    if not vh_trn:
        raise HTTPException(status_code=400, detail="vh_trn is required.")

    records = bhikku_service.list_bhikkus_by_vihara(db, vh_trn=vh_trn)
    return {
        "status": "success",
        "message": "Bhikkus for vihara retrieved successfully.",
        "data": records,
    }


@router.get(
    "/district-list",
    response_model=schemas.BhikkuDistrictListResponse,
    dependencies=[has_permission("bhikku:read")],
)
def list_district_bhikkus(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Return rows from the `bikkudtls_districtlist` database view.
    """
    records = bhikku_service.list_district_view(db)
    return {
        "status": "success",
        "message": "District list retrieved successfully.",
        "data": records,
    }


@router.get(
    "/province-list",
    response_model=schemas.BhikkuProvinceListResponse,
    dependencies=[has_permission("bhikku:read")],
)
def list_province_bhikkus(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Return rows from the `cmm_province` table.
    """
    records = bhikku_service.list_province_view(db)
    return {
        "status": "success",
        "message": "Province list retrieved successfully.",
        "data": records,
    }


@router.get(
    "/division-secretariat-list",
    response_model=schemas.BhikkuDivisionSecListResponse,
    dependencies=[has_permission("bhikku:read")],
)
def list_division_secretariat_bhikkus(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Return rows from the `bikkudtls_divisionsec_dtls` database view.
    """
    records = bhikku_service.list_division_sec_view(db)
    return {
        "status": "success",
        "message": "Division secretariat list retrieved successfully.",
        "data": records,
    }


@router.get(
    "/gn-division-list",
    response_model=schemas.BhikkuGNListResponse,
    dependencies=[has_permission("bhikku:read")],
)
def list_gn_division_bhikkus(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Return rows from the `bikkudtls_gn_dtls` database view.
    """
    records = bhikku_service.list_gn_view(db)
    return {
        "status": "success",
        "message": "GN division list retrieved successfully.",
        "data": records,
    }


@router.get(
    "/history-status-list",
    response_model=schemas.BhikkuHistoryStatusListResponse,
    dependencies=[has_permission("bhikku:read")],
)
def list_history_status_bhikkus(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Return rows from the `bikkudtls_histtystatus_list` database view.
    """
    records = bhikku_service.list_history_status_view(db)
    return {
        "status": "success",
        "message": "History status list retrieved successfully.",
        "data": records,
    }


@router.get(
    "/id-all-list",
    response_model=schemas.BhikkuIDAllListResponse,
    dependencies=[has_permission("bhikku:read")],
)
def list_id_all_bhikkus(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Return rows from the `bikkudtls_id_alllist` database view.
    """
    records = bhikku_service.list_id_all_view(db)
    return {
        "status": "success",
        "message": "ID all list retrieved successfully.",
        "data": records,
    }


@router.get(
    "/id-district-list",
    response_model=schemas.BhikkuIDDistrictListResponse,
    dependencies=[has_permission("bhikku:read")],
)
def list_id_district_bhikkus(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Return rows from the `bikkudtls_iddistrict_list` database view.
    """
    records = bhikku_service.list_id_district_view(db)
    return {
        "status": "success",
        "message": "ID district list retrieved successfully.",
        "data": records,
    }


@router.get(
    "/id-division-secretariat-list",
    response_model=schemas.BhikkuIDDvSecListResponse,
    dependencies=[has_permission("bhikku:read")],
)
def list_id_division_secretariat_bhikkus(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Return rows from the `bikkudtls_iddvsec_list` database view.
    """
    records = bhikku_service.list_id_division_sec_view(db)
    return {
        "status": "success",
        "message": "ID division secretariat list retrieved successfully.",
        "data": records,
    }


@router.get(
    "/id-gn-division-list",
    response_model=schemas.BhikkuIDGNListResponse,
    dependencies=[has_permission("bhikku:read")],
)
def list_id_gn_division_bhikkus(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Return rows from the `bikkudtls_idgn_list` database view.
    """
    records = bhikku_service.list_id_gn_view(db)
    return {
        "status": "success",
        "message": "ID GN division list retrieved successfully.",
        "data": records,
    }


@router.get(
    "/nikayanayaka-list",
    response_model=schemas.BhikkuNikayanayakaListResponse,
    dependencies=[has_permission("bhikku:read")],
)
def list_nikayanayaka_bhikkus(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Return rows from the `bikkudtls_nikayanayaka_list` database view.
    """
    records = bhikku_service.list_nikayanayaka_view(db)
    return {
        "status": "success",
        "message": "Nikayanayaka list retrieved successfully.",
        "data": records,
    }


@router.get(
    "/parshawa-list",
    response_model=schemas.BhikkuParshawaListResponse,
    dependencies=[has_permission("bhikku:read")],
)
def list_parshawa_bhikkus(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Return rows from the `bikkudtls_parshawa_list` database view.
    """
    records = bhikku_service.list_parshawa_view(db)
    return {
        "status": "success",
        "message": "Parshawa list retrieved successfully.",
        "data": records,
    }


@router.get(
    "/status-history-composite",
    response_model=schemas.BhikkuStatusHistoryCompositeResponse,
    dependencies=[has_permission("bhikku:read")],
)
def list_status_history_composite(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Return rows from the `bikkudtls_statushystry_composit` database view.
    """
    records = bhikku_service.list_status_history_composite(db)
    return {
        "status": "success",
        "message": "Status history composite retrieved successfully.",
        "data": records,
    }


@router.get(
    "/status-history-list",
    response_model=schemas.BhikkuStatusHistoryListResponse,
    dependencies=[has_permission("bhikku:read")],
)
def list_status_history(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Return rows from the `bikkudtls_statushystry_list` database view.
    """
    records = bhikku_service.list_status_history_list(db)
    return {
        "status": "success",
        "message": "Status history list retrieved successfully.",
        "data": records,
    }


@router.get(
    "/status-history-list2",
    response_model=schemas.BhikkuStatusHistoryList2Response,
    dependencies=[has_permission("bhikku:read")],
)
def list_status_history_aggregated(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Return rows from the `bikkudtls_statushystry_list2` database view.
    """
    records = bhikku_service.list_status_history_list2(db)
    return {
        "status": "success",
        "message": "Status history list 2 retrieved successfully.",
        "data": records,
    }


@router.get(
    "/viharadipathi-list",
    response_model=schemas.BhikkuViharadipathiListResponse,
    dependencies=[has_permission("bhikku:read")],
)
def list_viharadipathi_bhikkus(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Return rows from the `bikkudtls_viharadipathi_list` database view.
    """
    records = bhikku_service.list_viharadipathi_view(db)
    return {
        "status": "success",
        "message": "Viharadipathi list retrieved successfully.",
        "data": records,
    }


@router.post(
    "/vihara-list",
    response_model=BhikkuViharaListResponse,
    dependencies=[has_permission("bhikku:read")],
)
def get_vihara_for_bhikkus(
    request: BhikkuViharaManagementRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Get vihara information for bhikku users with support for READ_ONE and READ_ALL actions.
    This endpoint provides vihara details for use in bhikku forms and workflows.
    
    Accepts POST request with action and payload structure:
    
    READ_ONE:
    {
      "action": "READ_ONE",
      "payload": {
        "vh_id": 41
      }
    }
    
    READ_ALL:
    {
      "action": "READ_ALL",
      "payload": {
        "skip": 0,
        "limit": 10,
        "page": 1,
        "search_key": "w"
      }
    }
    """
    # Validate action
    if request.action not in ["READ_ONE", "READ_ALL"]:
        raise HTTPException(
            status_code=400,
            detail="Only READ_ONE and READ_ALL actions are supported for this endpoint"
        )
    
    if request.action == "READ_ONE":
        # Get the vihara by ID
        vihara = vihara_service.get_vihara(db, request.payload.vh_id)
        
        if not vihara:
            raise HTTPException(
                status_code=404,
                detail=f"Vihara with ID {request.payload.vh_id} not found"
            )
        
        # Convert to the expected response format
        vihara_item = {
            "vh_trn": vihara.vh_trn,
            "vh_vname": vihara.vh_vname,
            "vh_addrs": vihara.vh_addrs,
        }
        
        return {
            "status": "success",
            "message": "Vihara retrieved successfully.",
            "data": [vihara_item],
            "totalRecords": 1,
            "page": 1,
            "limit": 1,
        }
    
    else:  # READ_ALL
        # Calculate skip from page and limit
        skip = getattr(request.payload, 'skip', 0)
        limit = getattr(request.payload, 'limit', 10)
        page = getattr(request.payload, 'page', 1)
        search_key = getattr(request.payload, 'search_key', None)
        
        # If page is provided, calculate skip from it
        if page and page > 1:
            skip = (page - 1) * limit
        
        # Get viharas with search filter
        viharas = vihara_service.list_viharas(
            db,
            skip=skip,
            limit=limit,
            search=search_key
        )
        
        # Get total count
        total_count = vihara_service.count_viharas(
            db,
            search=search_key
        )
        
        # Convert to the expected response format
        vihara_items = [
            {
                "vh_trn": vihara.vh_trn,
                "vh_vname": vihara.vh_vname,
                "vh_addrs": vihara.vh_addrs,
            }
            for vihara in viharas
        ]
        
        # Also fetch temporary viharas and include them in results
        temp_viharas = temporary_vihara_service.list_temporary_viharas(
            db,
            skip=0,
            limit=200,
            search=search_key
        )
        
        # Add temporary viharas to the list
        for temp_vihara in temp_viharas:
            temp_vihara_item = {
                "vh_trn": f"TEMP-{temp_vihara.tv_id}",
                "vh_vname": temp_vihara.tv_name,
                "vh_addrs": temp_vihara.tv_address,
            }
            vihara_items.append(temp_vihara_item)
        
        # Update total count to include temporary viharas
        temp_count = temporary_vihara_service.count_temporary_viharas(db, search=search_key)
        total_with_temp = total_count + temp_count
        
        # Determine the page number
        response_page = page if page else (skip // limit) + 1
        
        return {
            "status": "success",
            "message": "Viharas retrieved successfully.",
            "data": vihara_items,
            "totalRecords": total_with_temp,
            "page": response_page,
            "limit": limit,
        }


@router.get(
    "/current-status-summary",
    response_model=schemas.BhikkuCurrentStatusSummaryResponse,
    dependencies=[has_permission("bhikku:read")],
)
def list_current_status_summary(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Return aggregated rows from the `bikkusumm_currstatus_list` database view.
    """
    records = bhikku_service.list_current_status_summary(db)
    return {
        "status": "success",
        "message": "Current status summary retrieved successfully.",
        "data": records,
    }


@router.get(
    "/district-summary",
    response_model=schemas.BhikkuDistrictSummaryResponse,
    dependencies=[has_permission("bhikku:read")],
)
def list_district_summary(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Return aggregated rows from the `bikkusumm_district_list` database view.
    """
    records = bhikku_service.list_district_summary(db)
    return {
        "status": "success",
        "message": "District summary retrieved successfully.",
        "data": records,
    }


@router.get(
    "/gn-summary",
    response_model=schemas.BhikkuGNSummaryResponse,
    dependencies=[has_permission("bhikku:read")],
)
def list_gn_summary(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Return aggregated rows from the `bikkusumm_gn_list` database view.
    """
    records = bhikku_service.list_gn_summary(db)
    return {
        "status": "success",
        "message": "GN summary retrieved successfully.",
        "data": records,
    }


@router.get(
    "/id-district-summary",
    response_model=schemas.BhikkuIDDistrictSummaryResponse,
    dependencies=[has_permission("bhikku:read")],
)
def list_id_district_summary(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Return aggregated rows from the `bikkusumm_iddistrict_list` database view.
    """
    records = bhikku_service.list_id_district_summary(db)
    return {
        "status": "success",
        "message": "ID district summary retrieved successfully.",
        "data": records,
    }


@router.get(
    "/id-gn-summary",
    response_model=schemas.BhikkuIDGNSummaryResponse,
    dependencies=[has_permission("bhikku:read")],
)
def list_id_gn_summary(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Return aggregated rows from the `bikkusumm_idgn_list` database view.
    """
    records = bhikku_service.list_id_gn_summary(db)
    return {
        "status": "success",
        "message": "ID GN summary retrieved successfully.",
        "data": records,
    }


@router.post(
    "/manage",
    response_model=schemas.BhikkuManagementResponse,
    dependencies=[has_any_permission("bhikku:create", "bhikku:read", "bhikku:update", "bhikku:delete")],
)
def manage_bhikku_records(
    request: schemas.BhikkuManagementRequest, 
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Unified endpoint for all Bhikku CRUD operations.
    Requires authentication + at least one of: bhikku:create, bhikku:update, bhikku:delete
    
    Note: Permission check is relaxed to allow any CRUD permission.
    For stricter enforcement, implement action-specific checks within the function.
    """
    action = request.action
    payload = request.payload

    # Get user identifier for audit trail
    user_id = current_user.ua_user_id

    if action == schemas.CRUDAction.CREATE:
        # Check CREATE permission
        check_bhikku_permission(db, current_user, "bhikku:create")
        
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
                db, payload=create_payload, actor_id=user_id, current_user=current_user
            )
        except ValueError as exc:
            raise validation_error([(None, str(exc))]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        # Convert SQLAlchemy model to Pydantic schema with enriched data
        enriched_data = bhikku_service.enrich_bhikku_dict(created_bhikku, db=db)
        bhikku_schema = schemas.Bhikku(**enriched_data)
        
        return schemas.BhikkuManagementResponse(
            status="success",
            message="Bhikku created successfully.",
            data=bhikku_schema,
        )

    elif action == schemas.CRUDAction.READ_ONE:
        if not payload.br_regn:
            raise validation_error(
                [("payload.br_regn", "br_regn is required for READ_ONE action")]
            )
        
        db_bhikku = bhikku_service.get_bhikku(db, br_regn=payload.br_regn)
        if db_bhikku is None:
            raise HTTPException(status_code=404, detail="Bhikku not found")
        
        # Enrich with resolved names (names replace codes)
        enriched_data = bhikku_service.enrich_bhikku_dict(db_bhikku, db=db)
        bhikku_schema = schemas.Bhikku(**enriched_data)
        return schemas.BhikkuManagementResponse(
            status="success",
            message="Bhikku retrieved successfully.",
            data=bhikku_schema,
        )

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
        
        # Get paginated bhikku records with search and filters
        bhikkus = bhikku_service.list_bhikkus(
            db, 
            skip=skip, 
            limit=limit, 
            search=search_key,
            province=payload.province,
            vh_trn=payload.vh_trn,
            district=payload.district,
            current_user=current_user,
            divisional_secretariat=payload.divisional_secretariat,
            gn_division=payload.gn_division,
            temple=payload.temple,
            child_temple=payload.child_temple,
            nikaya=payload.nikaya,
            parshawaya=payload.parshawaya,
            category=payload.category,
            status=payload.status,
            workflow_status=payload.workflow_status,
            date_from=payload.date_from,
            date_to=payload.date_to
        )
        
        # Get total count for pagination
        total_count = bhikku_service.count_bhikkus(
            db, 
            search=search_key,
            province=payload.province,
            vh_trn=payload.vh_trn,
            district=payload.district,
            current_user=current_user,
            divisional_secretariat=payload.divisional_secretariat,
            gn_division=payload.gn_division,
            temple=payload.temple,
            child_temple=payload.child_temple,
            nikaya=payload.nikaya,
            parshawaya=payload.parshawaya,
            category=payload.category,
            status=payload.status,
            workflow_status=payload.workflow_status,
            date_from=payload.date_from,
            date_to=payload.date_to
        )
        
        # Convert SQLAlchemy models to Pydantic schemas with enriched data (names replace codes)
        bhikku_schemas = [schemas.Bhikku(**bhikku_service.enrich_bhikku_dict(bhikku, db=db)) for bhikku in bhikkus]
        
        # Also fetch temporary bhikkus and include them in results
        # Only apply search filter for temporary bhikkus (other filters don't apply to them)
        temp_bhikkus = temporary_bhikku_service.list_temporary_bhikkus(
            db,
            skip=0,  # Get all matching temp bhikkus
            limit=200,  # Max allowed
            search=search_key
        )
        
        # Convert temporary bhikkus to Bhikku-compatible format
        for temp_bhikku in temp_bhikkus:
            # Truncate mobile to 10 chars if needed (br_mobile max is 10)
            mobile = temp_bhikku.tb_contact_number[:10] if temp_bhikku.tb_contact_number and len(temp_bhikku.tb_contact_number) > 10 else temp_bhikku.tb_contact_number
            temp_bhikku_dict = {
                "br_regn": f"TEMP-{temp_bhikku.tb_id}",  # Use TEMP prefix for identification
                "br_reqstdate": temp_bhikku.tb_created_at.date() if temp_bhikku.tb_created_at else date.today(),
                "br_mahananame": temp_bhikku.tb_name,
                "br_gihiname": temp_bhikku.tb_samanera_name,
                "br_mobile": mobile,
                "br_fathrsaddrs": temp_bhikku.tb_address,
                "br_mahanatemple": temp_bhikku.tb_living_temple,
                "br_currstat": "TEMPORARY",  # Mark as temporary status
                "br_parshawaya": "N/A",  # Not applicable for temporary
                "br_workflow_status": "TEMPORARY",  # Mark workflow as temporary
                "br_remarks": f"Temporary Bhikku Record (ID: {temp_bhikku.tb_id_number})" if temp_bhikku.tb_id_number else "Temporary Bhikku Record",
            }
            bhikku_schemas.append(schemas.Bhikku(**temp_bhikku_dict))
        
        # Update total count to include temporary bhikkus
        temp_count = temporary_bhikku_service.count_temporary_bhikkus(db, search=search_key)
        total_count_with_temp = total_count + temp_count
        
        return schemas.BhikkuManagementResponse(
            status="success",
            message="Bhikkus retrieved successfully.",
            data=bhikku_schemas,
            totalRecords=total_count_with_temp,
            page=page,
            limit=limit,
        )

    elif action == schemas.CRUDAction.UPDATE:
        # Check UPDATE permission
        check_bhikku_permission(db, current_user, "bhikku:update")
        
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

        # Return enriched data with resolved names
        enriched_data = bhikku_service.enrich_bhikku_dict(updated_bhikku, db=db)
        bhikku_schema = schemas.Bhikku(**enriched_data)
        return schemas.BhikkuManagementResponse(
            status="success",
            message="Bhikku updated successfully.",
            data=bhikku_schema,
        )

    elif action == schemas.CRUDAction.DELETE:
        # Check DELETE permission
        check_bhikku_permission(db, current_user, "bhikku:delete")
        
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

        return schemas.BhikkuManagementResponse(
            status="success",
            message="Bhikku deleted successfully.",
            data=None,
        )

    elif action == schemas.CRUDAction.APPROVE:
        if not payload.br_regn:
            raise validation_error(
                [("payload.br_regn", "br_regn is required for APPROVE action")]
            )
        
        try:
            approved_bhikku = bhikku_service.approve_bhikku(
                db, br_regn=payload.br_regn, actor_id=user_id
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message) from exc
            raise validation_error([(None, message)]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        enriched_data = bhikku_service.enrich_bhikku_dict(approved_bhikku, db=db)
        bhikku_schema = schemas.Bhikku(**enriched_data)
        return schemas.BhikkuManagementResponse(
            status="success",
            message="Bhikku approved successfully.",
            data=bhikku_schema,
        )

    elif action == schemas.CRUDAction.REJECT:
        if not payload.br_regn:
            raise validation_error(
                [("payload.br_regn", "br_regn is required for REJECT action")]
            )
        
        try:
            rejected_bhikku = bhikku_service.reject_bhikku(
                db, 
                br_regn=payload.br_regn, 
                actor_id=user_id,
                rejection_reason=payload.rejection_reason
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message) from exc
            raise validation_error([(None, message)]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        enriched_data = bhikku_service.enrich_bhikku_dict(rejected_bhikku, db=db)
        bhikku_schema = schemas.Bhikku(**enriched_data)
        return schemas.BhikkuManagementResponse(
            status="success",
            message="Bhikku rejected successfully.",
            data=bhikku_schema,
        )

    elif action == schemas.CRUDAction.MARK_PRINTED:
        if not payload.br_regn:
            raise validation_error(
                [("payload.br_regn", "br_regn is required for MARK_PRINTED action")]
            )
        
        try:
            printed_bhikku = bhikku_service.mark_printed(
                db, br_regn=payload.br_regn, actor_id=user_id
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message) from exc
            raise validation_error([(None, message)]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        enriched_data = bhikku_service.enrich_bhikku_dict(printed_bhikku, db=db)
        bhikku_schema = schemas.Bhikku(**enriched_data)
        return schemas.BhikkuManagementResponse(
            status="success",
            message="Bhikku certificate marked as printed successfully.",
            data=bhikku_schema,
        )

    elif action == schemas.CRUDAction.MARK_SCANNED:
        if not payload.br_regn:
            raise validation_error(
                [("payload.br_regn", "br_regn is required for MARK_SCANNED action")]
            )
        
        try:
            scanned_bhikku = bhikku_service.mark_scanned(
                db, br_regn=payload.br_regn, actor_id=user_id
            )
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message) from exc
            raise validation_error([(None, message)]) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        enriched_data = bhikku_service.enrich_bhikku_dict(scanned_bhikku, db=db)
        bhikku_schema = schemas.Bhikku(**enriched_data)
        return schemas.BhikkuManagementResponse(
            status="success",
            message="Bhikku certificate marked as scanned successfully.",
            data=bhikku_schema,
        )

    else:
        raise validation_error([("action", "Invalid action specified")])


@router.post(
    "/workflow",
    response_model=schemas.BhikkuWorkflowResponse,
    dependencies=[has_any_permission("bhikku:approve", "bhikku:update")],
)
def update_bhikku_workflow(
    request: schemas.BhikkuWorkflowRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Update workflow status of a bhikku record.
    
    Main Workflow Actions:
    - APPROVE: Approve pending bhikku registration (PEND-APPROVAL → COMPLETED)
    - REJECT: Reject pending bhikku registration (requires rejection_reason)
    - MARK_PRINTING: Mark as in printing process
    - MARK_PRINTED: Mark certificate as printed
    - MARK_SCANNED: Mark certificate as scanned (PRINTED → PEND-APPROVAL)
    - RESET_TO_PENDING: Reset workflow to pending state (for corrections)
    
    Reprint Workflow Actions:
    - REQUEST_REPRINT: Request a certificate reprint (requires reprint_reason, reprint_amount, optional reprint_remarks)
    - ACCEPT_REPRINT: Accept a reprint request
    - REJECT_REPRINT: Reject a reprint request (requires rejection_reason)
    - COMPLETE_REPRINT: Mark reprint as completed
    
    Requires: bhikku:approve OR bhikku:update permission
    """
    user_id = current_user.ua_user_id
    action = request.action
    br_regn = request.br_regn

    try:
        if action == schemas.WorkflowActionType.APPROVE:
            updated_bhikku = bhikku_service.approve_bhikku(
                db, br_regn=br_regn, actor_id=user_id
            )
            message = "Bhikku approved successfully."

        elif action == schemas.WorkflowActionType.REJECT:
            if not request.rejection_reason:
                raise validation_error(
                    [("rejection_reason", "Rejection reason is required when rejecting")]
                )
            updated_bhikku = bhikku_service.reject_bhikku(
                db, 
                br_regn=br_regn, 
                actor_id=user_id,
                rejection_reason=request.rejection_reason
            )
            message = "Bhikku rejected successfully."

        elif action == schemas.WorkflowActionType.MARK_PRINTING:
            updated_bhikku = bhikku_service.mark_printing(
                db, br_regn=br_regn, actor_id=user_id
            )
            message = "Bhikku marked as printing successfully."

        elif action == schemas.WorkflowActionType.MARK_PRINTED:
            updated_bhikku = bhikku_service.mark_printed(
                db, br_regn=br_regn, actor_id=user_id
            )
            message = "Bhikku certificate marked as printed successfully."

        elif action == schemas.WorkflowActionType.MARK_SCANNED:
            updated_bhikku = bhikku_service.mark_scanned(
                db, br_regn=br_regn, actor_id=user_id
            )
            message = "Bhikku certificate marked as scanned successfully."

        elif action == schemas.WorkflowActionType.RESET_TO_PENDING:
            updated_bhikku = bhikku_service.reset_to_pending(
                db, br_regn=br_regn, actor_id=user_id
            )
            message = "Bhikku workflow reset to pending successfully."

        # Reprint workflow actions
        elif action == schemas.WorkflowActionType.REQUEST_REPRINT:
            if not request.reprint_reason:
                raise validation_error(
                    [("reprint_reason", "Reprint reason is required when requesting reprint")]
                )
            if not request.reprint_amount:
                raise validation_error(
                    [("reprint_amount", "Reprint amount is required when requesting reprint")]
                )
            updated_bhikku = bhikku_service.request_reprint(
                db, 
                br_regn=br_regn, 
                actor_id=user_id,
                reprint_reason=request.reprint_reason,
                reprint_amount=request.reprint_amount,
                reprint_remarks=request.reprint_remarks
            )
            message = "Reprint request submitted successfully."

        elif action == schemas.WorkflowActionType.ACCEPT_REPRINT:
            updated_bhikku = bhikku_service.accept_reprint(
                db, br_regn=br_regn, actor_id=user_id
            )
            message = "Reprint request accepted successfully."

        elif action == schemas.WorkflowActionType.REJECT_REPRINT:
            if not request.rejection_reason:
                raise validation_error(
                    [("rejection_reason", "Rejection reason is required when rejecting reprint")]
                )
            updated_bhikku = bhikku_service.reject_reprint(
                db, 
                br_regn=br_regn, 
                actor_id=user_id,
                rejection_reason=request.rejection_reason
            )
            message = "Reprint request rejected successfully."

        elif action == schemas.WorkflowActionType.COMPLETE_REPRINT:
            updated_bhikku = bhikku_service.complete_reprint(
                db, br_regn=br_regn, actor_id=user_id
            )
            message = "Reprint completed successfully."

        else:
            raise validation_error([("action", "Invalid workflow action")])

    except ValueError as exc:
        error_msg = str(exc)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg) from exc
        raise validation_error([(None, error_msg)]) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    bhikku_schema = schemas.Bhikku.model_validate(updated_bhikku)
    return schemas.BhikkuWorkflowResponse(
        status="success",
        message=message,
        data=bhikku_schema,
    )


# Dedicated workflow endpoints for easier access
@router.post(
    "/{br_regn}/mark-printed",
    response_model=schemas.BhikkuWorkflowResponse,
    dependencies=[has_any_permission("bhikku:update")],
)
def mark_bhikku_printed(
    br_regn: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Mark bhikku certificate as printed.
    
    Transitions: PENDING → PRINTED
    
    Indicates that the certificate has been physically printed.
    This is the first action after creating a bhikku record.
    
    Requires: bhikku:update permission
    """
    user_id = current_user.ua_user_id
    
    try:
        updated_bhikku = bhikku_service.mark_printed(
            db, br_regn=br_regn, actor_id=user_id
        )
    except ValueError as exc:
        error_msg = str(exc)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg) from exc
        raise validation_error([(None, error_msg)]) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    
    bhikku_schema = schemas.Bhikku.model_validate(updated_bhikku)
    return schemas.BhikkuWorkflowResponse(
        status="success",
        message="Bhikku certificate marked as printed successfully.",
        data=bhikku_schema,
    )


@router.post(
    "/{br_regn}/mark-scanned",
    response_model=schemas.BhikkuWorkflowResponse,
    dependencies=[has_any_permission("bhikku:update")],
)
def mark_bhikku_scanned(
    br_regn: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Mark bhikku certificate as scanned.
    
    Transitions: PRINTED → SCANNED
    
    Indicates that the printed certificate has been scanned back into the system.
    After this step, the record can be approved or rejected.
    
    Requires: bhikku:update permission
    """
    user_id = current_user.ua_user_id
    
    try:
        updated_bhikku = bhikku_service.mark_scanned(
            db, br_regn=br_regn, actor_id=user_id
        )
    except ValueError as exc:
        error_msg = str(exc)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg) from exc
        raise validation_error([(None, error_msg)]) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    
    bhikku_schema = schemas.Bhikku.model_validate(updated_bhikku)
    return schemas.BhikkuWorkflowResponse(
        status="success",
        message="Bhikku certificate marked as scanned successfully.",
        data=bhikku_schema,
    )


@router.post(
    "/{br_regn}/approve",
    response_model=schemas.BhikkuWorkflowResponse,
    dependencies=[has_any_permission("bhikku:approve")],
)
def approve_bhikku_record(
    br_regn: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Approve bhikku registration.
    
    Transitions: SCANNED → COMPLETED (with approval_status = APPROVED)
    
    Once approved, the workflow is completed. This is the final step for successful registrations.
    
    Requires: bhikku:approve permission
    """
    user_id = current_user.ua_user_id
    
    try:
        updated_bhikku = bhikku_service.approve_bhikku(
            db, br_regn=br_regn, actor_id=user_id
        )
    except ValueError as exc:
        error_msg = str(exc)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg) from exc
        raise validation_error([(None, error_msg)]) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    
    bhikku_schema = schemas.Bhikku.model_validate(updated_bhikku)
    return schemas.BhikkuWorkflowResponse(
        status="success",
        message="Bhikku approved and completed successfully.",
        data=bhikku_schema,
    )


@router.post(
    "/{br_regn}/reject",
    response_model=schemas.BhikkuWorkflowResponse,
    dependencies=[has_any_permission("bhikku:approve")],
)
def reject_bhikku_record(
    br_regn: str,
    request: schemas.BhikkuRejectRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Reject bhikku registration.
    
    Transitions: SCANNED → REJECTED
    
    Rejects the bhikku registration with a reason. The record will be marked as rejected.
    
    Requires: bhikku:approve permission
    """
    user_id = current_user.ua_user_id
    
    try:
        updated_bhikku = bhikku_service.reject_bhikku(
            db, 
            br_regn=br_regn, 
            actor_id=user_id,
            rejection_reason=request.rejection_reason
        )
    except ValueError as exc:
        error_msg = str(exc)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg) from exc
        raise validation_error([(None, error_msg)]) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    
    bhikku_schema = schemas.Bhikku.model_validate(updated_bhikku)
    return schemas.BhikkuWorkflowResponse(
        status="success",
        message="Bhikku rejected successfully.",
        data=bhikku_schema,
    )


@router.post(
    "/{br_regn}/upload-scanned-document",
    response_model=schemas.BhikkuManagementResponse,
    dependencies=[has_any_permission("bhikku:update")],
)
async def upload_scanned_document(
    br_regn: str,
    file: UploadFile = File(..., description="Scanned document file (max 5MB, PDF, JPG, PNG)"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Upload a scanned document for a Bhikku record.
    
    **NEW BEHAVIOR**: Automatically changes workflow status from PRINTED → PEND-APPROVAL when document is uploaded.
    
    This endpoint allows uploading a scanned document (up to 5MB) for a specific bhikku.
    The file will be stored at: `app/storage/bhikku_regist/<year>/<month>/<day>/<br_regn>/scanned_document_*.ext`
    
    **Requirements:**
    - Maximum file size: 5MB
    - Allowed formats: PDF, JPG, JPEG, PNG
    - Current workflow status must be PRINTED
    - Requires: bhikku:update permission
    
    **Auto-Workflow Transition:**
    - Status automatically changes from PRINTED → PEND-APPROVAL
    - Sets br_scanned_by and br_scanned_at fields
    - Eliminates need for separate MARK_SCANNED action
    
    **Path Parameters:**
    - br_regn: Bhikku registration number (e.g., BH202500001)
    
    **Form Data:**
    - file: The scanned document file to upload
    
    **Response:**
    Returns the updated Bhikku record with:
    - br_scanned_document_path: File path stored  
    - br_workflow_status: "PEND-APPROVAL" (automatically set)
    - br_scanned_by: User who uploaded
    - br_scanned_at: Upload timestamp
    
    **Example Usage (Postman):**
    1. Method: POST
    2. URL: {{base_url}}/api/v1/bhikkus/BH202500001/upload-scanned-document
    3. Headers: Authorization: Bearer <token>
    4. Body: form-data
       - file: (select file)
    """
    username = current_user.ua_user_id if current_user else None
    
    try:
        # Validate file size (5MB = 5 * 1024 * 1024 bytes)
        MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
        
        # Read file content to check size
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size ({file_size / 1024 / 1024:.2f}MB) exceeds maximum allowed size (5MB)"
            )
        
        # Reset file pointer for later processing
        await file.seek(0)
        
        # Upload the file and update the bhikku record
        updated_bhikku = await bhikku_service.upload_scanned_document(
            db, br_regn=br_regn, file=file, actor_id=username
        )
        
        # Return enriched data
        enriched_data = bhikku_service.enrich_bhikku_dict(updated_bhikku, db=db)
        bhikku_schema = schemas.Bhikku(**enriched_data)
        
        return schemas.BhikkuManagementResponse(
            status="success",
            message="Scanned document uploaded successfully. Status automatically changed to PEND-APPROVAL.",
            data=bhikku_schema,
        )
        
    except ValueError as exc:
        message = str(exc)
        if "not found" in message.lower():
            raise HTTPException(status_code=404, detail=message) from exc
        raise HTTPException(status_code=400, detail=message) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/qr_search", response_model=schemas.QRSearchResponseWrapper)
def get_qr_search_details(
    request: schemas.QRSearchRequest,
    db: Session = Depends(get_db),
):
    """
    Get limited details via QR code search.
    This endpoint does not require authentication.
    
    Supports Bhikku, Silmatha, and High Bhikku records.
    Automatically detects record type if not specified.
    
    Returns limited information:
    - Name (ordained name)
    - Birth name
    - Date of birth
    - Contact number
    - Email
    - Live location (temple)
    - Current status
    - Category
    - Ordination date
    """
    result = bhikku_service.get_qr_search_details(
        db=db,
        record_id=request.id,
        record_type=request.record_type
    )
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"No record found with ID: {request.id}"
        )
    
    return {
        "status": "success",
        "message": "Record details retrieved successfully.",
        "data": result,
    }
