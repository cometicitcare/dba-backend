from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Integer,
    String,
    func,
    text,
)
from sqlalchemy.sql import expression

from app.db.base import Base


class ViharaData(Base):
    __tablename__ = "vihaddata"

    vh_id = Column(Integer, primary_key=True, index=True)
    vh_trn = Column(String(10), nullable=False, index=True, unique=True)
    vh_vname = Column(String(200))
    vh_addrs = Column(String(200))
    vh_mobile = Column(String(10), nullable=False)
    vh_whtapp = Column(String(10), nullable=False)
    vh_email = Column(String(200), nullable=False, index=True, unique=True)
    vh_typ = Column(String(10), nullable=False)
    vh_gndiv = Column(String(10), nullable=False)
    vh_fmlycnt = Column(Integer)
    vh_bgndate = Column(Date)
    vh_ownercd = Column(String(12), nullable=False)
    vh_parshawa = Column(String(10), nullable=False)
    vh_ssbmcode = Column(String(10))
    vh_syojakarmakrs = Column(String(100))
    vh_syojakarmdate = Column(Date)
    vh_landownrship = Column(String(150))
    vh_pralename = Column(String(50))
    vh_pralesigdate = Column(Date)
    vh_bacgrecmn = Column(String(100))
    vh_bacgrcmdate = Column(Date)
    vh_minissecrsigdate = Column(Date)
    vh_minissecrmrks = Column(String(200))
    vh_ssbmsigdate = Column(Date)
    
    # Document Storage
    vh_scanned_document_path = Column(String(500))
    
    # Workflow Fields (following bhikku_regist pattern)
    vh_workflow_status = Column(String(20), server_default=text("'PENDING'"), nullable=False, index=True)
    vh_approval_status = Column(String(20))
    vh_approved_by = Column(String(25))
    vh_approved_at = Column(DateTime(timezone=True))
    vh_rejected_by = Column(String(25))
    vh_rejected_at = Column(DateTime(timezone=True))
    vh_rejection_reason = Column(String(500))
    vh_printed_at = Column(DateTime(timezone=True))
    vh_printed_by = Column(String(25))
    vh_scanned_at = Column(DateTime(timezone=True))
    vh_scanned_by = Column(String(25))
    
    vh_version = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    vh_is_deleted = Column(Boolean, nullable=False, server_default=expression.false())
    vh_created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    vh_updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    vh_created_by = Column(String(25))
    vh_updated_by = Column(String(25))
    vh_version_number = Column(Integer, nullable=False, server_default="1")
