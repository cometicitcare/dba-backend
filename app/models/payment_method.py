# app/models/payment_method.py
from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    TIMESTAMP,
    text,
)
from sqlalchemy.sql import func

from app.db.base import Base


class PaymentMethod(Base):
    __tablename__ = "cmm_payment_methods"

    pm_id = Column(Integer, primary_key=True, index=True)
    pm_code = Column(String(10), nullable=False, unique=True, index=True)
    pm_method_name = Column(String(30), nullable=False)
    pm_is_active = Column(Boolean, nullable=False, server_default=text("true"))
    pm_version = Column(
        TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now()
    )
    pm_is_deleted = Column(Boolean, nullable=False, server_default=text("false"))
    pm_created_at = Column(TIMESTAMP, server_default=func.now())
    pm_updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    pm_created_by = Column(
        String(25), ForeignKey("user_accounts.ua_user_id"), nullable=True
    )
    pm_updated_by = Column(
        String(25), ForeignKey("user_accounts.ua_user_id"), nullable=True
    )
    pm_version_number = Column(Integer, nullable=False, server_default=text("1"))
