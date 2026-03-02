# app/models/bank.py
from sqlalchemy import Boolean, Column, Integer, String, TIMESTAMP, text
from sqlalchemy.sql import func

from app.db.base import Base


class Bank(Base):
    __tablename__ = "cmm_bnk"

    bk_id = Column(Integer, primary_key=True, index=True)
    bk_bcode = Column(String(10), nullable=False, unique=True, index=True)
    bk_bname = Column(String(200))
    bk_version = Column(TIMESTAMP, nullable=False, server_default=func.now())
    bk_is_deleted = Column(Boolean, server_default=text("false"))
    bk_created_at = Column(TIMESTAMP, server_default=func.now())
    bk_updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    bk_created_by = Column(String(25))
    bk_updated_by = Column(String(25))
    bk_version_number = Column(Integer, server_default=text("1"))
