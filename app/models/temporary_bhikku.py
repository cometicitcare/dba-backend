# app/models/temporary_bhikku.py
from sqlalchemy import Boolean, Column, Integer, String, TIMESTAMP, text
from sqlalchemy.sql import func
from app.db.base import Base


class TemporaryBhikku(Base):
    """
    Model for Temporary Bhikku Registration.
    Used when creating direct high bhikku with incomplete information.
    Stores partial data until full details are available.
    """
    __tablename__ = "temporary_bhikku"

    # Primary Key
    tb_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Basic Information Fields
    tb_name = Column(String(100), nullable=False, comment="Bhikku name")
    tb_id_number = Column(String(20), nullable=True, comment="National ID or other identification number")
    tb_contact_number = Column(String(15), nullable=True, comment="Contact/mobile number")
    tb_samanera_name = Column(String(100), nullable=True, comment="Samanera (novice) name")
    tb_address = Column(String(500), nullable=True, comment="Residential address")
    tb_living_temple = Column(String(200), nullable=True, comment="Current living temple/vihara")
    
    # Transfer Flag
    tb_is_transferred = Column(
        Boolean, nullable=False, server_default=text("false"),
        comment="Flag indicating this record has been transferred to bhikku_regist",
    )
    
    # Audit Fields
    tb_created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    tb_created_by = Column(String(25), nullable=True, comment="User ID who created this record")
    tb_updated_at = Column(TIMESTAMP, onupdate=func.now(), nullable=True)
    tb_updated_by = Column(String(25), nullable=True, comment="User ID who last updated this record")
    
    def __repr__(self):
        return f"<TemporaryBhikku(tb_id={self.tb_id}, tb_name={self.tb_name})>"
