from sqlalchemy import String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.mixins import AuditMixin


class Role(Base, AuditMixin):
    __tablename__ = "roles"
    __audit_field_prefix__ = "ro"


    ro_role_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    ro_role_name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    ro_description: Mapped[str | None] = mapped_column(String(200))
    ro_is_system_role: Mapped[bool] = mapped_column(default=False, server_default="false")

    user_roles = relationship("UserRole", back_populates="role")

    __table_args__ = (
        Index("ix_roles_role_name", "ro_role_name", unique=True),
    )
