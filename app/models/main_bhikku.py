# app/models/main_bhikku.py
from sqlalchemy import Boolean, Column, Date, Integer, String, TIMESTAMP, text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class MainBhikku(Base):
    __tablename__ = "main_bhikkus"

    mb_id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    # 'NIKAYA_MAHANAYAKA' or 'PARSHAWA_MAHANAYAKA'
    mb_type = Column(String(30), nullable=False, index=True)

    mb_nikaya_cd = Column(
        String(10),
        ForeignKey("cmm_nikayadata.nk_nkn"),
        nullable=False,
        index=True,
    )
    mb_parshawa_cd = Column(
        String(20),
        ForeignKey("cmm_parshawadata.pr_prn"),
        nullable=True,
        index=True,
    )
    mb_bhikku_regn = Column(
        String(20),
        ForeignKey("bhikku_regist.br_regn"),
        nullable=False,
        index=True,
    )

    mb_start_date = Column(Date, nullable=True)
    mb_end_date = Column(Date, nullable=True)
    mb_remarks = Column(String(500), nullable=True)
    mb_is_active = Column(Boolean, server_default=text("true"), nullable=False)

    # Audit
    mb_is_deleted = Column(Boolean, server_default=text("false"), nullable=False)
    mb_created_at = Column(TIMESTAMP, server_default=func.now())
    mb_updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    mb_created_by = Column(String(25), nullable=True)
    mb_updated_by = Column(String(25), nullable=True)
    mb_version_number = Column(Integer, server_default=text("1"), nullable=False)

    # Relationships
    nikaya = relationship("NikayaData", foreign_keys=[mb_nikaya_cd], lazy="joined")
    parshawa = relationship("ParshawaData", foreign_keys=[mb_parshawa_cd], lazy="joined")
    bhikku = relationship("Bhikku", foreign_keys=[mb_bhikku_regn], lazy="joined")
