# app/models/sangha_nayaka_contact.py
from sqlalchemy import Boolean, Column, Integer, String, TIMESTAMP, text, ForeignKey
from sqlalchemy.sql import func

from app.db.base import Base


class SanghaNayakaContact(Base):
    """Model for storing Sangha Nayaka (Senior Monks) contact information."""
    
    __tablename__ = "cmm_sangha_nayaka_contacts"

    snc_id = Column(Integer, primary_key=True, index=True)
    snc_nikaya_code = Column(String(10), ForeignKey('cmm_nikayadata.nk_nkn'), index=True)
    snc_parshawa_code = Column(String(20), index=True)
    snc_nikaya_name = Column(String(200))
    snc_parshawa_name = Column(String(200))
    snc_name = Column(String(300), nullable=False)
    snc_address = Column(String(500))
    snc_phone1 = Column(String(20))
    snc_phone2 = Column(String(20))
    snc_phone3 = Column(String(20))
    snc_designation = Column(String(100))
    snc_order_no = Column(Integer)
    snc_is_deleted = Column(Boolean, server_default=text("false"))
    snc_created_at = Column(TIMESTAMP, server_default=func.now())
    snc_updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
    )
    snc_created_by = Column(String(25))
    snc_updated_by = Column(String(25))
    snc_version_number = Column(Integer, server_default=text("1"))
