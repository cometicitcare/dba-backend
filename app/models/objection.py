from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression
import enum

from app.db.base import Base


class ObjectionStatus(str, enum.Enum):
    """Status of objection"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class Objection(Base):
    """
    Objection table for managing restrictions on entities:
    1. REPRINT_RESTRICTION - Blocks reprint requests
    2. RESIDENCY_RESTRICTION - Blocks adding more residents
    
    Supports 6 entity types (only ONE should be set, enforced by check constraint):
    - vh_trn: Vihara TRN (starts with TRN)
    - ar_trn: Arama TRN (starts with ARN)
    - dv_trn: Devala TRN (starts with DVL)
    - bh_regn: Bhikku Registration Number (starts with BH)
    - sil_regn: Silmatha Registration Number (starts with SIL)
    - dbh_regn: High Bhikku Registration Number (starts with DBH/UPS)
    """
    __tablename__ = "objections"

    # Primary Key
    obj_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Entity Identifiers (only ONE should be set) - with Foreign Keys
    vh_trn = Column(String(20), ForeignKey("vihaddata.vh_trn", ondelete="CASCADE"), nullable=True, index=True, comment="Vihara TRN")
    ar_trn = Column(String(20), ForeignKey("aramadata.ar_trn", ondelete="CASCADE"), nullable=True, index=True, comment="Arama TRN")
    dv_trn = Column(String(20), ForeignKey("devaladata.dv_trn", ondelete="CASCADE"), nullable=True, index=True, comment="Devala TRN")
    bh_regn = Column(String(20), ForeignKey("bhikku_regist.br_regn", ondelete="CASCADE"), nullable=True, index=True, comment="Bhikku registration number")
    sil_regn = Column(String(20), ForeignKey("silmatha_regist.sil_regn", ondelete="CASCADE"), nullable=True, index=True, comment="Silmatha registration number")
    dbh_regn = Column(String(20), ForeignKey("direct_bhikku_high.dbh_regn", ondelete="CASCADE"), nullable=True, index=True, comment="High Bhikku registration number")
    
    # Objection Type Code - with Foreign Key
    ot_code = Column(String(50), ForeignKey("objection_types.ot_code", ondelete="RESTRICT"), nullable=False, index=True, comment="Objection type code (REPRINT_RESTRICTION, RESIDENCY_RESTRICTION)")
    
    # Form ID (if objection is related to a specific form)
    form_id = Column(String(50), nullable=True, index=True, comment="Related form ID/number")
    
    # Requester Information
    obj_requester_name = Column(String(200), nullable=True, comment="Name of the person making the request")
    obj_requester_contact = Column(String(20), nullable=True, comment="Contact number of requester")
    obj_requester_id_num = Column(String(20), nullable=True, comment="ID number of requester (NIC/Passport)")
    
    # Time Period
    obj_valid_from = Column(DateTime(timezone=True), nullable=True, comment="Objection validity start date")
    obj_valid_until = Column(DateTime(timezone=True), nullable=True, comment="Objection validity end date (null = indefinite)")
    
    # Check constraint: exactly one entity identifier must be set
    __table_args__ = (
        CheckConstraint(
            '(vh_trn IS NOT NULL AND ar_trn IS NULL AND dv_trn IS NULL AND bh_regn IS NULL AND sil_regn IS NULL AND dbh_regn IS NULL) OR '
            '(vh_trn IS NULL AND ar_trn IS NOT NULL AND dv_trn IS NULL AND bh_regn IS NULL AND sil_regn IS NULL AND dbh_regn IS NULL) OR '
            '(vh_trn IS NULL AND ar_trn IS NULL AND dv_trn IS NOT NULL AND bh_regn IS NULL AND sil_regn IS NULL AND dbh_regn IS NULL) OR '
            '(vh_trn IS NULL AND ar_trn IS NULL AND dv_trn IS NULL AND bh_regn IS NOT NULL AND sil_regn IS NULL AND dbh_regn IS NULL) OR '
            '(vh_trn IS NULL AND ar_trn IS NULL AND dv_trn IS NULL AND bh_regn IS NULL AND sil_regn IS NOT NULL AND dbh_regn IS NULL) OR '
            '(vh_trn IS NULL AND ar_trn IS NULL AND dv_trn IS NULL AND bh_regn IS NULL AND sil_regn IS NULL AND dbh_regn IS NOT NULL)',
            name='objection_one_entity_identifier_check'
        ),
    )
    
    # Objection Details
    obj_reason = Column(String(1000), nullable=False, comment="Reason for objection/restriction")
    obj_status = Column(
        Enum(ObjectionStatus), 
        nullable=False, 
        server_default="PENDING", 
        index=True,
        comment="Status of objection (PENDING, APPROVED, REJECTED, CANCELLED)"
    )
    
    # Workflow Fields
    obj_submitted_by = Column(String(25), comment="Username who submitted the objection")
    obj_submitted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Timestamp of submission")
    
    obj_approved_by = Column(String(25), comment="Username who approved the objection")
    obj_approved_at = Column(DateTime(timezone=True), comment="Timestamp of approval")
    
    obj_rejected_by = Column(String(25), comment="Username who rejected the objection")
    obj_rejected_at = Column(DateTime(timezone=True), comment="Timestamp of rejection")
    obj_rejection_reason = Column(String(500), comment="Reason for rejection")
    
    obj_cancelled_by = Column(String(25), comment="Username who cancelled the objection")
    obj_cancelled_at = Column(DateTime(timezone=True), comment="Timestamp of cancellation")
    obj_cancellation_reason = Column(String(500), comment="Reason for cancellation")
    
    # Audit Fields
    obj_is_deleted = Column(Boolean, nullable=False, server_default=expression.false(), comment="Soft delete flag")
    obj_created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Creation timestamp")
    obj_updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="Last update timestamp")
    obj_updated_by = Column(String(25), comment="Username who last updated")
    
    # Relationships (using ot_code as join)
    objection_type = relationship(
        "ObjectionType",
        foreign_keys="Objection.ot_code",
        primaryjoin="Objection.ot_code==ObjectionType.ot_code",
        back_populates="objections",
        viewonly=True
    )
