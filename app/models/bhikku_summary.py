# app/models/bhikku_summary.py
from sqlalchemy import Boolean, Column, Date, Integer, String, Text, TIMESTAMP, text
from sqlalchemy.sql import func

from app.db.base import Base


class BhikkuSummary(Base):
    __tablename__ = "bikkusummary"

    bs_regn = Column(String(12), primary_key=True, index=True)
    bs_mahananame = Column(String(50))
    bs_birthpls = Column(String(50))
    bs_gihiname = Column(String(50))
    bs_dofb = Column(Date)
    bs_fathrname = Column(String(50))
    bs_mahanadate = Column(Date)
    bs_teacher = Column(String(50))
    bs_teachadrs = Column(String(200))
    bs_mhanavh = Column(String(30))
    bs_livetemple = Column(String(30))
    bs_viharadipathi = Column(String(50))
    bs_pname = Column(String(25))
    bs_nname = Column(String(25))
    bs_nikayanayaka = Column(String(100))
    bs_effctdate = Column(Date)
    bs_curstatus = Column(String(30))
    bs_catogry = Column(String(30))
    bs_vadescrdtls = Column(Text)
    bs_qualifications = Column(Text)
    bs_version = Column(TIMESTAMP, nullable=False, server_default=func.now())
    bs_is_deleted = Column(Boolean, server_default=text("false"))
    bs_created_at = Column(TIMESTAMP, server_default=func.now())
    bs_updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    bs_created_by = Column(String(25))
    bs_updated_by = Column(String(25))
    bs_version_number = Column(Integer, server_default=text("1"))

