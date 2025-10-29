# app/models/religion.py
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


class Religion(Base):
    __tablename__ = "cmm_religion"

    rl_id = Column(Integer, primary_key=True, index=True)
    rl_code = Column(String(10), nullable=False, unique=True, index=True)
    rl_descr = Column(String(30))
    rl_version = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    rl_is_deleted = Column(Boolean, server_default=text("false"))
    rl_created_at = Column(TIMESTAMP, server_default=func.now())
    rl_updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    rl_created_by = Column(
        String(25),
        ForeignKey("user_accounts.ua_user_id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
    )
    rl_updated_by = Column(
        String(25),
        ForeignKey("user_accounts.ua_user_id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
    )
    rl_version_number = Column(Integer, server_default=text("1"))

