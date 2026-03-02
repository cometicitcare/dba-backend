from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from app.db.base import Base


class MainBranch(Base):
    __tablename__ = "main_branches"

    mb_id = Column(Integer, primary_key=True, index=True)
    mb_code = Column(String(10), nullable=False, index=True, unique=True)
    mb_name = Column(String(200), nullable=False)
    mb_description = Column(String(500))
    mb_is_deleted = Column(Boolean, nullable=False, server_default=expression.false())
    mb_created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    mb_updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        onupdate=func.now(),
    )
    mb_created_by = Column(String(25))
    mb_updated_by = Column(String(25))
    mb_version_number = Column(Integer, nullable=False, server_default="1")

    # Relationships
    users = relationship("UserAccount", back_populates="main_branch", foreign_keys="UserAccount.ua_main_branch_id")
