from sqlalchemy import Column, String, Integer, Text, ForeignKey, TIMESTAMP, Index  
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from datetime import datetime
from typing import Optional


class Permission(Base):
    __tablename__ = "permissions"

    # Primary key for the permission
    pe_permission_id: Mapped[int] = mapped_column(primary_key=True)
    
    # Name of the permission (now unique across all groups)
    pe_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    
    # The resource the permission applies to
    pe_resource: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # The action the permission allows (e.g., CREATE, READ, etc.)
    pe_action: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Description of the permission
    pe_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Foreign key reference to the group this permission belongs to
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey("groups.group_id", ondelete="CASCADE"))
    
    # Audit fields to track who created and updated the permission
    pe_created_by: Mapped[str] = mapped_column(String(50), nullable=True)
    pe_updated_by: Mapped[str] = mapped_column(String(50), nullable=True)
    pe_created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    pe_updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    group = relationship("Group", back_populates="permissions")
    role_permissions = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")
    user_permissions = relationship("UserPermission", back_populates="permission", cascade="all, delete-orphan")

    # Indexes to optimize queries
    __table_args__ = (
        Index("ix_permissions_name", "pe_name", unique=True),
        Index("ix_permissions_resource_action", "pe_resource", "pe_action"),
    )

    def __repr__(self):
        return f"<Permission(pe_permission_id={self.pe_permission_id}, pe_name={self.pe_name})>"