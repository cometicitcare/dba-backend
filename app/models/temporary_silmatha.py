# app/models/temporary_silmatha.py
from sqlalchemy import Column, Integer, String, Date, TIMESTAMP
from sqlalchemy.sql import func
from app.db.base import Base


class TemporarySilmatha(Base):
    """
    Model for Temporary Silmatha (Nun) Registration.
    Used when creating records with incomplete silmatha information.
    Stores partial data until full details are available.
    """
    __tablename__ = "temporary_silmatha"

    # Primary Key
    ts_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Basic Information Fields
    ts_name = Column(String(200), nullable=False, comment="Silmatha/Nun name")
    ts_nic = Column(String(15), nullable=True, comment="NIC number")
    ts_contact_number = Column(String(15), nullable=True, comment="Contact/mobile number")
    ts_address = Column(String(500), nullable=True, comment="Address")
    ts_district = Column(String(100), nullable=True, comment="District name or code")
    ts_province = Column(String(100), nullable=True, comment="Province name or code")
    ts_arama_name = Column(String(200), nullable=True, comment="Arama/Hermitage name")
    ts_ordained_date = Column(Date, nullable=True, comment="Date of ordination")
    
    # Audit Fields
    ts_created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    ts_created_by = Column(String(25), nullable=True, comment="User ID who created this record")
    ts_updated_at = Column(TIMESTAMP, onupdate=func.now(), nullable=True)
    ts_updated_by = Column(String(25), nullable=True, comment="User ID who last updated this record")
    
    def __repr__(self):
        return f"<TemporarySilmatha(ts_id={self.ts_id}, ts_name={self.ts_name})>"
