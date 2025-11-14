# app/models/bhikku_workflow_flag.py
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


class WorkflowFlagEnum(str, Enum):
    """Workflow status flags for bhikku registration process"""
    PENDING = "pending"  # New data entry submitted
    APPROVED = "approved"  # Officer approved the record
    REJECTED = "rejected"  # Officer rejected the record
    PRINTED = "printed"  # Form has been printed
    SCANNED = "scanned"  # Printed form has been scanned
    COMPLETED = "completed"  # Process complete and delivered


class BhikkuWorkflowFlag(Base):
    """Track workflow status and history for bhikku registrations"""
    __tablename__ = "bhikku_workflow_flags"

    bwf_id = Column(Integer, primary_key=True, index=True)
    bwf_bhikku_id = Column(
        Integer,
        ForeignKey("bhikku_regist.br_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    bwf_bhikku_regn = Column(String(20), nullable=False, index=True)
    bwf_current_flag = Column(
        SQLEnum(WorkflowFlagEnum),
        nullable=False,
        default=WorkflowFlagEnum.PENDING,
        index=True
    )
    
    # Workflow transition tracking
    bwf_pending_date = Column(TIMESTAMP)  # When marked as pending
    bwf_approval_date = Column(TIMESTAMP)  # When approved/rejected
    bwf_approval_by = Column(String(25))  # Officer ID who approved/rejected
    bwf_approval_notes = Column(String(500))  # Approval/rejection notes
    
    bwf_printing_date = Column(TIMESTAMP)  # When sent to printing
    bwf_print_by = Column(String(25))  # Printing officer ID
    
    bwf_scan_date = Column(TIMESTAMP)  # When scanned
    bwf_scan_by = Column(String(25))  # Scanning officer ID
    
    bwf_completion_date = Column(TIMESTAMP)  # When completed
    bwf_completed_by = Column(String(25))  # Completion officer ID
    
    # Audit Fields
    bwf_created_at = Column(TIMESTAMP, server_default=func.now())
    bwf_updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    bwf_created_by = Column(
        String(25),
        ForeignKey("user_accounts.ua_user_id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True
    )
    bwf_updated_by = Column(
        String(25),
        ForeignKey("user_accounts.ua_user_id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True
    )
    bwf_is_deleted = Column(Boolean, nullable=False, server_default=text("false"))
    bwf_version_number = Column(Integer, nullable=True, server_default=text("1"))
