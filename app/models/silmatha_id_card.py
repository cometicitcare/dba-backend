# app/models/silmatha_id_card.py
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
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.db.base import Base


class SilmathaIDCard(Base):
    __tablename__ = "silmatha_id_card"

    sic_id = Column(Integer, primary_key=True, index=True)
    sic_regn = Column(
        Integer,
        ForeignKey("bhikku_regist.br_id"),
        nullable=False,
        index=True,
    )
    sic_br_id = Column(
        Integer,
        ForeignKey("bhikku_regist.br_id"),
        nullable=False,
        index=True,
    )
    sic_form_no = Column(String(20), nullable=False)
    sic_title_post = Column(String(100))
    sic_robing_date = Column(Date)
    sic_robing_place = Column(String(150))
    sic_robing_nikaya = Column(String(20))
    sic_robing_parshawaya = Column(String(20))
    sic_samanera_reg_no = Column(String(50))
    sic_upasampada_reg_no = Column(String(50))
    sic_higher_ord_date = Column(Date)
    sic_higher_ord_name = Column(String(150))
    sic_perm_residence = Column(Text)
    sic_national_id = Column(String(20))
    sic_stay_history = Column(JSONB)
    sic_left_thumbprint_url = Column(String(255))
    sic_applicant_image_url = Column(String(255))
    sic_acharya_name = Column(String(150))
    sic_current_chief_incumbent = Column(String(150))
    sic_current_chief_address = Column(Text)
    sic_nikaya_chapter_declared = Column(
        Boolean, nullable=False, server_default=text("false")
    )
    sic_grama_niladari_declared = Column(
        Boolean, nullable=False, server_default=text("false")
    )
    sic_final_approved = Column(
        Boolean, nullable=False, server_default=text("false")
    )
    sic_version = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    sic_is_deleted = Column(Boolean, nullable=False, server_default=text("false"))
    sic_created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    sic_updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    sic_created_by = Column(String(20))
    sic_updated_by = Column(String(20))
    sic_version_number = Column(Integer, nullable=False, server_default=text("1"))

