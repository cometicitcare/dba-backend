from datetime import datetime
from sqlalchemy import String, Index, ForeignKey, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.models.mixins import AuditMixin


class UserRole(Base, AuditMixin):
    __tablename__ = "user_roles"


    ur_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ur_user_id: Mapped[str] = mapped_column(String(10), ForeignKey("user_accounts.ua_user_id", ondelete="RESTRICT"), nullable=False)
    ur_role_id: Mapped[str] = mapped_column(String(10), ForeignKey("roles.ro_role_id", ondelete="RESTRICT"), nullable=False)
    ur_assigned_date: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=False), nullable=True)
    ur_expires_date: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=False), nullable=True)


    __table_args__ = (
        Index("ix_user_roles_user_role", "ur_user_id", "ur_role_id", unique=True),
        Index("ix_user_roles_user_id", "ur_user_id"),
        Index("ix_user_roles_role_id", "ur_role_id"),
    )