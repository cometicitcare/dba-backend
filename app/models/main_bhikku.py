from sqlalchemy import Boolean, Column, Date, Integer, String, TIMESTAMP, text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class MainBhikku(Base):
    """Stores Nikaya Mahanayaka and Parshawaya Mahanayaka bhikku assignments."""

    __tablename__ = "main_bhikkus"

    mb_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    mb_type = Column(String(30), nullable=False, index=True)  # NIKAYA_MAHANAYAKA | PARSHAWA_MAHANAYAKA
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
    mb_start_date = Column(Date)
    mb_end_date = Column(Date)
    mb_remarks = Column(String(500))
    mb_is_active = Column(Boolean, nullable=False, server_default=text("true"))

    # Audit
    mb_is_deleted = Column(Boolean, nullable=False, server_default=text("false"))
    mb_created_at = Column(TIMESTAMP, server_default=func.now())
    mb_updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    mb_created_by = Column(String(25))
    mb_updated_by = Column(String(25))
    mb_version_number = Column(Integer, nullable=False, server_default=text("1"))

    # Relationships
    nikaya = relationship("NikayaData", foreign_keys=[mb_nikaya_cd], primaryjoin="MainBhikku.mb_nikaya_cd == NikayaData.nk_nkn", lazy="joined")
    parshawa = relationship("ParshawaData", foreign_keys=[mb_parshawa_cd], primaryjoin="MainBhikku.mb_parshawa_cd == ParshawaData.pr_prn", lazy="joined")
    bhikku = relationship("Bhikku", foreign_keys=[mb_bhikku_regn], primaryjoin="MainBhikku.mb_bhikku_regn == Bhikku.br_regn", lazy="joined")
