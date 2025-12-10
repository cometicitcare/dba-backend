from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.objection import Objection, ObjectionStatus, EntityType
from app.schemas.objection import ObjectionCreate, ObjectionUpdate


class ObjectionRepository:
    """Data access helpers for objection records."""

    def get(self, db: Session, obj_id: int) -> Optional[Objection]:
        """Get objection by ID"""
        return (
            db.query(Objection)
            .filter(Objection.obj_id == obj_id, Objection.obj_is_deleted.is_(False))
            .first()
        )

    def get_by_entity(
        self, 
        db: Session, 
        entity_type: EntityType, 
        entity_trn: str,
        status: Optional[ObjectionStatus] = None
    ) -> Optional[Objection]:
        """Get objection for specific entity"""
        query = db.query(Objection).filter(
            Objection.obj_entity_type == entity_type,
            Objection.obj_entity_trn == entity_trn,
            Objection.obj_is_deleted.is_(False)
        )
        
        if status:
            query = query.filter(Objection.obj_status == status)
        
        return query.order_by(Objection.obj_submitted_at.desc()).first()

    def has_active_objection(
        self, 
        db: Session, 
        entity_type: EntityType, 
        entity_trn: str
    ) -> bool:
        """Check if entity has an active (approved) objection"""
        return (
            db.query(Objection)
            .filter(
                Objection.obj_entity_type == entity_type,
                Objection.obj_entity_trn == entity_trn,
                Objection.obj_status == ObjectionStatus.APPROVED,
                Objection.obj_is_deleted.is_(False)
            )
            .first()
        ) is not None

    def list(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 10,
        entity_type: Optional[EntityType] = None,
        entity_trn: Optional[str] = None,
        status: Optional[ObjectionStatus] = None
    ) -> List[Objection]:
        """List objections with filters"""
        query = db.query(Objection).filter(Objection.obj_is_deleted.is_(False))

        if entity_type:
            query = query.filter(Objection.obj_entity_type == entity_type)
        
        if entity_trn:
            query = query.filter(Objection.obj_entity_trn == entity_trn)
        
        if status:
            query = query.filter(Objection.obj_status == status)

        return (
            query.order_by(Objection.obj_submitted_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count(
        self,
        db: Session,
        *,
        entity_type: Optional[EntityType] = None,
        entity_trn: Optional[str] = None,
        status: Optional[ObjectionStatus] = None
    ) -> int:
        """Count objections with filters"""
        query = db.query(Objection).filter(Objection.obj_is_deleted.is_(False))

        if entity_type:
            query = query.filter(Objection.obj_entity_type == entity_type)
        
        if entity_trn:
            query = query.filter(Objection.obj_entity_trn == entity_trn)
        
        if status:
            query = query.filter(Objection.obj_status == status)

        return query.count()

    def create(
        self, 
        db: Session, 
        *, 
        data: ObjectionCreate,
        submitted_by: Optional[str] = None
    ) -> Objection:
        """Create new objection"""
        objection = Objection(
            obj_entity_type=data.obj_entity_type,
            obj_entity_trn=data.obj_entity_trn,
            obj_entity_name=data.obj_entity_name,
            obj_reason=data.obj_reason,
            obj_status=ObjectionStatus.PENDING,
            obj_submitted_by=submitted_by
        )
        
        db.add(objection)
        db.commit()
        db.refresh(objection)
        return objection

    def approve(
        self, 
        db: Session, 
        *, 
        objection: Objection,
        approved_by: Optional[str] = None
    ) -> Objection:
        """Approve objection"""
        from datetime import datetime
        
        objection.obj_status = ObjectionStatus.APPROVED
        objection.obj_approved_by = approved_by
        objection.obj_approved_at = datetime.utcnow()
        objection.obj_updated_by = approved_by
        
        db.commit()
        db.refresh(objection)
        return objection

    def reject(
        self, 
        db: Session, 
        *, 
        objection: Objection,
        rejection_reason: str,
        rejected_by: Optional[str] = None
    ) -> Objection:
        """Reject objection"""
        from datetime import datetime
        
        objection.obj_status = ObjectionStatus.REJECTED
        objection.obj_rejected_by = rejected_by
        objection.obj_rejected_at = datetime.utcnow()
        objection.obj_rejection_reason = rejection_reason
        objection.obj_updated_by = rejected_by
        
        db.commit()
        db.refresh(objection)
        return objection

    def cancel(
        self, 
        db: Session, 
        *, 
        objection: Objection,
        cancellation_reason: Optional[str] = None,
        cancelled_by: Optional[str] = None
    ) -> Objection:
        """Cancel objection"""
        from datetime import datetime
        
        objection.obj_status = ObjectionStatus.CANCELLED
        objection.obj_cancelled_by = cancelled_by
        objection.obj_cancelled_at = datetime.utcnow()
        objection.obj_cancellation_reason = cancellation_reason
        objection.obj_updated_by = cancelled_by
        
        db.commit()
        db.refresh(objection)
        return objection


objection_repo = ObjectionRepository()
