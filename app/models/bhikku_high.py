# app/models/bhikku_high.py
from sqlalchemy import Boolean, Column, Date, Integer, String, TIMESTAMP, text
from sqlalchemy.sql import func

from app.db.base import Base


class BhikkuHighRegist(Base):
    __tablename__ = "bhikku_high_regist"

    bhr_id = Column(Integer, primary_key=True, index=True)
    bhr_regn = Column(String(12), nullable=False, index=True)
    bhr_samanera_serial_no = Column(String(20))
    bhr_mahanaacharyacd = Column(String(12))
    bhr_multi_mahanaacharyacd = Column(String(200))
    bhr_karmacharya = Column(String(12))
    bhr_multi_karmacharya = Column(String(200))
    bhr_ordination_temple = Column(String(10))
    bhr_mahanadate = Column(Date)
    bhr_effctdate = Column(Date)
    bhr_reqstdate = Column(Date, nullable=False)
    bhr_gndiv = Column(String(10))
    bhr_remarks = Column(String(100))
    bhr_currstat = Column(String(5), nullable=False)
    bhr_parshawaya = Column(String(10), nullable=False)
    bhr_livtemple = Column(String(10), nullable=False)
    bhr_mahananame = Column(String(50))
    bhr_cat = Column(String(5))
    bhr_mobile = Column(String(10))
    bhr_email = Column(String(50))
    bhr_version = Column(TIMESTAMP, nullable=False, server_default=func.now())
    bhr_is_deleted = Column(Boolean, server_default=text("false"))
    bhr_created_at = Column(TIMESTAMP, server_default=func.now())
    bhr_updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    bhr_created_by = Column(String(25))
    bhr_updated_by = Column(String(25))
    bhr_version_number = Column(Integer, server_default=text("1"))

