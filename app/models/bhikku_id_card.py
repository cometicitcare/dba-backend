# app/models/bhikku_id_card.py
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
    Text,
    TIMESTAMP,
    text,
    Enum,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from enum import Enum as PyEnum

from app.db.base import Base


class IDCardWorkflowStatusEnum(PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PRINTED = "printed"
    SCANNED = "scanned"
    COMPLETED = "completed"


class BhikkuIDCard(Base):
    __tablename__ = "bhikku_id_card"
    __table_args__ = (
        UniqueConstraint(
            "bic_regn", name="uq_bhikku_id_card_bic_regn"
        ),
        UniqueConstraint(
            "bic_br_id", name="uq_bhikku_id_card_bic_br_id"
        ),
    )

    bic_id = Column(Integer, primary_key=True, index=True)
    bic_regn = Column(
        String(20),
        ForeignKey("bhikku_regist.br_regn"),
        nullable=False,
        index=True,
    )
    bic_br_id = Column(
        Integer,
        ForeignKey("bhikku_regist.br_id"),
        nullable=False,
        index=True,
    )
    bic_form_no = Column(String(20), nullable=False, unique=False)
    bic_title_post = Column(String(100))
    bic_robing_date = Column(Date)
    bic_robing_place = Column(String(150))
    bic_robing_nikaya = Column(String(20))
    bic_robing_parshawaya = Column(String(20))
    bic_samanera_reg_no = Column(String(50))
    bic_upasampada_reg_no = Column(String(50))
    bic_higher_ord_date = Column(Date)
    bic_higher_ord_name = Column(String(150))
    bic_perm_residence = Column(Text)
    bic_national_id = Column(String(20))
    bic_stay_history = Column(JSONB)
    bic_left_thumbprint_url = Column(String(255))
    bic_applicant_image_url = Column(String(255))
    bic_acharya_name = Column(String(150))
    bic_current_chief_incumbent = Column(String(150))
    bic_current_chief_address = Column(Text)
    bic_nikaya_chapter_declared = Column(
        Boolean, nullable=False, server_default=text("false")
    )
    bic_grama_niladari_declared = Column(
        Boolean, nullable=False, server_default=text("false")
    )
    bic_final_approved = Column(
        Boolean, nullable=False, server_default=text("false")
    )
    bic_workflow_status = Column(String(20), nullable=False, default="pending", index=True)
    bic_version = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    bic_is_deleted = Column(Boolean, nullable=False, server_default=text("false"))
    bic_created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    bic_updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    bic_created_by = Column(String(20))
    bic_updated_by = Column(String(20))
    bic_version_number = Column(Integer, nullable=False, server_default=text("1"))
