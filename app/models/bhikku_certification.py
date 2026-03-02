# app/models/bhikku_certification.py
from sqlalchemy import Boolean, Column, Date, Integer, Numeric, String, TIMESTAMP, text
from sqlalchemy.sql import func

from app.db.base import Base


class BhikkuCertification(Base):
    __tablename__ = "bikku_certification"

    bc_id = Column(Integer, primary_key=True, index=True)
    bc_regno = Column(String(12), nullable=False, index=True)
    bc_issuedate = Column(Date, nullable=False)
    bc_reqstdate = Column(Date)
    bc_adminautho = Column(String(200))
    bc_prtoptn = Column(String(5))
    bc_usr = Column(String(10))
    bc_admnusr = Column(String(10))
    bc_paydate = Column(Date, nullable=False)
    bc_payamount = Column(Numeric(6, 2), nullable=False)
    bc_version = Column(TIMESTAMP, nullable=False, server_default=func.now())
    bc_is_deleted = Column(Boolean, server_default=text("false"))
    bc_created_at = Column(TIMESTAMP, server_default=func.now())
    bc_updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    bc_created_by = Column(String(25))
    bc_updated_by = Column(String(25))
    bc_version_number = Column(Integer, server_default=text("1"))

