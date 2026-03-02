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


class DevalaLand(Base):
    """Land records associated with devala"""
    __tablename__ = "devala_land"

    id = Column(Integer, primary_key=True, index=True)
    dv_id = Column(Integer, ForeignKey("devaladata.dv_id", ondelete="CASCADE"), nullable=False, index=True)
    
    serial_number = Column(Integer, nullable=False)
    land_name = Column(String(200))
    village = Column(String(200))
    district = Column(String(100))
    extent = Column(String(100))
    cultivation_description = Column(String(500))
    ownership_nature = Column(String(200))
    deed_number = Column(String(100))
    title_registration_number = Column(String(100))
    tax_details = Column(String(500))
    land_occupants = Column(String(500))
    
    is_deleted = Column(Boolean, nullable=False, server_default=expression.false())
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationship
    devala = relationship("DevalaData", back_populates="devala_lands")
