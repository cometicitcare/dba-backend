# app/models/gov_officers.py
from sqlalchemy import Boolean, Column, Integer, String, TIMESTAMP
from sqlalchemy.sql import func

from app.db.base import Base


class GovOfficer(Base):
    """
    Model for Government Officers (cmm_gov_officers table).
    Stores contact information for government officers.
    """

    __tablename__ = "cmm_gov_officers"

    # ── Primary Key ──────────────────────────────────────────────────────────
    go_id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # ── Personal Details ──────────────────────────────────────────────────────
    go_title = Column(String(100), nullable=False, comment="Title (e.g. Mr., Mrs., Dr.)")
    go_first_name = Column(String(100), nullable=False, comment="First name")
    go_last_name = Column(String(100), nullable=False, comment="Last name")

    # ── Contact ───────────────────────────────────────────────────────────────
    go_contact_number = Column(String(20), nullable=False, comment="Contact phone number")
    go_email = Column(String(255), nullable=True, comment="Email address (optional)")
    go_address = Column(String(500), nullable=False, comment="Address")

    # ── Identity ──────────────────────────────────────────────────────────────
    go_id_number = Column(String(50), nullable=True, comment="National ID / NIC number (optional)")

    # ── Audit Fields ──────────────────────────────────────────────────────────
    go_is_deleted = Column(Boolean, default=False, server_default="false", nullable=False)
    go_created_at = Column(TIMESTAMP(timezone=False), server_default=func.now(), nullable=True)
    go_updated_at = Column(
        TIMESTAMP(timezone=False),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True,
    )
    go_created_by = Column(String(100), nullable=True)
    go_updated_by = Column(String(100), nullable=True)
    go_version_number = Column(Integer, default=1, server_default="1", nullable=False)
