from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    func,
)
from sqlalchemy.sql import expression

from app.db.base import Base


class District(Base):
    __tablename__ = "cmm_districtdata"

    dd_id = Column(Integer, primary_key=True, index=True)
    dd_dcode = Column(String(10), nullable=False, index=True, unique=True)
    dd_dname = Column(String(200))
    dd_prcode = Column(String(10), nullable=False, index=True)
    dd_version = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    dd_is_deleted = Column(Boolean, nullable=False, server_default=expression.false())
    dd_created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    dd_updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        onupdate=func.now(),
    )
    dd_created_by = Column(String(25))
    dd_updated_by = Column(String(25))
    dd_version_number = Column(Integer, nullable=False, server_default="1")
