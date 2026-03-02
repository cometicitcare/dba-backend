# app/models/temporary_arama.py
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.sql import func
from app.db.base import Base


class TemporaryArama(Base):
    """
    Model for Temporary Arama Registration.
    Used when creating records with incomplete arama information.
    Stores partial data until full details are available.
    """
    __tablename__ = "temporary_arama"

    # Primary Key
    ta_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Basic Information Fields
    ta_name = Column(String(200), nullable=False, comment="Arama/Hermitage name")
    ta_address = Column(String(500), nullable=True, comment="Arama address")
    ta_contact_number = Column(String(15), nullable=True, comment="Contact/mobile number")
    ta_district = Column(String(100), nullable=True, comment="District name or code")
    ta_province = Column(String(100), nullable=True, comment="Province name or code")
    ta_aramadhipathi_name = Column(String(200), nullable=True, comment="Aramadhipathi/Chief incumbent name")
    
    # Audit Fields
    ta_created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    ta_created_by = Column(String(25), nullable=True, comment="User ID who created this record")
    ta_updated_at = Column(TIMESTAMP, onupdate=func.now(), nullable=True)
    ta_updated_by = Column(String(25), nullable=True, comment="User ID who last updated this record")
    
    def __repr__(self):
        return f"<TemporaryArama(ta_id={self.ta_id}, ta_name={self.ta_name})>"
