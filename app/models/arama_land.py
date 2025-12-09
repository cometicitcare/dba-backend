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


class AramaLand(Base):
    """Land records associated with arama"""
    __tablename__ = "arama_land"

    id = Column(Integer, primary_key=True, index=True)
    ar_id = Column(Integer, ForeignKey("aramadata.ar_id", ondelete="CASCADE"), nullable=False, index=True)
    
    serial_number = Column(Integer, nullable=False)
    plot_number = Column(String(100))
    survey_number = Column(String(100))
    title_number = Column(String(100))
    land_name = Column(String(200))
    village = Column(String(200))
    district = Column(String(100))
    extent = Column(String(100))
    extent_unit = Column(String(50))
    cultivation_description = Column(String(500))
    ownership_nature = Column(String(200))
    ownership_type = Column(String(200))
    deed_number = Column(String(100))
    title_registration_number = Column(String(100))
    tax_details = Column(String(500))
    land_occupants = Column(String(500))
    land_notes = Column(String(1000))
    
    is_deleted = Column(Boolean, nullable=False, server_default=expression.false())
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationship
    arama = relationship("AramaData", back_populates="arama_lands")
