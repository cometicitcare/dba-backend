from datetime import datetime
from sqlalchemy import Boolean, TIMESTAMP, func, Integer
from sqlalchemy.orm import Mapped, mapped_column


class AuditMixin:
    is_deleted: Mapped[bool] = mapped_column("is_deleted", Boolean, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=False), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=False), server_default=func.now(), onupdate=func.now())
    created_by: Mapped[str | None] = mapped_column("created_by", nullable=True)
    updated_by: Mapped[str | None] = mapped_column("updated_by", nullable=True)
    version_number: Mapped[int] = mapped_column(Integer, default=1, server_default="1")