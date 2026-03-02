from sqlalchemy import Boolean, Column, Date, Integer, String, TIMESTAMP, text
from sqlalchemy.sql import func

from app.db.base import Base


class ParshawaData(Base):
    __tablename__ = "cmm_parshawadata"

    pr_id = Column(Integer, primary_key=True, index=True)
    pr_prn = Column(String(20), nullable=False, index=True)
    pr_pname = Column(String(200))
    pr_nayakahimi = Column(String(20), nullable=False, index=True)
    pr_rmrks = Column(String(200))
    pr_startdate = Column(Date)
    pr_nikayacd = Column(String(10), index=True)
    pr_version = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    pr_is_deleted = Column(Boolean, nullable=False, server_default=text("false"))
    pr_created_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
    )
    pr_updated_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    pr_created_by = Column(String(25))
    pr_updated_by = Column(String(25))
    pr_version_number = Column(Integer, nullable=False, server_default=text("1"))
