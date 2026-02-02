from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.objection import Objection, ObjectionStatus
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

    def get_by_vh_trn(
        self, 
        db: Session, 
        vh_trn: str,
        status: Optional[ObjectionStatus] = None,
        ot_code: Optional[str] = None
    ) -> Optional[Objection]:
        """Get objection for vihara"""
        query = db.query(Objection).filter(
            Objection.vh_trn == vh_trn,
            Objection.obj_is_deleted.is_(False)
        )
        
        if status:
            query = query.filter(Objection.obj_status == status)
        
        if ot_code:
            query = query.filter(Objection.ot_code == ot_code)
        
        return query.order_by(Objection.obj_submitted_at.desc()).first()

    def get_by_ar_trn(
        self, 
        db: Session, 
        ar_trn: str,
        status: Optional[ObjectionStatus] = None,
        ot_code: Optional[str] = None
    ) -> Optional[Objection]:
        """Get objection for arama"""
        query = db.query(Objection).filter(
            Objection.ar_trn == ar_trn,
            Objection.obj_is_deleted.is_(False)
        )
        
        if status:
            query = query.filter(Objection.obj_status == status)
        
        if ot_code:
            query = query.filter(Objection.ot_code == ot_code)
        
        return query.order_by(Objection.obj_submitted_at.desc()).first()

    def get_by_dv_trn(
        self, 
        db: Session, 
        dv_trn: str,
        status: Optional[ObjectionStatus] = None,
        ot_code: Optional[str] = None
    ) -> Optional[Objection]:
        """Get objection for devala"""
        query = db.query(Objection).filter(
            Objection.dv_trn == dv_trn,
            Objection.obj_is_deleted.is_(False)
        )
        
        if status:
            query = query.filter(Objection.obj_status == status)
        
        if ot_code:
            query = query.filter(Objection.ot_code == ot_code)
        
        return query.order_by(Objection.obj_submitted_at.desc()).first()

    def has_active_objection_by_vh_trn(self, db: Session, vh_trn: str) -> bool:
        """Check if vihara has an active (approved) objection"""
        return (
            db.query(Objection)
            .filter(
                Objection.vh_trn == vh_trn,
                Objection.obj_status == ObjectionStatus.APPROVED,
                Objection.obj_is_deleted.is_(False)
            )
            .first()
        ) is not None

    def has_active_objection_by_ar_trn(self, db: Session, ar_trn: str) -> bool:
        """Check if arama has an active (approved) objection"""
        return (
            db.query(Objection)
            .filter(
                Objection.ar_trn == ar_trn,
                Objection.obj_status == ObjectionStatus.APPROVED,
                Objection.obj_is_deleted.is_(False)
            )
            .first()
        ) is not None

    def has_active_objection_by_dv_trn(self, db: Session, dv_trn: str) -> bool:
        """Check if devala has an active (approved) objection"""
        return (
            db.query(Objection)
            .filter(
                Objection.dv_trn == dv_trn,
                Objection.obj_status == ObjectionStatus.APPROVED,
                Objection.obj_is_deleted.is_(False)
            )
            .first()
        ) is not None

    def get_by_bh_regn(
        self, 
        db: Session, 
        bh_regn: str,
        status: Optional[ObjectionStatus] = None,
        ot_code: Optional[str] = None
    ) -> Optional[Objection]:
        """Get objection for bhikku"""
        query = db.query(Objection).filter(
            Objection.bh_regn == bh_regn,
            Objection.obj_is_deleted.is_(False)
        )
        
        if status:
            query = query.filter(Objection.obj_status == status)
        
        if ot_code:
            query = query.filter(Objection.ot_code == ot_code)
        
        return query.order_by(Objection.obj_submitted_at.desc()).first()

    def get_by_sil_regn(
        self, 
        db: Session, 
        sil_regn: str,
        status: Optional[ObjectionStatus] = None,
        ot_code: Optional[str] = None
    ) -> Optional[Objection]:
        """Get objection for silmatha"""
        query = db.query(Objection).filter(
            Objection.sil_regn == sil_regn,
            Objection.obj_is_deleted.is_(False)
        )
        
        if status:
            query = query.filter(Objection.obj_status == status)
        
        if ot_code:
            query = query.filter(Objection.ot_code == ot_code)
        
        return query.order_by(Objection.obj_submitted_at.desc()).first()

    def get_by_dbh_regn(
        self, 
        db: Session, 
        dbh_regn: str,
        status: Optional[ObjectionStatus] = None,
        ot_code: Optional[str] = None
    ) -> Optional[Objection]:
        """Get objection for high bhikku"""
        query = db.query(Objection).filter(
            Objection.dbh_regn == dbh_regn,
            Objection.obj_is_deleted.is_(False)
        )
        
        if status:
            query = query.filter(Objection.obj_status == status)
        
        if ot_code:
            query = query.filter(Objection.ot_code == ot_code)
        
        return query.order_by(Objection.obj_submitted_at.desc()).first()

    def has_active_objection_by_bh_regn(self, db: Session, bh_regn: str, ot_code: Optional[str] = None) -> bool:
        """Check if bhikku has an active (approved) objection"""
        query = db.query(Objection).filter(
            Objection.bh_regn == bh_regn,
            Objection.obj_status == ObjectionStatus.APPROVED,
            Objection.obj_is_deleted.is_(False)
        )
        
        if ot_code:
            query = query.filter(Objection.ot_code == ot_code)
        
        return query.first() is not None

    def has_active_objection_by_sil_regn(self, db: Session, sil_regn: str, ot_code: Optional[str] = None) -> bool:
        """Check if silmatha has an active (approved) objection"""
        query = db.query(Objection).filter(
            Objection.sil_regn == sil_regn,
            Objection.obj_status == ObjectionStatus.APPROVED,
            Objection.obj_is_deleted.is_(False)
        )
        
        if ot_code:
            query = query.filter(Objection.ot_code == ot_code)
        
        return query.first() is not None

    def has_active_objection_by_dbh_regn(self, db: Session, dbh_regn: str, ot_code: Optional[str] = None) -> bool:
        """Check if high bhikku has an active (approved) objection"""
        query = db.query(Objection).filter(
            Objection.dbh_regn == dbh_regn,
            Objection.obj_status == ObjectionStatus.APPROVED,
            Objection.obj_is_deleted.is_(False)
        )
        
        if ot_code:
            query = query.filter(Objection.ot_code == ot_code)
        
        return query.first() is not None

    def list(
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
    ) -> List[Objection]:
        """List objections with filters"""
        query = db.query(Objection).filter(Objection.obj_is_deleted.is_(False))

        if vh_trn:
            query = query.filter(Objection.vh_trn == vh_trn)
        
        if ar_trn:
            query = query.filter(Objection.ar_trn == ar_trn)
        
        if dv_trn:
            query = query.filter(Objection.dv_trn == dv_trn)
        
        if bh_regn:
            query = query.filter(Objection.bh_regn == bh_regn)
        
        if sil_regn:
            query = query.filter(Objection.sil_regn == sil_regn)
        
        if dbh_regn:
            query = query.filter(Objection.dbh_regn == dbh_regn)
        
        if status:
            query = query.filter(Objection.obj_status == status)
        
        # Global search across multiple fields
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Objection.vh_trn.ilike(search_pattern),
                    Objection.ar_trn.ilike(search_pattern),
                    Objection.dv_trn.ilike(search_pattern),
                    Objection.bh_regn.ilike(search_pattern),
                    Objection.sil_regn.ilike(search_pattern),
                    Objection.dbh_regn.ilike(search_pattern),
                    Objection.obj_reason.ilike(search_pattern),
                    Objection.obj_requester_name.ilike(search_pattern),
                    Objection.form_id.ilike(search_pattern)
                )
            )

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
        vh_trn: Optional[str] = None,
        ar_trn: Optional[str] = None,
        dv_trn: Optional[str] = None,
        bh_regn: Optional[str] = None,
        sil_regn: Optional[str] = None,
        dbh_regn: Optional[str] = None,
        status: Optional[ObjectionStatus] = None,
        search: Optional[str] = None
    ) -> int:
        """Count objections with filters"""
        query = db.query(Objection).filter(Objection.obj_is_deleted.is_(False))

        if vh_trn:
            query = query.filter(Objection.vh_trn == vh_trn)
        
        if ar_trn:
            query = query.filter(Objection.ar_trn == ar_trn)
        
        if dv_trn:
            query = query.filter(Objection.dv_trn == dv_trn)
        
        if bh_regn:
            query = query.filter(Objection.bh_regn == bh_regn)
        
        if sil_regn:
            query = query.filter(Objection.sil_regn == sil_regn)
        
        if dbh_regn:
            query = query.filter(Objection.dbh_regn == dbh_regn)
        
        if status:
            query = query.filter(Objection.obj_status == status)
        
        # Global search across multiple fields
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Objection.vh_trn.ilike(search_pattern),
                    Objection.ar_trn.ilike(search_pattern),
                    Objection.dv_trn.ilike(search_pattern),
                    Objection.bh_regn.ilike(search_pattern),
                    Objection.sil_regn.ilike(search_pattern),
                    Objection.dbh_regn.ilike(search_pattern),
                    Objection.obj_reason.ilike(search_pattern),
                    Objection.obj_requester_name.ilike(search_pattern),
                    Objection.form_id.ilike(search_pattern)
                )
            )

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
            vh_trn=data.vh_trn,
            ar_trn=data.ar_trn,
            dv_trn=data.dv_trn,
            bh_regn=data.bh_regn,
            sil_regn=data.sil_regn,
            dbh_regn=data.dbh_regn,
            ot_code=data.ot_code,
            obj_reason=data.obj_reason,
            form_id=data.form_id,
            obj_requester_name=data.obj_requester_name,
            obj_requester_contact=data.obj_requester_contact,
            obj_requester_id_num=data.obj_requester_id_num,
            obj_valid_from=data.obj_valid_from,
            obj_valid_until=data.obj_valid_until,
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
