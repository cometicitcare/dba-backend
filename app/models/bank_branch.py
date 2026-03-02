# app/models/bank_branch.py
from sqlalchemy import Boolean, Column, Integer, String, TIMESTAMP, text
from sqlalchemy.sql import func

from app.db.base import Base


class BankBranch(Base):
    __tablename__ = "cmm_bnkbrnch"

    bb_id = Column(Integer, primary_key=True, index=True)
    bb_bcode = Column(String(10), nullable=False, index=True)
    bb_bbcode = Column(String(10), nullable=False, unique=True, index=True)
    bb_brname = Column(String(200))
    bb_version = Column(TIMESTAMP, nullable=False, server_default=func.now())
    bb_is_deleted = Column(Boolean, server_default=text("false"))
    bb_created_at = Column(TIMESTAMP, server_default=func.now())
    bb_updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    bb_created_by = Column(String(25))
    bb_updated_by = Column(String(25))
    bb_version_number = Column(Integer, server_default=text("1"))
