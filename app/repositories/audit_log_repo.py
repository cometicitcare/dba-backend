# app/repositories/audit_log_repo.py
from __future__ import annotations

from typing import Optional, Sequence, Tuple

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogCreate, AuditLogRequestPayload, AuditLogUpdate


class AuditLogRepository:
    """Data access utilities for the audit_log table."""

    def get(self, db: Session, al_id: int) -> Optional[AuditLog]:
        return (
            db.query(AuditLog)
            .filter(AuditLog.al_id == al_id)
            .first()
        )

    def create(self, db: Session, data: AuditLogCreate) -> AuditLog:
        entity = AuditLog(**data.model_dump())
        db.add(entity)
        db.flush()
        return entity

    def update(self, db: Session, entity: AuditLog, data: AuditLogUpdate) -> AuditLog:
        payload = data.model_dump(exclude_unset=True)
        for key, value in payload.items():
            setattr(entity, key, value)
        db.flush()
        return entity

    def delete(self, db: Session, entity: AuditLog) -> None:
        db.delete(entity)
        db.flush()

    def list(
        self,
        db: Session,
        payload: AuditLogRequestPayload,
    ) -> Tuple[Sequence[AuditLog], int]:
        query = db.query(AuditLog)

        if payload.al_id:
            query = query.filter(AuditLog.al_id == payload.al_id)
        if payload.al_table_name:
            query = query.filter(AuditLog.al_table_name == payload.al_table_name)
        if payload.al_record_id:
            query = query.filter(AuditLog.al_record_id == payload.al_record_id)
        if payload.al_operation:
            query = query.filter(AuditLog.al_operation == payload.al_operation)
        if payload.al_user_id:
            query = query.filter(AuditLog.al_user_id == payload.al_user_id)
        if payload.al_transaction_id:
            query = query.filter(
                AuditLog.al_transaction_id == payload.al_transaction_id
            )
        if payload.created_from and payload.created_to:
            query = query.filter(
                and_(
                    AuditLog.al_timestamp >= payload.created_from,
                    AuditLog.al_timestamp <= payload.created_to,
                )
            )
        elif payload.created_from:
            query = query.filter(AuditLog.al_timestamp >= payload.created_from)
        elif payload.created_to:
            query = query.filter(AuditLog.al_timestamp <= payload.created_to)

        if payload.search:
            pattern = f"%{payload.search}%"
            query = query.filter(
                or_(
                    AuditLog.al_table_name.ilike(pattern),
                    AuditLog.al_record_id.ilike(pattern),
                    AuditLog.al_operation.ilike(pattern),
                    AuditLog.al_user_id.ilike(pattern),
                    AuditLog.al_session_id.ilike(pattern),
                    AuditLog.al_transaction_id.ilike(pattern),
                )
            )

        total = query.with_entities(func.count(AuditLog.al_id)).scalar() or 0

        page = payload.page if payload.page and payload.page > 0 else 1
        skip = payload.skip if payload.page is None else max(0, (page - 1) * payload.limit)

        records = (
            query.order_by(AuditLog.al_timestamp.desc())
            .offset(skip)
            .limit(payload.limit)
            .all()
        )
        return records, int(total)


audit_log_repo = AuditLogRepository()

