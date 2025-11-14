from sqlalchemy import String, Index, ForeignKey, Integer, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from datetime import datetime


class RolePermission(Base):
    __tablename__ = "role_permissions"

    rp_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    rp_role_id: Mapped[str] = mapped_column(String(10), ForeignKey("roles.ro_role_id", ondelete="CASCADE"), nullable=False)
    rp_permission_id: Mapped[int] = mapped_column(Integer, ForeignKey("permissions.pe_permission_id", ondelete="CASCADE"), nullable=False)  # Fixed: Integer not String
    rp_granted: Mapped[bool] = mapped_column(default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=False), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=False), server_default=func.now(), onupdate=func.now())

    # Relationships
    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")

    __table_args__ = (
        Index("ix_role_permissions_role_perm", "rp_role_id", "rp_permission_id", unique=True),
        Index("ix_role_permissions_role_id", "rp_role_id"),
        Index("ix_role_permissions_permission_id", "rp_permission_id"),
    )

# We will add the rest of the DBML tables incrementally (geographic hierarchy, monk/temple, certifications, education, donations, etc.) with typed columns matching your spec.