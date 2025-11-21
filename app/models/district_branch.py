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


class DistrictBranch(Base):
    __tablename__ = "district_branches"

    db_id = Column(Integer, primary_key=True, index=True)
    db_code = Column(String(10), nullable=False, index=True, unique=True)
    db_name = Column(String(200), nullable=False)
    db_description = Column(String(500))
    db_province_branch_id = Column(Integer)  # Not using province branches yet
    db_district_code = Column(String(10), index=True)  # Links to cmm_districtdata.dd_dcode
    db_is_deleted = Column(Boolean, nullable=False, server_default=expression.false())
    db_created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    db_updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        onupdate=func.now(),
    )
    db_created_by = Column(String(25))
    db_updated_by = Column(String(25))
    db_version_number = Column(Integer, nullable=False, server_default="1")

    # Relationships
    users = relationship("UserAccount", back_populates="district_branch", foreign_keys="UserAccount.ua_district_branch_id")
