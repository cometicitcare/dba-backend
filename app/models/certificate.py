# app/models/certificate.py
from sqlalchemy import Boolean, Column, Date, Integer, String, TIMESTAMP, text
from sqlalchemy.sql import func

from app.db.base import Base


class CertificateData(Base):
    __tablename__ = "certificatedata"

    cd_id = Column(Integer, primary_key=True, index=True)
    cd_code = Column(String(12), nullable=False, index=True)
    cd_stat = Column(String(5), nullable=False)
    cd_remarks = Column(String(50))
    cd_initdate = Column(Date)
    cd_currstatupddat = Column(Date)
    cd_url = Column(String(50))
    cd_cat = Column(String(5))
    cd_version = Column(TIMESTAMP, nullable=False, server_default=func.now())
    cd_is_deleted = Column(Boolean, server_default=text("false"))
    cd_created_at = Column(TIMESTAMP, server_default=func.now())
    cd_updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    cd_created_by = Column(String(25))
    cd_updated_by = Column(String(25))
    cd_version_number = Column(Integer, server_default=text("1"))

