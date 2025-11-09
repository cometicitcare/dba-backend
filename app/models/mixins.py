from datetime import datetime
from sqlalchemy import Boolean, TIMESTAMP, func, Integer
from sqlalchemy.orm import Mapped, mapped_column, declared_attr


class AuditMixin:
    """Mixin that maps audit columns while allowing per-table prefixes."""

    __audit_field_prefix__: str | None = None

    @classmethod
    def _audit_column_name(cls, base_name: str) -> str:
        prefix = getattr(cls, "__audit_field_prefix__", None)
        if prefix:
            return f"{prefix}_{base_name}"
        return base_name

    @declared_attr
    def is_deleted(cls) -> Mapped[bool]:
        return mapped_column(
            cls._audit_column_name("is_deleted"),
            Boolean,
            default=False,
            server_default="false",
        )

    @declared_attr
    def created_at(cls) -> Mapped[datetime]:
        return mapped_column(
            cls._audit_column_name("created_at"),
            TIMESTAMP(timezone=False),
            server_default=func.now(),
        )

    @declared_attr
    def updated_at(cls) -> Mapped[datetime]:
        return mapped_column(
            cls._audit_column_name("updated_at"),
            TIMESTAMP(timezone=False),
            server_default=func.now(),
            onupdate=func.now(),
        )

    @declared_attr
    def created_by(cls) -> Mapped[str | None]:
        return mapped_column(
            cls._audit_column_name("created_by"),
            nullable=True,
        )

    @declared_attr
    def updated_by(cls) -> Mapped[str | None]:
        return mapped_column(
            cls._audit_column_name("updated_by"),
            nullable=True,
        )

    @declared_attr
    def version_number(cls) -> Mapped[int]:
        return mapped_column(
            cls._audit_column_name("version_number"),
            Integer,
            default=1,
            server_default="1",
        )
