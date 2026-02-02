from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from app.db.base import Base


class AramaResidentSilmatha(Base):
    """Resident silmatha records associated with arama"""
    __tablename__ = "arama_resident_silmathas"

    id = Column(Integer, primary_key=True, index=True)
    ar_id = Column(Integer, ForeignKey("aramadata.ar_id", ondelete="CASCADE"), nullable=False, index=True)
    
    name = Column(String(200), nullable=False)
    national_id = Column(String(20))
    date_of_birth = Column(Date)
    ordination_date = Column(Date)
    position = Column(String(200))
    notes = Column(String(1000))
    is_head_nun = Column(Boolean, server_default=expression.false())
    
    is_deleted = Column(Boolean, nullable=False, server_default=expression.false())
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationship
    arama = relationship("AramaData", back_populates="resident_silmathas")
