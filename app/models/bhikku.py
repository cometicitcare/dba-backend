# app/models/bhikku.py
from sqlalchemy import Boolean, Column, Integer, String, Date, TIMESTAMP, text
from sqlalchemy.sql import func
from app.db.base import Base

class Bhikku(Base):
    __tablename__ = "bhikku_regist"

    br_id = Column(Integer, primary_key=True, index=True)
    br_regn = Column(String(20), unique=True, nullable=False, index=True)
    br_reqstdate = Column(Date, nullable=False)
    # ... (the rest of your columns from the original models.py)
    br_vilage = Column(String(50))
    br_gndiv = Column(String(10), nullable=False)
    br_gihiname = Column(String(50))
    br_dofb = Column(Date)
    br_fathrname = Column(String(50))
    br_remarks = Column(String(100))
    br_currstat = Column(String(5), nullable=False)
    br_effctdate = Column(Date)
    br_parshawaya = Column(String(10), nullable=False)
    br_livtemple = Column(String(10), nullable=False)
    br_mahanatemple = Column(String(10), nullable=False)
    br_mahanaacharyacd = Column(String(12), nullable=False)
    br_multi_mahanaacharyacd = Column(String(200))
    br_mahananame = Column(String(50))
    br_mahanadate = Column(Date)
    br_cat = Column(String(5))
    br_mobile = Column(String(10))
    br_email = Column(String(50))
    br_fathrsaddrs = Column(String(200))
    br_fathrsmobile = Column(String(10))
    br_version = Column(TIMESTAMP, nullable=False, server_default=func.now())
    br_upasampada_serial_no = Column(String(20))
    br_is_deleted = Column(Boolean, server_default=text('false'))
    br_created_at = Column(TIMESTAMP, server_default=func.now())
    br_updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    br_created_by = Column(String(25))
    br_updated_by = Column(String(25))
    br_version_number = Column(Integer, server_default=text('1'))