# app/models/sasanarakshaka.py
from sqlalchemy import Boolean, Column, Integer, String, TIMESTAMP, ForeignKey, text
from sqlalchemy.sql import func
from app.db.base import Base


class SasanarakshakaBalaMandalaya(Base):
    """
    Model for Sasanarakshaka Bala Mandalaya (cmm_sasanarbm table).
    This table stores information about Sasana Rakshaka Bala Mandalaya organizations.
    """
    __tablename__ = "cmm_sasanarbm"

    # Primary Key
    sr_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Main Fields
    sr_ssbmcode = Column(String(10), nullable=False, unique=True, index=True, comment="Sasana Rakshaka Bala Mandalaya Code")
    sr_dvcd = Column(
        String(10), 
        ForeignKey("cmm_dvsec.dv_dvcode", ondelete="RESTRICT"), 
        nullable=False, 
        index=True,
        comment="Divisional Secretariat Code (FK to cmm_dvsec.dv_dvcode)"
    )
    sr_ssbname = Column(String(200), nullable=True, comment="Sasana Rakshaka Bala Mandalaya Name")
    sr_sbmnayakahimi = Column(
        String(12), 
        ForeignKey("bhikku_regist.br_regn", ondelete="RESTRICT"), 
        nullable=True,
        index=True,
        comment="Nayaka Himi Registration Number (FK to bhikku_regist.br_regn)"
    )
    
    # Audit Fields
    sr_version = Column(TIMESTAMP, nullable=False, server_default=func.now(), comment="Version timestamp")
    sr_is_deleted = Column(Boolean, server_default=text('false'), nullable=True, comment="Soft delete flag")
    sr_created_at = Column(TIMESTAMP, server_default=func.now(), nullable=True, comment="Creation timestamp")
    sr_updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=True, comment="Last update timestamp")
    sr_created_by = Column(String(25), nullable=True, comment="User who created the record")
    sr_updated_by = Column(String(25), nullable=True, comment="User who last updated the record")
    sr_version_number = Column(Integer, server_default=text('1'), nullable=True, comment="Version number for optimistic locking")
