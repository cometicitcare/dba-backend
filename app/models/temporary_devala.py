# app/models/temporary_devala.py
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.sql import func
from app.db.base import Base


class TemporaryDevala(Base):
    """
    Model for Temporary Devala Registration.
    Used when creating records with incomplete devala information.
    Stores partial data until full details are available.
    """
    __tablename__ = "temporary_devala"

    # Primary Key
    td_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Basic Information Fields
    td_name = Column(String(200), nullable=False, comment="Devala/Shrine name")
    td_address = Column(String(500), nullable=True, comment="Devala address")
    td_contact_number = Column(String(15), nullable=True, comment="Contact/mobile number")
    td_district = Column(String(100), nullable=True, comment="District name or code")
    td_province = Column(String(100), nullable=True, comment="Province name or code")
    td_basnayake_nilame_name = Column(String(200), nullable=True, comment="Basnayake Nilame name")
    
    # Audit Fields
    td_created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    td_created_by = Column(String(25), nullable=True, comment="User ID who created this record")
    td_updated_at = Column(TIMESTAMP, onupdate=func.now(), nullable=True)
    td_updated_by = Column(String(25), nullable=True, comment="User ID who last updated this record")
    
    def __repr__(self):
        return f"<TemporaryDevala(td_id={self.td_id}, td_name={self.td_name})>"
