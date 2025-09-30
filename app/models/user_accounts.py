from sqlalchemy import String, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.models.mixins import AuditMixin


class UserAccount(Base, AuditMixin):
    __tablename__ = "user_accounts"


    ua_user_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    ua_username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    ua_email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    ua_password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    ua_salt: Mapped[str] = mapped_column(String(100), nullable=False)
    ua_first_name: Mapped[str | None] = mapped_column(String(50))
    ua_last_name: Mapped[str | None] = mapped_column(String(50))
    ua_phone: Mapped[str | None] = mapped_column(String(15))
    ua_status: Mapped[str | None] = mapped_column(String(20), default="active", server_default="active")
    ua_last_login: Mapped["datetime" | None]
    ua_login_attempts: Mapped[int] = mapped_column(default=0, server_default="0")
    ua_locked_until: Mapped["datetime" | None]
    ua_password_expires: Mapped["datetime" | None]
    ua_must_change_password: Mapped[bool] = mapped_column(default=False, server_default="false")
    ua_two_factor_enabled: Mapped[bool] = mapped_column(default=False, server_default="false")
    ua_two_factor_secret: Mapped[str | None] = mapped_column(String(100))


    __table_args__ = (
        Index("ix_user_accounts_username", "ua_username", unique=True),
        Index("ix_user_accounts_email", "ua_email", unique=True),
        Index("ix_user_accounts_status", "ua_status"),
        UniqueConstraint("ua_username", name="uq_user_accounts_username"),
        UniqueConstraint("ua_email", name="uq_user_accounts_email"),
    )