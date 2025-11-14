# app/models/bhikku_id_card_workflow_flag.py
from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    TIMESTAMP,
    Enum as SQLEnum,
    text,
)
from sqlalchemy.sql import func
from enum import Enum

from app.db.base import Base


class IDCardWorkflowFlagEnum(str, Enum):
    """Workflow status flags for bhikku ID card process"""
    PENDING = "pending"  # New data entry submitted
    APPROVED = "approved"  # Officer approved the record
    REJECTED = "rejected"  # Officer rejected the record
    PRINTED = "printed"  # Card has been printed
    SCANNED = "scanned"  # Printed card has been scanned
    COMPLETED = "completed"  # Process complete and delivered


class BhikkuIDCardWorkflowFlag(Base):
    """Track workflow status and history for bhikku ID card registrations"""
    __tablename__ = "bhikku_id_card_workflow_flags"

    bicwf_id = Column(Integer, primary_key=True, index=True)
    bicwf_bhikku_id_card_id = Column(
        Integer,
        ForeignKey("bhikku_id_card.bic_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    bicwf_bhikku_id = Column(
        Integer,
        ForeignKey("bhikku_regist.br_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    bicwf_current_flag = Column(
        SQLEnum(IDCardWorkflowFlagEnum),
        nullable=False,
        default=IDCardWorkflowFlagEnum.PENDING,
        index=True
    )
    
    # Workflow transition tracking
    bicwf_pending_date = Column(TIMESTAMP)  # When marked as pending
    bicwf_approval_date = Column(TIMESTAMP)  # When approved/rejected
    bicwf_approval_by = Column(String(25))  # Officer ID who approved/rejected
    bicwf_approval_notes = Column(String(500))  # Approval/rejection notes
    
    bicwf_printing_date = Column(TIMESTAMP)  # When sent to printing
    bicwf_print_by = Column(String(25))  # Printing officer ID
    
    bicwf_scan_date = Column(TIMESTAMP)  # When scanned
    bicwf_scan_by = Column(String(25))  # Scanning officer ID
    
    bicwf_completion_date = Column(TIMESTAMP)  # When completed
    bicwf_completed_by = Column(String(25))  # Completion officer ID
    
    # Audit Fields
    bicwf_created_at = Column(TIMESTAMP, server_default=func.now())
    bicwf_updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    bicwf_created_by = Column(
        String(25),
        ForeignKey("user_accounts.ua_user_id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True
    )
    bicwf_updated_by = Column(
        String(25),
        ForeignKey("user_accounts.ua_user_id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True
    )
    bicwf_is_deleted = Column(Boolean, nullable=False, server_default=text("false"))
    bicwf_version_number = Column(Integer, nullable=True, server_default=text("1"))
