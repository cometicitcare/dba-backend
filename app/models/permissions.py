from sqlalchemy import String, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.models.mixins import AuditMixin


class Permission(Base, AuditMixin):
    __tablename__ = "permissions"


    pe_permission_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    pe_permission_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    pe_resource: Mapped[str] = mapped_column(String(50), nullable=False)
    pe_action: Mapped[str] = mapped_column(String(50), nullable=False)
    pe_description: Mapped[str | None] = mapped_column(String(200))


    __table_args__ = (
        Index("ix_permissions_name", "pe_permission_name", unique=True),
        Index("ix_permissions_resource_action", "pe_resource", "pe_action"),
    )