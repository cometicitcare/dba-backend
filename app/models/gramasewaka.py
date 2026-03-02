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


class Gramasewaka(Base):
    """SQLAlchemy model for the cmm_gndata table."""

    __tablename__ = "cmm_gndata"

    gn_id = Column(Integer, primary_key=True, index=True)
    gn_gnc = Column(String(10), nullable=False, unique=True, index=True)
    gn_gnname = Column(String(200))
    gn_mbile = Column(String(10), unique=True)
    gn_email = Column(String(40), unique=True)
    gn_dvcode = Column(String(10), nullable=False, index=True)
    gn_version = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    gn_is_deleted = Column(Boolean, nullable=False, server_default=expression.false())
    gn_created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    gn_updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        onupdate=func.now(),
    )
    gn_created_by = Column(String(25))
    gn_updated_by = Column(String(25))
    gn_version_number = Column(Integer, nullable=False, server_default="1")
