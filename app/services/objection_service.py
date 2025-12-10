from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.objection import Objection, ObjectionStatus, EntityType
from app.schemas.objection import ObjectionCreate, ObjectionUpdate
from app.repositories.objection_repo import objection_repo
from app.repositories.vihara_repo import vihara_repo
from app.repositories.arama_repo import arama_repo
from app.repositories.devala_repo import devala_repo


class ObjectionService:
    """Business logic layer for objection data."""

    def __init__(self):
        self.repository = objection_repo

    def validate_entity_exists(
        self, 
        db: Session, 
        entity_type: EntityType, 
        entity_trn: str
    ) -> tuple[bool, Optional[str]]:
        """
        Validate that the entity exists
        Returns: (exists: bool, entity_name: Optional[str])
        """
        if entity_type == EntityType.VIHARA:
            entity = vihara_repo.get_by_trn(db, entity_trn)
            if entity:
                return True, entity.vh_vname
        elif entity_type == EntityType.ARAMA:
            entity = arama_repo.get_by_trn(db, entity_trn)
            if entity:
                return True, entity.ar_vname
        elif entity_type == EntityType.DEVALA:
            entity = devala_repo.get_by_trn(db, entity_trn)
            if entity:
                return True, entity.dv_vname
        
        return False, None

    def create_objection(
        self,
        db: Session,
        *,
        data: ObjectionCreate,
        submitted_by: Optional[str] = None
    ) -> Objection:
        """
        Create a new objection
        
        Validates that:
        1. The entity exists
        2. No active objection already exists for this entity
        """
        # Validate entity exists
        exists, entity_name = self.validate_entity_exists(
            db, data.obj_entity_type, data.obj_entity_trn
        )
        
        if not exists:
            raise HTTPException(
                status_code=404,
                detail=f"{data.obj_entity_type.value} with TRN '{data.obj_entity_trn}' not found"
            )
        
        # Auto-populate entity name if not provided
        if not data.obj_entity_name and entity_name:
            data.obj_entity_name = entity_name
        
        # Check for existing active objection
        existing = self.repository.get_by_entity(
            db,
            entity_type=data.obj_entity_type,
            entity_trn=data.obj_entity_trn,
            status=ObjectionStatus.APPROVED
        )
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Active objection already exists for this {data.obj_entity_type.value}"
            )
        
        return self.repository.create(db, data=data, submitted_by=submitted_by)

    def get_objection(
        self, 
        db: Session, 
        obj_id: int
    ) -> Objection:
        """Get objection by ID"""
        objection = self.repository.get(db, obj_id)
        if not objection:
            raise HTTPException(
                status_code=404,
                detail=f"Objection with ID {obj_id} not found"
            )
        return objection

    def list_objections(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 10,
        entity_type: Optional[EntityType] = None,
        entity_trn: Optional[str] = None,
        status: Optional[ObjectionStatus] = None
    ) -> tuple[List[Objection], int]:
        """List objections with filters"""
        objections = self.repository.list(
            db,
            skip=skip,
            limit=limit,
            entity_type=entity_type,
            entity_trn=entity_trn,
            status=status
        )
        
        total = self.repository.count(
            db,
            entity_type=entity_type,
            entity_trn=entity_trn,
            status=status
        )
        
        return objections, total

    def approve_objection(
        self,
        db: Session,
        *,
        obj_id: int,
        approved_by: Optional[str] = None
    ) -> Objection:
        """Approve an objection"""
        objection = self.get_objection(db, obj_id)
        
        if objection.obj_status != ObjectionStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot approve objection with status {objection.obj_status.value}. Only PENDING objections can be approved."
            )
        
        return self.repository.approve(db, objection=objection, approved_by=approved_by)

    def reject_objection(
        self,
        db: Session,
        *,
        obj_id: int,
        rejection_reason: str,
        rejected_by: Optional[str] = None
    ) -> Objection:
        """Reject an objection"""
        objection = self.get_objection(db, obj_id)
        
        if objection.obj_status != ObjectionStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot reject objection with status {objection.obj_status.value}. Only PENDING objections can be rejected."
            )
        
        if not rejection_reason or not rejection_reason.strip():
            raise HTTPException(
                status_code=400,
                detail="Rejection reason is required"
            )
        
        return self.repository.reject(
            db, 
            objection=objection, 
            rejection_reason=rejection_reason,
            rejected_by=rejected_by
        )

    def cancel_objection(
        self,
        db: Session,
        *,
        obj_id: int,
        cancellation_reason: Optional[str] = None,
        cancelled_by: Optional[str] = None
    ) -> Objection:
        """Cancel an objection"""
        objection = self.get_objection(db, obj_id)
        
        if objection.obj_status not in [ObjectionStatus.PENDING, ObjectionStatus.APPROVED]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot cancel objection with status {objection.obj_status.value}. Only PENDING or APPROVED objections can be cancelled."
            )
        
        return self.repository.cancel(
            db,
            objection=objection,
            cancellation_reason=cancellation_reason,
            cancelled_by=cancelled_by
        )

    def check_active_objection(
        self,
        db: Session,
        *,
        entity_type: EntityType,
        entity_trn: str
    ) -> tuple[bool, Optional[Objection]]:
        """
        Check if entity has an active objection
        Returns: (has_active: bool, objection: Optional[Objection])
        """
        objection = self.repository.get_by_entity(
            db,
            entity_type=entity_type,
            entity_trn=entity_trn,
            status=ObjectionStatus.APPROVED
        )
        
        return objection is not None, objection


objection_service = ObjectionService()
