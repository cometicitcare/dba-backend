from sqlalchemy import String, Integer, TIMESTAMP, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from datetime import datetime

class UserGroup(Base):
    __tablename__ = "user_groups"

    ug_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(10), ForeignKey("user_accounts.ua_user_id", ondelete="CASCADE"), nullable=False)
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey("groups.group_id", ondelete="CASCADE"), nullable=False)
    assigned_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=False), server_default=func.now(), nullable=False)
    expires_date: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=False), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, server_default="true")
    assigned_by: Mapped[str | None] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    group = relationship("Group", back_populates="user_groups")
    user = relationship("UserAccount", back_populates="user_groups")

    __table_args__ = (
        Index("ix_user_groups_user_group", "user_id", "group_id", unique=True),
        Index("ix_user_groups_user_id", "user_id"),
        Index("ix_user_groups_group_id", "group_id"),
        Index("ix_user_groups_active", "is_active"),
        Index("ix_user_groups_expires", "expires_date"),
    )

    def __repr__(self):
        return f"<UserGroup(ug_id={self.ug_id}, user_id={self.user_id}, group_id={self.group_id})>"