from sqlalchemy import String, Index, ForeignKey, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.base import Base

class Role(Base):
    __tablename__ = "roles"

    ro_role_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    ro_role_name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    ro_description: Mapped[str | None] = mapped_column(String(200))
    ro_level: Mapped[str] = mapped_column(String(20), nullable=False, default="DATA_ENTRY")  # SUPER_ADMIN, ADMIN, DATA_ENTRY, VIEWER, PUBLIC
    ro_department_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("groups.group_id", ondelete="SET NULL"), nullable=True)
    ro_is_system_role: Mapped[bool] = mapped_column(default=False, server_default="false")
    ro_is_active: Mapped[bool] = mapped_column(default=True, server_default="true")
    
    # Audit columns
    ro_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    ro_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    ro_created_by: Mapped[str | None] = mapped_column(String(25))
    ro_updated_by: Mapped[str | None] = mapped_column(String(25))
    ro_version_number: Mapped[int | None] = mapped_column(Integer, default=1)

    __table_args__ = (
        Index("ix_roles_role_name", "ro_role_name", unique=True),
        Index("ix_roles_department", "ro_department_id"),
        Index("ix_roles_level", "ro_level"),
    )

    # Relationships
    department = relationship("Group", back_populates="roles", foreign_keys=[ro_department_id])
    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")
    role_permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")