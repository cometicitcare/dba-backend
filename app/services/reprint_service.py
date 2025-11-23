# app/services/reprint_service.py
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.bhikku import Bhikku
from app.models.bhikku_high import BhikkuHighRegist
from app.models.silmatha_regist import SilmathaRegist
from app.models.reprint_request import ReprintRequest
from app.schemas.reprint import ReprintFlowStatus, ReprintRequestCreate, ReprintType


class ReprintService:
    """Central handler for reprint requests across bhikku, high bhikku, and upasampada records."""

    def _detect_type_from_regn(self, regn: str) -> ReprintType:
        upper = (regn or "").upper()
        if upper.startswith("BH"):
            return ReprintType.BHIKKU
        if upper.startswith("SI"):
            return ReprintType.SILMATHA
        if upper.startswith("UP"):
            return ReprintType.HIGH_BHIKKU
        raise ValueError(f"Cannot auto-detect request type from regn '{regn}'. Expected prefixes: BH, SI, UP.")

    def _attach_target(self, db: Session, entity: ReprintRequest, request_type: ReprintType, regn: str) -> None:
        if request_type == ReprintType.BHIKKU:
            exists = db.query(Bhikku).filter(Bhikku.br_regn == regn, Bhikku.br_is_deleted.is_(False)).first()
            if not exists:
                raise ValueError(f"Bhikku record not found for regn: {regn}")
            entity.bhikku_regn = regn
        elif request_type == ReprintType.HIGH_BHIKKU:
            exists = db.query(BhikkuHighRegist).filter(BhikkuHighRegist.bhr_regn == regn, BhikkuHighRegist.bhr_is_deleted.is_(False)).first()
            if not exists:
                raise ValueError(f"High Bhikku record not found for regn: {regn}")
            entity.bhikku_high_regn = regn
        elif request_type == ReprintType.UPASAMPADA:
            exists = db.query(BhikkuHighRegist).filter(BhikkuHighRegist.bhr_regn == regn, BhikkuHighRegist.bhr_is_deleted.is_(False)).first()
            if not exists:
                raise ValueError(f"Upasampada record not found for regn: {regn}")
            entity.upasampada_regn = regn
        elif request_type == ReprintType.SILMATHA:
            exists = db.query(SilmathaRegist).filter(SilmathaRegist.sil_regn == regn, SilmathaRegist.sil_is_deleted.is_(False)).first()
            if not exists:
                raise ValueError(f"Silmatha record not found for regn: {regn}")
            entity.silmatha_regn = regn
        else:
            raise ValueError(f"Unsupported request_type: {request_type}")

    def create_request(
        self,
        db: Session,
        *,
        payload: ReprintRequestCreate,
        actor_id: Optional[str],
    ) -> ReprintRequest:
        auto_type = self._detect_type_from_regn(payload.regn)
        chosen_type = payload.request_type or auto_type
        if payload.request_type and payload.request_type != auto_type:
            raise ValueError(
                f"request_type '{payload.request_type.value}' does not match regn prefix-derived type '{auto_type.value}'"
            )

        entity = ReprintRequest(
            request_type=chosen_type.value,
            form_no=payload.form_no,
            request_reason=payload.request_reason,
            amount=payload.amount,
            remarks=payload.remarks,
            flow_status=ReprintFlowStatus.PENDING.value,
            requested_by=actor_id,
            requested_at=datetime.utcnow(),
        )

        self._attach_target(db, entity, chosen_type, payload.regn)

        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def approve(
        self,
        db: Session,
        *,
        request_id: int,
        actor_id: Optional[str],
    ) -> ReprintRequest:
        entity = db.get(ReprintRequest, request_id)
        if not entity:
            raise ValueError(f"Reprint request {request_id} not found.")
        if entity.flow_status != ReprintFlowStatus.PENDING.value:
            raise ValueError(f"Cannot approve a request that is not PENDING (current: {entity.flow_status}).")

        entity.flow_status = ReprintFlowStatus.APPROVED.value
        entity.approved_by = actor_id
        entity.approved_at = datetime.utcnow()
        entity.rejected_by = None
        entity.rejected_at = None
        entity.rejection_reason = None
        db.commit()
        db.refresh(entity)
        return entity

    def reject(
        self,
        db: Session,
        *,
        request_id: int,
        actor_id: Optional[str],
        rejection_reason: str,
    ) -> ReprintRequest:
        entity = db.get(ReprintRequest, request_id)
        if not entity:
            raise ValueError(f"Reprint request {request_id} not found.")
        if entity.flow_status != ReprintFlowStatus.PENDING.value:
            raise ValueError(f"Cannot reject a request that is not PENDING (current: {entity.flow_status}).")

        entity.flow_status = ReprintFlowStatus.REJECTED.value
        entity.rejected_by = actor_id
        entity.rejected_at = datetime.utcnow()
        entity.rejection_reason = rejection_reason
        db.commit()
        db.refresh(entity)
        return entity

    def mark_printed(
        self,
        db: Session,
        *,
        request_id: int,
        actor_id: Optional[str],
    ) -> ReprintRequest:
        entity = db.get(ReprintRequest, request_id)
        if not entity:
            raise ValueError(f"Reprint request {request_id} not found.")
        if entity.flow_status != ReprintFlowStatus.APPROVED.value:
            raise ValueError(f"Cannot mark printed unless status is APPROVED (current: {entity.flow_status}).")

        now_ts = datetime.utcnow()
        entity.flow_status = ReprintFlowStatus.COMPLETED.value
        entity.printed_by = actor_id
        entity.printed_at = now_ts
        entity.completed_by = actor_id
        entity.completed_at = now_ts
        db.commit()
        db.refresh(entity)
        return entity

    def list_requests(
        self,
        db: Session,
        *,
        flow_status: Optional[ReprintFlowStatus] = None,
        request_type: Optional[ReprintType] = None,
    ) -> List[ReprintRequest]:
        query = db.query(ReprintRequest)
        if flow_status:
            query = query.filter(ReprintRequest.flow_status == flow_status.value)
        if request_type:
            query = query.filter(ReprintRequest.request_type == request_type.value)
        return query.order_by(ReprintRequest.requested_at.desc()).all()

    def get_by_id(self, db: Session, *, request_id: int) -> Optional[ReprintRequest]:
        return db.get(ReprintRequest, request_id)

    def delete(self, db: Session, *, request_id: int) -> None:
        entity = db.get(ReprintRequest, request_id)
        if not entity:
            raise ValueError(f"Reprint request {request_id} not found.")
        db.delete(entity)
        db.commit()


reprint_service = ReprintService()
