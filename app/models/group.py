from sqlalchemy import String, Text, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from datetime import datetime
from typing import Optional

class Group(Base):
    __tablename__ = "groups"

    group_id: Mapped[int] = mapped_column(primary_key=True)
    group_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    group_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[str] = mapped_column(String(50), nullable=True)
    updated_by: Mapped[str] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("UserGroup", back_populates="group")  # Link to the UserGroup model (many-to-many)
    permissions = relationship("Permission", back_populates="group")  # Link to the Permission model (one-to-many)

    def __repr__(self):
        return f"<Group(group_id={self.group_id}, group_name={self.group_name}, created_at={self.created_at})>"
