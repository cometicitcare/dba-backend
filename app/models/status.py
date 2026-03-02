# app/models/status.py
from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    TIMESTAMP,
    text,
)
from sqlalchemy.sql import func

from app.db.base import Base


class StatusData(Base):
    __tablename__ = "statusdata"

    st_id = Column(Integer, primary_key=True, index=True)
    st_descr = Column(String(200), nullable=True)
    st_statcd = Column(String(5), nullable=False, unique=True, index=True)
    st_version = Column(
        TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now()
    )
    st_is_deleted = Column(Boolean, nullable=False, server_default=text("false"))
    st_created_at = Column(TIMESTAMP, server_default=func.now())
    st_updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    st_created_by = Column(
        String(25),
        ForeignKey("user_accounts.ua_user_id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
    )
    st_updated_by = Column(
        String(25),
        ForeignKey("user_accounts.ua_user_id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
    )
    st_version_number = Column(Integer, nullable=True, server_default=text("1"))
