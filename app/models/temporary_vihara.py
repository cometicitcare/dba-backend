# app/models/temporary_vihara.py
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.sql import func
from app.db.base import Base


class TemporaryVihara(Base):
    """
    Model for Temporary Vihara Registration.
    Used when creating records with incomplete vihara information.
    Stores partial data until full details are available.
    """
    __tablename__ = "temporary_vihara"

    # Primary Key
    tv_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Basic Information Fields
    tv_name = Column(String(200), nullable=False, comment="Vihara/Temple name")
    tv_address = Column(String(500), nullable=True, comment="Temple address")
    tv_contact_number = Column(String(15), nullable=True, comment="Contact/mobile number")
    tv_district = Column(String(100), nullable=True, comment="District name or code")
    tv_province = Column(String(100), nullable=True, comment="Province name or code")
    tv_viharadhipathi_name = Column(String(200), nullable=True, comment="Viharadhipathi/Chief incumbent name")
    
    # Audit Fields
    tv_created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    tv_created_by = Column(String(25), nullable=True, comment="User ID who created this record")
    tv_updated_at = Column(TIMESTAMP, onupdate=func.now(), nullable=True)
    tv_updated_by = Column(String(25), nullable=True, comment="User ID who last updated this record")
    
    def __repr__(self):
        return f"<TemporaryVihara(tv_id={self.tv_id}, tv_name={self.tv_name})>"
