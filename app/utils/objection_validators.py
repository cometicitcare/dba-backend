"""
Validation helpers for objection checks
"""
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.services.objection_service import objection_service


def validate_no_active_objection(
    db: Session,
    vh_trn: Optional[str] = None,
    ar_trn: Optional[str] = None,
    dv_trn: Optional[str] = None,
    bh_regn: Optional[str] = None,
    sil_regn: Optional[str] = None,
    dbh_regn: Optional[str] = None,
    operation_description: str = "add resident bhikkus/silmathas"
) -> None:
    """
    Validate that there is no active objection for the entity.
    Raises HTTPException if an active objection exists.
    
    Provide exactly ONE of the entity identifiers.
    
    Args:
        db: Database session
        vh_trn: Vihara TRN (optional)
        ar_trn: Arama TRN (optional)
        dv_trn: Devala TRN (optional)
        bh_regn: Bhikku REGN (optional)
        sil_regn: Silmatha REGN (optional)
        dbh_regn: High Bhikku REGN (optional)
        operation_description: Description of the operation being prevented
    
    Raises:
        HTTPException: If an active objection exists
    
    Example:
        # Before adding resident bhikkhus to vihara
        validate_no_active_objection(db, vh_trn="TRN0001234")
        
        # Before adding resident silmathas to arama
        validate_no_active_objection(db, ar_trn="ARN0005678")
    """
    has_active, objection = objection_service.check_active_objection_by_id(
        db, vh_trn=vh_trn, ar_trn=ar_trn, dv_trn=dv_trn, 
        bh_regn=bh_regn, sil_regn=sil_regn, dbh_regn=dbh_regn
    )
    
    if has_active and objection:
        entity_type = "entity"
        if vh_trn:
            entity_type = "VIHARA"
        elif ar_trn:
            entity_type = "ARAMA"
        elif dv_trn:
            entity_type = "DEVALA"
        elif bh_regn:
            entity_type = "BHIKKU"
        elif sil_regn:
            entity_type = "SILMATHA"
        elif dbh_regn:
            entity_type = "HIGH_BHIKKU"
        
        raise HTTPException(
            status_code=403,
            detail=(
                f"Cannot {operation_description} to this {entity_type}. "
                f"An active objection exists (ID: {objection.obj_id}). "
                f"Reason: {objection.obj_reason}"
            )
        )
