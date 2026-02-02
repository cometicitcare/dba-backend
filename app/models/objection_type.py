from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from app.db.base import Base


class ObjectionType(Base):
    """
    Objection types lookup table
    Defines different types/categories of objections
    """
    __tablename__ = "objection_types"

    # Primary Key
    ot_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Type Information
    ot_code = Column(String(50), nullable=False, unique=True, index=True, comment="Unique type code (e.g., REPRINT_RESTRICTION, RESIDENCY_RESTRICTION)")
    ot_name_en = Column(String(200), nullable=False, comment="Type name in English")
    ot_name_si = Column(String(200), comment="Type name in Sinhala")
    ot_name_ta = Column(String(200), comment="Type name in Tamil")
    ot_description = Column(String(500), comment="Description of this objection type")
    
    # Status
    ot_is_active = Column(Boolean, nullable=False, server_default=expression.true(), comment="Whether this type is active")
    
    # Audit Fields
    ot_is_deleted = Column(Boolean, nullable=False, server_default=expression.false(), comment="Soft delete flag")
    ot_created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Creation timestamp")
    ot_updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="Last update timestamp")
    ot_created_by = Column(String(25), comment="Username who created")
    ot_updated_by = Column(String(25), comment="Username who last updated")
    
    # Relationship (using ot_code as join)
    objections = relationship(
        "Objection",
        foreign_keys="Objection.ot_code",
        primaryjoin="ObjectionType.ot_code==foreign(Objection.ot_code)",
        back_populates="objection_type",
        viewonly=True
    )
