# app/models/reprint_request.py
from sqlalchemy import Column, Integer, String, TIMESTAMP, Numeric, CheckConstraint, ForeignKey, text
from sqlalchemy.orm import relationship

from app.db.base import Base


class ReprintRequest(Base):
    __tablename__ = "reprint_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_type = Column(String(30), nullable=False, index=True)  # BHIKKU, HIGH_BHIKKU, UPASAMPADA
    bhikku_regn = Column(String(12), ForeignKey("bhikku_regist.br_regn", ondelete="CASCADE"), nullable=True, index=True)
    bhikku_high_regn = Column(String(12), ForeignKey("bhikku_high_regist.bhr_regn", ondelete="CASCADE"), nullable=True, index=True)
    upasampada_regn = Column(String(20), ForeignKey("bhikku_high_regist.bhr_regn", ondelete="CASCADE"), nullable=True, index=True)
    silmatha_regn = Column(String(20), ForeignKey("silmatha_regist.sil_regn", ondelete="CASCADE"), nullable=True, index=True)

    form_no = Column(String(50), nullable=True, index=True)
    request_reason = Column(String(500), nullable=True)
    amount = Column(Numeric(10, 2), nullable=True)
    remarks = Column(String(500), nullable=True)
    flow_status = Column(String(20), nullable=False, server_default=text("'PENDING'"), index=True)  # PENDING, APPROVED, REJECTED, COMPLETED

    requested_by = Column(String(25), nullable=True)
    requested_at = Column(TIMESTAMP, server_default=text("now()"), nullable=False)
    approved_by = Column(String(25), nullable=True)
    approved_at = Column(TIMESTAMP, nullable=True)
    rejected_by = Column(String(25), nullable=True)
    rejected_at = Column(TIMESTAMP, nullable=True)
    rejection_reason = Column(String(500), nullable=True)
    printed_by = Column(String(25), nullable=True)
    printed_at = Column(TIMESTAMP, nullable=True)
    completed_by = Column(String(25), nullable=True)
    completed_at = Column(TIMESTAMP, nullable=True)

    created_at = Column(TIMESTAMP, server_default=text("now()"), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=text("now()"), onupdate=text("now()"), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "(bhikku_regn IS NOT NULL)::int + (bhikku_high_regn IS NOT NULL)::int + (upasampada_regn IS NOT NULL)::int + (silmatha_regn IS NOT NULL)::int >= 1",
            name="ck_reprint_requests_target_present",
        ),
    )

    # Optional relationships for convenience
    bhikku = relationship("Bhikku", foreign_keys=[bhikku_regn], viewonly=True)
    bhikku_high = relationship("BhikkuHighRegist", foreign_keys=[bhikku_high_regn], viewonly=True)
    silmatha = relationship("SilmathaRegist", foreign_keys=[silmatha_regn], viewonly=True)
