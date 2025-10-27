# app/models/certificate_change.py
from sqlalchemy import Boolean, Column, Date, Integer, String, TIMESTAMP, text
from sqlalchemy.sql import func

from app.db.base import Base


class CertificateChange(Base):
    __tablename__ = "certifichanges"

    ch_id = Column(Integer, primary_key=True, index=True)
    ch_dofchg = Column(Date, nullable=False)
    ch_prt = Column(String(5), nullable=False)
    ch_regno = Column(String(200), nullable=False, index=True)
    ch_autho = Column(String(50), nullable=False)
    ch_admnusr = Column(String(50), nullable=False)
    ch_dptusr = Column(String(50), nullable=False)
    ch_version = Column(TIMESTAMP, nullable=False, server_default=func.now())
    ch_is_deleted = Column(Boolean, server_default=text("false"))
    ch_created_at = Column(TIMESTAMP, server_default=func.now())
    ch_updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    ch_created_by = Column(String(50))
    ch_updated_by = Column(String(50))
    ch_version_number = Column(Integer, server_default=text("1"))
