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
from app.repositories.bhikku_repo import bhikku_repo
from app.repositories.silmatha_regist_repo import silmatha_regist_repo
from app.repositories.direct_bhikku_high_repo import direct_bhikku_high_repo


class ObjectionService:
    """Business logic layer for objection data."""

    def __init__(self):
        self.repository = objection_repo

    def validate_entity_by_id(
        self, 
        db: Session, 
        vh_trn: Optional[str] = None,
        ar_trn: Optional[str] = None,
        dv_trn: Optional[str] = None,
        bh_regn: Optional[str] = None,
        sil_regn: Optional[str] = None,
        dbh_regn: Optional[str] = None
    ) -> tuple[bool, str]:
        """
        Validate that exactly one entity exists by TRN/REGN
        Returns: (exists: bool, entity_type: str)
        """
        if vh_trn:
            entity = vihara_repo.get_by_trn(db, vh_trn)
            if entity:
                return True, "VIHARA"
            raise HTTPException(status_code=404, detail=f"Vihara with TRN {vh_trn} not found")
        
        elif ar_trn:
            entity = arama_repo.get_by_trn(db, ar_trn)
            if entity:
                return True, "ARAMA"
            raise HTTPException(status_code=404, detail=f"Arama with TRN {ar_trn} not found")
        
        elif dv_trn:
            entity = devala_repo.get_by_trn(db, dv_trn)
            if entity:
                return True, "DEVALA"
            raise HTTPException(status_code=404, detail=f"Devala with TRN {dv_trn} not found")
        
        elif bh_regn:
            entity = bhikku_repo.get_by_regn(db, bh_regn)
            if entity:
                return True, "BHIKKU"
            raise HTTPException(status_code=404, detail=f"Bhikku with registration {bh_regn} not found")
        
        elif sil_regn:
            entity = silmatha_regist_repo.get_by_regn(db, sil_regn)
            if entity:
                return True, "SILMATHA"
            raise HTTPException(status_code=404, detail=f"Silmatha with registration {sil_regn} not found")
        
        elif dbh_regn:
            entity = direct_bhikku_high_repo.get_by_regn(db, dbh_regn)
            if entity:
                return True, "HIGH_BHIKKU"
            raise HTTPException(status_code=404, detail=f"High Bhikku with registration {dbh_regn} not found")
        
        return False, ""

    def lookup_entity_id_by_id(
        self, 
        db: Session, 
        entity_id: str
    ) -> tuple[Optional[str], Optional[str], Optional[str], Optional[str], Optional[str], Optional[str], str]:
        """
        Look up and validate entity from registration ID/TRN
        Returns: (vh_trn, ar_trn, dv_trn, bh_regn, sil_regn, dbh_regn, entity_type)
        """
        id_upper = entity_id.upper().strip()
        
        if id_upper.startswith("TRN"):
            entity = vihara_repo.get_by_trn(db, entity_id)
            if entity:
                return entity.vh_trn, None, None, None, None, None, "VIHARA"
            raise HTTPException(status_code=404, detail=f"Vihara with ID '{entity_id}' not found")
        
        elif id_upper.startswith("ARN"):
            entity = arama_repo.get_by_trn(db, entity_id)
            if entity:
                return None, entity.ar_trn, None, None, None, None, "ARAMA"
            raise HTTPException(status_code=404, detail=f"Arama with ID '{entity_id}' not found")
        
        elif id_upper.startswith("DVL"):
            entity = devala_repo.get_by_trn(db, entity_id)
            if entity:
                return None, None, entity.dv_trn, None, None, None, "DEVALA"
            raise HTTPException(status_code=404, detail=f"Devala with ID '{entity_id}' not found")
        
        elif id_upper.startswith("BH"):
            entity = bhikku_repo.get_by_regn(db, entity_id)
            if entity:
                return None, None, None, entity.br_regn, None, None, "BHIKKU"
            raise HTTPException(status_code=404, detail=f"Bhikku with ID '{entity_id}' not found")
        
        elif id_upper.startswith("SIL"):
            entity = silmatha_regist_repo.get_by_regn(db, entity_id)
            if entity:
                return None, None, None, None, entity.sil_regn, None, "SILMATHA"
            raise HTTPException(status_code=404, detail=f"Silmatha with ID '{entity_id}' not found")
        
        elif id_upper.startswith("DBH") or id_upper.startswith("UPS"):
            entity = direct_bhikku_high_repo.get_by_regn(db, entity_id)
            if entity:
                return None, None, None, None, None, entity.dbh_regn, "HIGH_BHIKKU"
            raise HTTPException(status_code=404, detail=f"High Bhikku with ID '{entity_id}' not found")
        
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid ID format: '{entity_id}'. Must start with TRN, ARN, DVL, BH, SIL, DBH, or UPS"
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
        # If ID provided, look up the entity TRN/REGN
        if data.id:
            vh_trn, ar_trn, dv_trn, bh_regn, sil_regn, dbh_regn, entity_type = self.lookup_entity_id_by_id(db, data.id)
            # Update the data object with looked-up TRN/REGN
            data.vh_trn = vh_trn
            data.ar_trn = ar_trn
            data.dv_trn = dv_trn
            data.bh_regn = bh_regn
            data.sil_regn = sil_regn
            data.dbh_regn = dbh_regn
        
        # Validate objection type exists and is active
        objection_type = objection_type_repo.get_by_code(db, data.ot_code)
        if not objection_type:
            raise HTTPException(
                status_code=404,
                detail=f"Objection type with code '{data.ot_code}' not found"
            )
        
        if not objection_type.ot_is_active:
            raise HTTPException(
                status_code=400,
                detail=f"Objection type '{objection_type.ot_name_en}' is not active"
            )
        
        # Validate entity exists by ID
        exists, entity_type = self.validate_entity_by_id(
            db, vh_trn=data.vh_trn, ar_trn=data.ar_trn, dv_trn=data.dv_trn,
            bh_regn=data.bh_regn, sil_regn=data.sil_regn, dbh_regn=data.dbh_regn
        )
        
        if not exists:
            raise HTTPException(
                status_code=404,
                detail=f"Entity not found"
            )
        
        # Check for existing active objection of the same type
        existing = None
        if data.vh_trn:
            existing = self.repository.get_by_vh_trn(db, data.vh_trn, status=ObjectionStatus.APPROVED, ot_code=data.ot_code)
        elif data.ar_trn:
            existing = self.repository.get_by_ar_trn(db, data.ar_trn, status=ObjectionStatus.APPROVED, ot_code=data.ot_code)
        elif data.dv_trn:
            existing = self.repository.get_by_dv_trn(db, data.dv_trn, status=ObjectionStatus.APPROVED, ot_code=data.ot_code)
        elif data.bh_regn:
            existing = self.repository.get_by_bh_regn(db, data.bh_regn, status=ObjectionStatus.APPROVED, ot_code=data.ot_code)
        elif data.sil_regn:
            existing = self.repository.get_by_sil_regn(db, data.sil_regn, status=ObjectionStatus.APPROVED, ot_code=data.ot_code)
        elif data.dbh_regn:
            existing = self.repository.get_by_dbh_regn(db, data.dbh_regn, status=ObjectionStatus.APPROVED, ot_code=data.ot_code)
        
        if existing:
            objection_type_name = objection_type.ot_name_en if objection_type else "this type"
            raise HTTPException(
                status_code=400,
                detail=f"Active {objection_type_name} objection already exists for this {entity_type}"
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
        vh_trn: Optional[str] = None,
        ar_trn: Optional[str] = None,
        dv_trn: Optional[str] = None,
        bh_regn: Optional[str] = None,
        sil_regn: Optional[str] = None,
        dbh_regn: Optional[str] = None,
        status: Optional[ObjectionStatus] = None,
        search: Optional[str] = None
    ) -> tuple[List[Objection], int]:
        """List objections with filters"""
        objections = self.repository.list(
            db,
            skip=skip,
            limit=limit,
            vh_trn=vh_trn,
            ar_trn=ar_trn,
            dv_trn=dv_trn,
            bh_regn=bh_regn,
            sil_regn=sil_regn,
            dbh_regn=dbh_regn,
            status=status,
            search=search
        )
        
        total = self.repository.count(
            db,
            vh_trn=vh_trn,
            ar_trn=ar_trn,
            dv_trn=dv_trn,
            bh_regn=bh_regn,
            sil_regn=sil_regn,
            dbh_regn=dbh_regn,
            status=status,
            search=search
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
        Check if entity has an active objection by TRN/ID
        Returns: (has_active: bool, objection: Optional[Objection])
        """
        # Look up entity TRN/REGN from ID
        vh_trn, ar_trn, dv_trn, bh_regn, sil_regn, dbh_regn, entity_type = self.lookup_entity_id_by_id(db, trn)
        
        # Check for active objection
        objection = None
        if vh_trn:
            objection = self.repository.get_by_vh_trn(db, vh_trn, status=ObjectionStatus.APPROVED)
        elif ar_trn:
            objection = self.repository.get_by_ar_trn(db, ar_trn, status=ObjectionStatus.APPROVED)
        elif dv_trn:
            objection = self.repository.get_by_dv_trn(db, dv_trn, status=ObjectionStatus.APPROVED)
        elif bh_regn:
            objection = self.repository.get_by_bh_regn(db, bh_regn, status=ObjectionStatus.APPROVED)
        elif sil_regn:
            objection = self.repository.get_by_sil_regn(db, sil_regn, status=ObjectionStatus.APPROVED)
        elif dbh_regn:
            objection = self.repository.get_by_dbh_regn(db, dbh_regn, status=ObjectionStatus.APPROVED)
        
        return objection is not None, objection

    def check_active_objection_by_id(
        self,
        db: Session,
        *,
        vh_trn: Optional[str] = None,
        ar_trn: Optional[str] = None,
        dv_trn: Optional[str] = None,
        bh_regn: Optional[str] = None,
        sil_regn: Optional[str] = None,
        dbh_regn: Optional[str] = None
    ) -> tuple[bool, Optional[Objection]]:
        """
        Check if entity has an active objection by entity TRN/REGN
        Returns: (has_active: bool, objection: Optional[Objection])
        """
        objection = None
        if vh_trn:
            objection = self.repository.get_by_vh_trn(db, vh_trn, status=ObjectionStatus.APPROVED)
        elif ar_trn:
            objection = self.repository.get_by_ar_trn(db, ar_trn, status=ObjectionStatus.APPROVED)
        elif dv_trn:
            objection = self.repository.get_by_dv_trn(db, dv_trn, status=ObjectionStatus.APPROVED)
        elif bh_regn:
            objection = self.repository.get_by_bh_regn(db, bh_regn, status=ObjectionStatus.APPROVED)
        elif sil_regn:
            objection = self.repository.get_by_sil_regn(db, sil_regn, status=ObjectionStatus.APPROVED)
        elif dbh_regn:
            objection = self.repository.get_by_dbh_regn(db, dbh_regn, status=ObjectionStatus.APPROVED)
        
        return objection is not None, objection


objection_service = ObjectionService()
