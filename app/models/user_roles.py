from datetime import datetime
from sqlalchemy import String, Index, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class UserRole(Base):
    __tablename__ = "user_roles"

    ur_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ur_user_id: Mapped[str] = mapped_column(String(10), ForeignKey("user_accounts.ua_user_id", ondelete="CASCADE"), nullable=False)
    ur_role_id: Mapped[str] = mapped_column(String(10), ForeignKey("roles.ro_role_id", ondelete="CASCADE"), nullable=False)
    ur_assigned_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=False), server_default=func.now(), nullable=False)
    ur_expires_date: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=False), nullable=True)
    ur_is_active: Mapped[bool] = mapped_column(default=True, server_default="true")
    ur_assigned_by: Mapped[str | None] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=False), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=False), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("UserAccount", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")

    __table_args__ = (
        Index("ix_user_roles_user_role", "ur_user_id", "ur_role_id", unique=True),
        Index("ix_user_roles_user_id", "ur_user_id"),
        Index("ix_user_roles_role_id", "ur_role_id"),
        Index("ix_user_roles_active", "ur_is_active"),
        Index("ix_user_roles_expires", "ur_expires_date"),
    )