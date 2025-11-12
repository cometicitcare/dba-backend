# app/api/v1/routes/bhikkus.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.auth_middleware import get_current_user
from app.models.user import UserAccount
from app.schemas import bhikku as schemas
from app.services.bhikku_service import bhikku_service
from app.utils.http_exceptions import validation_error
from pydantic import ValidationError

router = APIRouter()


@router.get(
    "/mahanayaka-list",
    response_model=schemas.BhikkuMahanayakaListResponse,
)
def list_mahanayaka_bhikkus(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Return rows from the `bikkudtls_mahanayakalist` database view.
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
)
def list_nikaya_bhikkus(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Return rows from the `bikkudtls_nikaya_list` database view.
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
    "/district-list",
    response_model=schemas.BhikkuDistrictListResponse,
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
    "/division-secretariat-list",
    response_model=schemas.BhikkuDivisionSecListResponse,
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


@router.get(
    "/current-status-summary",
    response_model=schemas.BhikkuCurrentStatusSummaryResponse,
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

        return {
            "status": "success",
            "message": "Bhikku created successfully.",
            "data": created_bhikku,
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
