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


class BeneficiaryData(Base):
    __tablename__ = "benifshrdata"

    bf_id = Column(Integer, primary_key=True, index=True)
    bf_bnn = Column(String(10), nullable=False, unique=True, index=True)
    bf_bfname = Column(String(200))
    bf_bfaddrs = Column(String(200))
    bf_whatapp = Column(String(10))
    bf_mobile = Column(String(10))
    bf_email = Column(String(40), unique=True)
    bf_version = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    bf_is_deleted = Column(Boolean, nullable=False, server_default=expression.false())
    bf_created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    bf_updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        onupdate=func.now(),
    )
    bf_created_by = Column(String(25))
    bf_updated_by = Column(String(25))
    bf_version_number = Column(Integer, nullable=False, server_default="1")
