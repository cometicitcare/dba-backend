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


class BhikkuCategory(Base):
    __tablename__ = "cmm_cat"

    cc_id = Column(Integer, primary_key=True, index=True)
    cc_code = Column(String(5), nullable=False, index=True, unique=True)
    cc_catogry = Column(String(200))
    cc_version = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    cc_is_deleted = Column(Boolean, nullable=False, server_default=expression.false())
    cc_created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    cc_updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        onupdate=func.now(),
    )
    cc_created_by = Column(String(25))
    cc_updated_by = Column(String(25))
    cc_version_number = Column(Integer, nullable=False, server_default="1")
