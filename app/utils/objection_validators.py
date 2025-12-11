"""
Validation helpers for objection checks
"""
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.services.objection_service import objection_service


def validate_no_active_objection(
    db: Session,
    vh_id: Optional[int] = None,
    ar_id: Optional[int] = None,
    dv_id: Optional[int] = None,
    operation_description: str = "add resident bhikkus/silmathas"
) -> None:
    """
    Validate that there is no active objection for the entity.
    Raises HTTPException if an active objection exists.
    
    Provide exactly ONE of vh_id, ar_id, or dv_id.
    
    Args:
        db: Database session
        vh_id: Vihara ID (optional)
        ar_id: Arama ID (optional)
        dv_id: Devala ID (optional)
        operation_description: Description of the operation being prevented
    
    Raises:
        HTTPException: If an active objection exists
    
    Example:
        # Before adding resident bhikkhus to vihara
        validate_no_active_objection(db, vh_id=123)
        
        # Before adding resident silmathas to arama
        validate_no_active_objection(db, ar_id=456)
    """
    has_active, objection = objection_service.check_active_objection_by_id(
        db, vh_id=vh_id, ar_id=ar_id, dv_id=dv_id
    )
    
    if has_active and objection:
        entity_type = "entity"
        if vh_id:
            entity_type = "VIHARA"
        elif ar_id:
            entity_type = "ARAMA"
        elif dv_id:
            entity_type = "DEVALA"
        
        raise HTTPException(
            status_code=403,
            detail=(
                f"Cannot {operation_description} to this {entity_type}. "
                f"An active objection exists (ID: {objection.obj_id}). "
                f"Reason: {objection.obj_reason}"
            )
        )
