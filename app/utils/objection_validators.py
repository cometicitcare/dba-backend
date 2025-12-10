"""
Validation helpers for objection checks
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.objection import EntityType
from app.services.objection_service import objection_service


def validate_no_active_objection(
    db: Session,
    entity_type: EntityType,
    entity_trn: str,
    operation_description: str = "add resident bhikkus/silmathas"
) -> None:
    """
    Validate that there is no active objection for the entity.
    Raises HTTPException if an active objection exists.
    
    Args:
        db: Database session
        entity_type: Type of entity (VIHARA, ARAMA, DEVALA)
        entity_trn: TRN of the entity
        operation_description: Description of the operation being prevented
    
    Raises:
        HTTPException: If an active objection exists
    """
    has_active, objection = objection_service.check_active_objection(
        db, entity_type=entity_type, entity_trn=entity_trn
    )
    
    if has_active and objection:
        raise HTTPException(
            status_code=403,
            detail=(
                f"Cannot {operation_description} to this {entity_type.value}. "
                f"An active objection exists (ID: {objection.obj_id}). "
                f"Reason: {objection.obj_reason}"
            )
        )
