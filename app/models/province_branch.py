# app/models/province_branch.py
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.sql import expression
from sqlalchemy.orm import relationship

from app.db.base import Base


class ProvinceBranch(Base):
    """
    Represents province-level branches in the organizational hierarchy.
    There are 9 province branches, each belonging to a main branch.
    """
    __tablename__ = "province_branches"

    pb_id = Column(Integer, primary_key=True, index=True)
    pb_code = Column(String(10), nullable=False, unique=True, index=True)
    pb_name = Column(String(200), nullable=False)
    pb_description = Column(String(500))
    
    # Foreign key to main branch
    pb_main_branch_id = Column(Integer, ForeignKey("main_branches.mb_id"), nullable=False, index=True)
    
    # Reference to existing province table (for mapping to actual provinces)
    pb_province_code = Column(String(10), index=True)  # Links to cmm_province.cp_code
    
    pb_is_deleted = Column(Boolean, nullable=False, server_default=expression.false())
    pb_created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    pb_updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        onupdate=func.now(),
    )
    pb_created_by = Column(String(25))
    pb_updated_by = Column(String(25))
    pb_version_number = Column(Integer, nullable=False, server_default="1")

    # Relationships
    main_branch = relationship("MainBranch", back_populates="province_branches")
    district_branches = relationship("DistrictBranch", back_populates="province_branch")
    users = relationship("UserAccount", back_populates="province_branch")
