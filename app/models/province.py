from sqlalchemy import Boolean, Column, DateTime, Integer, String, func
from sqlalchemy.sql import expression

from app.db.base import Base


class Province(Base):
    __tablename__ = "cmm_province"

    cp_id = Column(Integer, primary_key=True, index=True)
    cp_code = Column(String(10), nullable=False, index=True, unique=True)
    cp_name = Column(String(200), unique=True)
    cp_version = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    cp_is_deleted = Column(Boolean, nullable=False, server_default=expression.false())
    cp_created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    cp_updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        onupdate=func.now(),
    )
    cp_created_by = Column(String(25))
    cp_updated_by = Column(String(25))
    cp_version_number = Column(Integer, nullable=False, server_default="1")
