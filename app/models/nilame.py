# app/models/nilame.py
from sqlalchemy import Boolean, Column, Date, Integer, String, TIMESTAMP, text
from sqlalchemy.sql import func

from app.db.base import Base


class NilameRegist(Base):
    __tablename__ = "nilame_regist"

    kr_id = Column(Integer, primary_key=True, index=True)
    kr_krn = Column(String(20), nullable=False, index=True)
    kr_kname = Column(String(20))
    kr_nic = Column(String(20))
    kr_nic_issue_date = Column(Date)
    kr_dofb = Column(Date)
    kr_addrs = Column(String(100))
    kr_grndiv = Column(String(10))
    kr_trn = Column(String(10))
    kr_version = Column(TIMESTAMP, nullable=False, server_default=func.now())
    kr_is_deleted = Column(Boolean, server_default=text("false"))
    kr_created_at = Column(TIMESTAMP, server_default=func.now())
    kr_updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    kr_created_by = Column(String(25))
    kr_updated_by = Column(String(25))
    kr_version_number = Column(Integer, server_default=text("1"))

