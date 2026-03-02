# app/models/audit_log.py
from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Column,
    ForeignKey,
    String,
    TIMESTAMP,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.sql import func

from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    al_id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )
    al_table_name = Column(String(50), nullable=False)
    al_record_id = Column(String(50), nullable=False)
    al_operation = Column(String(10), nullable=False)
    al_old_values = Column(JSONB, nullable=True)
    al_new_values = Column(JSONB, nullable=True)
    al_changed_fields = Column(ARRAY(String), nullable=True)
    al_user_id = Column(
        String(10),
        ForeignKey("user_accounts.ua_user_id", ondelete="RESTRICT"),
        nullable=True,
    )
    al_session_id = Column(String(100), nullable=True)
    al_ip_address = Column(String(45), nullable=True)
    al_user_agent = Column(String(500), nullable=True)
    al_timestamp = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    al_transaction_id = Column(String(100), nullable=True)

    def __repr__(self) -> str:
        return (
            f"<AuditLog(table={self.al_table_name!r}, record={self.al_record_id!r}, "
            f"operation={self.al_operation!r})>"
        )
