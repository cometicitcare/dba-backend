from sqlalchemy import Boolean, Column, DateTime, Integer, String, func
from sqlalchemy.sql import expression

from app.db.base import Base


class DivisionalSecretariat(Base):
    __tablename__ = "cmm_dvsec"

    dv_id = Column(Integer, primary_key=True, index=True)
    dv_dvcode = Column(String(10), nullable=False, index=True, unique=True)
    dv_distrcd = Column(String(10), nullable=False, index=True)
    dv_dvname = Column(String(200))
    dv_version = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    dv_is_deleted = Column(Boolean, nullable=False, server_default=expression.false())
    dv_created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    dv_updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        onupdate=func.now(),
    )
    dv_created_by = Column(String(25))
    dv_updated_by = Column(String(25))
    dv_version_number = Column(Integer, nullable=False, server_default="1")
