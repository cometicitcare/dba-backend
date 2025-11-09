from sqlalchemy import String, Index, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.models.mixins import AuditMixin


class RolePermission(Base, AuditMixin):
    __tablename__ = "role_permissions"


    rp_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    rp_role_id: Mapped[str] = mapped_column(String(10), ForeignKey("roles.ro_role_id", ondelete="RESTRICT"), nullable=False)
    rp_permission_id: Mapped[str] = mapped_column(String(10), ForeignKey("permissions.pe_permission_id", ondelete="RESTRICT"), nullable=False)
    rp_granted: Mapped[bool] = mapped_column(default=True, server_default="true")


    __table_args__ = (
        Index("ix_role_permissions_role_perm", "rp_role_id", "rp_permission_id", unique=True),
        Index("ix_role_permissions_role_id", "rp_role_id"),
        Index("ix_role_permissions_permission_id", "rp_permission_id"),
    )

# We will add the rest of the DBML tables incrementally (geographic hierarchy, monk/temple, certifications, education, donations, etc.) with typed columns matching your spec.