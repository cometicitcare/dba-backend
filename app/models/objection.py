from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Integer,
    String,
    func,
)
from sqlalchemy.sql import expression
import enum

from app.db.base import Base


class EntityType(str, enum.Enum):
    """Type of entity for objection"""
    VIHARA = "VIHARA"
    ARAMA = "ARAMA"
    DEVALA = "DEVALA"


class ObjectionStatus(str, enum.Enum):
    """Status of objection"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class Objection(Base):
    """
    Objection table for restricting resident bhikkus/silmathas addition
    to vihara, arama, or devala
    """
    __tablename__ = "objections"

    # Primary Key
    obj_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Entity Information
    obj_entity_type = Column(Enum(EntityType), nullable=False, index=True, comment="Type of entity (VIHARA, ARAMA, DEVALA)")
    obj_entity_trn = Column(String(50), nullable=False, index=True, comment="TRN of the vihara/arama/devala")
    obj_entity_name = Column(String(200), comment="Name of the entity for reference")
    
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
