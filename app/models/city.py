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


class City(Base):
    __tablename__ = "cmm_city"

    ct_id = Column(Integer, primary_key=True, index=True)
    ct_code = Column(String(10), nullable=False, index=True)
    ct_gncode = Column(String(10), nullable=False, index=True)
    ct_descr_name = Column(String(200))
    ct_dvcode = Column(String(10))
    ct_version = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    ct_is_deleted = Column(Boolean, nullable=False, server_default=expression.false())
    ct_created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    ct_updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        onupdate=func.now(),
    )
    ct_created_by = Column(String(25))
    ct_updated_by = Column(String(25))
    ct_version_number = Column(Integer, nullable=False, server_default="1")
