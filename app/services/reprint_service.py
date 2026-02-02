# app/services/reprint_service.py
from datetime import datetime
from typing import List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session, noload

from app.models.bhikku import Bhikku
from app.models.bhikku_high import BhikkuHighRegist
from app.models.silmatha_regist import SilmathaRegist
from app.models.reprint_request import ReprintRequest
from app.schemas.reprint import (
    ReprintFlowStatus,
    ReprintRequestCreate,
    ReprintSubject,
    ReprintType,
)


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
            exists = db.query(BhikkuHighRegist).options(noload('*')).filter(BhikkuHighRegist.bhr_regn == regn, BhikkuHighRegist.bhr_is_deleted.is_(False)).first()
            if not exists:
                raise ValueError(f"High Bhikku record not found for regn: {regn}")
            entity.bhikku_high_regn = regn
        elif request_type == ReprintType.UPASAMPADA:
            exists = db.query(BhikkuHighRegist).options(noload('*')).filter(BhikkuHighRegist.bhr_regn == regn, BhikkuHighRegist.bhr_is_deleted.is_(False)).first()
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
        regn: Optional[str] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        search_key: Optional[str] = None,
    ) -> tuple[List[ReprintRequest], int]:
        query = db.query(ReprintRequest)
        if flow_status:
            query = query.filter(ReprintRequest.flow_status == flow_status.value)
        if request_type:
            query = query.filter(ReprintRequest.request_type == request_type.value)
        if regn:
            regn_clean = regn.strip().upper()
            if regn_clean:
                query = query.filter(
                    or_(
                        ReprintRequest.bhikku_regn == regn_clean,
                        ReprintRequest.silmatha_regn == regn_clean,
                        ReprintRequest.bhikku_high_regn == regn_clean,
                        ReprintRequest.upasampada_regn == regn_clean,
                    )
                )
        if search_key:
            pattern = f"%{search_key.strip()}%"
            query = query.outerjoin(
                Bhikku, ReprintRequest.bhikku_regn == Bhikku.br_regn
            ).outerjoin(
                SilmathaRegist, ReprintRequest.silmatha_regn == SilmathaRegist.sil_regn
            ).outerjoin(
                BhikkuHighRegist, 
                or_(
                    ReprintRequest.bhikku_high_regn == BhikkuHighRegist.bhr_regn,
                    ReprintRequest.upasampada_regn == BhikkuHighRegist.bhr_regn
                )
            ).filter(
                or_(
                    ReprintRequest.form_no.ilike(pattern),
                    ReprintRequest.request_reason.ilike(pattern),
                    ReprintRequest.remarks.ilike(pattern),
                    ReprintRequest.bhikku_regn.ilike(pattern),
                    ReprintRequest.silmatha_regn.ilike(pattern),
                    ReprintRequest.bhikku_high_regn.ilike(pattern),
                    ReprintRequest.upasampada_regn.ilike(pattern),
                    Bhikku.br_mahananame.ilike(pattern),
                    Bhikku.br_gihiname.ilike(pattern),
                    SilmathaRegist.sil_mahananame.ilike(pattern),
                    SilmathaRegist.sil_gihiname.ilike(pattern),
                    BhikkuHighRegist.bhr_assumed_name.ilike(pattern),
                )
            )

        total_records = query.count()
        page_num = page or 1
        page_size = limit or 50
        offset = max((page_num - 1) * page_size, 0)

        records = (
            query.order_by(ReprintRequest.requested_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )
        return self._attach_subjects(db, records), total_records

    def get_by_id(self, db: Session, *, request_id: int) -> Optional[ReprintRequest]:
        record = db.get(ReprintRequest, request_id)
        if not record:
            return None
        enriched = self._attach_subjects(db, [record])
        self._attach_qr_details(db, enriched)
        return enriched[0] if enriched else None

    def get_by_identifier(
        self, db: Session, *, identifier: Optional[object]
    ) -> Optional[ReprintRequest]:
        """
        Fetch a reprint request by numeric id or by registration number (BH/SI/UP prefixes).
        When a registration number is supplied, the most recent matching request is returned.
        """
        if identifier is None:
            return None

        # Handle registration numbers (non-numeric strings)
        if isinstance(identifier, str):
            stripped = identifier.strip()
            if not stripped:
                return None
            if not stripped.isdigit():
                regn = stripped.upper()
                record = (
                    db.query(ReprintRequest)
                    .filter(
                        or_(
                            ReprintRequest.bhikku_regn == regn,
                            ReprintRequest.silmatha_regn == regn,
                            ReprintRequest.bhikku_high_regn == regn,
                            ReprintRequest.upasampada_regn == regn,
                        )
                    )
                    .order_by(ReprintRequest.requested_at.desc())
                    .first()
                )
                if not record:
                    return None
                enriched = self._attach_subjects(db, [record])
                self._attach_qr_details(db, enriched)
                return enriched[0] if enriched else None

        # Fallback to numeric id lookup
        try:
            numeric_id = int(identifier)
        except (TypeError, ValueError):
            return None

        return self.get_by_id(db, request_id=numeric_id)

    def delete(self, db: Session, *, request_id: int) -> None:
        entity = db.get(ReprintRequest, request_id)
        if not entity:
            raise ValueError(f"Reprint request {request_id} not found.")
        db.delete(entity)
        db.commit()

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _attach_subjects(self, db: Session, records: List[ReprintRequest]) -> List[ReprintRequest]:
        if not records:
            return records

        bh_regns = {r.bhikku_regn for r in records if r.bhikku_regn}
        sil_regns = {r.silmatha_regn for r in records if r.silmatha_regn}
        high_regns = {r.bhikku_high_regn for r in records if r.bhikku_high_regn}
        upa_regns = {r.upasampada_regn for r in records if r.upasampada_regn}
        high_regns.update(upa_regns)

        bh_map = {}
        if bh_regns:
            bh_rows = (
                db.query(Bhikku)
                .filter(Bhikku.br_regn.in_(bh_regns), Bhikku.br_is_deleted.is_(False))
                .all()
            )
            for row in bh_rows:
                bh_map[row.br_regn] = self._make_subject_from_bhikku(row)

        sil_map = {}
        if sil_regns:
            sil_rows = (
                db.query(SilmathaRegist)
                .filter(SilmathaRegist.sil_regn.in_(sil_regns), SilmathaRegist.sil_is_deleted.is_(False))
                .all()
            )
            for row in sil_rows:
                sil_map[row.sil_regn] = self._make_subject_from_silmatha(row)

        high_map = {}
        if high_regns:
            high_rows = (
                db.query(BhikkuHighRegist)
                .options(noload('*'))
                .filter(BhikkuHighRegist.bhr_regn.in_(high_regns), BhikkuHighRegist.bhr_is_deleted.is_(False))
                .all()
            )
            for row in high_rows:
                high_map[row.bhr_regn] = self._make_subject_from_high(row)

        for r in records:
            subject = None
            if r.bhikku_regn and r.bhikku_regn in bh_map:
                subject = bh_map[r.bhikku_regn]
            elif r.silmatha_regn and r.silmatha_regn in sil_map:
                subject = sil_map[r.silmatha_regn]
            elif r.bhikku_high_regn and r.bhikku_high_regn in high_map:
                subject = high_map[r.bhikku_high_regn]
            elif r.upasampada_regn and r.upasampada_regn in high_map:
                subject = high_map[r.upasampada_regn]

            if subject:
                setattr(r, "subject", subject)

            primary_regn = (
                r.bhikku_regn
                or r.silmatha_regn
                or r.bhikku_high_regn
                or r.upasampada_regn
            )
            if primary_regn:
                setattr(r, "regn", primary_regn)

        return records

    def _make_subject_from_bhikku(self, row: Bhikku) -> ReprintSubject:
        address = row.br_fathrsaddrs or row.br_residence_at_declaration
        return ReprintSubject(
            name=row.br_mahananame or row.br_gihiname,
            gihi_name=row.br_gihiname,
            address=address,
            phone=row.br_mobile,
            dob=row.br_dofb,
            regn=row.br_regn,
            type=ReprintType.BHIKKU,
        )

    def _make_subject_from_silmatha(self, row: SilmathaRegist) -> ReprintSubject:
        address = row.sil_fathrsaddrs
        return ReprintSubject(
            name=getattr(row, "sil_mahananame", None) or row.sil_gihiname,
            gihi_name=row.sil_gihiname,
            address=address,
            phone=row.sil_mobile,
            dob=row.sil_dofb,
            regn=row.sil_regn,
            type=ReprintType.SILMATHA,
        )

    def _make_subject_from_high(self, row: BhikkuHighRegist) -> ReprintSubject:
        return ReprintSubject(
            name=row.bhr_assumed_name,
            gihi_name=None,
            address=row.bhr_declaration_residence_address,
            phone=None,
            dob=None,
            regn=row.bhr_regn,
            type=ReprintType.HIGH_BHIKKU,
        )

    def _qr_lookup(self, db: Session, identifier: Optional[str], record_type: Optional[str] = None) -> Optional[list]:
        """Proxy to bhikku_service QR search for reuse across endpoints."""
        if not identifier:
            return None
        try:
            from app.services.bhikku_service import bhikku_service
        except Exception:
            return None
        return bhikku_service.get_qr_search_details(
            db=db,
            record_id=identifier,
            record_type=record_type,
        )

    def _resolve_record_type(self, request_type: Optional[object]) -> Optional[str]:
        """Map stored request type (enum or string) to qr_search record_type values."""
        if isinstance(request_type, ReprintType):
            value = request_type.value
        else:
            value = request_type

        type_map = {
            ReprintType.BHIKKU.value: "bhikku",
            ReprintType.SILMATHA.value: "silmatha",
            ReprintType.HIGH_BHIKKU.value: "bhikku_high",
            ReprintType.UPASAMPADA.value: "bhikku_high",
        }
        return type_map.get(value)

    def _extract_regn_from_record(self, record: Optional[ReprintRequest]) -> Optional[str]:
        if not record:
            return None
        return (
            record.bhikku_regn
            or record.silmatha_regn
            or record.bhikku_high_regn
            or record.upasampada_regn
        )

    def resolve_qr_details(
        self,
        db: Session,
        *,
        record: Optional[ReprintRequest],
        identifier: Optional[object],
    ) -> Optional[list]:
        """
        Produce QR-style payload for reprint lookups.
        Prefers data already attached to the record, then falls back to QR search by regn/identifier.
        """
        if record:
            qr_details = getattr(record, "qr_details", None)
            if qr_details:
                return qr_details

            regn = self._extract_regn_from_record(record)
            if regn:
                qr_details = self._qr_lookup(
                    db,
                    regn,
                    record_type=self._resolve_record_type(record.request_type),
                )
                if qr_details:
                    return qr_details

            # Attempt using subject.regn if available (defensive)
            subject = getattr(record, "subject", None)
            if subject and getattr(subject, "regn", None):
                qr_details = self._qr_lookup(
                    db,
                    subject.regn,
                    record_type=self._resolve_record_type(record.request_type),
                )
                if qr_details:
                    return qr_details

        # Final fallback: behave like /qr_search using provided identifier (string only)
        if isinstance(identifier, str):
            cleaned = identifier.strip()
            if cleaned:
                return self._qr_lookup(db, cleaned)
        return None

    def get_scanned_document_path(
        self,
        db: Session,
        *,
        regn: str,
    ) -> dict:
        """
        Return scanned document path and base64 data for a given registration number, auto-detecting type.
        """
        import base64
        import os
        from pathlib import Path
        
        regn_clean = (regn or "").strip().upper()
        if not regn_clean:
            raise ValueError("regn is required")

        req_type = self._detect_type_from_regn(regn_clean)

        if req_type == ReprintType.BHIKKU:
            entity = (
                db.query(Bhikku)
                .filter(Bhikku.br_regn == regn_clean, Bhikku.br_is_deleted.is_(False))
                .first()
            )
            if not entity:
                raise ValueError(f"Bhikku record not found for regn: {regn_clean}")
            path = entity.br_scanned_document_path
        elif req_type in (ReprintType.HIGH_BHIKKU, ReprintType.UPASAMPADA):
            entity = (
                db.query(BhikkuHighRegist)
                .options(noload('*'))
                .filter(
                    BhikkuHighRegist.bhr_regn == regn_clean,
                    BhikkuHighRegist.bhr_is_deleted.is_(False),
                )
                .first()
            )
            if not entity:
                raise ValueError(f"High Bhikku record not found for regn: {regn_clean}")
            path = entity.bhr_scanned_document_path
        elif req_type == ReprintType.SILMATHA:
            entity = (
                db.query(SilmathaRegist)
                .filter(
                    SilmathaRegist.sil_regn == regn_clean,
                    SilmathaRegist.sil_is_deleted.is_(False),
                )
                .first()
            )
            if not entity:
                raise ValueError(f"Silmatha record not found for regn: {regn_clean}")
            path = entity.sil_scanned_document_path
        else:
            raise ValueError(f"Unsupported type for regn: {regn_clean}")

        # Read file and encode to base64
        base64_data = None
        if path:
            try:
                # Import settings
                from app.core.config import settings
                import logging
                
                logger = logging.getLogger(__name__)
                
                # Remove leading /storage/ prefix if present (paths are stored as /storage/relative/path)
                relative_path = path
                if relative_path.startswith("/storage/"):
                    relative_path = relative_path[9:]  # Remove "/storage/" prefix
                
                # Construct full file path using the base storage directory
                file_path = Path(settings.STORAGE_DIR) / relative_path
                
                logger.info(f"Attempting to read file from: {file_path}")
                
                if file_path.exists() and file_path.is_file():
                    with open(file_path, "rb") as f:
                        file_content = f.read()
                        base64_data = base64.b64encode(file_content).decode("utf-8")
                    logger.info(f"Successfully encoded file to base64, size: {len(base64_data)} chars")
                else:
                    # Log for debugging but don't fail
                    logger.warning(f"File not found at {file_path}. File may be on production server.")
            except Exception as e:
                # Log the error but don't fail the request
                # The path will still be returned even if base64 encoding fails
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to encode file to base64: {e}", exc_info=True)

        return {
            "regn": regn_clean,
            "request_type": req_type,
            "scanned_document_path": path,
            "base64_data": base64_data,
        }

    def _attach_qr_details(self, db: Session, records: List[ReprintRequest]) -> None:
        """Populate qr_details field using the existing QR search formatter."""
        if not records:
            return

        try:
            from app.services.bhikku_service import bhikku_service
        except Exception:
            return

        type_map = {
            ReprintType.BHIKKU.value: "bhikku",
            ReprintType.SILMATHA.value: "silmatha",
            ReprintType.HIGH_BHIKKU.value: "bhikku_high",
            ReprintType.UPASAMPADA.value: "bhikku_high",
        }

        for record in records:
            regn = (
                record.bhikku_regn
                or record.silmatha_regn
                or record.bhikku_high_regn
                or record.upasampada_regn
            )
            if not regn:
                continue

            record_type = type_map.get(record.request_type)
            details = bhikku_service.get_qr_search_details(
                db=db, record_id=regn, record_type=record_type
            )
            if details:
                setattr(record, "qr_details", details)


reprint_service = ReprintService()
