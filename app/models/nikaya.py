from sqlalchemy import Boolean, Column, Date, Integer, String, TIMESTAMP, text
from sqlalchemy.sql import func

from app.db.base import Base


class NikayaData(Base):
    __tablename__ = "cmm_nikayadata"

    nk_id = Column(Integer, primary_key=True, index=True)
    nk_nkn = Column(String(10), nullable=False, index=True)
    nk_nname = Column(String(200))
    nk_nahimicd = Column(String(12), index=True)
    nk_startdate = Column(Date)
    nk_rmakrs = Column(String(200))
    nk_version = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    nk_is_deleted = Column(Boolean, server_default=text("false"))
    nk_created_at = Column(TIMESTAMP, server_default=func.now())
    nk_updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
    )
    nk_created_by = Column(String(25))
    nk_updated_by = Column(String(25))
    nk_version_number = Column(Integer, server_default=text("1"))
