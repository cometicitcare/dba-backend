from sqlalchemy import String, Text, TIMESTAMP, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from datetime import datetime
from typing import Optional

class Group(Base):
    __tablename__ = "groups"

    group_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    group_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    group_type: Mapped[str] = mapped_column(String(50), nullable=False)  # BHIKKU, SILMATHA, DAMMA_SCHOOL, DIV_SECRETARIAT, PUBLIC, SYSTEM
    group_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, server_default="true")
    created_by: Mapped[str] = mapped_column(String(50), nullable=True)
    updated_by: Mapped[str] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_groups_name", "group_name", unique=True),
        Index("ix_groups_type", "group_type"),
        Index("ix_groups_active", "is_active"),
    )

    # Relationships
    user_groups = relationship("UserGroup", back_populates="group", cascade="all, delete-orphan")
    permissions = relationship("Permission", back_populates="group", cascade="all, delete-orphan")
    roles = relationship("Role", back_populates="department", foreign_keys="Role.ro_department_id")

    def __repr__(self):
        return f"<Group(group_id={self.group_id}, group_name={self.group_name}, group_type={self.group_type})>"
