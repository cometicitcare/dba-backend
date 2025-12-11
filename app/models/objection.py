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
    Objection table for restricting resident bhikkus/silmathas addition
    to vihara, arama, or devala.
    
    Only ONE of vh_id, ar_id, or dv_id should be set (enforced by check constraint).
    Entity type is determined by which FK is populated:
    - vh_id: Vihara (TRN starts with TRN)
    - ar_id: Arama (TRN starts with ARN)
    - dv_id: Devala (TRN starts with DVL)
    """
    __tablename__ = "objections"

    # Primary Key
    obj_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Entity Foreign Keys (only ONE should be set)
    vh_id = Column(Integer, ForeignKey("vihaddata.vh_id"), nullable=True, index=True, comment="Foreign key to vihara (if objection is for vihara)")
    ar_id = Column(Integer, ForeignKey("aramadata.ar_id"), nullable=True, index=True, comment="Foreign key to arama (if objection is for arama)")
    dv_id = Column(Integer, ForeignKey("devaladata.dv_id"), nullable=True, index=True, comment="Foreign key to devala (if objection is for devala)")
    
    # Objection Type (Foreign Key)
    obj_type_id = Column(Integer, ForeignKey("objection_types.ot_id"), nullable=False, index=True, comment="Foreign key to objection_types table")
    
    # Check constraint: exactly one entity FK must be set
    __table_args__ = (
        CheckConstraint(
            '(vh_id IS NOT NULL AND ar_id IS NULL AND dv_id IS NULL) OR '
            '(vh_id IS NULL AND ar_id IS NOT NULL AND dv_id IS NULL) OR '
            '(vh_id IS NULL AND ar_id IS NULL AND dv_id IS NOT NULL)',
            name='objection_one_entity_check'
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
    
    # Relationships
    objection_type = relationship("ObjectionType", back_populates="objections")
    vihara = relationship("ViharaData", foreign_keys=[vh_id])
    arama = relationship("AramaData", foreign_keys=[ar_id])
    devala = relationship("DevalaData", foreign_keys=[dv_id])
