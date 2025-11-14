from datetime import datetime
from sqlalchemy import String, Index, ForeignKey, Integer, TIMESTAMP, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class UserPermission(Base):
    """
    User-level permission overrides.
    Allows granting or denying specific permissions to individual users,
    overriding their role-based permissions.
    """
    __tablename__ = "user_permissions"

    up_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    up_user_id: Mapped[str] = mapped_column(String(10), ForeignKey("user_accounts.ua_user_id", ondelete="CASCADE"), nullable=False)
    up_permission_id: Mapped[int] = mapped_column(Integer, ForeignKey("permissions.pe_permission_id", ondelete="CASCADE"), nullable=False)
    up_granted: Mapped[bool] = mapped_column(nullable=False)  # True = allow, False = deny
    up_assigned_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=False), server_default=func.now(), nullable=False)
    up_expires_date: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=False), nullable=True)
    up_is_active: Mapped[bool] = mapped_column(default=True, server_default="true")
    up_assigned_by: Mapped[str | None] = mapped_column(String(10), nullable=True)
    up_reason: Mapped[str | None] = mapped_column(Text, nullable=True)  # Why this override was given
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=False), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=False), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("UserAccount", back_populates="user_permissions")
    permission = relationship("Permission", back_populates="user_permissions")

    __table_args__ = (
        Index("ix_user_permissions_user_perm", "up_user_id", "up_permission_id", unique=True),
        Index("ix_user_permissions_user_id", "up_user_id"),
        Index("ix_user_permissions_permission_id", "up_permission_id"),
        Index("ix_user_permissions_active", "up_is_active"),
        Index("ix_user_permissions_expires", "up_expires_date"),
    )

    def __repr__(self):
        return f"<UserPermission(up_id={self.up_id}, user={self.up_user_id}, perm={self.up_permission_id}, granted={self.up_granted})>"
