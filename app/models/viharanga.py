# app/models/viharanga.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Sequence
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from app.db.base import Base


class Viharanga(Base):
    """Viharanga (cmm_viharanga table) - Vihara Type/Category"""
    __tablename__ = "cmm_viharanga"
    __table_args__ = {"schema": "public"}

    vg_id = Column(Integer, Sequence('cmm_viharanga_vg_id_seq'), primary_key=True, autoincrement=True)
    vg_code = Column(String(10), nullable=False, unique=True)
    vg_item = Column(String(200), nullable=True)
    vg_version = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    vg_is_deleted = Column(Boolean, nullable=True, default=False)
    vg_created_at = Column(DateTime, nullable=True, default=datetime.utcnow)
    vg_updated_at = Column(DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)
    vg_created_by = Column(String(25), nullable=True)
    vg_updated_by = Column(String(25), nullable=True)
    vg_version_number = Column(Integer, nullable=True, default=1)
