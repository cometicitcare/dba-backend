from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from app.db.base import Base


class ResidentBhikkhu(Base):
    """Resident bhikkhus associated with vihara"""
    __tablename__ = "resident_bhikkhu"

    id = Column(Integer, primary_key=True, index=True)
    vh_id = Column(Integer, ForeignKey("vihaddata.vh_id", ondelete="CASCADE"), nullable=False, index=True)
    
    serial_number = Column(Integer, nullable=False)
    bhikkhu_name = Column(String(200))
    registration_number = Column(String(100))
    occupation_education = Column(String(500))
    
    is_deleted = Column(Boolean, nullable=False, server_default=expression.false())
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationship
    vihara = relationship("ViharaData", back_populates="resident_bhikkhus")
