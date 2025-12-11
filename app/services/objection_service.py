from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.objection import Objection, ObjectionStatus
from app.schemas.objection import ObjectionCreate, ObjectionUpdate
from app.repositories.objection_repo import objection_repo
from app.repositories.objection_type_repo import objection_type_repo
from app.repositories.vihara_repo import vihara_repo
from app.repositories.arama_repo import arama_repo
from app.repositories.devala_repo import devala_repo


class ObjectionService:
    """Business logic layer for objection data."""

    def __init__(self):
        self.repository = objection_repo

    def validate_entity_by_id(
        self, 
        db: Session, 
        vh_id: Optional[int] = None,
        ar_id: Optional[int] = None,
        dv_id: Optional[int] = None
    ) -> tuple[bool, str]:
        """
        Validate that exactly one entity exists by ID
        Returns: (exists: bool, entity_type: str)
        """
        if vh_id:
            entity = vihara_repo.get(db, vh_id)
            if entity:
                return True, "VIHARA"
            raise HTTPException(status_code=404, detail=f"Vihara with ID {vh_id} not found")
        
        elif ar_id:
            entity = arama_repo.get(db, ar_id)
            if entity:
                return True, "ARAMA"
            raise HTTPException(status_code=404, detail=f"Arama with ID {ar_id} not found")
        
        elif dv_id:
            entity = devala_repo.get(db, dv_id)
            if entity:
                return True, "DEVALA"
            raise HTTPException(status_code=404, detail=f"Devala with ID {dv_id} not found")
        
        return False, ""

    def lookup_entity_id_by_trn(
        self, 
        db: Session, 
        trn: str
    ) -> tuple[Optional[int], Optional[int], Optional[int], str]:
        """
        Look up entity ID from TRN
        Returns: (vh_id, ar_id, dv_id, entity_type)
        """
        trn_upper = trn.upper().strip()
        
        if trn_upper.startswith("TRN"):
            entity = vihara_repo.get_by_trn(db, trn)
            if entity:
                return entity.vh_id, None, None, "VIHARA"
            raise HTTPException(status_code=404, detail=f"Vihara with TRN '{trn}' not found")
        
        elif trn_upper.startswith("ARN"):
            entity = arama_repo.get_by_trn(db, trn)
            if entity:
                return None, entity.ar_id, None, "ARAMA"
            raise HTTPException(status_code=404, detail=f"Arama with TRN '{trn}' not found")
        
        elif trn_upper.startswith("DVL"):
            entity = devala_repo.get_by_trn(db, trn)
            if entity:
                return None, None, entity.dv_id, "DEVALA"
            raise HTTPException(status_code=404, detail=f"Devala with TRN '{trn}' not found")
        
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid TRN format: '{trn}'. Must start with TRN, ARN, or DVL"
            )

    def create_objection(
        self,
        db: Session,
        *,
        data: ObjectionCreate,
        submitted_by: Optional[str] = None
    ) -> Objection:
        """
        Create a new objection
        
        Accepts either:
        - TRN (auto-detects entity and looks up ID)
        - Direct entity ID (vh_id, ar_id, or dv_id)
        
        Validates that:
        1. The objection type exists and is active
        2. The entity exists
        3. No active objection already exists for this entity
        """
        # If TRN provided, look up the entity ID
        if data.trn:
            vh_id, ar_id, dv_id, entity_type = self.lookup_entity_id_by_trn(db, data.trn)
            # Update the data object with looked-up IDs
            data.vh_id = vh_id
            data.ar_id = ar_id
            data.dv_id = dv_id
        
        # Validate objection type exists and is active
        objection_type = objection_type_repo.get(db, data.obj_type_id)
        if not objection_type:
            raise HTTPException(
                status_code=404,
                detail=f"Objection type with ID {data.obj_type_id} not found"
            )
        
        if not objection_type.ot_is_active:
            raise HTTPException(
                status_code=400,
                detail=f"Objection type '{objection_type.ot_name_en}' is not active"
            )
        
        # Validate entity exists by ID
        exists, entity_type = self.validate_entity_by_id(
            db, vh_id=data.vh_id, ar_id=data.ar_id, dv_id=data.dv_id
        )
        
        if not exists:
            raise HTTPException(
                status_code=404,
                detail=f"Entity not found"
            )
        
        # Check for existing active objection
        existing = None
        if data.vh_id:
            existing = self.repository.get_by_vh_id(db, data.vh_id, status=ObjectionStatus.APPROVED)
        elif data.ar_id:
            existing = self.repository.get_by_ar_id(db, data.ar_id, status=ObjectionStatus.APPROVED)
        elif data.dv_id:
            existing = self.repository.get_by_dv_id(db, data.dv_id, status=ObjectionStatus.APPROVED)
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Active objection already exists for this {entity_type}"
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
        vh_id: Optional[int] = None,
        ar_id: Optional[int] = None,
        dv_id: Optional[int] = None,
        status: Optional[ObjectionStatus] = None
    ) -> tuple[List[Objection], int]:
        """List objections with filters"""
        objections = self.repository.list(
            db,
            skip=skip,
            limit=limit,
            vh_id=vh_id,
            ar_id=ar_id,
            dv_id=dv_id,
            status=status
        )
        
        total = self.repository.count(
            db,
            vh_id=vh_id,
            ar_id=ar_id,
            dv_id=dv_id,
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

    def check_active_objection_by_trn(
        self,
        db: Session,
        *,
        trn: str
    ) -> tuple[bool, Optional[Objection]]:
        """
        Check if entity has an active objection by TRN
        Returns: (has_active: bool, objection: Optional[Objection])
        """
        # Look up entity ID from TRN
        vh_id, ar_id, dv_id, entity_type = self.lookup_entity_id_by_trn(db, trn)
        
        # Check for active objection
        objection = None
        if vh_id:
            objection = self.repository.get_by_vh_id(db, vh_id, status=ObjectionStatus.APPROVED)
        elif ar_id:
            objection = self.repository.get_by_ar_id(db, ar_id, status=ObjectionStatus.APPROVED)
        elif dv_id:
            objection = self.repository.get_by_dv_id(db, dv_id, status=ObjectionStatus.APPROVED)
        
        return objection is not None, objection

    def check_active_objection_by_id(
        self,
        db: Session,
        *,
        vh_id: Optional[int] = None,
        ar_id: Optional[int] = None,
        dv_id: Optional[int] = None
    ) -> tuple[bool, Optional[Objection]]:
        """
        Check if entity has an active objection by entity ID
        Returns: (has_active: bool, objection: Optional[Objection])
        """
        objection = None
        if vh_id:
            objection = self.repository.get_by_vh_id(db, vh_id, status=ObjectionStatus.APPROVED)
        elif ar_id:
            objection = self.repository.get_by_ar_id(db, ar_id, status=ObjectionStatus.APPROVED)
        elif dv_id:
            objection = self.repository.get_by_dv_id(db, dv_id, status=ObjectionStatus.APPROVED)
        
        return objection is not None, objection


objection_service = ObjectionService()
