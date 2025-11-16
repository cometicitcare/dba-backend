# app/models/district_branch.py
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.sql import expression
from sqlalchemy.orm import relationship

from app.db.base import Base


class DistrictBranch(Base):
    """
    Represents district-level branches in the organizational hierarchy.
    There are 25 district branches, each belonging to a province branch.
    """
    __tablename__ = "district_branches"

    db_id = Column(Integer, primary_key=True, index=True)
    db_code = Column(String(10), nullable=False, unique=True, index=True)
    db_name = Column(String(200), nullable=False)
    db_description = Column(String(500))
    
    # Foreign key to province branch
    db_province_branch_id = Column(Integer, ForeignKey("province_branches.pb_id"), nullable=False, index=True)
    
    # Reference to existing district table (for mapping to actual districts)
    db_district_code = Column(String(10), index=True)  # Links to cmm_districtdata.dd_dcode
    
    db_is_deleted = Column(Boolean, nullable=False, server_default=expression.false())
    db_created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
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
    province_branch = relationship("ProvinceBranch", back_populates="district_branches")
    users = relationship("UserAccount", back_populates="district_branch")
